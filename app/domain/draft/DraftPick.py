from math import ceil
from app.domain import Base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class DraftPick(Base):
    __tablename__ = 'draft_pick'
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('team.id'))
    team = relationship("Team", foreign_keys=[team_id])
    round = Column(Integer, nullable=False)
    pick = Column(Integer, nullable=False)
    overall_pick = Column(Integer, nullable=False)

    def __init__(self, team, overall_pick):
        self.team = team
        self.overall_pick = overall_pick
        self.round = ceil(overall_pick / 32)
        self.pick = overall_pick % 32 if overall_pick % 32 != 0 else 32

    def toJSON(self):
        return {
            "id": self.id,
            "team": self.team.toJSON(),
            "round": self.round,
            "pick": self.pick,
            "overall_pick": self.overall_pick
        }
