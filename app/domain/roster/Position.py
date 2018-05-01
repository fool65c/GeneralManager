from app.domain import Base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String


class Position(Base):
    __tablename__ = 'position'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    shortName = Column(String, nullable=False)
    position_weight = Column(Integer, nullable=False)
    speed_weight = Column(Integer, nullable=False)
    strength_weight = Column(Integer, nullable=False)
    position_ability_weight = Column(Integer, nullable=False)

    def __init__(self, name,
                 shortName,
                 position_weight,
                 speed_weight,
                 strength_weight,
                 position_ability_weight):
        self.name = name
        self.shortName = shortName
        self.position_weight = position_weight
        self.speed_weight = speed_weight
        self.strength_weight = strength_weight
        self.position_ability_weight = position_ability_weight

    def toJSON(self):
        return {
            "id": self.id,
            "name": self.name,
            "shortName": self.shortName
        }
