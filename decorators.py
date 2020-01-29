import logging
import sys
import traceback

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
        LOG.info(f"Сработала функция: {func.__name__} со следующими аргументами: {args}, {kwargs}. "
                 f"Вызов из модуля {func.__module__}")
        stack = traceback.format_stack()
        for line in range(len(stack)):
            LOG.info(f"Функция была вызвана из {(stack[line]) if line == len(stack) - 2 else None}")
        return res
    return wrapper


class Log:
    """ Класс-декоратор логирования (отправлю логировать клиента) """
    def __call__(self, func):
        def decorator(*args, **kwargs):
            res = func(*args, **kwargs)
            LOG.info(f"Сработала функция: {func.__name__} со следующими аргументами: {args}, {kwargs}. "
                     f"Вызов из модуля {func.__module__}")
            stack = traceback.format_stack()
            for line in range(len(stack)):
                LOG.info(f"Функция была вызвана из {(stack[line]) if line == len(stack) - 2 else None}")
            return res
        return decorator
