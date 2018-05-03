from app.domain import Base
from sqlalchemy import Integer
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class Champions(Base):
    __tablename__ = 'champions'
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("team.id"), nullable=True)
    team = relationship("Team", foreign_keys=[team_id])
    season_id = Column(Integer, ForeignKey("season.id"), nullable=True)
    season = relationship("Season", foreign_keys=[season_id])

    def __init__(self, team, season):
        self.team = team
        self.season = season

    def toJSON(self):
        return {
            "season": self.season,
            "team": self.team.city
        }
