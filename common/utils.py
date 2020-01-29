import json
from common.settings import MAX_PACKAGE_LENGTH, ENCODING


def get_and_print_message(client):
    """
    Функция принимает данные от клиента (в байтовом представлении)
    декодирует их в строку и помещает в переменную json_response
    затем с помощью модуля json метода loads переводим из строки
    в тип "словарь"
    :param client(class socket)
    :return: response(class dict)
    """
    data = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(data, bytes):  # проверка типа данных (байты)
        json_response = data.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):  # проверка типа данных (словарь)
            # print(response)
            # print(f"тип данных client: {type(client)}")
            # print(f"тип данных json_response: {type(json_response)}")
            # print(f"тип данных response: {type(response)}")
            return response
        return ValueError
    return ValueError


def encode_and_send_message(sock, message):
    """
    Функция превращает словарь в строку с помощью модуля json метода dumps
    а затем кодирует строку в байтовое представление и отправляет как сокет
    :param sock:
    :param message:
    :return:
    """
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
