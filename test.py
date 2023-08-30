import time

from Src.path import *
from Src.threadpool import DarkThreadPool, get_current_threads_num
from Src.logger import *


def f1(a):
    time.sleep(0.2)
    print("{}".format(a))
    time.sleep(1)
    print("{}".format(a))


if __name__ == "__main__":
    pool = DarkThreadPool(200)
    for i in range(300):
        time.sleep(0.3)
        pool.submit(f1, str(i))
        iprint("Alive Thread: {}".format(get_current_threads_num()))
