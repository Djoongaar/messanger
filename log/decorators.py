import time
import requests

def log(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        LOG.info(f"Сработала функция: {func.__name__} со следующими аргументами: {args}, {kwargs}")
        return res
    return wrapper
