from pydantic import BaseModel
from typing import Optional

class MeetingBotBase(BaseModel):
    meeting_id: int

class MeetingBotCreate(MeetingBotBase):
    pass

class MeetingBot(MeetingBotBase):
    id: int

    class Config:
        orm_mode = True

class MeetingBotUpdate(BaseModel):
    meeting_id: Optional[int] = None