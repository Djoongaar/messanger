# ===============  Настройки соединения сервера ==================

DEFAULT_PORT = 8888
DEFAULT_IP_ADDRESS = '127.0.0.1'
MAX_CONNECTIONS = 5
MAX_PACKAGE_LENGTH = 1024
ENCODING = 'utf-8'

# =============== Основные ключи протокола JIM ==================

TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'

# ключи действий в JIM
ACTION = 'action'
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
PROBE = 'probe'
MSG = 'msg'
QUIT = 'quit'
AUTHENTICATE = 'authenticate'
JOIN = 'join'
LEAVE = 'leave'
