from app.domain import Base
from sqlalchemy import Integer
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class Division(Base):
    __tablename__ = 'division'
    id = Column(Integer, primary_key=True)
    conference_id = Column(Integer,
                           ForeignKey('conference.id'),
                           nullable=False)
    conference = relationship("Conference", foreign_keys=[conference_id])
    teams = relationship("Team")
    name = Column(String, nullable=False)

    def toJSON(self):
        return {
            'name': self.name,
            'teams': [team.toJSON() for team in self.teams]
        }
