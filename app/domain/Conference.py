from app.domain import Base
from sqlalchemy import Integer
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.orm import relationship


class Conference(Base):
    __tablename__ = 'conference'
    id = Column(Integer, primary_key=True)
    divisions = relationship("Division", back_populates="conference", lazy="dynamic")
    name = Column(String, nullable=False)
    shortName = Column(String, nullable=False)

    def toJSON(self):
        return {
            'name': self.name,
            'shortName': self.shortName,
            'divisions': [division.toJSON() for division in self.divisions]
        }
