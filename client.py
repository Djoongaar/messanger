import argparse
import json
import re
import sys
import threading
import time
import socket
import logging

from descriptors import AccountName
from log import client_log_config
from decorators import Log
from errors import ReqFieldMissingError, ServerError, IncorrectDataRecivedError
from common.settings import *
from common.utils import *
from metaclasses import ClientMaker

LOG = logging.getLogger('client')


# ============================================= CLIENTS ACTIONS =============================================
class ClientActions(threading.Thread):
    """ Класс активных действий клиента """
    account_name = AccountName('account_name')

    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def run(self):
        """ Взаимодействие с клиентом """
        self.print_help()
        print(type(self.account_name))
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.write_message()
            elif command == 'help':
                self.print_help()
            elif command == 'quit':
                encode_and_send_message(self.sock, self.write_quit_message())
                print('Завершение соединения')
                LOG.info(f'Завершение работы пользователя {self.account_name} по команде quit')
                time.sleep(2)
                break
            else:
                LOG.debug(f"Ошибка ввода команды пользователем. Команды {command} не существует")
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    def print_help(self):
        """ СПРАВКА """
        print('Поддерживаемые команды:')
        print('message - отправить сообщение.')
        print('help - вывести подсказки по командам.')
        print('quit - выход из программы.')

    def write_message(self):
        """ CREATE MESSAGE """
        to_user = input('Введите имя получателя: ')
        message = input('Введите сообщение для отправки: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        LOG.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            encode_and_send_message(self.sock, message_dict)
            LOG.info(f"Отправлено сообщение для пользователя {to_user}")
        except (ConnectionRefusedError, ConnectionError, ConnectionAbortedError):
            LOG.critical('Потеряно соединение с сервером')
            sys.exit(1)

    def write_quit_message(self):
        """ EXIT MESSAGE """
        return {
            ACTION: QUIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }


# ======================================== CLIENT READING ===========================================

class ClientReadsMessage(threading.Thread):
    """ Класс чтения сообщений клиентом """
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def run(self):
        """ Функция - обработчик сообщений других пользователей, поступающих с сервера"""
        while True:
            try:
                message = get_and_print_message(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and \
                        SENDER in message and MESSAGE_TEXT in message and message[DESTINATION] == self.account_name:
                    print(f'Получено сообщение от пользователя '
                          f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    LOG.info(f'Получено сообщение от пользователя '
                             f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                else:
                    LOG.error(f'Получено некорректное сообщение с сервера: {message}')
            except IncorrectDataRecivedError:
                LOG.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                LOG.critical(f'Потеряно соединение с сервером.')
                break

# ======================================== / MESSAGE PROCESSING ===========================================


@Log()
def make_presence_message(account_name):
    """ PRESENCE MESSAGE """
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
    """ Функция разбирает ответ сервера """
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            LOG.info("200: OK")
            return '200: OK'
        LOG.info("400: ERROR")
        return f"400: {message[ERROR]}"
    LOG.debug("Что-то странное прилетело от сервера")
    return ValueError


def parse_cmd_args():
    """ Парсер аргументов командной строки """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default='None', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    account_name = namespace.name

    # Проверка номера порта
    if not 1023 < server_port < 65536:
        LOG.critical(
            f'Попытка запуска сервера с указанием неподходящего порта'
            f'{server_port}. Допустимы адреса с 1024 до 65535.'
        )
        sys.exit(1)

    return server_address, server_port, account_name


# ============================================== MAIN =================================================


def main():
    """ Загружаем параметры командной строки """
    print('Консольный месседжер. Клиентский модуль.')

    # Загружаем параметры командной строки
    server_address, server_port, account_name = parse_cmd_args()
    if not account_name:
        client_name = input('Введите имя пользователя: ')

    LOG.info(
        f'Запущен клиент с параметрами: адрес сервера: {server_address}'
        f'порт: {server_port}, режим работы: {account_name}'
    )
    #  Инициализация сокета и обмен
    try:
        transp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transp.connect((server_address, server_port))
        encode_and_send_message(transp, make_presence_message(account_name))
        answer = process_answer(get_and_print_message(transp))
        LOG.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
    except json.JSONDecodeError:
        LOG.debug("Не удалось декодировать полученнную JSON строку")
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
        #  Если соединение настроено корректно то запускаем клиентский процесс приема сообщений
        receiver = ClientReadsMessage(account_name, transp)
        receiver.daemon = True
        receiver.start()

        # затем запускаем отправку сообщений
        user_interface = ClientActions(account_name, transp)
        user_interface.daemon = True
        user_interface.start()
        user_interface.join()
        LOG.debug('Запущены процессы')

        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
