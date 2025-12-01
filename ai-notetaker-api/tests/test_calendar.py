from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.database import get_db
from src.models.calendar import Calendar
from src.schemas.calendar import CalendarCreate
import pytest

app = FastAPI()

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def test_calendar(db):
    calendar_data = CalendarCreate(user_id=1)
    calendar = Calendar(**calendar_data.dict())
    db.add(calendar)
    db.commit()
    db.refresh(calendar)
    return calendar

def test_create_calendar(client, test_calendar):
    response = client.post("/calendars/", json={"user_id": 1})
    assert response.status_code == 201
    assert response.json()["user_id"] == 1

def test_get_calendar(client, test_calendar):
    response = client.get(f"/calendars/{test_calendar.id}")
    assert response.status_code == 200
    assert response.json()["id"] == test_calendar.id

def test_get_nonexistent_calendar(client):
    response = client.get("/calendars/999")
    assert response.status_code == 404

def test_delete_calendar(client, test_calendar):
    response = client.delete(f"/calendars/{test_calendar.id}")
    assert response.status_code == 204
    response = client.get(f"/calendars/{test_calendar.id}")
    assert response.status_code == 404