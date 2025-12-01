from fastapi.testclient import TestClient
from src.main import app
from src.models.meeting_bot import MeetingBot
from src.services.meeting_bot_service import MeetingBotService

client = TestClient(app)

def test_create_meeting_bot():
    response = client.post("/meeting_bots/", json={"meeting_id": 1})
    assert response.status_code == 201
    assert response.json()["meeting_id"] == 1

def test_get_meeting_bot():
    response = client.get("/meeting_bots/1")
    assert response.status_code == 200
    assert "meeting_id" in response.json()

def test_update_meeting_bot():
    response = client.put("/meeting_bots/1", json={"meeting_id": 2})
    assert response.status_code == 200
    assert response.json()["meeting_id"] == 2

def test_delete_meeting_bot():
    response = client.delete("/meeting_bots/1")
    assert response.status_code == 204
    assert response.content == b"" 

def test_meeting_bot_not_found():
    response = client.get("/meeting_bots/999")
    assert response.status_code == 404