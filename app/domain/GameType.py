from app.domain import Base
from sqlalchemy import Integer
from sqlalchemy import Column
from sqlalchemy import String


class GameType(Base):
    __tablename__ = 'game_type'
    id = Column(Integer, primary_key=True)
    game_type = Column(String(128),  nullable=False)

    def __init__(self, gameType):
        self.game_type = gameType

    def toJSON(self):
        return {
            'id': self.id,
            'game_type': self.game_type
        }
