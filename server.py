import argparse
import json
import select
import sys
import socket
import logging
import time

from log import server_log_config
from decorators import log
from common.settings import DEFAULT_PORT, MAX_CONNECTIONS, PRESENCE, ACTION, USER, TIME, \
    ACCOUNT_NAME, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT, SENDER
from common.utils import get_and_print_message, encode_and_send_message

LOG = logging.getLogger('server')


@log
def process_client_message(message, messages_list, client):
    """
    Обработчик сообщений от клиентов
    :param message:
    :param messages_list:
    :param client:
    :return:
    """
    LOG.info(f'Разбираем сообщение от клиента: {message}')
    if ACTION in message \
            and message[ACTION] == PRESENCE \
            and TIME in message \
            and USER in message \
            and message[USER][ACCOUNT_NAME] == 'Guest':
        PARAMS = {'message': message}
        LOG.info("Новое сообщение от клиента: %(message)s", PARAMS)
        encode_and_send_message(client, {RESPONSE: 200})
        return
    elif ACTION in message \
            and message[ACTION] == MESSAGE \
            and TIME in message \
            and MESSAGE_TEXT in message:
        PARAMS = {'message': message}
        LOG.info("Новое сообщение от клиента: %(message)s", PARAMS)
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
    else:
        PARAMS = {'message': message}
        LOG.info("Некорректное сообщение от клиента: %(message)s", PARAMS)
        encode_and_send_message(client, {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        })
        return


@log
def parse_cmd_args():
    """ Парсим командную строку """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if not 1023 < listen_port < 65536:
        LOG.critical(
            f'Попытка запустить сервер на неподходящем порту'
            f'{listen_port}. Допустимы адресу с 1024 по 65535'
        )
        sys.exit(1)

    return listen_address, listen_port


@log
def main():
    """
    Загрузка параметров командной строки из parse_cmd_args(),
    или устанавливается значение по умолчанию
    :return:
    """
    listen_address, listen_port = parse_cmd_args()
    # Логируем событие
    LOG.info(f'Сервер запущен на порту: {listen_port}'
             f'Адрес для подключения: {listen_address}'
             f'Если не указан то принимаются любые сокеты')
    #  Готовим сокет
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.settimeout(1)

    # Создаем очередь клиентов и сообщений
    clients = []
    messages = []

    #  Капускаем цикл прослушивания порта
    transport.listen(MAX_CONNECTIONS)
    while True:
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            LOG.info(f'Установлено соединение с ПК {client_address}')
            clients.append(client)
        read_data_list = []
        write_data_list = []
        error_list = []
        # Проверяем на наличие ждущих клиентов
        try:
            if clients:
                read_data_list, write_data_list, error_list = select.select(clients, clients, [], 0)
        except OSError:
            pass

        if read_data_list:
            for client_with_message in read_data_list:
                try:
                    process_client_message(get_and_print_message(client_with_message),
                                           messages, client_with_message)
                except:
                    LOG.info(f'Клиент {client_with_message.getpeername()}'
                             f'Отключился от сервера'
                             )
        if messages and write_data_list:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            for waiting_client in write_data_list:
                try:
                    encode_and_send_message(waiting_client, message)
                except:
                    LOG.info(f'Клиент {waiting_client.getpeername()} отключился от сервера')
                    clients.remove(waiting_client)


if __name__ == '__main__':
    main()
