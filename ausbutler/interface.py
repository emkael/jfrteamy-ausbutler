from .db import Session


class Interface:

    def __init__(self):
        self.session = Session()

    def init_db(self, force=False):
        from .model import Base
        if force:
            Base.metadata.drop_all(self.session.get_bind())
        Base.metadata.create_all(self.session.get_bind())

