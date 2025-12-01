from fastapi.testclient import TestClient
from src.main import app
from src.models.meeting import Meeting
from src.services.meeting_service import MeetingService

client = TestClient(app)

def test_create_meeting():
    response = client.post("/meetings/", json={"title": "Team Sync", "scheduled_time": "2023-10-01T10:00:00"})
    assert response.status_code == 201
    assert response.json()["title"] == "Team Sync"

def test_get_meeting():
    response = client.get("/meetings/1")
    assert response.status_code == 200
    assert "title" in response.json()

def test_update_meeting():
    response = client.put("/meetings/1", json={"title": "Updated Team Sync"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Team Sync"

def test_delete_meeting():
    response = client.delete("/meetings/1")
    assert response.status_code == 204
    response = client.get("/meetings/1")
    assert response.status_code == 404

def test_list_meetings():
    response = client.get("/meetings/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)