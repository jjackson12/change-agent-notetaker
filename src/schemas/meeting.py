from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MeetingStatus(str, Enum):
    """Status of a meeting and its bot"""

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    PROCESSING = "processing"
    DONE = "done"
    ERRORED = "errored"


class TranscriptSegment(BaseModel):
    """A segment of meeting transcript"""

    name: Optional[str] = None  # Speaker name
    id: Optional[str] = None  # Speaker ID
    words: str  # The text content
    start_timestamp: Optional[float] = None  # Seconds from start
    end_timestamp: Optional[float] = None  # Seconds from start


class SummarySegment(BaseModel):
    """A segment of meeting summary (text, participant mention, or timestamp link)"""

    type: str  # "text", "participant", or "timestamp_link"
    content: str
    participant_id: Optional[str] = Field(
        None, alias="participantId"
    )  # For participant type
    timestamp: Optional[float] = None  # For timestamp_link type
    class_name: Optional[str] = Field(None, alias="className")  # For styling

    class Config:
        populate_by_name = True


class ParticipantInfo(BaseModel):
    """Information about a meeting participant"""

    id: str
    name: str
    color_class: str = Field(
        ..., alias="colorClass"
    )  # e.g., "bg-blue-50 text-blue-900"

    class Config:
        populate_by_name = True


class Summary(BaseModel):
    """AI-generated meeting summary"""

    content: List[SummarySegment]
    participants: List[ParticipantInfo]


class MeetingCreate(BaseModel):
    """Schema for creating a new meeting (triggering a bot)"""

    meeting_url: str = Field(..., description="Google Meet or Zoom meeting URL")
    user_id: Optional[int] = None


class MeetingSchedule(BaseModel):
    """Schema for scheduling a bot for a future meeting"""

    meeting_url: str
    scheduled_time: datetime
    title: Optional[str] = None
    user_id: Optional[int] = None


class MeetingUpdate(BaseModel):
    """Schema for updating meeting"""

    title: Optional[str] = None
    status: Optional[MeetingStatus] = None
    transcript: Optional[List[TranscriptSegment]] = None
    summary: Optional[Summary] = None
    participants: Optional[List[str]] = None
    duration: Optional[str] = None


class MeetingResponse(BaseModel):
    """Schema for meeting response"""

    id: int
    title: str
    meeting_url: str
    status: MeetingStatus
    bot_id: Optional[str] = None
    transcript: Optional[List[TranscriptSegment]] = None
    summary: Optional[Summary] = None
    participants: Optional[List[str]] = None
    duration: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    user_id: Optional[int] = None

    class Config:
        from_attributes = True


class MeetingList(BaseModel):
    """Schema for listing meetings"""

    meetings: List[MeetingResponse]
    total: int


class VideoUrlResponse(BaseModel):
    """Schema for video URL response"""

    video_url: str
    expires_in: str
    meeting: dict
