from app.domain import Base
from sqlalchemy import Integer
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.domain.Result import Result
from app.server import db


class Schedule(Base):
    __tablename__ = 'schedule'
    id = Column(Integer, primary_key=True)
    week = Column(Integer, nullable=False)
    game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
    result_id = Column(Integer, ForeignKey("result.id"), nullable=True)
    game = relationship("Game", foreign_keys=[game_id])
    result = relationship(Result, foreign_keys=[result_id])

    def __init__(self, week, game, result=None):
        self.week = week
        self.game = game
        self.result = result

    def toJSON(self):
        results = {}
        results['id'] = self.id
        results['week'] = self.week
        results['game'] = self.game.toJSON()

        if self.result is None:
            results['result'] = self.result
        else:
            results['result'] = self.result.toJSON()
        return results

    def play(self):
        if self.result is None:
            self.result = self.game.play()
            if self.result.home_score > self.result.away_score:
                self.game.home.wins += 1
                self.game.away.losses += 1
            else:
                self.game.away.wins += 1
                self.game.home.losses += 1

            self.game.home.points_for += self.result.home_score
            self.game.home.points_against += self.result.away_score
            self.game.away.points_for += self.result.away_score
            self.game.away.points_against += self.result.home_score

            db.session.commit()
