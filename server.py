import json
import sys
import socket
import logging
from log import server_log_config
from decorators import log
from common.settings import DEFAULT_PORT, MAX_CONNECTIONS, PRESENCE, ACTION, USER, TIME, \
    ACCOUNT_NAME, RESPONSE, ERROR
from common.utils import get_and_print_message, encode_and_send_message
LOG = logging.getLogger('server')


@log
def process_client_message(message):
    """
    Обработчик сообщений от клиентов
    :param message:
    :return:
    """
    if ACTION in message \
            and message[ACTION] == PRESENCE \
            and TIME in message \
            and USER in message \
            and message[USER][ACCOUNT_NAME] == 'Guest':
        PARAMS = {'message': message}
        LOG.info("Новое сообщение от клиента: %(message)s", PARAMS)
        return {RESPONSE: 200}
    PARAMS = {'message': message}
    LOG.info("Некорректное сообщение от клиента: %(message)s", PARAMS)
    return {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }


@log
def main():
    """
    Загрузка параметров командной строки, или устанавливается значение по умолчанию
    Для проверки запуска в параметрах PyCharm указать
    server.py -p 9090 -a 127.0.0.1
    :return:
    """
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        LOG.debug("После параметра -p необходимо указать номер порта")
        sys.exit(1)
    except ValueError:
        LOG.debug("В качестве параметров должно быть указано число от 1024 до 65535")
        sys.exit(1)

    #  Затем загружать какой адрес слушать
    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''

    except IndexError:
        LOG.debug("После параметра -a - необходимо указать адрес который будет слушать сервер")
        sys.exit(1)

    #  Готовим сокет

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))

    #  Слушаем порт
    transport.listen(MAX_CONNECTIONS)
    PARAMS = {'port': listen_port, 'error': ValueError}
    LOG.info("Сервер запущен на порту %(port)d", PARAMS)
    while True:
        client, client_address = transport.accept()
        try:
            message_from_client = get_and_print_message(client)
            response = process_client_message(message_from_client)
            encode_and_send_message(client, response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            LOG.debug("Принято некорректное сообщение от клиента")
            client.close()


if __name__ == '__main__':
    main()
