"""
Meeting endpoints for accessing meeting data, transcripts, and summaries
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import logging

from ..database import get_db
from ..models.meeting import Meeting
from ..schemas.meeting import MeetingResponse, MeetingList, VideoUrlResponse
from ..services.recall_service import RecallService
from ..services.change_agent_service import ChangeAgentService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[MeetingResponse])
def list_meetings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List all meetings, sorted by most recent first
    """
    meetings = (
        db.query(Meeting)
        .order_by(Meeting.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return meetings


@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific meeting

    This endpoint is polled by the frontend to check meeting status
    and get updated data as the meeting progresses.
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return meeting


@router.get("/{meeting_id}/video", response_model=VideoUrlResponse)
async def get_meeting_video(meeting_id: int, db: Session = Depends(get_db)):
    """
    Get a fresh video URL for a completed meeting

    Note: Recall.ai video URLs expire after 6 hours, so this endpoint
    generates a fresh URL when needed.
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if meeting.status.value != "done":
        raise HTTPException(status_code=400, detail="Meeting not completed yet")

    if not meeting.bot_id:
        raise HTTPException(status_code=400, detail="No bot ID found for this meeting")

    try:
        # Retrieve fresh bot data from Recall.ai
        bot_data = await RecallService.retrieve_bot_data(meeting.bot_id)

        # Extract video URL
        video_url = await RecallService.get_video_url(bot_data)

        if not video_url:
            raise HTTPException(
                status_code=404, detail="No video available for this meeting"
            )

        return VideoUrlResponse(
            video_url=video_url,
            expires_in="6 hours",
            meeting={
                "id": meeting.id,
                "title": meeting.title,
                "status": meeting.status.value,
            },
        )

    except Exception as e:
        logger.error(f"Failed to fetch video URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch video URL")


@router.post("/{meeting_id}/summarize")
async def generate_summary(meeting_id: int, db: Session = Depends(get_db)):
    """
    Manually trigger summary generation for a meeting

    This is useful if automatic summary generation failed or
    if you want to regenerate the summary.
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if not meeting.transcript:
        raise HTTPException(
            status_code=400, detail="No transcript available for this meeting"
        )

    try:
        logger.info(f"Generating AI summary for meeting: {meeting_id}")

        summary = await ChangeAgentService.generate_meeting_summary(
            meeting.transcript, meeting.participants or []
        )

        # Update the meeting with the summary
        meeting.summary = summary
        db.commit()

        logger.info(f"AI summary generated successfully for meeting: {meeting_id}")

        return {
            "success": True,
            "summary": summary,
            "message": "Summary generated successfully",
        }

    except Exception as e:
        logger.error(f"Failed to generate summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate summary")


@router.delete("/{meeting_id}")
def delete_meeting(meeting_id: int, db: Session = Depends(get_db)):
    """
    Delete a meeting and all associated data
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    db.delete(meeting)
    db.commit()

    return {"detail": "Meeting deleted successfully"}
