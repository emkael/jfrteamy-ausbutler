from cached_property import cached_property
from sqlalchemy import Column, ForeignKey, MetaData, Table, func, join, literal
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import Float, Integer, String

from .db import get_session

Base = declarative_base()
session = get_session()


class Team(Base):
    __table__ = Table('teams', MetaData(bind=session.bind),
                      autoload=True)

    def __repr__(self):
        return self.shortname.encode('utf8')


class Player(Base):
    __table__ = Table('players', MetaData(bind=session.bind),
                      Column('id', Integer, primary_key=True),
                      Column('team', Integer, ForeignKey(Team.id)),
                      autoload=True)
    team_ = relationship(Team, uselist=False)

    def __repr__(self):
        return ('%s %s' % (self.gname, self.sname)).encode('utf8')


class AusButler(Base):
    __tablename__ = 'aus_butler'
    id = Column(Integer, primary_key=True)
    match = Column(Integer, primary_key=True)
    segment = Column(Integer, primary_key=True)
    score = Column(Float)
    cut_score = Column(Float)
    opp_score = Column(Float)
    corrected_score = Column(Float)
    board_count = Column(Integer)
    player = relationship('Player',
                          uselist=False,
                          foreign_keys=[id],
                          primaryjoin='AusButler.id == Player.id')

    @cached_property
    def table(self):
        for table in session.query(Segment).filter(
                (Segment.rnd == self.match) & (Segment.segment == self.segment)
        ).all():
            if self.id in [
                    table.openN, table.openS, table.openW, table.openE,
                    table.closeN, table.closeS, table.closeW, table.closeE]:
                return table
        return None

    def __repr__(self):
        return '[%d] %d-%d: %.2f-%.2f=%.2f' % (self.id,
                                               self.match, self.segment,
                                               self.score or 0.0,
                                               self.opp_score or 0.0,
                                               self.corrected_score or 0.0)


class Butler(Base):
    __table__ = Table('butler', MetaData(bind=session.bind),
                      Column('id', Integer, primary_key=True),
                      autoload=True)


class Score(Base):
    __table__ = Table('scores', MetaData(bind=session.bind),
                      Column('rnd', Integer, primary_key=True),
                      Column('segment', Integer, primary_key=True),
                      Column('tabl', Integer, primary_key=True),
                      Column('room', Integer, primary_key=True),
                      Column('board', Integer, primary_key=True),
                      autoload=True)


class Segment(Base):
    __table__ = Table('segments', MetaData(bind=session.bind),
                      Column('rnd', Integer, primary_key=True),
                      Column('segment', Integer, primary_key=True),
                      Column('tabl', Integer, primary_key=True),
                      autoload=True)

    count_cache = {
        (b.rnd, b.segment, b.tabl): {
            'open': int(b.open), 'closed': int(b.closed)
        } for b in
        session.query(
            Score.rnd, Score.segment, Score.tabl,
            func.sum(Score.butler * (Score.room == 1)).label('open'),
            func.sum(Score.butler * (Score.room == 2)).label('closed')
        ).group_by(Score.rnd, Score.segment, Score.tabl).all()
    }

    @cached_property
    def butler_count(self):
        return Segment.count_cache[(self.rnd, self.segment, self.tabl)]


class Translation(Base):
    __table__ = Table('logoh', MetaData(bind=session.bind),
                      Column('id', Integer, primary_key=True),
                      autoload=True)


class Admin(Base):
    __table__ = Table('admin', MetaData(bind=session.bind),
                      Column('shortname', String, primary_key=True),
                      autoload=True)


class Params(Base):
    __table__ = Table('params', MetaData(bind=session.bind),
                      Column('datasource', Integer, primary_key=True),
                      autoload=True)


class Parameters(Base):
    __table__ = join(Admin, Params, literal(True))
