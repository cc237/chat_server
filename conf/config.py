import logging
from os.path import abspath, dirname, join

# Application name
APP_NAME = 'chat-server'

# Directories
BASE_DIR = abspath(join(dirname(__file__), '..'))
LOG_DIR = join(BASE_DIR, 'logs')

# Logging parameters
LOG_LEVEL = logging.DEBUG
LOG_SIZE = 10 * 1024 * 1024
LOG_COUNT = 10
LOG_FORMAT_P1 = '[%(asctime)s] [%(levelname)8s] -- %(message)s '
LOG_FORMAT_P2 = '(%(funcName)s@%(pathname)s:%(lineno)d) '
LOG_FORMAT_P3 = '[PID:%(process)d-%(threadName)s:%(thread)d]'
LOG_FORMAT = LOG_FORMAT_P1 + LOG_FORMAT_P2 + LOG_FORMAT_P3

# Database
SQLALCHEMY_DATABASE_URI = 'sqlite:///{dir:s}/chat_serv.db'.format(dir=BASE_DIR)
SQLALCHEMY_TRACK_MODIFICATIONS = False
