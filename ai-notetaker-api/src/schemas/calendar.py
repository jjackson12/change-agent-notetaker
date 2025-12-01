from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CalendarBase(BaseModel):
    user_id: int
    title: str
    description: Optional[str] = None

class CalendarCreate(CalendarBase):
    pass

class CalendarUpdate(CalendarBase):
    pass

class Calendar(CalendarBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CalendarList(BaseModel):
    calendars: List[Calendar]