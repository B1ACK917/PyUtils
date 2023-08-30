import logging
import sys

from .path import check_file

cur_logger = None
INFO = logging.INFO
DEBUG = logging.DEBUG
ERROR = logging.ERROR


def iprint(*args, **kwargs):
    if isinstance(cur_logger, logging.Logger):
        return cur_logger.info(*args, **kwargs)
    else:
        return print(*args, **kwargs)


def dprint(*args, **kwargs):
    if isinstance(cur_logger, logging.Logger):
        return cur_logger.debug(*args, **kwargs)
    else:
        return print(*args, **kwargs)


def eprint(*args, **kwargs):
    if isinstance(cur_logger, logging.Logger):
        return cur_logger.error(*args, **kwargs)
    else:
        return print(*args, **kwargs)


def create_global_logger(log_level, log_file=None):
    global cur_logger
    logger = logging.getLogger("Dark Logger")
    logger.setLevel(log_level)

    c_handler = logging.StreamHandler(stream=sys.stdout)
    c_handler.setLevel(log_level)

    c_format = logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s][%(message)s]")
    c_handler.setFormatter(c_format)

    logger.addHandler(c_handler)

    if log_file is not None:
        check_file(log_file)
        f_handler = logging.FileHandler(log_file)
        f_handler.setLevel(logging.DEBUG)
        f_format = logging.Formatter(
            "[%(asctime)s][%(name)s][%(levelname)s][%(message)s]"
        )
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)

    cur_logger = logger


def create_custom_logger(log_name, log_level, log_file=None):
    logger = logging.getLogger(log_name)
    logger.setLevel(log_level)

    c_handler = logging.StreamHandler(stream=sys.stdout)
    c_handler.setLevel(log_level)

    c_format = logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s][%(message)s]")
    c_handler.setFormatter(c_format)

    logger.addHandler(c_handler)

    if log_file is not None:
        check_file(log_file)
        f_handler = logging.FileHandler(log_file)
        f_handler.setLevel(logging.DEBUG)
        f_format = logging.Formatter(
            "[%(asctime)s][%(name)s][%(levelname)s][%(message)s]"
        )
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)

    return logger


logger_file = "log/run.log"
create_global_logger(DEBUG, logger_file)
