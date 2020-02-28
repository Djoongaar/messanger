# ===============  Настройки соединения сервера ==================

DEFAULT_PORT = 8888
DEFAULT_IP_ADDRESS = '127.0.0.1'
MAX_CONNECTIONS = 5
MAX_PACKAGE_LENGTH = 1024
ENCODING = 'utf-8'

# =============== Основные ключи протокола JIM ==================

TIME = 'time'
USER = 'user'
SENDER = 'sender'
ACCOUNT_NAME = 'account_name'
DESTINATION = 'to'

# ключи действий в JIM
ACTION = 'action'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
PROBE = 'probe'
MSG = 'msg'
QUIT = 'quit'
AUTHENTICATE = 'authenticate'
JOIN = 'join'
LEAVE = 'leave'
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'data_list'
DELETE_CONTACT = 'remove'
ADD_CONTACT = 'add'
USERS_REQUEST = 'get_users'

# Словари - ответы:
# 200
RESPONSE_200 = {RESPONSE: 200}
# 202
RESPONSE_202 = {RESPONSE: 202, LIST_INFO: None}
# 400
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}
