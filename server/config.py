class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_HOST = "localhost"
    DATABASE_PORT = 27017

class ProductionConfig(Config):
    DATABASE_URI = 'movies-prod'

class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_NAME = 'movies-dev'

class TestingConfig(Config):
    TESTING = True
    DATABASE_NAME = 'movies-test'
