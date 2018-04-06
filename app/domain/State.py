from app.domain import Base
from sqlalchemy import Integer
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class State(Base):
    __tablename__ = 'state'
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("team.id"), nullable=True)
    phase_id = Column(Integer, ForeignKey("phase.id"), nullable=False)
    team = relationship("Team", foreign_keys=[team_id])
    phase = relationship("Phase", foreign_keys=[phase_id])

    def __init__(self, phase, team):
        self.team = team
        self.phase = phase

    def setTeam(self, team):
        if self.phase.phase == "NEWGAME":
            self.team = team
            self.advancePhase()
        else:
            raise Exception('Can not switch teams while game is inprogress')

    def advancePhase(self):
        self.phase = self.phase.advance()

    def toJSON(self):
        state = {}
        state['phase'] = self.phase.toJSON()
        if self.team is None:
            state['team'] = None
        else:
            state['team'] = self.team.toJSON()

        return state
