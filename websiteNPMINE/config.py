import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY').encode('utf-8')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    TEMP_FOLDER = os.getenv('TEMP_FOLDER')
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')
    MAIL_USERNAME = os.getenv('EMAIL_USER')
    MAIL_PASSWORD = os.getenv('EMAIL_PASS')
    TEMPLATES_AUTO_RELOAD = True

class DevelopmentConfig(Config):
    DEBUG = True # Ensure debug is True for dev
    TEMPLATES_AUTO_RELOAD = True
    # ... other dev-specific settings

class ProductionConfig(Config):
    DEBUG = False
    TEMPLATES_AUTO_RELOAD = False # Explicitly false or omit for prod
    # ... other prod-specific settings