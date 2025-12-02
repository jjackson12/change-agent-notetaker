"""
Notes endpoints for accessing meeting transcripts and summaries

Notes in this system are generated automatically from meetings.
The transcripts and AI summaries are the "notes" for each meeting.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.meeting import Meeting, MeetingStatus
from ..schemas.meeting import MeetingResponse

router = APIRouter()


@router.get("/", response_model=List[MeetingResponse])
def get_all_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all meeting notes (completed meetings with transcripts/summaries)

    This returns meetings that have finished and have note data available.
    """
    meetings = (
        db.query(Meeting)
        .filter(Meeting.status == MeetingStatus.DONE)
        .order_by(Meeting.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return meetings


@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_note(meeting_id: int, db: Session = Depends(get_db)):
    """
    Get notes for a specific meeting

    Returns the transcript and AI-generated summary for the meeting.
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return meeting


@router.get("/meeting/{meeting_url:path}")
def get_note_by_url(meeting_url: str, db: Session = Depends(get_db)):
    """
    Get notes for a meeting by its URL

    This is useful for looking up notes when you have the meeting link.
    """
    meeting = db.query(Meeting).filter(Meeting.meeting_url == meeting_url).first()

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return meeting
