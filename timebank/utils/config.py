from datetime import timedelta


class Config(object):
    DEBUG = False
    TESTING = False
    JWT_SECRET_KEY = '71d69e882b38fa377e97affa0ad8e4875b8ea5e10e858ba54cbb79c4b0c66739' #import os, os.urandom(32).hex()
    JWT_ACCESS_COOKIE_PATH = '/auth/'
    JWT_REFRESH_COOKIE_PATH = '/auth/refresh'
    JWT_TOKEN_LOCATION = ["cookies", "headers"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_ACCESS_CSRF_HEADER_NAME = "X-CSRF-TOKEN-ACCESS"
    JWT_REFRESH_CSRF_HEADER_NAME = "X-CSRF-TOKEN-REFRESH"

    CORS_HEADERS = 'Content-Type'

    DB_HOST = 'localhost'
    DB_PORT = '3306'
    DB_NAME = "testdatabase"
    DB_USERNAME = "root"
    DB_PASSWORD = "root"
    DB_CHARSET = "utf8mb4"

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:" \
                              f"{DB_PORT}/{DB_NAME}?charset={DB_CHARSET}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_SECURE = True

    FLASK_ADMIN_SWATCH = 'spacelab'


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = False
    TESTING = True
