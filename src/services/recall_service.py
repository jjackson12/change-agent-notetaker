"""
Recall.ai API integration service.
Handles all interactions with the Recall.ai bot API.
"""
import httpx
from typing import Dict, Any, List, Optional
import logging
from ..config import settings

logger = logging.getLogger(__name__)

RECALL_API_BASE = "https://us-east-1.recall.ai/api/v1"

class RecallService:
    """Service for interacting with Recall.ai API"""
    
    @staticmethod
    async def create_bot(meeting_url: str) -> Dict[str, Any]:
        """
        Create a bot to join a meeting via Recall.ai API
        
        Args:
            meeting_url: The Google Meet or Zoom meeting URL
            
        Returns:
            Dict containing bot data including bot ID
            
        Raises:
            httpx.HTTPError: If the API request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{RECALL_API_BASE}/bot/",
                json={
                    "meeting_url": meeting_url,
                    "recording_config": {
                        "transcript": {
                            "provider": {
                                "recallai_streaming": {}
                            }
                        }
                    }
                },
                headers={
                    "accept": "application/json",
                    "content-type": "application/json",
                    "Authorization": f"Token {settings.RECALL_API_KEY}"
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    @staticmethod
    async def retrieve_bot_data(bot_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed bot data from Recall.ai
        
        Args:
            bot_id: The Recall.ai bot ID
            
        Returns:
            Dict containing full bot data including recordings, transcript, etc.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{RECALL_API_BASE}/bot/{bot_id}/",
                headers={
                    "accept": "application/json",
                    "Authorization": f"Token {settings.RECALL_API_KEY}"
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    @staticmethod
    async def extract_transcript(bot_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract and process transcript data from bot data
        
        Args:
            bot_data: Full bot data from Recall.ai
            
        Returns:
            List of transcript segments with speaker, text, and timestamps
        """
        recordings = bot_data.get("recordings", [])
        if not recordings:
            return []
        
        transcript_url = (
            recordings[0]
            .get("media_shortcuts", {})
            .get("transcript", {})
            .get("data", {})
            .get("download_url")
        )
        
        if not transcript_url:
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(transcript_url, timeout=30.0)
                response.raise_for_status()
                transcript_data = response.json()
            
            # Process transcript data
            processed_transcript = []
            for participant_data in transcript_data:
                words = participant_data.get("words", [])
                
                if not words:
                    continue
                
                # Combine all word texts into a single string
                combined_text = " ".join(word.get("text", "") for word in words)
                
                # Get relative timestamps from first and last words
                first_word = words[0]
                last_word = words[-1]
                
                segment = {
                    "name": participant_data.get("participant", {}).get("name"),
                    "id": participant_data.get("participant", {}).get("id"),
                    "words": combined_text,
                    "start_timestamp": first_word.get("start_timestamp", {}).get("relative"),
                    "end_timestamp": last_word.get("end_timestamp", {}).get("relative")
                }
                
                processed_transcript.append(segment)
            
            return processed_transcript
            
        except Exception as e:
            logger.error(f"Error extracting transcript: {e}")
            return []
    
    @staticmethod
    async def extract_participants(bot_data: Dict[str, Any]) -> List[str]:
        """
        Extract participant names from bot data
        
        Args:
            bot_data: Full bot data from Recall.ai
            
        Returns:
            List of participant names
        """
        recordings = bot_data.get("recordings", [])
        if not recordings:
            return []
        
        participants_url = (
            recordings[0]
            .get("media_shortcuts", {})
            .get("participant_events", {})
            .get("data", {})
            .get("participants_download_url")
        )
        
        if not participants_url:
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(participants_url, timeout=30.0)
                response.raise_for_status()
                participants_data = response.json()
            
            return [p.get("name") for p in participants_data if p.get("name")]
            
        except Exception as e:
            logger.error(f"Error extracting participants: {e}")
            return []
    
    @staticmethod
    def calculate_duration(bot_data: Dict[str, Any]) -> Optional[str]:
        """
        Calculate meeting duration from recording data
        
        Args:
            bot_data: Full bot data from Recall.ai
            
        Returns:
            Duration string like "45 min" or None
        """
        recordings = bot_data.get("recordings", [])
        if not recordings:
            return None
        
        # Find first recording with start and end times
        for recording in recordings:
            started_at = recording.get("started_at")
            completed_at = recording.get("completed_at")
            
            if started_at and completed_at:
                from datetime import datetime
                start_time = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                end_time = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                duration_seconds = (end_time - start_time).total_seconds()
                duration_minutes = round(duration_seconds / 60)
                return f"{duration_minutes} min"
        
        return None
    
    @staticmethod
    async def get_video_url(bot_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract video recording URL from bot data
        
        Args:
            bot_data: Full bot data from Recall.ai
            
        Returns:
            Video download URL or None
        """
        recordings = bot_data.get("recordings", [])
        if not recordings:
            return None
        
        video_url = (
            recordings[0]
            .get("media_shortcuts", {})
            .get("video_mixed", {})
            .get("data", {})
            .get("download_url")
        )
        
        return video_url
    
    @staticmethod
    async def process_bot_data(bot_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process all relevant data from bot data
        
        Args:
            bot_data: Full bot data from Recall.ai
            
        Returns:
            Dict with processed duration, participants, transcript, and title
        """
        duration = RecallService.calculate_duration(bot_data)
        participants = await RecallService.extract_participants(bot_data)
        transcript = await RecallService.extract_transcript(bot_data)
        title = bot_data.get("meeting_metadata", {}).get("title") or "Completed Meeting"
        
        return {
            "duration": duration,
            "participants": participants,
            "transcript": transcript,
            "title": title
        }
