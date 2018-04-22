from app.domain import Base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class Playoff(Base):
    __tablename__ = 'playoff'
    id = Column(Integer, primary_key=True)
    rank = Column(Integer, nullable=False)
    playoff_round = Column(Integer, nullable=False)
    team_id = Column(Integer, ForeignKey('team.id'), nullable=False)
    team = relationship("Team", foreign_keys=[team_id])
    conf_id = Column(Integer, ForeignKey('conference.id'), nullable=False)
    conf = relationship("Conference", foreign_keys=[conf_id])
    game_id = Column(Integer, ForeignKey('game.id'), nullable=True)
    game = relationship("Game", foreign_keys=[game_id])
    result_id = Column(Integer, ForeignKey("result.id"), nullable=True)
    result = relationship("Result", foreign_keys=[result_id])

    def __init__(self, conf, team, playoff_round, rank, game, result=None):
        self.conf = conf
        self.team = team
        self.rank = rank
        self.playoff_round = playoff_round
        self.game = game
        self.result = result
