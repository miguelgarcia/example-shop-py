import os

class BaseConfig:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_secret')
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../simple-shop.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #SQLALCHEMY_ECHO = True

class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True

class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'sqlite:////tmp/simple-shop_test.db')

class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
    
