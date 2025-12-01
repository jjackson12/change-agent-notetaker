from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Meeting(Base):
    __tablename__ = 'meetings'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    scheduled_time = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="meetings")
    notes = relationship("Note", back_populates="meeting")
    meeting_bots = relationship("MeetingBot", back_populates="meeting")

    def __repr__(self):
        return f"<Meeting(id={self.id}, title={self.title}, scheduled_time={self.scheduled_time})>"