from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config

db = SQLAlchemy()

class Settings(object):
    SECRET_KEY = Config.SECRET_KEY
    SQLALCHEMY_DATABASE_URI = Config.DATABASE_URL