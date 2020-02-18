import argparse
import json
import select
import sys
import socket
import logging
import time

from descriptors import Port, Address
from log import server_log_config
from decorators import log
from common.settings import DEFAULT_PORT, MAX_CONNECTIONS, PRESENCE, ACTION, USER, TIME, \
    ACCOUNT_NAME, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT, SENDER, RESPONSE_200, RESPONSE_400, DESTINATION, QUIT
from common.utils import get_and_print_message, encode_and_send_message
from metaclasses import ServerMaker

LOG = logging.getLogger('server')


@log
def parse_cmd_args():
    """ Парсим командную строку """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='127.0.0.1', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    return listen_address, listen_port


# class Server:
class Server(metaclass=ServerMaker):
    port = Port()
    addr = Address('addr')

    def __init__(self, listen_address, listen_port):
        self.addr = listen_address
        self.port = listen_port
        self.clients = []
        self.messages = []
        self.names = dict()

    def init_socket(self):
        """ Инициализируем сокет """
        # Логируем событие
        LOG.info(f'Сервер запущен на порту: {self.port}'
                 f'Адрес для подключения: {self.addr}'
                 f'Если не указан то принимаются любые сокеты')
        #  Готовим сокет
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.addr, self.port))
        transport.settimeout(1)

        # Начинаем слушать сокет
        self.sock = transport
        self.sock.listen()

    @log
    def process_client_message(self, message, client):
        """ Обработчик сообщений от клиентов """
        LOG.info(f'Разбираем сообщение от клиента: {message}')
        if ACTION in message and message[ACTION] == PRESENCE \
                and TIME in message and USER in message:
            # Если такой пользователь ещё не зарегистрирован,
            # регистрируем, а иначе отправляем 400 и завершаем соединение.
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                encode_and_send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято'
                encode_and_send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        elif ACTION in message and message[ACTION] == MESSAGE \
                and DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            self.messages.append(message)
            return
        elif ACTION in message and message[ACTION] == QUIT and ACCOUNT_NAME in message:
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            return
        else:
            # Иначе выкидываем исключение
            # PARAMS = {'message': message}
            # LOG.info("Некорректное сообщение от клиента: %(message)s", PARAMS)
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            encode_and_send_message(client, response)
            return

    @log
    def process_message(self, message, listen_socks):
        """ Отправка сообщения определённому клиенту """
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_socks:
            encode_and_send_message(self.names[message[DESTINATION]], message)
            LOG.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                     f'от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            LOG.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
                f'отправка сообщения невозможна.')

    @log
    def main_process(self):
        # запускаем инициацию сокета
        self.init_socket()
        while True:
            #  ждем подключения
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                LOG.info(f'Установлено соединение с ПК {client_address}')
                self.clients.append(client)

            read_data_list = []
            write_data_list = []
            error_list = []

            # Проверяем наличие ждущих клиентов
            try:
                if self.clients:
                    read_data_list, write_data_list, error_list = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            # Принимаем сообщение и если ошибка выбрасываем исключение
            if read_data_list:
                for client_with_message in read_data_list:
                    try:
                        self.process_client_message(get_and_print_message(client_with_message), client_with_message)
                    except Exception:
                        LOG.info(f'Клиент {client_with_message.getpeername()}'
                                 f'Отключился от сервера')
                        self.clients.remove(client_with_message)
            for message in self.messages:
                try:
                    self.process_message(message, write_data_list)
                except:
                    LOG.info(f"Связь с клиентом с именем {message[DESTINATION]} была потеряна")
                    self.clients.remove(self.names[message[DESTINATION]])
                    del self.names[message[DESTINATION]]
            self.messages.clear()


def main():
    """ Загрузка параметров командной строки из parse_cmd_args(), или устанавливается значение по умолчанию """
    listen_address, listen_port = parse_cmd_args()

    # создаем экземпляр класса Server()
    server = Server(listen_address, listen_port)
    server.main_process()


if __name__ == '__main__':
    main()
