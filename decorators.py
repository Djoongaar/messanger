import logging
import sys

if sys.argv[0].find('client') == -1:
    print(sys.argv)
    LOG = logging.getLogger('server')
else:
    print(sys.argv)
    LOG = logging.getLogger('client')


def log(func):
    """ Функция-декоратор логирования (отправлю логировать сервер) """
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        LOG.info(f"Сработала функция: {func.__name__} со следующими аргументами: {args}, {kwargs}")
        return res
    return wrapper


class Log:
    """ Класс-декоратор логирования (отправлю логировать клиента) """
    def __call__(self, func):
        def decorator(*args, **kwargs):
            res = func(*args, **kwargs)
            LOG.info(f"Сработала функция: {func.__name__} со следующими аргументами: {args}, {kwargs}")
            return res
        return decorator
