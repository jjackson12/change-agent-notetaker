from typing import List, Optional
from sqlalchemy.orm import Session
from models.meeting import Meeting
from schemas.meeting import MeetingCreate, MeetingUpdate

class MeetingService:
    def __init__(self, db: Session):
        self.db = db

    def create_meeting(self, meeting: MeetingCreate) -> Meeting:
        db_meeting = Meeting(**meeting.dict())
        self.db.add(db_meeting)
        self.db.commit()
        self.db.refresh(db_meeting)
        return db_meeting

    def get_meeting(self, meeting_id: int) -> Optional[Meeting]:
        return self.db.query(Meeting).filter(Meeting.id == meeting_id).first()

    def get_meetings(self) -> List[Meeting]:
        return self.db.query(Meeting).all()

    def update_meeting(self, meeting_id: int, meeting: MeetingUpdate) -> Optional[Meeting]:
        db_meeting = self.get_meeting(meeting_id)
        if db_meeting:
            for key, value in meeting.dict(exclude_unset=True).items():
                setattr(db_meeting, key, value)
            self.db.commit()
            self.db.refresh(db_meeting)
            return db_meeting
        return None

    def delete_meeting(self, meeting_id: int) -> Optional[Meeting]:
        db_meeting = self.get_meeting(meeting_id)
        if db_meeting:
            self.db.delete(db_meeting)
            self.db.commit()
            return db_meeting
        return None