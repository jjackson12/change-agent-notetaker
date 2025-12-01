from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class MeetingBot(Base):
    __tablename__ = 'meeting_bots'

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'))

    meeting = relationship("Meeting", back_populates="bots")

    def __repr__(self):
        return f"<MeetingBot(id={self.id}, meeting_id={self.meeting_id})>"