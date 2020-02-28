import argparse
import configparser
import os
import select
import sys
import socket
import logging
import threading

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMessageBox

from descriptors import Port, Address
from decorators import log
from common.settings import PRESENCE, ACTION, USER, TIME, \
    ACCOUNT_NAME, ERROR, MESSAGE, MESSAGE_TEXT, SENDER, RESPONSE_200, RESPONSE_400, DESTINATION, QUIT, GET_CONTACTS, \
    RESPONSE_202, LIST_INFO, ADD_CONTACT, DELETE_CONTACT, USERS_REQUEST
from common.utils import get_and_print_message, encode_and_send_message
from metaclasses import ServerMaker
from server_db import ServerDatabase
from server_gui import MainWindow, gui_create_model, HistoryWindow, create_stat_model, ConfigWindow

LOG = logging.getLogger('server')

# Флаг о подключении нового пользователя, чтобы не мучать БД постоянными запросами
new_connection = False
con_flag_lock = threading.Lock()


@log
def parse_cmd_args(default_address, default_port):
    """ Парсим командную строку """
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default=default_address, nargs='?')
    parser.add_argument('-p', default=default_port, type=int, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    return listen_address, listen_port


class Server(threading.Thread, metaclass=ServerMaker):
    port = Port()
    addr = Address('addr')

    def __init__(self, listen_address, listen_port, database):
        self.addr = listen_address
        self.port = listen_port
        self.database = database
        self.clients = []
        self.messages = []
        self.names = dict()
        super().__init__()

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

# ------------------------------------- ОБРАБОТКА СООБЩЕНИЙ КЛИЕНТА -------------------------------------

    def process_client_message(self, message, client):
        """ Обработчик сообщений от клиентов """
        global new_connection
        LOG.info(f'Разбираем сообщение от клиента: {message}')

        # --------------------- PRESENCE MESSAGE
        if ACTION in message and message[ACTION] == PRESENCE \
                and TIME in message and USER in message:
            # Если такой пользователь ещё не зарегистрирован,
            # регистрируем, а иначе отправляем 400 и завершаем соединение.
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                # client_ip, client_port = client.getpeername()
                # self.database.login_user(client, client_ip, client_port)
                encode_and_send_message(client, RESPONSE_200)
                with con_flag_lock:
                    new_connection = True
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято'
                encode_and_send_message(client, response)
                self.clients.remove(client)
                client.close()
            return

        # --------------------- TEXT MESSAGE
        elif ACTION in message and message[ACTION] == MESSAGE \
                and DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            self.messages.append(message)
            return

        # --------------------- QUIT
        elif ACTION in message and message[ACTION] == QUIT and ACCOUNT_NAME in message:
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            with con_flag_lock:
                new_connection = True
            return

        # --------------------- GET CONTACTS
        elif ACTION in message and message[ACTION] == GET_CONTACTS and USER in message and \
                self.names[message[USER]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = self.database.get_contacts(message[USER])
            encode_and_send_message(client, response)

        # --------------------- ADD CONTACT
        elif ACTION in message and message[ACTION] == ADD_CONTACT and ACCOUNT_NAME in message and USER in message \
                and self.names[message[USER]] == client:
            self.database.add_new_contact(message[USER])
            encode_and_send_message(client, RESPONSE_200)

        # --------------------- DELETE CONTACT
        elif ACTION in message and message[ACTION] == DELETE_CONTACT and ACCOUNT_NAME in message and USER in message \
                and self.names[message[USER]] == client:
            self.database.delete_contact(message[USER])
            encode_and_send_message(client, RESPONSE_200)

        # --------------------- USERS REQUEST
        elif ACTION in message and message[ACTION] == USERS_REQUEST and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = self.database.get_users()
            encode_and_send_message(client, response)

        # --------------------- BAD REQUEST
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            encode_and_send_message(client, response)
            return

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

    def run(self):
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
    # Загрузка файла конфигурации сервера
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f"{dir_path}/{'server.ini'}")

    listen_address, listen_port = parse_cmd_args(config['SETTINGS']['listen_address'], config['SETTINGS']['default_port'])

    database = ServerDatabase(
        os.path.join(
            config['SETTINGS']['database_path'],
            config['SETTINGS']['database_file']
        )
    )
    # создаем экземпляр класса Server()
    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    # Создаём графическое окуружение для сервера:
    server_app = QApplication(sys.argv)
    main_window = MainWindow()

    # Инициализируем параметры в окна
    main_window.statusBar().showMessage('Server Working')
    main_window.active_clients_table.setModel(gui_create_model(database))
    main_window.active_clients_table.resizeColumnsToContents()
    main_window.active_clients_table.resizeRowsToContents()

    def list_update():
        """ Function is updating list of connected users """
        global new_connection
        if new_connection:
            main_window.active_clients_table.setModel(gui_create_model(database))
            main_window.active_clients_table.resizeColumnsToContents()
            main_window.active_clients_table.resizeRowsToContents()
            with con_flag_lock:
                new_connection = False

    def show_statistics():
        """ Функция создающяя окно со статистикой клиентов """
        global stat_window
        stat_window = HistoryWindow()
        stat_window.history_table.setModel(create_stat_model(database))
        stat_window.history_table.resizeColumnsToContents()
        stat_window.history_table.resizeRowsToContents()
        stat_window.show()

    def server_config():
        """ Функция создающяя окно с настройками сервера """
        global config_window
        # Создаём окно и заносим в него текущие параметры
        config_window = ConfigWindow()
        config_window.db_path.insert(config['SETTINGS']['database_path'])
        config_window.db_file.insert(config['SETTINGS']['database_file'])
        config_window.port.insert(config['SETTINGS']['default_port'])
        config_window.ip.insert(config['SETTINGS']['listen_address'])
        config_window.save_btn.clicked.connect(save_server_config)

    def save_server_config():
        """ Функция сохранения настроек """
        global config_window
        message = QMessageBox()
        config['SETTINGS']['database_path'] = config_window.db_path.text()
        config['SETTINGS']['database_file'] = config_window.db_file.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
        else:
            config['SETTINGS']['listen_address'] = config_window.ip.text()
            if 1023 < port < 65536:
                config['SETTINGS']['Default_port'] = str(port)
                print(port)
                with open('server.ini', 'w') as conf:
                    config.write(conf)
                    message.information(
                        config_window, 'OK', 'Настройки успешно сохранены!')
            else:
                message.warning(
                    config_window,
                    'Ошибка',
                    'Порт должен быть от 1024 до 65536')

    # Таймер, обновляющий список клиентов 1 раз в секунду
    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(1000)

    # Связываем кнопки с процедурами
    main_window.refresh_button.triggered.connect(list_update)
    main_window.show_history_button.triggered.connect(show_statistics)
    main_window.config_btn.triggered.connect(server_config)

    # Запускаем GUI
    server_app.exec_()


if __name__ == '__main__':
    main()
