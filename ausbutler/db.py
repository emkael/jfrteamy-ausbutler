from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import load_config


def get_session(config=None):
    if config is None:
        config = load_config('db')
    session = sessionmaker(bind=create_engine(
        "mysql+mysqlconnector://{0[user]}:{0[pass]}@{0[host]}/{0[db]}?charset=utf8".format(
            config
        )))
    return session()
