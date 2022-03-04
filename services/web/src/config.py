import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # SQLite fall back for unit testing
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = f"{os.getenv('APP_FOLDER')}/project/static"
    MEDIA_FOLDER = f"{os.getenv('APP_FOLDER')}/project/media"
    SECRET_KEY = os.getenv("SECRET_KEY", "hardcoded-key-for-dev")
