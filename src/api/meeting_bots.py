"""
Meeting bot endpoints for triggering bots to join meetings
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging

from ..database import get_db
from ..models.meeting import Meeting, MeetingStatus
from ..schemas.meeting import MeetingCreate, MeetingResponse
from ..services.recall_service import RecallService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/send-bot", response_model=MeetingResponse)
async def send_bot_to_meeting(
    meeting_data: MeetingCreate,
    db: Session = Depends(get_db)
):
    """
    Trigger a bot to join an active meeting immediately
    
    This endpoint:
    1. Creates a bot via Recall.ai API
    2. Creates a meeting record in the database
    3. Returns the meeting ID for tracking
    
    The bot will join the meeting and start recording/transcribing.
    When the meeting ends, Recall.ai will send a webhook to update the meeting data.
    """
    try:
        # Validate meeting URL
        if not meeting_data.meeting_url or not meeting_data.meeting_url.strip():
            raise HTTPException(status_code=400, detail="Meeting URL is required")
        
        logger.info(f"Creating bot for meeting URL: {meeting_data.meeting_url}")
        
        # Create bot via Recall.ai
        bot_response = await RecallService.create_bot(meeting_data.meeting_url)
        bot_id = bot_response.get("id")
        
        if not bot_id:
            raise HTTPException(status_code=500, detail="Failed to create bot - no bot ID returned")
        
        logger.info(f"Bot created successfully with ID: {bot_id}")
        
        # Create meeting record in database
        meeting = Meeting(
            meeting_url=meeting_data.meeting_url,
            bot_id=bot_id,
            status=MeetingStatus.IN_PROGRESS,
            title="Meeting in Progress",
            user_id=meeting_data.user_id
        )
        
        db.add(meeting)
        db.commit()
        db.refresh(meeting)
        
        logger.info(f"Meeting created with ID: {meeting.id}")
        
        return meeting
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send bot to meeting: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send bot to meeting: {str(e)}"
        )


@router.post("/schedule-bot")
async def schedule_bot_for_meeting(
    # TODO: Implement scheduling logic
    # This will require a background scheduler (Celery, APScheduler, etc.)
    # For now, return not implemented
):
    """
    Schedule a bot to join a future meeting
    
    NOTE: This endpoint is not yet implemented.
    Requires integration with calendar API and background scheduler.
    """
    raise HTTPException(
        status_code=501,
        detail="Scheduling not yet implemented - use /send-bot for immediate meetings"
    )


@router.delete("/unschedule-bot/{meeting_id}")
async def unschedule_bot(
    meeting_id: int,
    db: Session = Depends(get_db)
):
    """
    Un-schedule a bot from a future meeting
    
    NOTE: This endpoint is not yet implemented.
    """
    raise HTTPException(
        status_code=501,
        detail="Un-scheduling not yet implemented"
    )