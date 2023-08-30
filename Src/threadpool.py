import atexit
import queue
import threading
import weakref
from concurrent.futures import Executor, Future

from .logger import *

_shutdown = False
_threads_queues = weakref.WeakKeyDictionary()


def _python_exit():
    global _shutdown
    _shutdown = True
    items = list(_threads_queues.items())
    for t, q in items:
        q.put(None)
    for t, q in items:
        t.join()


atexit.register(_python_exit)
logger = create_custom_logger("ThreadPool Logger", logging.INFO, "log/threadpool.log")


class ThreadWorker:
    def __init__(self, future, fn, args, kwargs):
        self.future = future
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        if not self.future.set_running_or_notify_cancel():
            return
        try:
            logger.debug("{} thread activate".format(self.fn.__name__))
            result = self.fn(*self.args, **self.kwargs)
        except BaseException as exc:
            logger.exception(f"---{self.fn.__name__}---{type(exc)} {exc} ")
            self.future.set_exception(exc)
            self = None
        else:
            self.future.set_result(result)

    def __str__(self):
        return f"{(self.fn.__name__, self.args, self.kwargs)}"


class DarkThreadPool(Executor):
    MIN_WORKERS = 1
    KEEP_ALIVE_TIME = 10

    def __init__(self, max_workers: int = None, thread_name_prefix=""):
        self._max_workers = max_workers or 4
        self._thread_name_prefix = thread_name_prefix
        self._work_queue = queue.Queue(max_workers or 10)
        self._threads = weakref.WeakSet()
        self._lock_compute_threads_free_count = threading.Lock()
        self.threads_free_count = 0
        self._shutdown = False
        self._shutdown_lock = threading.Lock()

    def _change_threads_free_count(self, change_num):
        with self._lock_compute_threads_free_count:
            self.threads_free_count += change_num

    def submit(self, func, *args, **kwargs):
        with self._shutdown_lock:
            if self._shutdown:
                raise RuntimeError("Pool already shutdown")
            f = Future()
            w = ThreadWorker(f, func, args, kwargs)
            self._work_queue.put(w)
            self._adjust_thread_count()
            return f

    def _adjust_thread_count(self):
        if (self.threads_free_count <= self.MIN_WORKERS) and (
            len(self._threads) < self._max_workers
        ):
            t = SingleThread(self)
            t.daemon = True
            t.start()
            self._threads.add(t)
            _threads_queues[t] = self._work_queue

    def shutdown(self, wait=True):
        with self._shutdown_lock:
            self._shutdown = True
            self._work_queue.put(None)
        if wait:
            for t in self._threads:
                t.join()

    def get_work_queue(self):
        return self._work_queue


class SingleThread(threading.Thread):
    _lock_for_judge_threads_free_count = threading.Lock()

    def __init__(self, executorx: DarkThreadPool):
        super().__init__()
        self._executorx = executorx

    def _remove_thread(self, stop_resson=""):
        self._executorx._change_threads_free_count(-1)
        self._executorx._threads.remove(self)
        _threads_queues.pop(self)

    def run(self):
        self._executorx._change_threads_free_count(1)
        while True:
            try:
                work_item = self._executorx.get_work_queue().get(
                    block=True, timeout=self._executorx.KEEP_ALIVE_TIME
                )
            except queue.Empty:
                with self._lock_for_judge_threads_free_count:
                    if self._executorx.threads_free_count > self._executorx.MIN_WORKERS:
                        self._remove_thread()
                        break
                    else:
                        continue

            if work_item is not None:
                self._executorx._change_threads_free_count(-1)
                work_item.run()
                del work_item
                self._executorx._change_threads_free_count(1)
                continue
            if _shutdown or self._executorx._shutdown:
                self._executorx.get_work_queue().put(None)
                break


def get_current_threads_num():
    return threading.active_count()


def set_thread_pool_executor_shrinkable(min_works, keep_alive_time):
    DarkThreadPool.MIN_WORKERS = min_works
    DarkThreadPool.KEEP_ALIVE_TIME = keep_alive_time
