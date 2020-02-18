import logging
from re import fullmatch

LOG_SERVER = logging.getLogger('server')
LOG_CLIENT = logging.getLogger('client')


class Port:
    """ Дескриптор порта. В новом стиле """
    def __set__(self, instance, value):
        # instance - <__main__.Server object at 0x000000D582740C50>
        # value - 7777
        if not isinstance(value, int):
            LOG_SERVER.critical(
                f'Попытка запуска сервера с указанием неподходящего порта {value}. Допустимы адреса с только цифры.')
            exit(1)
        elif not 1023 < value < 65536:
            LOG_SERVER.critical(
                f'Попытка запуска сервера с указанием неподходящего порта {value}. Допустимы адреса с 1024 до 65535.')
            exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


class Address:
    """ Дескриптор адреса. В старом стиле """
    def __init__(self, my_attr):
        self.my_attr = my_attr

    def __get__(self, instance, owner):
        return instance.__dict__[self.my_attr]

    def __set__(self, instance, value):
        if not fullmatch(r'[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}', value):
            LOG_SERVER.critical(f"Указан недопустимый адрес {value}")
            exit(1)
        instance.__dict__[self.my_attr] = value

    def __delete__(self, instance):
        del instance.__dict__[self.my_attr]


class AccountName:
    """ Дескриптор имени аккаунта. В старом стиле """
    def __init__(self, my_attr):
        self.my_attr = my_attr

    def __get__(self, instance, owner):
        return instance.__dict__[self.my_attr]

    def __set__(self, instance, value):
        if not isinstance(value, str):
            LOG_CLIENT.critical(f"Имя пользователя должно иметь <class:'str'>")
            exit(1)
        elif not fullmatch(r'[a-zA-Z_\-]{2,30}[0-9]{,10}', value):
            LOG_CLIENT.critical(f"'Указано недопустимое имя клиента {value}")
            LOG_CLIENT.critical(f'Имя может содержать от 2 до 30 букв английского алфавита и не более 10 цифр в конце')
            exit(1)
        instance.__dict__[self.my_attr] = value

    def __delete__(self, instance):
        del instance.__dict__[self.my_attr]
