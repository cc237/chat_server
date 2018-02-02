from os.path import abspath, dirname, join

# Application name
APP_NAME = 'chat-server'

# Directories
BASE_DIR = abspath(join(dirname(__file__), '..'))
LOG_DIR = join(BASE_DIR, 'logs')

# Database
SQLALCHEMY_DATABASE_URI = 'sqlite:///{dir:s}/chat_serv.db'.format(dir=BASE_DIR)
SQLALCHEMY_TRACK_MODIFICATIONS = False
