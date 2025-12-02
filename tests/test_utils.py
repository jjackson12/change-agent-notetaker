"""
Test utilities and fixtures for meeting workflow tests.

This module provides:
- Mock data factories for consistent test data
- Database fixtures for test isolation
- Helper functions for common test operations
- Webhook simulation utilities
"""

import pytest
from typing import Dict, Any, List
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from src.database import Base, get_db
from src.main import app
from src.models.meeting import Meeting, MeetingStatus
from src.models.user import User


# ============================================================================
# Database Fixtures
# ============================================================================


@pytest.fixture(scope="function")
def test_db():
    """
    Create a test database for each test function
    Provides complete isolation between tests
    """
    # Use in-memory SQLite for fast tests
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_client(test_db):
    """
    Test client with isolated database
    """

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(test_db):
    """Create a test user in the database"""
    user = User(name="Test User", email="test@example.com")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


# ============================================================================
# Mock Data Factories
# ============================================================================


class MockDataFactory:
    """Factory for creating consistent mock data"""

    @staticmethod
    def create_bot_response(
        bot_id: str = "test_bot_123",
        meeting_url: str = "https://meet.google.com/abc-defg-hij",
        status: str = "ready",
    ) -> Dict[str, Any]:
        """Create a mock bot creation response"""
        return {
            "id": bot_id,
            "meeting_url": meeting_url,
            "status_changes": [
                {"code": status, "created_at": datetime.utcnow().isoformat() + "Z"}
            ],
        }

    @staticmethod
    def create_bot_data_with_status(
        bot_id: str = "test_bot_123", statuses: List[str] = None
    ) -> Dict[str, Any]:
        """
        Create bot data with multiple status changes
        Default: ready -> in_call_recording -> done
        """
        if statuses is None:
            statuses = ["ready", "in_call_recording", "done"]

        status_changes = []
        base_time = datetime.utcnow()

        for i, status in enumerate(statuses):
            status_changes.append(
                {
                    "code": status,
                    "created_at": (base_time + timedelta(minutes=i * 5)).isoformat()
                    + "Z",
                }
            )

        return {
            "id": bot_id,
            "meeting_url": "https://meet.google.com/abc-defg-hij",
            "status_changes": status_changes,
            "meeting_metadata": {"title": "Test Meeting"},
        }

    @staticmethod
    def create_complete_bot_data(
        bot_id: str = "test_bot_123",
        title: str = "Team Standup",
        duration_minutes: int = 55,
    ) -> Dict[str, Any]:
        """Create complete bot data with recordings and metadata"""
        start_time = datetime.utcnow() - timedelta(minutes=duration_minutes)
        end_time = datetime.utcnow()

        return {
            "id": bot_id,
            "meeting_url": "https://meet.google.com/abc-defg-hij",
            "status_changes": [
                {
                    "code": "ready",
                    "created_at": (start_time - timedelta(minutes=5)).isoformat() + "Z",
                },
                {
                    "code": "in_call_recording",
                    "created_at": start_time.isoformat() + "Z",
                },
                {"code": "done", "created_at": end_time.isoformat() + "Z"},
            ],
            "meeting_metadata": {"title": title},
            "recordings": [
                {
                    "started_at": start_time.isoformat() + "Z",
                    "completed_at": end_time.isoformat() + "Z",
                    "media_shortcuts": {
                        "transcript": {
                            "data": {
                                "download_url": f"https://recall.ai/transcript/{bot_id}"
                            }
                        },
                        "participant_events": {
                            "data": {
                                "participants_download_url": f"https://recall.ai/participants/{bot_id}"
                            }
                        },
                        "video_mixed": {
                            "data": {
                                "download_url": f"https://recall.ai/video/{bot_id}"
                            }
                        },
                    },
                }
            ],
        }

    @staticmethod
    def create_transcript_data(
        speakers: List[str] = None, messages_per_speaker: int = 2
    ) -> List[Dict[str, Any]]:
        """Create mock transcript data"""
        if speakers is None:
            speakers = ["Alice", "Bob"]

        transcript = []
        timestamp = 0

        for speaker_id, speaker in enumerate(speakers):
            words = []
            for i in range(messages_per_speaker):
                word_data = {
                    "text": f"Message {i+1} from {speaker}",
                    "start_timestamp": {"relative": timestamp},
                    "end_timestamp": {"relative": timestamp + 2},
                }
                words.append(word_data)
                timestamp += 3

            transcript.append(
                {
                    "participant": {"name": speaker, "id": f"participant_{speaker_id}"},
                    "words": words,
                }
            )

        return transcript

    @staticmethod
    def create_participants_data(names: List[str] = None) -> List[Dict[str, str]]:
        """Create mock participants data"""
        if names is None:
            names = ["Alice", "Bob", "Charlie"]

        return [{"name": name} for name in names]

    @staticmethod
    def create_summary_data(
        overview: str = "Team standup meeting",
        num_key_points: int = 3,
        num_action_items: int = 2,
    ) -> Dict[str, Any]:
        """Create mock AI summary data"""
        return {
            "overview": overview,
            "key_points": [f"Key point {i+1}" for i in range(num_key_points)],
            "action_items": [f"Action item {i+1}" for i in range(num_action_items)],
            "decisions": ["Decision 1", "Decision 2"],
        }

    @staticmethod
    def create_webhook_payload(
        event: str, bot_id: str, meeting_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create webhook payload"""
        payload = {"event": event, "data": {"bot": {"id": bot_id}}}

        if meeting_metadata:
            payload["data"]["meeting_metadata"] = meeting_metadata

        return payload


# ============================================================================
# Helper Functions
# ============================================================================


class TestHelpers:
    """Helper functions for tests"""

    @staticmethod
    def assert_meeting_status(meeting_data: Dict[str, Any], expected_status: str):
        """Assert meeting has expected status"""
        assert (
            meeting_data["status"] == expected_status
        ), f"Expected status '{expected_status}', got '{meeting_data['status']}'"

    @staticmethod
    def assert_bot_in_meeting(status_data: Dict[str, Any], expected: bool = True):
        """Assert bot is in meeting"""
        assert (
            status_data["in_meeting"] == expected
        ), f"Expected in_meeting={expected}, got {status_data['in_meeting']}"

    @staticmethod
    def assert_meeting_complete(meeting_data: Dict[str, Any]):
        """Assert meeting has all processed data"""
        assert meeting_data["status"] == "done"
        assert meeting_data["title"] is not None
        assert meeting_data["transcript"] is not None
        assert meeting_data["participants"] is not None
        assert meeting_data["duration"] is not None
        assert meeting_data["summary"] is not None

    @staticmethod
    def create_meeting_in_db(
        db: Session,
        bot_id: str = "test_bot_123",
        status: MeetingStatus = MeetingStatus.IN_PROGRESS,
        user_id: int = None,
    ) -> Meeting:
        """Create a meeting directly in the database"""
        meeting = Meeting(
            title="Test Meeting",
            meeting_url="https://meet.google.com/test-meeting",
            bot_id=bot_id,
            status=status,
            user_id=user_id,
        )
        db.add(meeting)
        db.commit()
        db.refresh(meeting)
        return meeting


# ============================================================================
# Mock Context Managers
# ============================================================================


class MockRecallAPI:
    """
    Context manager for mocking Recall.ai API
    Makes it easy to mock multiple API calls consistently
    """

    def __init__(
        self,
        bot_data: Dict[str, Any] = None,
        transcript_data: List[Dict[str, Any]] = None,
        participants_data: List[Dict[str, str]] = None,
    ):
        self.bot_data = bot_data or MockDataFactory.create_complete_bot_data()
        self.transcript_data = (
            transcript_data or MockDataFactory.create_transcript_data()
        )
        self.participants_data = (
            participants_data or MockDataFactory.create_participants_data()
        )
        self.patches = []

    def __enter__(self):
        from unittest.mock import patch

        # Mock bot data retrieval
        p1 = patch(
            "src.services.recall_service.RecallService.retrieve_bot_data",
            new=AsyncMock(return_value=self.bot_data),
        )
        self.patches.append(p1)
        p1.__enter__()

        # Mock HTTP requests for transcript and participants
        async def mock_get_side_effect(url, *args, **kwargs):
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            if "transcript" in url:
                mock_resp.json = MagicMock(return_value=self.transcript_data)
            elif "participants" in url:
                mock_resp.json = MagicMock(return_value=self.participants_data)
            return mock_resp

        p2 = patch("httpx.AsyncClient.get", side_effect=mock_get_side_effect)
        self.patches.append(p2)
        p2.__enter__()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for p in reversed(self.patches):
            p.__exit__(exc_type, exc_val, exc_tb)


# ============================================================================
# Pytest Fixtures
# ============================================================================


@pytest.fixture
def mock_factory():
    """Provide MockDataFactory instance"""
    return MockDataFactory()


@pytest.fixture
def test_helpers():
    """Provide TestHelpers instance"""
    return TestHelpers()


@pytest.fixture
def mock_recall_api():
    """Provide MockRecallAPI factory"""
    return MockRecallAPI
