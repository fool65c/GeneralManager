from math import floor
from app.domain import Base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.domain.roster.Position import Position


class Player(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    position_id = Column(Integer, ForeignKey('position.id'))
    position = relationship(Position, foreign_keys=[position_id])
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    speed = Column(Integer, nullable=False)
    strength = Column(Integer, nullable=False)
    position_ability = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)

    def __init__(self, position,
                 firstName,
                 lastName,
                 age,
                 speed,
                 strength,
                 position_ability):
        self.position = position
        self.first_name = firstName
        self.last_name = lastName
        self.age = age
        self.speed = speed
        self.strength = strength
        self.position_ability = position_ability

    def getOverallLevel(self):
        speed_weight = self.position.speed_weight * self.speed / 100
        strength_weight = self.position.strength_weight * self.strength / 100
        position_ability = (self.position.position_ability_weight
                            * self.position_ability / 100)
        overall = speed_weight + strength_weight + position_ability
        contribution = overall * self.position.position_weight / 100
        return contribution

    def toJSON(self):
        return {
            'position': self.position.toJSON(),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'age': self.age,
            'speed': self.speed,
            'strength': self.strength,
            'skill': self.position_ability,
            'level': floor((self.getOverallLevel() /
                            self.position.position_weight) * 5),
            'level2': self.getOverallLevel(),
            'possible': self.position.position_weight
        }
