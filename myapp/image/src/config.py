from os import getenv
from random import randrange

class Config:
    port = int(getenv('PORT', 8080))
    debug = getenv('DEBUG') == "true"
    alive_timeout = randrange(0, int(getenv('ALIVE_TIMEOUT', 60)), 5)
    version = getenv('VERSION', 'red')
