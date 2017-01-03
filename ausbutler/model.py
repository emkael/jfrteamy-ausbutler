from cached_property import cached_property
from sqlalchemy import Column, ForeignKey, MetaData, Table, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Float, Integer

from .db import Session

Base = declarative_base()
session = Session()

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
        (b.rnd, b.segment, b.tabl) : {
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
