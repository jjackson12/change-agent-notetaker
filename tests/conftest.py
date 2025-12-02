from pytest import fixture
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base, get_db
from src.main import app
from fastapi.testclient import TestClient


@fixture(scope="session")
def test_client():
    from fastapi.testclient import TestClient
    from src.main import app

    client = TestClient(app)
    yield client


@fixture
def sample_user():
    return {"name": "Test User", "email": "testuser@example.com"}


@fixture
def sample_meeting():
    return {"title": "Test Meeting", "scheduled_time": "2023-10-01T10:00:00Z"}


@fixture
def sample_note():
    return {"meeting_id": 1, "content": "This is a test note."}


@fixture
def sample_meeting_bot():
    return {"meeting_id": 1}


@fixture
def sample_calendar():
    return {"user_id": 1}


# Import test utilities fixtures
from tests.test_utils import (
    test_db,
    test_client as isolated_test_client,
    test_user,
    mock_factory,
    test_helpers,
    mock_recall_api,
)
