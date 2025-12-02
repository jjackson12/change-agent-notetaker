from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class WebhookBot(BaseModel):
    """Bot information from webhook"""
    id: str

class WebhookTranscriptSegment(BaseModel):
    """Transcript segment from webhook"""
    speaker: str
    text: str

class WebhookMeetingMetadata(BaseModel):
    """Meeting metadata from webhook"""
    title: Optional[str] = None
    participants: Optional[List[str]] = None

class WebhookData(BaseModel):
    """Data payload from recall.ai webhook"""
    bot: Optional[WebhookBot] = None
    transcript_segments: Optional[List[WebhookTranscriptSegment]] = None
    meeting_metadata: Optional[WebhookMeetingMetadata] = None

class WebhookPayload(BaseModel):
    """Full webhook payload from recall.ai"""
    data: WebhookData
    event: str  # e.g., "bot.done", "bot.error", "bot.video_call_ended"

class WebhookResponse(BaseModel):
    """Response to webhook"""
    message: str
    bot_id: Optional[str] = None
    event: Optional[str] = None
