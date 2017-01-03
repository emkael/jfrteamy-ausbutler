from .db import Session
from .model import AusButler, Butler
from .butler import cutoff, get_room
import re


class Interface:

    def __init__(self):
        self.session = Session()

    def init_db(self, force=False):
        from .model import Base
        if force:
            Base.metadata.drop_all(self.session.get_bind())
        Base.metadata.create_all(self.session.get_bind())

    def populate_db(self):
        self.session.query(AusButler).delete()
        column_name = re.compile(r'^seg(\d+)_(\d+)$')
        for butler in self.session.query(Butler).all():
            for column, value in butler.__dict__.iteritems():
                column_match = re.match(column_name, column)
                if column_match:
                    if value is not None:
                        aus_b = AusButler()
                        aus_b.id = butler.id
                        aus_b.match = int(column_match.group(1), base=10)
                        aus_b.segment = int(column_match.group(2))
                        aus_b.score = float(value)
                        aus_b.cut_score = cutoff(aus_b.score)
                        aus_b.board_count = aus_b.table.butler_count[
                            get_room(aus_b, butler.id)]
                        self.session.add(aus_b)
        self.session.commit()

