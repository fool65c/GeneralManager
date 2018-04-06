from app.domain import Base
from sqlalchemy import Integer
from sqlalchemy import Column
from sqlalchemy import String
from app.server import query

class Phase(Base):
    __tablename__ = 'phase'
    id = Column(Integer, primary_key=True)
    phase = Column(String, nullable=False)
    route = Column(String, nullable=False)

    def __init__(self, phase, route):
        self.phase = phase
        self.route = route

    def advance(self):
        return query(Phase).filter_by(id=self.id+1).first()

    def toJSON(self):
        return {
            'phase': self.phase,
            'id': self.id,
            'route': self.route
        }
