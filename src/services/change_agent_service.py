"""
Change Agent API integration service.
Handles AI summarization using the custom Change Agent API.
"""
import httpx
from typing import Dict, Any, List
import logging
from ..config import settings

logger = logging.getLogger(__name__)

class ChangeAgentService:
    """Service for interacting with Change Agent API"""
    
    @staticmethod
    def get_participant_color(index: int) -> str:
        """
        Get consistent color class for a participant
        
        Args:
            index: Participant index
            
        Returns:
            Tailwind color class string
        """
        colors = [
            "bg-blue-50 text-blue-900",
            "bg-green-50 text-green-900",
            "bg-purple-50 text-purple-900",
            "bg-orange-50 text-orange-900",
            "bg-pink-50 text-pink-900",
            "bg-indigo-50 text-indigo-900",
        ]
        return colors[index % len(colors)]
    
    @staticmethod
    async def generate_meeting_summary(
        transcript: List[Dict[str, Any]],
        participants: List[str]
    ) -> Dict[str, Any]:
        """
        Generate AI meeting summary using Change Agent API
        
        Args:
            transcript: List of transcript segments
            summary: List of participant names
            
        Returns:
            Dict containing structured summary with segments and participants
            
        # TODO: Implement actual Change Agent API integration
        # For now, this is a placeholder that needs to be connected to your custom API
        """
        if not transcript:
            raise ValueError("Transcript is required for summary generation")
        
        # Generate consistent colors for participants
        participant_colors = [
            {
                "name": participant,
                "id": participant.lower().replace(" ", "_"),
                "colorClass": ChangeAgentService.get_participant_color(index)
            }
            for index, participant in enumerate(participants)
        ]
        
        # Convert transcript to text format
        transcript_text = "\n".join(
            f"{seg.get('name', 'Speaker')}: {seg.get('words', '')}"
            for seg in transcript
        )
        
        # TODO: Replace this with actual Change Agent API call
        # Example structure of what the API should return:
        """
        {
            "content": [
                {"type": "text", "content": "This was a productive meeting between "},
                {"type": "participant", "content": "John Smith", "participantId": "john_smith"},
                {"type": "text", "content": " and "},
                {"type": "participant", "content": "Sarah Johnson", "participantId": "sarah_johnson"},
                {"type": "text", "content": ". "},
                {"type": "timestamp_link", "content": "the Q4 budget planning", "timestamp": 120},
                {"type": "text", "content": " was discussed..."}
            ],
            "participants": participant_colors
        }
        """
        
        # Placeholder implementation - generate basic summary
        try:
            # TODO: Make actual API call to Change Agent
            # async with httpx.AsyncClient() as client:
            #     response = await client.post(
            #         f"{settings.CHANGE_AGENT_API_URL}/summarize",
            #         json={
            #             "transcript": transcript_text,
            #             "participants": participants
            #         },
            #         headers={
            #             "Authorization": f"Bearer {settings.CHANGE_AGENT_API_KEY}",
            #             "Content-Type": "application/json"
            #         },
            #         timeout=60.0
            #     )
            #     response.raise_for_status()
            #     return response.json()
            
            # For now, return a basic structured summary
            logger.warning("Using placeholder summary - Change Agent API not yet implemented")
            
            summary_content = [
                {"type": "text", "content": "Meeting summary: "}
            ]
            
            # Add participants
            for i, participant in enumerate(participants[:3]):  # First 3 participants
                if i > 0:
                    summary_content.append({"type": "text", "content": ", "})
                summary_content.append({
                    "type": "participant",
                    "content": participant,
                    "participantId": participant.lower().replace(" ", "_")
                })
            
            summary_content.append({
                "type": "text",
                "content": " discussed various topics during this meeting."
            })
            
            return {
                "content": summary_content,
                "participants": participant_colors
            }
            
        except Exception as e:
            logger.error(f"Error generating meeting summary: {e}")
            raise
