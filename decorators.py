import logging
import sys

if sys.argv[0].find('client') == -1:
    LOG = logging.getLogger('server')
else:
    LOG = logging.getLogger('client')


def log(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        LOG.info(f"Сработала функция: {func.__name__} со следующими аргументами: {args}, {kwargs}")
        return res
    return wrapper
