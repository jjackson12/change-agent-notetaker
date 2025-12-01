from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.meeting import Meeting
from ..schemas.meeting import MeetingCreate, MeetingResponse
from ..services.meeting_service import MeetingService

router = APIRouter()
meeting_service = MeetingService()

@router.post("/", response_model=MeetingResponse)
def create_meeting(meeting: MeetingCreate, db: Session = Depends(get_db)):
    return meeting_service.create_meeting(meeting, db)

@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = meeting_service.get_meeting(meeting_id, db)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

@router.get("/", response_model=list[MeetingResponse])
def list_meetings(db: Session = Depends(get_db)):
    return meeting_service.list_meetings(db)