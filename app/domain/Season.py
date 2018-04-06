from app.domain import Base
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Column


class Season(Base):
    __tablename__ = 'season'
    id = Column(Integer, primary_key=True)
    season = Column(String(128),  nullable=False)

    def __init__(self, season):
        self.season = season

    def toJSON(self):
        return {
            "season": self.season
        }
