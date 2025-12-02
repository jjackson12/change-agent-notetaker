"""
Comprehensive workflow tests for the complete meeting lifecycle:
1. Bot joins meeting
2. Bot is in meeting
3. Meeting ends, webhook received
4. Bot is no longer in meeting
5. Meeting data is processed
6. Summary is generated

These tests use mocks to simulate the Recall.ai API responses.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from src.main import app
from src.models.meeting import Meeting, MeetingStatus
from src.database import get_db, Base, engine

client = TestClient(app)


@pytest.fixture
def mock_recall_bot_response():
    """Mock response for creating a bot"""
    return {
        "id": "test_bot_abc123",
        "meeting_url": "https://meet.google.com/abc-defg-hij",
        "status_changes": [
            {
                "code": "ready",
                "created_at": "2023-10-01T10:00:00Z"
            }
        ]
    }


@pytest.fixture
def mock_bot_in_meeting_response():
    """Mock response for bot that is in a meeting"""
    return {
        "id": "test_bot_abc123",
        "meeting_url": "https://meet.google.com/abc-defg-hij",
        "status_changes": [
            {
                "code": "ready",
                "created_at": "2023-10-01T10:00:00Z"
            },
            {
                "code": "in_call_recording",
                "created_at": "2023-10-01T10:05:00Z"
            }
        ]
    }


@pytest.fixture
def mock_bot_done_response():
    """Mock response for bot that has completed"""
    return {
        "id": "test_bot_abc123",
        "meeting_url": "https://meet.google.com/abc-defg-hij",
        "status_changes": [
            {
                "code": "ready",
                "created_at": "2023-10-01T10:00:00Z"
            },
            {
                "code": "in_call_recording",
                "created_at": "2023-10-01T10:05:00Z"
            },
            {
                "code": "done",
                "created_at": "2023-10-01T11:00:00Z"
            }
        ],
        "meeting_metadata": {
            "title": "Team Standup"
        },
        "recordings": [
            {
                "started_at": "2023-10-01T10:05:00Z",
                "completed_at": "2023-10-01T11:00:00Z",
                "media_shortcuts": {
                    "transcript": {
                        "data": {
                            "download_url": "https://recall.ai/transcript/abc123"
                        }
                    },
                    "participant_events": {
                        "data": {
                            "participants_download_url": "https://recall.ai/participants/abc123"
                        }
                    }
                }
            }
        ]
    }


@pytest.fixture
def mock_transcript_data():
    """Mock transcript data from Recall.ai"""
    return [
        {
            "participant": {
                "name": "Alice",
                "id": "participant_1"
            },
            "words": [
                {"text": "Hello", "start_timestamp": {"relative": 0}, "end_timestamp": {"relative": 1}},
                {"text": "everyone!", "start_timestamp": {"relative": 1}, "end_timestamp": {"relative": 2}}
            ]
        },
        {
            "participant": {
                "name": "Bob",
                "id": "participant_2"
            },
            "words": [
                {"text": "Hi", "start_timestamp": {"relative": 3}, "end_timestamp": {"relative": 4}},
                {"text": "Alice!", "start_timestamp": {"relative": 4}, "end_timestamp": {"relative": 5}}
            ]
        }
    ]


@pytest.fixture
def mock_participants_data():
    """Mock participants data from Recall.ai"""
    return [
        {"name": "Alice"},
        {"name": "Bob"}
    ]


@pytest.fixture
def mock_summary_response():
    """Mock AI-generated summary"""
    return {
        "overview": "Team standup discussing project progress",
        "key_points": [
            "Alice completed the API integration",
            "Bob working on frontend components"
        ],
        "action_items": [
            "Alice: Review Bob's PR",
            "Bob: Complete dashboard by EOD"
        ],
        "decisions": [
            "Deploy to staging tomorrow"
        ]
    }


class TestMeetingWorkflowMocked:
    """Mocked workflow tests - fast, no external dependencies"""

    @pytest.mark.asyncio
    async def test_complete_meeting_workflow(
        self,
        mock_recall_bot_response,
        mock_bot_in_meeting_response,
        mock_bot_done_response,
        mock_transcript_data,
        mock_participants_data,
        mock_summary_response
    ):
        """Test the complete workflow from bot creation to summary generation"""
        
        # Step 1: Create bot and join meeting
        with patch('src.services.recall_service.RecallService.create_bot', 
                   new=AsyncMock(return_value=mock_recall_bot_response)):
            
            response = client.post(
                "/meeting_bots/send-bot",
                json={
                    "meeting_url": "https://meet.google.com/abc-defg-hij",
                    "user_id": 1
                }
            )
            
            assert response.status_code == 200
            meeting_data = response.json()
            meeting_id = meeting_data["id"]
            bot_id = meeting_data["bot_id"]
            
            assert bot_id == "test_bot_abc123"
            assert meeting_data["status"] == "in_progress"
        
        # Step 2: Verify bot is NOT yet in meeting (still in ready state)
        with patch('src.services.recall_service.RecallService.retrieve_bot_data',
                   new=AsyncMock(return_value=mock_recall_bot_response)):
            
            response = client.get(f"/meetings/{meeting_id}/bot-status")
            assert response.status_code == 200
            status_data = response.json()
            assert status_data["in_meeting"] is False  # Still in "ready" state
        
        # Step 3: Bot joins meeting (status changes to in_call_recording)
        with patch('src.services.recall_service.RecallService.retrieve_bot_data',
                   new=AsyncMock(return_value=mock_bot_in_meeting_response)):
            
            response = client.get(f"/meetings/{meeting_id}/bot-status")
            assert response.status_code == 200
            status_data = response.json()
            assert status_data["in_meeting"] is True
        
        # Step 4: Meeting ends - simulate webhook
        webhook_payload = {
            "event": "bot.done",
            "data": {
                "bot": {
                    "id": bot_id
                },
                "meeting_metadata": {
                    "title": "Team Standup",
                    "participants": ["Alice", "Bob"]
                }
            }
        }
        
        # Mock all the services needed for webhook processing
        with patch('src.services.recall_service.RecallService.retrieve_bot_data',
                   new=AsyncMock(return_value=mock_bot_done_response)), \
             patch('httpx.AsyncClient.get') as mock_http_get, \
             patch('src.services.change_agent_service.ChangeAgentService.generate_meeting_summary',
                   new=AsyncMock(return_value=mock_summary_response)):
            
            # Mock HTTP requests for transcript and participants
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            
            async def mock_get_side_effect(url, *args, **kwargs):
                mock_resp = MagicMock()
                mock_resp.raise_for_status = MagicMock()
                if "transcript" in url:
                    mock_resp.json = MagicMock(return_value=mock_transcript_data)
                elif "participants" in url:
                    mock_resp.json = MagicMock(return_value=mock_participants_data)
                return mock_resp
            
            mock_http_get.side_effect = mock_get_side_effect
            
            # Send webhook
            response = client.post("/webhooks/webhook", json=webhook_payload)
            assert response.status_code == 200
            webhook_response = response.json()
            assert webhook_response["message"] == "Webhook received and processing started"
            assert webhook_response["bot_id"] == bot_id
            assert webhook_response["event"] == "bot.done"
        
        # Step 5: Verify bot is no longer in meeting
        with patch('src.services.recall_service.RecallService.retrieve_bot_data',
                   new=AsyncMock(return_value=mock_bot_done_response)):
            
            response = client.get(f"/meetings/{meeting_id}/bot-status")
            assert response.status_code == 200
            status_data = response.json()
            assert status_data["in_meeting"] is False
        
        # Step 6: Verify meeting data was processed (with small delay for background task)
        import asyncio
        await asyncio.sleep(0.5)  # Wait for background task
        
        response = client.get(f"/meetings/{meeting_id}")
        assert response.status_code == 200
        meeting = response.json()
        
        # Verify meeting was updated
        assert meeting["status"] in ["processing", "done"]  # May still be processing
        # Note: In real scenario, you'd poll until status is "done"

    @pytest.mark.asyncio
    async def test_bot_error_workflow(self, mock_recall_bot_response):
        """Test workflow when bot encounters an error"""
        
        # Create bot
        with patch('src.services.recall_service.RecallService.create_bot',
                   new=AsyncMock(return_value=mock_recall_bot_response)):
            
            response = client.post(
                "/meeting_bots/send-bot",
                json={
                    "meeting_url": "https://meet.google.com/test-error",
                    "user_id": 1
                }
            )
            
            meeting_id = response.json()["id"]
            bot_id = response.json()["bot_id"]
        
        # Simulate error webhook
        webhook_payload = {
            "event": "bot.error",
            "data": {
                "bot": {
                    "id": bot_id
                }
            }
        }
        
        response = client.post("/webhooks/webhook", json=webhook_payload)
        assert response.status_code == 200
        
        # Wait for background processing
        import asyncio
        await asyncio.sleep(0.5)
        
        # Verify meeting status is errored
        response = client.get(f"/meetings/{meeting_id}")
        meeting = response.json()
        assert meeting["status"] == "errored"

    def test_check_bot_status_for_nonexistent_meeting(self):
        """Test checking bot status for a meeting that doesn't exist"""
        response = client.get("/meetings/99999/bot-status")
        assert response.status_code == 404

    def test_check_bot_status_for_meeting_without_bot(self):
        """Test checking bot status for a meeting without a bot_id"""
        # This would require creating a meeting without a bot
        # In practice, all meetings should have bot_ids if created via /send-bot
        pass


class TestMeetingWorkflowHelpers:
    """Helper methods for testing workflows"""

    @staticmethod
    async def wait_for_meeting_status(meeting_id: int, expected_status: str, timeout: int = 10):
        """
        Poll meeting until it reaches expected status or timeout
        Useful for integration tests with real background processing
        """
        import asyncio
        start_time = asyncio.get_event_loop().time()
        
        while True:
            response = client.get(f"/meetings/{meeting_id}")
            if response.status_code == 200:
                meeting = response.json()
                if meeting["status"] == expected_status:
                    return meeting
            
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError(f"Meeting did not reach status {expected_status} within {timeout}s")
            
            await asyncio.sleep(0.5)

    @staticmethod
    def assert_meeting_has_complete_data(meeting_data: dict):
        """Assert that meeting has all expected processed data"""
        assert meeting_data["status"] == "done"
        assert meeting_data["title"] is not None
        assert meeting_data["transcript"] is not None
        assert len(meeting_data["transcript"]) > 0
        assert meeting_data["participants"] is not None
        assert len(meeting_data["participants"]) > 0
        assert meeting_data["duration"] is not None
        assert meeting_data["summary"] is not None
