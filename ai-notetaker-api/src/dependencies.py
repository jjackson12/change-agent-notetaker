from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models.user import User
from .models.meeting import Meeting
from .models.note import Note
from .models.meeting_bot import MeetingBot
from .models.calendar import Calendar

def get_current_user(db: Session = Depends(get_db), user_id: int = 0) -> User:
    return db.query(User).filter(User.id == user_id).first()

def get_meeting(db: Session = Depends(get_db), meeting_id: int = 0) -> Meeting:
    return db.query(Meeting).filter(Meeting.id == meeting_id).first()

def get_note(db: Session = Depends(get_db), note_id: int = 0) -> Note:
    return db.query(Note).filter(Note.id == note_id).first()

def get_meeting_bot(db: Session = Depends(get_db), bot_id: int = 0) -> MeetingBot:
    return db.query(MeetingBot).filter(MeetingBot.id == bot_id).first()

def get_calendar(db: Session = Depends(get_db), calendar_id: int = 0) -> Calendar:
    return db.query(Calendar).filter(Calendar.id == calendar_id).first()