from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class MeetingBase(BaseModel):
    title: str
    scheduled_time: datetime

class MeetingCreate(MeetingBase):
    pass

class MeetingUpdate(MeetingBase):
    title: Optional[str] = None
    scheduled_time: Optional[datetime] = None

class Meeting(MeetingBase):
    id: int

    class Config:
        orm_mode = True

class MeetingList(BaseModel):
    meetings: List[Meeting]