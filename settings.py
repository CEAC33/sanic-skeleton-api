import dotenv
from os import environ
from os.path import join, dirname

class Settings(object):

    def __init__(self, filename='.env'):
        envpath = join(dirname(__file__), filename)
        dotenv.load_dotenv(envpath)

        self.SECRET_KEY = environ.get('SECRET_KEY')
        self.SANIC_RESPONSE_TIMEOUT = 1000000000
        self.RESPONSE_TIMEOUT = 1000000000

        self.REQUEST_MAX_SIZE = 10000000000 # default 100000000
        self.REQUEST_BUFFER_QUEUE_SIZE = 10000 # default 100
