import argparse
import json
import sys
import time
import socket
import logging
from log import client_log_config
from decorators import Log
from errors import ReqFieldMissingError, ServerError
from common.settings import DEFAULT_PORT, ACTION, PRESENCE, TIME, ACCOUNT_NAME, USER, RESPONSE, ERROR, \
    DEFAULT_IP_ADDRESS, MESSAGE, MESSAGE_TEXT, SENDER
from common.utils import get_and_print_message, encode_and_send_message
LOG = logging.getLogger('client')


@Log()
def message_from_server(message):
    """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
    if ACTION in message and message[ACTION] == MESSAGE and \
            SENDER in message and MESSAGE_TEXT in message:
        print(f'Получено сообщение от пользователя '
              f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        LOG.info(f'Получено сообщение от пользователя '
                 f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    else:
        LOG.error(f'Получено некорректное сообщение с сервера: {message}')


@Log()
def write_message(sock, account_name='Guest'):
    """Функция запрашивает текст сообщения и возвращает его.
    Так же завершает работу при вводе подобной комманды
    """
    message = input('Введите сообщение для отправки или \'!!!\' для завершения работы: ')
    if message == '!!!':
        sock.close()
        LOG.info('Завершение работы по команде пользователя.')
        print('Спасибо за использование нашего сервиса!')
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }
    LOG.debug(f'Сформирован словарь сообщения: {message_dict}')
    return message_dict


@Log()
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


@Log()
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


@Log()
def parse_cmd_args():
    """ Парсер аргументов командной строки """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    # Проверка номера порта
    if not 1023 < server_port < 65536:
        LOG.critical(
            f'Попытка запуска сервера с указанием неподходящего порта'
            f'{server_port}. Допустимы адреса с 1024 до 65535.'
        )
        sys.exit(1)
    if client_mode not in ('listen', 'send'):
        LOG.critical(f'Указан недопустимый режим работы {client_mode}')
        sys.exit(1)

    return server_address, server_port, client_mode


@Log()
def main():
    """
    Загружаем параметры командной строки
    :return:
    """
    server_address, server_port, client_mode = parse_cmd_args()
    LOG.info(
        f'Запущен клиент с параметрами: адрес сервера: {server_address}'
        f'порт: {server_port}, режим работы: {client_mode}'
    )
    #  Инициализация сокета и обмен
    try:
        TRANSP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TRANSP.connect((server_address, server_port))
        encode_and_send_message(TRANSP, make_presence_message())
        answer = process_answer(get_and_print_message(TRANSP))
        LOG.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
    except json.JSONDecodeError:
        LOG.debug("не удалось декодировать полученнную JSON строку")
        sys.exit(1)
    except ServerError as error:
        LOG.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        LOG.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        sys.exit(1)
    except ConnectionRefusedError:
        LOG.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}, '
            f'конечный компьютер отверг запрос на подключение.'
        )
        sys.exit(1)
    else:
        #  Если соединение настроено корректно то начинается обмен сообщений с ними
        if client_mode == 'send':
            print('Режим работы - отправка сообщений')
        else:
            print('Режим работы - приём сообщений')
        while True:
            if client_mode == 'send':
                try:
                    encode_and_send_message(TRANSP, write_message(TRANSP))
                except (ConnectionRefusedError, ConnectionError, ConnectionAbortedError):
                    LOG.error(f'Соединение с сервером было потеряно')
                    sys.exit(1)
            if client_mode == 'listen':
                try:
                    message_from_server(get_and_print_message(TRANSP))
                except (ConnectionRefusedError, ConnectionError, ConnectionAbortedError):
                    LOG.error(f'Соединение с сервером {server_address} было потеряно')
                    sys.exit(1)


if __name__ == '__main__':
    main()
