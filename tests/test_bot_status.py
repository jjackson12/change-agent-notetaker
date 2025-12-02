"""
Tests for bot status checking functionality
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from src.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_check_bot_status_in_meeting():
    """Test checking if a bot is currently in a meeting"""
    bot_id = "test_bot_123"
    
    # Mock the RecallService.is_bot_in_meeting method
    with patch('src.services.recall_service.RecallService.is_bot_in_meeting') as mock_check:
        mock_check.return_value = True
        
        response = client.get(f"/meeting_bots/bot-status/{bot_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["bot_id"] == bot_id
        assert data["in_meeting"] is True


@pytest.mark.asyncio
async def test_check_bot_status_not_in_meeting():
    """Test checking if a bot is not currently in a meeting"""
    bot_id = "test_bot_456"
    
    # Mock the RecallService.is_bot_in_meeting method
    with patch('src.services.recall_service.RecallService.is_bot_in_meeting') as mock_check:
        mock_check.return_value = False
        
        response = client.get(f"/meeting_bots/bot-status/{bot_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["bot_id"] == bot_id
        assert data["in_meeting"] is False


@pytest.mark.asyncio
async def test_recall_service_is_bot_in_meeting():
    """Test the RecallService.is_bot_in_meeting method directly"""
    from src.services.recall_service import RecallService
    
    bot_id = "test_bot_789"
    
    # Mock retrieve_bot_data to return bot data with in_call_recording status
    mock_bot_data = {
        "id": bot_id,
        "status_changes": [
            {"code": "ready", "created_at": "2023-10-01T10:00:00Z"},
            {"code": "in_call_recording", "created_at": "2023-10-01T10:05:00Z"}
        ]
    }
    
    with patch.object(RecallService, 'retrieve_bot_data', new=AsyncMock(return_value=mock_bot_data)):
        result = await RecallService.is_bot_in_meeting(bot_id)
        assert result is True


@pytest.mark.asyncio
async def test_recall_service_bot_not_in_meeting():
    """Test the RecallService.is_bot_in_meeting method when bot is done"""
    from src.services.recall_service import RecallService
    
    bot_id = "test_bot_finished"
    
    # Mock retrieve_bot_data to return bot data with done status
    mock_bot_data = {
        "id": bot_id,
        "status_changes": [
            {"code": "ready", "created_at": "2023-10-01T10:00:00Z"},
            {"code": "in_call_recording", "created_at": "2023-10-01T10:05:00Z"},
            {"code": "done", "created_at": "2023-10-01T11:00:00Z"}
        ]
    }
    
    with patch.object(RecallService, 'retrieve_bot_data', new=AsyncMock(return_value=mock_bot_data)):
        result = await RecallService.is_bot_in_meeting(bot_id)
        assert result is False


@pytest.mark.asyncio
async def test_recall_service_bot_no_status_changes():
    """Test the RecallService.is_bot_in_meeting method when no status changes exist"""
    from src.services.recall_service import RecallService
    
    bot_id = "test_bot_no_status"
    
    # Mock retrieve_bot_data to return bot data with no status changes
    mock_bot_data = {
        "id": bot_id,
        "status_changes": []
    }
    
    with patch.object(RecallService, 'retrieve_bot_data', new=AsyncMock(return_value=mock_bot_data)):
        result = await RecallService.is_bot_in_meeting(bot_id)
        assert result is False
