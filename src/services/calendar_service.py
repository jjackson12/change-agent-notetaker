from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from src.models.calendar import Calendar
from src.schemas.calendar import CalendarCreate, CalendarUpdate

class CalendarService:
    def __init__(self, db: Session):
        self.db = db

    def create_event(self, event: CalendarCreate) -> Calendar:
        db_event = Calendar(**event.dict())
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event

    def get_event(self, event_id: int) -> Optional[Calendar]:
        return self.db.query(Calendar).filter(Calendar.id == event_id).first()

    def get_user_events(self, user_id: int) -> List[Calendar]:
        return self.db.query(Calendar).filter(Calendar.user_id == user_id).all()

    def update_event(self, event_id: int, event: CalendarUpdate) -> Optional[Calendar]:
        db_event = self.get_event(event_id)
        if db_event:
            for key, value in event.dict(exclude_unset=True).items():
                setattr(db_event, key, value)
            self.db.commit()
            self.db.refresh(db_event)
            return db_event
        return None

    def delete_event(self, event_id: int) -> bool:
        db_event = self.get_event(event_id)
        if db_event:
            self.db.delete(db_event)
            self.db.commit()
            return True
        return False

    def schedule_event(self, user_id: int, title: str, start_time: datetime, end_time: datetime) -> Calendar:
        event = Calendar(user_id=user_id, title=title, start_time=start_time, end_time=end_time)
        return self.create_event(event)