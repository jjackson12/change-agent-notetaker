"""
Example tests demonstrating how to use the testing utilities.

These examples show common testing patterns and best practices.
"""

import pytest
from unittest.mock import patch, AsyncMock
from tests.test_utils import MockDataFactory, MockRecallAPI, TestHelpers


class ExampleMockedTests:
    """Examples of mocked tests - recommended approach"""

    @pytest.mark.asyncio
    async def test_example_simple_workflow(self, mock_factory):
        """
        Simple example: Test bot creation and status check

        This example shows:
        - Using MockDataFactory for test data
        - Mocking Recall.ai API calls
        - Making API requests
        - Asserting responses
        """
        from fastapi.testclient import TestClient
        from src.main import app

        client = TestClient(app)

        # Create mock data
        bot_response = mock_factory.create_bot_response(
            bot_id="example_bot_123", status="ready"
        )

        # Mock the Recall.ai create_bot call
        with patch(
            "src.services.recall_service.RecallService.create_bot",
            new=AsyncMock(return_value=bot_response),
        ):

            # Create a bot
            response = client.post(
                "/meeting_bots/send-bot",
                json={"meeting_url": "https://meet.google.com/example", "user_id": 1},
            )

            # Assert success
            assert response.status_code == 200
            meeting_data = response.json()
            assert meeting_data["bot_id"] == "example_bot_123"
            assert meeting_data["status"] == "in_progress"

    @pytest.mark.asyncio
    async def test_example_bot_joins_meeting(self, mock_factory):
        """
        Example: Test bot joining a meeting

        Shows how to test status transitions
        """
        from fastapi.testclient import TestClient
        from src.main import app

        client = TestClient(app)

        # Step 1: Create bot
        create_response = mock_factory.create_bot_response(bot_id="example_bot_456")

        with patch(
            "src.services.recall_service.RecallService.create_bot",
            new=AsyncMock(return_value=create_response),
        ):
            response = client.post(
                "/meeting_bots/send-bot",
                json={"meeting_url": "https://meet.google.com/example", "user_id": 1},
            )
            meeting_id = response.json()["id"]

        # Step 2: Check bot status when in meeting
        in_meeting_data = mock_factory.create_bot_data_with_status(
            bot_id="example_bot_456", statuses=["ready", "in_call_recording"]
        )

        with patch(
            "src.services.recall_service.RecallService.retrieve_bot_data",
            new=AsyncMock(return_value=in_meeting_data),
        ):

            response = client.get(f"/meetings/{meeting_id}/bot-status")
            status_data = response.json()

            # Use helper to assert
            TestHelpers.assert_bot_in_meeting(status_data, expected=True)

    @pytest.mark.asyncio
    async def test_example_webhook_processing(self, mock_factory):
        """
        Example: Test webhook processing

        Shows how to:
        - Simulate webhook events
        - Mock data processing
        - Verify background task results
        """
        from fastapi.testclient import TestClient
        from src.main import app
        import asyncio

        client = TestClient(app)

        # Create a meeting first
        create_response = mock_factory.create_bot_response(bot_id="webhook_bot_789")

        with patch(
            "src.services.recall_service.RecallService.create_bot",
            new=AsyncMock(return_value=create_response),
        ):
            response = client.post(
                "/meeting_bots/send-bot",
                json={
                    "meeting_url": "https://meet.google.com/webhook-example",
                    "user_id": 1,
                },
            )
            meeting_id = response.json()["id"]
            bot_id = response.json()["bot_id"]

        # Prepare webhook
        webhook_payload = mock_factory.create_webhook_payload(
            event="bot.done",
            bot_id=bot_id,
            meeting_metadata={"title": "Webhook Test Meeting"},
        )

        # Mock the data processing
        complete_bot_data = mock_factory.create_complete_bot_data(
            bot_id=bot_id, title="Webhook Test Meeting"
        )

        with MockRecallAPI(bot_data=complete_bot_data), patch(
            "src.services.change_agent_service.ChangeAgentService.generate_meeting_summary",
            new=AsyncMock(return_value=mock_factory.create_summary_data()),
        ):

            # Send webhook
            response = client.post("/webhooks/webhook", json=webhook_payload)
            assert response.status_code == 200

            # Wait for background processing
            await asyncio.sleep(0.5)

            # Verify meeting was updated
            response = client.get(f"/meetings/{meeting_id}")
            meeting = response.json()

            # Meeting should be processing or done
            assert meeting["status"] in ["processing", "done"]


class ExampleTestWithIsolatedDatabase:
    """Examples using isolated test database"""

    def test_example_with_test_db(self, test_db, test_user):
        """
        Example: Using isolated test database

        Shows:
        - Using test_db fixture for database isolation
        - Creating test data with fixtures
        - Direct database operations
        """
        from src.models.meeting import Meeting, MeetingStatus

        # Create a meeting directly in test database
        meeting = Meeting(
            title="DB Test Meeting",
            meeting_url="https://meet.google.com/db-test",
            bot_id="db_test_bot",
            status=MeetingStatus.IN_PROGRESS,
            user_id=test_user.id if test_user else None,
        )
        test_db.add(meeting)
        test_db.commit()
        test_db.refresh(meeting)

        # Query it back
        queried = test_db.query(Meeting).filter(Meeting.id == meeting.id).first()
        assert queried is not None
        assert queried.title == "DB Test Meeting"
        assert queried.status == MeetingStatus.IN_PROGRESS

    def test_example_helper_create_meeting(self, test_db):
        """
        Example: Using TestHelpers to create test data
        """
        # Create meeting using helper
        meeting = TestHelpers.create_meeting_in_db(
            db=test_db, bot_id="helper_bot_123", status="in_progress"
        )

        assert meeting.id is not None
        assert meeting.bot_id == "helper_bot_123"


class ExampleErrorHandlingTests:
    """Examples of testing error cases"""

    def test_example_missing_meeting(self):
        """Example: Test 404 for missing meeting"""
        from fastapi.testclient import TestClient
        from src.main import app

        client = TestClient(app)

        response = client.get("/meetings/999999/bot-status")
        assert response.status_code == 404

    def test_example_invalid_webhook(self):
        """Example: Test webhook with missing data"""
        from fastapi.testclient import TestClient
        from src.main import app

        client = TestClient(app)

        # Webhook with missing bot ID
        invalid_webhook = {"event": "bot.done", "data": {}}

        response = client.post("/webhooks/webhook", json=invalid_webhook)
        # Should handle gracefully
        assert response.status_code in [400, 500]

    @pytest.mark.asyncio
    async def test_example_bot_error_event(self, mock_factory):
        """Example: Test bot.error webhook"""
        from fastapi.testclient import TestClient
        from src.main import app
        import asyncio

        client = TestClient(app)

        # Create meeting
        with patch(
            "src.services.recall_service.RecallService.create_bot",
            new=AsyncMock(
                return_value=mock_factory.create_bot_response(bot_id="error_bot")
            ),
        ):
            response = client.post(
                "/meeting_bots/send-bot",
                json={
                    "meeting_url": "https://meet.google.com/error-test",
                    "user_id": 1,
                },
            )
            meeting_id = response.json()["id"]
            bot_id = response.json()["bot_id"]

        # Send error webhook
        error_webhook = mock_factory.create_webhook_payload(
            event="bot.error", bot_id=bot_id
        )

        response = client.post("/webhooks/webhook", json=error_webhook)
        assert response.status_code == 200

        # Wait for processing
        await asyncio.sleep(0.5)

        # Verify meeting status is errored
        response = client.get(f"/meetings/{meeting_id}")
        meeting = response.json()
        TestHelpers.assert_meeting_status(meeting, "errored")


# Run these examples with:
# pytest tests/test_examples.py -v -s
