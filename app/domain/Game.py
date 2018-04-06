from app.domain import Base
from sqlalchemy import Integer
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.domain.Result import Result
import math
import random


class Game(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    home_id = Column(Integer, ForeignKey("team.id"), nullable=False)
    away_id = Column(Integer, ForeignKey("team.id"), nullable=False)
    home = relationship("Team", foreign_keys=[home_id])
    away = relationship("Team", foreign_keys=[away_id])

    def __init__(self, home, away):
        self.home = home
        self.away = away

    def toJSON(self):
        return {
            'id': self.id,
            'home': self.home.toJSON(),
            'away': self.away.toJSON()
        }

    def play(self):
        homeScore = self.__weighted_score(self.home.offense, self.away.defense)
        awayScore = self.__weighted_score(self.away.offense, self.home.defense)

        # check if there is a tie
        if homeScore == awayScore:
            tieBreaker = self.__weighted_score(self.home.special_teams,
                                               self.away.special_teams)
            # home team has the advantage in the case of a tie
            if tieBreaker >= 3:
                homeScore += 3
            else:
                awayScore += 3

        result = Result(homeScore, awayScore)
        return result

    def __weighted_score(self, rating1, rating2):
        score = random.triangular(0, 55, (rating1 - rating2) * 10)
        if rating2 == 0:
            rating2 = 1
        score = score * rating1 / rating2
        score = math.ceil(score)
        if score <= 2:
            return 0
        if score <= 5:
            return 3
        if score == 8:
            return 7
        if score == 11:
            return 10
        if score > 55:
            return 55

        return score
