from math import floor
from app.domain import Base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class Team(Base):
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True)
    city = Column(String(128),  nullable=False)
    points_for = Column(Integer, default=0)
    points_against = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    offense = Column(Integer, default=0)
    defense = Column(Integer, default=0)
    special_teams = Column(Integer, default=0)
    division_id = Column(Integer, ForeignKey('division.id'), nullable=False)
    division = relationship("Division", foreign_keys=[division_id])

    def __init__(self, city, division, offense, defense, sT):
        self.city = city
        self.division = division
        self.offense = offense
        self.defense = defense
        self.special_teams = sT
        self.wins = 0
        self.losses = 0
        self.points_for = 0
        self.points_against = 0

    def toJSON(self):
        return {
            "id": self.id,
            "city": self.city,
            "offense": floor(self.offense),
            "defense": floor(self.defense),
            "special_teams": floor(self.special_teams),
            "wins": self.wins,
            "losses": self.losses,
            "points_for": self.points_for,
            "points_against": self.points_against
        }
