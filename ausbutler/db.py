import json
from os import path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import __main__

def get_session():
    session = sessionmaker(bind=create_engine(
        "mysql://{0[user]}:{0[pass]}@{0[host]}/{0[db]}".format(
            json.load(open(
                path.join(path.dirname(__main__.__file__), 'config', 'db.json')
            )))))
    return session()
