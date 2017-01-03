from .db import Session
from .model import AusButler, Butler
from .butler import cutoff, get_opponents, get_room, normalize
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

    def opp_scores(self):
        butlers = self.session.query(AusButler).all()
        for butler in butlers:
            opps = get_opponents(butler, butler.id)
            averages = {opps[0]: {'sum': 0.0, 'count': 0},
                        opps[1]: {'sum': 0.0, 'count': 0}}
            for opp_butler in butlers:
                if opp_butler.id in opps and (opp_butler.match < butler.match or (opp_butler.match == butler.match and opp_butler.segment < butler.segment)):
                    averages[opp_butler.id]['sum'] += opp_butler.score
                    averages[opp_butler.id]['count'] += opp_butler.board_count
            butler.opp_score = sum(
                [opp['sum'] / opp['count'] if opp['count'] > 0 else 0.0
                 for opp in averages.values()]
            ) / 2
        self.session.commit()

    def normalize_scores(self):
        for butler in self.session.query(AusButler).all():
            butler.corrected_score = normalize(butler)
        self.session.commit()
