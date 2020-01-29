import time
import requests

def log(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        LOG.info(f"��������� �������: {func.__name__} �� ���������� �����������: {args}, {kwargs}")
        return res
    return wrapper
