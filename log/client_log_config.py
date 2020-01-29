""" Конфигурации клиентского логгера """

import sys
from logging import getLogger, Formatter, StreamHandler, DEBUG, INFO, FileHandler

# Создаю логгер - "Регистратор" верхнего уровня
LOG = getLogger('client')

# Создаем "Обработчик" выводящий сообщения в stderr (красный текст в консоли)
STREAM_HAND = StreamHandler(sys.stderr)
FILE_HAND = FileHandler("log/client.log", encoding='utf-8')

# Устанавливаю уровень важности "Обработчику"
STREAM_HAND.setLevel(DEBUG)  # выводит логи в стандартный поток ошибок
FILE_HAND.setLevel(DEBUG)  # выводит логи в файл в кодировке unicode

# Определяем формат сообщений
FORMATTER = Formatter("%(levelname)-10s %(asctime)s %(message)s")

# Подключаю объект форматтер к "Обработчику"
STREAM_HAND.setFormatter(FORMATTER)
FILE_HAND.setFormatter(FORMATTER)

# Добавить обработчик к "Регистратору"
# LOG.addHandler(INFO_HAND)
# выводим сразу два логера
LOG.addHandler(STREAM_HAND)  # для вывода в поток
LOG.addHandler(FILE_HAND)  # и для записи в файл

# Устанавливаю уровень важности "Регистратору"
# Уровень важности "Регистратора" выше чем уровень важности "Обрботчика"
LOG.setLevel(DEBUG)


def log(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        LOG.info(f"Сработала функция: {func.__name__} со следующими аргументами: {args}, {kwargs}")
        return res
    return wrapper
