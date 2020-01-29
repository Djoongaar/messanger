import json
import sys
import time
import socket
import logging
from log import client_log_config
from log.client_log_config import log
from common.settings import DEFAULT_PORT, ACTION, PRESENCE, TIME, ACCOUNT_NAME, USER, RESPONSE, ERROR, \
    DEFAULT_IP_ADDRESS
from common.utils import get_and_print_message, encode_and_send_message
LOG = logging.getLogger('client')


@log
def make_presence_message(account_name='Guest'):
    """
    Функция генерирует запрос на сервер о присутствии клиента
    :param account_name: по умолчанию Гость
    :return:
    """
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    return out


@log
def process_answer(message):
    """
    Функция разбирает ответ сервера
    :param message:
    :return:
    """
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            LOG.info("200: OK")
            return '200: OK'
        LOG.info("400: ERROR")
        return f"400: {message[ERROR]}"
    LOG.debug("Что-то странное прилетело от сервера")
    return ValueError


@log
def main():
    """
    Загружаем параметры командной строки
    :return:
    """
    try:
        server_address = sys.argv[2]
        server_port = int(sys.argv[1])
        if server_port < 1024 or server_port > 65535:
            LOG.debug("Порт может быть от 1024 до 65535")
            raise ValueError
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
    except ValueError:
        LOG.debug("Некорректный номер порта. Должен быть от 1024 до 65535")
        sys.exit(1)
    #  Инициализация сокета и обмен
    TRANSP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        TRANSP.connect((server_address, server_port))
    except ConnectionRefusedError:
        LOG.debug("Подключение не установлено, т.к. сервер отверг запрос на подключение")
    MSG_TO_SERV = make_presence_message()
    encode_and_send_message(TRANSP, MSG_TO_SERV)
    try:
        answer = process_answer(get_and_print_message(TRANSP))
        PARAMS = {'answer': answer}
        LOG.info("answer: %(answer)s", PARAMS)
    except (ValueError, json.JSONDecodeError):
        LOG.debug("Не удалось декодировать сообщение сервера")


if __name__ == '__main__':
    main()
