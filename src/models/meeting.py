from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base


class MeetingStatus(enum.Enum):
    """Status of a meeting and its bot"""

    SCHEDULED = "scheduled"  # Bot scheduled for future meeting
    IN_PROGRESS = "in_progress"  # Bot has joined meeting
    PROCESSING = "processing"  # Meeting ended, processing transcript/summary
    DONE = "done"  # All processing complete
    ERRORED = "errored"  # Something went wrong


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, default="Meeting in Progress")
    meeting_url = Column(String, nullable=False)  # Google Meet/Zoom URL
    status = Column(Enum(MeetingStatus), default=MeetingStatus.IN_PROGRESS)

    # Recall.ai bot tracking
    bot_id = Column(String, nullable=True, index=True)  # Recall.ai bot ID

    # Meeting data
    transcript = Column(JSON, nullable=True)  # Array of transcript segments
    summary = Column(JSON, nullable=True)  # AI-generated summary with segments
    participants = Column(JSON, nullable=True)  # Array of participant names
    duration = Column(String, nullable=True)  # e.g., "45 min"

    # Timestamps
    scheduled_time = Column(DateTime, nullable=True)  # For future scheduled meetings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    user = relationship("User", back_populates="meetings")
    notes = relationship("Note", back_populates="meeting", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Meeting(id={self.id}, title={self.title}, status={self.status}, bot_id={self.bot_id})>"
