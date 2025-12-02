from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
    content = Column(Text, nullable=False)

    meeting = relationship("Meeting", back_populates="notes")

    def __repr__(self):
        return f"<Note id={self.id} meeting_id={self.meeting_id} content={self.content[:20]}...>"