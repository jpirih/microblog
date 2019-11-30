import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Main application config class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'This is top secret'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 3
    ADMINS = ['janko.pirih@gmail.com']


class TestConfig(Config):
    """application testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
