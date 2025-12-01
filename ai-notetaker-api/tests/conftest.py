from pytest import fixture

@fixture(scope="session")
def test_client():
    from fastapi.testclient import TestClient
    from src.main import app

    client = TestClient(app)
    yield client

@fixture
def sample_user():
    return {
        "name": "Test User",
        "email": "testuser@example.com"
    }

@fixture
def sample_meeting():
    return {
        "title": "Test Meeting",
        "scheduled_time": "2023-10-01T10:00:00Z"
    }

@fixture
def sample_note():
    return {
        "meeting_id": 1,
        "content": "This is a test note."
    }

@fixture
def sample_meeting_bot():
    return {
        "meeting_id": 1
    }

@fixture
def sample_calendar():
    return {
        "user_id": 1
    }