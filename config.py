import os


class Config(object):
    """
    Common configurations
    """

    # Server configuration
    HOST = '127.0.0.1'
    PORT = 8080
    SECRET_KEY = os.urandom(24).encode('hex')

    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'postgresql://fus:plop@localhost/'
    SQLALCHEMY_DATABASE_DROP = False

    # FUS configuration
    FUS_EMPTY_UPDATE = '<?xml version="1.0"?><updates></updates>'
    FUS_DOWNLOAD_PATH = 'http://192.168.248.133/download/'


class DevelopmentConfig(Config):
    """
    Development configurations
    """

    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
