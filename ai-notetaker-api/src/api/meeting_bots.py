from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..models.meeting_bot import MeetingBot
from ..schemas.meeting_bot import MeetingBotCreate, MeetingBotResponse
from ..services.meeting_bot_service import MeetingBotService
from ..database import get_db

router = APIRouter()

@router.post("/", response_model=MeetingBotResponse)
def create_meeting_bot(meeting_bot: MeetingBotCreate, db: Session = Depends(get_db)):
    return MeetingBotService.create_meeting_bot(db=db, meeting_bot=meeting_bot)

@router.get("/{meeting_bot_id}", response_model=MeetingBotResponse)
def get_meeting_bot(meeting_bot_id: int, db: Session = Depends(get_db)):
    meeting_bot = MeetingBotService.get_meeting_bot(db=db, meeting_bot_id=meeting_bot_id)
    if meeting_bot is None:
        raise HTTPException(status_code=404, detail="Meeting bot not found")
    return meeting_bot

@router.delete("/{meeting_bot_id}", response_model=dict)
def delete_meeting_bot(meeting_bot_id: int, db: Session = Depends(get_db)):
    result = MeetingBotService.delete_meeting_bot(db=db, meeting_bot_id=meeting_bot_id)
    if not result:
        raise HTTPException(status_code=404, detail="Meeting bot not found")
    return {"detail": "Meeting bot deleted successfully"}