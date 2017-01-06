import re
from copy import copy
from datetime import datetime
from os import path

from jinja2 import Environment, FileSystemLoader

from .butler import cutoff, get_line, get_opponents, get_room, normalize
from .db import get_session
from .model import AusButler, Butler
from .tour_config import Constants, Translations


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
                   and (opp_butler.match < butler.match or
                        (opp_butler.match == butler.match and
                         opp_butler.segment <= butler.segment)):
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

    def generate_all(self):
        files = []
        files += self.generate_segments()
        files += self.generate_frames()
        files += self.generate_table()
        return list(set(files))

    def generate_frames(self):
        files = []
        template = self.template.get_template('frame.html')
        for round_no in range(1, Constants.rnd + 1):
            for segment_no in range(1, Constants.segmentsperround + 1):
                first_board = 1 + (segment_no - 1) * Constants.boardspersegment
                filename = '%snormbutler%d-%d.htm' % (
                    Constants.shortname,
                    round_no, segment_no
                )
                file(path.join(Constants.path, filename), 'w').write(
                    template.render({
                        'prefix': Constants.shortname,
                        'round_no': round_no,
                        'segment_no': segment_no,
                        'first_board': first_board
                    }).encode('utf8')
                )
                files.append(filename)
        return files

    def generate_segments(self):
        files = []
        template = self.template.get_template('segment.html')
        for round_no in range(1, Constants.rnd + 1):
            for segment_no in range(1, Constants.segmentsperround + 1):
                first_board = 1 + (segment_no - 1) * Constants.boardspersegment
                filename = '%snormbutler%d-%d.html' % (
                    Constants.shortname,
                    round_no, segment_no
                )
                results = {}
                for butler in self.session.query(AusButler).filter(
                        AusButler.match == round_no,
                        AusButler.segment == segment_no):
                    line = 'TABLE_%s' % (get_line(butler, butler.id))
                    position = '%d%s' % (
                        butler.table.tabl,
                        self.translation.get_translation(line)
                    )
                    if position not in results:
                        results[position] = {'players': []}
                    results[position]['place'] = ''
                    results[position]['players'].append(
                        str(butler.player).decode('utf8'))
                    results[position]['position'] = position
                    results[position]['team'] = str(
                        butler.player.team_).decode('utf8')
                    results[position]['score'] = butler.score
                    results[position]['opp_score'] = butler.opp_score
                    results[position]['norm_score'] = butler.corrected_score
                results = sorted(results.values(),
                                 key=lambda r: r['norm_score'], reverse=True)
                place = 1
                previous = None
                for r in range(0, len(results)):
                    if results[r]['norm_score'] != previous:
                        results[r]['place'] = place
                    previous = results[r]['norm_score']
                    place += 1
                file(path.join(Constants.path, filename), 'w').write(
                    template.render({
                        'prefix': Constants.shortname,
                        'logoh': Constants.logoh,
                        'round_no': round_no,
                        'segment_no': segment_no,
                        'results': results,
                        'boards': range(
                            first_board,
                            first_board + Constants.boardspersegment
                        ),
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'time': datetime.now().strftime('%H:%M')
                    }).encode('utf8')
                )
                files.append(filename)
        return files

    def generate_table(self):
        template = self.template.get_template('table.html')
        filename = '%snormbutler.html' % (Constants.shortname)
        segments = []
        result_template = []
        for rnd in range(1, Constants.rnd + 1):
            for segment in range(1, Constants.segmentsperround + 1):
                segments.append({'round': rnd, 'segment': segment})
                result_template.append('')
        players = {}
        for butler in self.session.query(AusButler).all():
            if butler.id not in players:
                players[butler.id] = {
                    'name': str(butler.player).decode('utf8'),
                    'team': str(butler.player.team_).decode('utf8'),
                    'sum': 0,
                    'count': 0,
                    'results': copy(result_template)
                }
            players[butler.id]['sum'] += butler.corrected_score
            players[butler.id]['count'] += butler.board_count
            players[butler.id]['results'][
                (butler.match - 1) * Constants.segmentsperround +
                butler.segment - 1
            ] = butler.corrected_score
        for player in players.values():
            if player['count'] > 0:
                player['sum'] /= player['count']
        players = sorted(players.values(),
                         key=lambda p: p['sum'], reverse=True)
        board_threshold = Constants.boardspersegment
        board_threshold *= Constants.segmentsperround
        board_threshold *= Constants.rnd + (
            Constants.roundcnt * (Constants.minbutler / 100.0 - 1)
        )
        above_threshold = []
        below_threshold = []
        for player in players:
            if player['count'] >= board_threshold:
                above_threshold.append(player)
            else:
                below_threshold.append(player)
        for p_list in [above_threshold, below_threshold]:
            place = 1
            prev = None
            for player in p_list:
                if player['sum'] != prev:
                    player['place'] = place
                prev = player['sum']
                place += 1
        file(path.join(Constants.path, filename), 'w').write(
            template.render({
                'prefix': Constants.shortname,
                'logoh': Constants.logoh,
                'percent_threshold': Constants.minbutler,
                'segments': segments,
                'segment_limit': self.config['segments_in_table_limit'],
                'above_threshold': above_threshold,
                'below_threshold': below_threshold,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': datetime.now().strftime('%H:%M')
            }).encode('utf8')
        )
        return [filename]
