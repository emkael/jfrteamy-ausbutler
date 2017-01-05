from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import load_config

def get_session():
    session = sessionmaker(bind=create_engine(
        "mysql://{0[user]}:{0[pass]}@{0[host]}/{0[db]}".format(
            load_config('db')
        )))
    return session()
