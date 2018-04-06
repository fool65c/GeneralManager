from app.domain import Base
from sqlalchemy import Integer
from sqlalchemy import Column


class Result(Base):
    __tablename__ = 'result'
    id = Column(Integer, primary_key=True)
    home_score = Column(Integer, nullable=False)
    away_score = Column(Integer, nullable=False)

    def __init__(self, home_score, away_score):
        self.home_score = home_score
        self.away_score = away_score

    def toJSON(self):
        return {
            'id': self.id,
            'home_score': self.home_score,
            'away_score': self.away_score
        }
