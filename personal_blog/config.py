import os
import platform
import json


if platform.system() != 'Windows':
    with open('/etc/blog_config.json') as config_file:
        config = json.load(config_file)
        config_exists = True
else:
    config_exists = False


if config_exists:
    class Config:
        SECRET_KEY = config.get('SECRET_KEY')
        SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
        MAIL_SERVER = 'smtp.googlemail.com'
        MAIL_PORT = 587
        MAIL_USE_TLS = True
        MAIL_USERNAME = config.get('MAIL_USERNAME')
        MAIL_PASSWORD = config.get('MAIL_PASSWORD')
        BLOG_PASSWORD = config.get('BLOG_PASSWORD')
else:
    class Config:
        SECRET_KEY = os.environ.get('SECRET_KEY')
        SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
        MAIL_SERVER = 'smtp.googlemail.com'
        MAIL_PORT = 587
        MAIL_USE_TLS = True
        MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
        MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
        BLOG_PASSWORD = os.environ.get('BLOG_PASSWORD')
