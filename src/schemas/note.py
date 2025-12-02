from pydantic import BaseModel
from typing import Optional

class NoteBase(BaseModel):
    meeting_id: int
    content: str

class NoteCreate(NoteBase):
    pass

class NoteUpdate(NoteBase):
    content: Optional[str] = None

class NoteInDB(NoteBase):
    id: int

    class Config:
        orm_mode = True

class NoteResponse(NoteInDB):
    pass