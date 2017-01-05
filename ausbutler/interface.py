import re
from jinja2 import Environment, FileSystemLoader

from .butler import cutoff, get_opponents, get_room, normalize
from .db import get_session
from .model import AusButler, Butler
from .tour_config import Translations


class Interface(object):

    def __init__(self, config):
        self.session = get_session()
        self.config = config
        self.translation = Translations()
        self.template = Environment(loader=FileSystemLoader('template'))
        self.template.filters['translate'] = self.translation.get_translation


    def calculate_all(self):
        self.init_db()
        self.populate_db()
        self.opp_scores()
        self.normalize_scores()

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
                        aus_b.cut_score = cutoff(
                            aus_b.score,
                            self.config['cutoff_point'],
                            self.config['cutoff_rate'])
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
                if opp_butler.id in opps \
                   and (opp_butler.match < butler.match or \
                        (opp_butler.match == butler.match and opp_butler.segment <= butler.segment)):
                    averages[opp_butler.id]['sum'] += opp_butler.cut_score
                    averages[opp_butler.id]['count'] += opp_butler.board_count
            butler.opp_score = sum(
                [opp['sum'] / opp['count'] if opp['count'] > 0 else 0.0
                 for opp in averages.values()]
            ) / 2
        self.session.commit()

    def normalize_scores(self):
        for butler in self.session.query(AusButler).all():
            butler.corrected_score = normalize(
                butler, self.config['opponent_factor'])
        self.session.commit()
