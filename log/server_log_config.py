""" Конфигурации серверного логгера """

import sys
from datetime import datetime
from logging import getLogger, Formatter, StreamHandler, DEBUG, INFO, FileHandler


# функция создает файл от текущей даты
# сегодня убедился в правильности работы функции - создался файл от 29 января
def get_log_file_name():
    t = datetime.now()
    return f"log/{t.year}-{t.month}-{t.day}.log"


# Создаю логгер - "Регистратор" верхнего уровня
LOG = getLogger('server')

# Создаем "Обработчик" выводящий сообщения в stderr (красный текст в консоли)
STREAM_HAND = StreamHandler(sys.stderr)
filename = get_log_file_name()
FILE_HAND = FileHandler(filename=filename, encoding='utf-8')

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
