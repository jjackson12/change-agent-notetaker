"""
Webhook endpoints for receiving callbacks from Recall.ai
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
import logging
from typing import Dict, Any

from ..database import get_db
from ..models.meeting import Meeting, MeetingStatus
from ..schemas.webhook import WebhookPayload, WebhookResponse
from ..services.recall_service import RecallService
from ..services.change_agent_service import ChangeAgentService

router = APIRouter()
logger = logging.getLogger(__name__)


async def process_webhook_async(
    meeting_id: int, bot_id: str, event_name: str, data: Dict[str, Any], db: Session
):
    """
    Process webhook asynchronously after responding to recall.ai
    This prevents webhook timeouts while we do heavy processing
    """
    logger.info(f"Starting async processing for bot {bot_id}, event: {event_name}")

    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        logger.error(f"Meeting {meeting_id} not found during async processing")
        return

    try:
        if event_name == "bot.done":
            # Set to processing status
            meeting.status = MeetingStatus.PROCESSING
            db.commit()

            try:
                # Retrieve detailed bot data from Recall.ai
                logger.info(f"Fetching bot data for botId: {bot_id}")
                bot_data = await RecallService.retrieve_bot_data(bot_id)

                # Process bot data to extract meeting information
                processed_data = await RecallService.process_bot_data(bot_data)

                # Update meeting with basic data
                meeting.title = processed_data["title"]
                meeting.participants = processed_data["participants"]
                meeting.duration = processed_data["duration"]
                meeting.transcript = processed_data["transcript"]
                db.commit()

                logger.info(f"Updated meeting {meeting_id} with basic data")

                # Generate AI summary if we have a transcript
                if processed_data["transcript"]:
                    try:
                        logger.info(f"Generating AI summary for botId: {bot_id}")
                        summary = await ChangeAgentService.generate_meeting_summary(
                            processed_data["transcript"],
                            processed_data["participants"] or [],
                        )

                        # Update with summary and mark as done
                        meeting.summary = summary
                        meeting.status = MeetingStatus.DONE
                        db.commit()

                        logger.info(
                            f"AI summary generated successfully for botId: {bot_id}"
                        )
                    except Exception as summary_error:
                        logger.error(
                            f"Failed to generate AI summary for {bot_id}: {summary_error}"
                        )
                        # Mark as done even without summary
                        meeting.status = MeetingStatus.DONE
                        db.commit()
                else:
                    # No transcript, just mark as done
                    meeting.status = MeetingStatus.DONE
                    db.commit()

            except Exception as error:
                logger.error(f"Failed to retrieve bot data for {bot_id}: {error}")
                # Try fallback with webhook data
                if data.get("meeting_metadata"):
                    meeting.title = data["meeting_metadata"].get(
                        "title", "Completed Meeting"
                    )
                    meeting.participants = data["meeting_metadata"].get(
                        "participants", []
                    )
                meeting.status = MeetingStatus.DONE
                db.commit()

        elif event_name == "bot.error":
            meeting.status = MeetingStatus.ERRORED
            db.commit()
            logger.error(f"Bot {bot_id} encountered an error")

    except Exception as e:
        logger.error(f"Error in async webhook processing: {e}")
        meeting.status = MeetingStatus.ERRORED
        db.commit()

    logger.info(f"Updated meeting {meeting_id} to status: {meeting.status}")


@router.post("/webhook", response_model=WebhookResponse)
async def receive_webhook(
    payload: WebhookPayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Receive webhooks from Recall.ai

    This endpoint receives notifications when:
    - bot.done: Meeting has ended and data is ready
    - bot.error: Bot encountered an error
    - bot.video_call_ended: Call ended (may arrive before bot.done)
    - bot.recording_ready: Recording is ready
    """
    try:
        bot_id = payload.data.bot.id if payload.data.bot else None
        event_name = payload.event

        if not bot_id or not event_name:
            raise HTTPException(
                status_code=400,
                detail="Invalid webhook payload - missing bot ID or event name",
            )

        logger.info(f"Webhook received: {event_name} for bot {bot_id}")

        # Find the meeting by bot_id
        meeting = db.query(Meeting).filter(Meeting.bot_id == bot_id).first()

        if not meeting:
            logger.warning(f"No meeting found for bot {bot_id}")
            return WebhookResponse(
                message="Webhook processed but no matching meeting found",
                bot_id=bot_id,
                event=event_name,
            )

        # Respond immediately with 200 to prevent webhook retries
        # The actual processing happens asynchronously
        background_tasks.add_task(
            process_webhook_async,
            meeting.id,
            bot_id,
            event_name,
            payload.data.dict(),
            db,
        )

        return WebhookResponse(
            message="Webhook received and processing started",
            bot_id=bot_id,
            event=event_name,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process webhook")
