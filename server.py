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
    ACCOUNT_NAME, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT, SENDER, RESPONSE_200, RESPONSE_400, DESTINATION, QUIT
from common.utils import get_and_print_message, encode_and_send_message

LOG = logging.getLogger('server')


@log
def process_client_message(message, messages_list, client, clients, names):
    """ Обработчик сообщений от клиентов """
    LOG.info(f'Разбираем сообщение от клиента: {message}')
    if ACTION in message and message[ACTION] == PRESENCE \
            and TIME in message and USER in message:
        # Если такой пользователь ещё не зарегистрирован,
        # регистрируем, а иначе отправляем 400 и завершаем соединение.
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            encode_and_send_message(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Имя пользователя уже занято'
            encode_and_send_message(client, response)
            clients.remove(client)
            client.close()
        return
    elif ACTION in message and message[ACTION] == MESSAGE \
            and DESTINATION in message and TIME in message \
            and SENDER in message and MESSAGE_TEXT in message:
        # PARAMS = {'message': message}
        # LOG.info("Новое сообщение от клиента: %(message)s", PARAMS)
        messages_list.append(message)
        return
    elif ACTION in message and message[ACTION] == QUIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    else:
        # PARAMS = {'message': message}
        # LOG.info("Некорректное сообщение от клиента: %(message)s", PARAMS)
        response = RESPONSE_400
        response[ERROR] = 'Запрос некорректен.'
        encode_and_send_message(client, response)
        return


@log
def process_message(message, names, listen_socks):
    """ Отправка сообщения определённому клиенту """
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        encode_and_send_message(names[message[DESTINATION]], message)
        LOG.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                 f'от пользователя {message[SENDER]}.')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        LOG.error(
            f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
            f'отправка сообщения невозможна.')


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


def main():
    """ Загрузка параметров командной строки из parse_cmd_args(), или устанавливается значение по умолчанию """
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

    # Словарь, содержащий имена пользователей и соответствующие им сокеты.
    names = dict()

    #  Запускаем цикл прослушивания порта
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
                                           messages, client_with_message, clients, names)
                except Exception:
                    LOG.info(f'Клиент {client_with_message.getpeername()}'
                             f'Отключился от сервера'
                             )
                    clients.remove(client_with_message)
        for i in messages:
            try:
                process_message(i, names, write_data_list)
            except Exception:
                LOG.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                clients.remove(names[i[DESTINATION]])
                del names[i[DESTINATION]]
        messages.clear()


if __name__ == '__main__':
    main()
