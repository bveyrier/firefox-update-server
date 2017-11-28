import os

DEBUG = True

# Server configuration
HOST = '127.0.0.1'
PORT = 8080
SECRET_KEY = os.urandom(24).encode('hex')
