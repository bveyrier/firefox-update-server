import os

DEBUG = True

# Server configuration
HOST = '127.0.0.1'
PORT = 8080
SECRET_KEY = os.urandom(24).encode('hex')


# Database configuration
SQLALCHEMY_DB_URI = 'postgresql://fus:plop@localhost/'
SQLALCHEMY_DB_DROP = False


# FUS configuration
FUS_EMPTY_UPDATE = '<?xml version="1.0"?><updates></updates>'
