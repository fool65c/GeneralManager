from app.domain import Base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class TeamToPlayer(Base):
    __tablename__ = 'team_player'
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    player = relationship("Player", foreign_keys=[player_id])
    team_id = Column(Integer, ForeignKey('team.id'))
    team = relationship("Team", foreign_keys=[team_id])
    starter = Column(Boolean, default=False)

    def __init__(self, player, team, starter):
        self.player = player
        self.starter = starter
        self.team = team

    def toJSON(self):
        return {
            "id": self.id,
            "player": self.player.toJSON(),
            "team": self.team.toJSON(),
            "starter": self.starter
        }
