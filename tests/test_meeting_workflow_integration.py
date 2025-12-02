"""
Integration tests for the complete meeting workflow.

These tests can be run against real Recall.ai meetings.
Use environment variable INTEGRATION_TEST=true to enable.
Set RECALL_API_KEY and TEST_MEETING_URL in environment.

WARNING: These tests will:
- Create real bots on Recall.ai
- Join real meetings
- Consume Recall.ai API credits
- Take actual meeting time to complete (several minutes)

Usage:
    # Skip by default
    pytest tests/test_meeting_workflow_integration.py

    # Run integration tests
    INTEGRATION_TEST=true RECALL_API_KEY=your_key TEST_MEETING_URL=https://meet.google.com/... pytest tests/test_meeting_workflow_integration.py -v -s
"""
import pytest
import os
import asyncio
from fastapi.testclient import TestClient
from src.main import app
from src.models.meeting import MeetingStatus

client = TestClient(app)

# Skip all tests in this file unless INTEGRATION_TEST is set
pytestmark = pytest.mark.skipif(
    os.getenv("INTEGRATION_TEST") != "true",
    reason="Integration tests disabled. Set INTEGRATION_TEST=true to run."
)


class TestRealMeetingWorkflow:
    """
    Integration tests using real Recall.ai API and real meetings
    
    Prerequisites:
    - Valid RECALL_API_KEY in environment or .env
    - Active Google Meet or Zoom meeting URL in TEST_MEETING_URL
    - Meeting should be at least 2-3 minutes long for proper testing
    """

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_full_real_meeting_workflow(self):
        """
        Complete integration test with a real meeting
        
        Steps:
        1. Create bot and send to real meeting
        2. Poll to verify bot joined
        3. Wait for meeting to naturally end or manually end it
        4. Verify webhook is received (or poll for completion)
        5. Verify all data is processed correctly
        """
        meeting_url = os.getenv("TEST_MEETING_URL")
        if not meeting_url:
            pytest.skip("TEST_MEETING_URL not set")
        
        print(f"\n{'='*60}")
        print("REAL MEETING INTEGRATION TEST")
        print(f"{'='*60}")
        print(f"Meeting URL: {meeting_url}")
        print("This test will take several minutes to complete...")
        print(f"{'='*60}\n")
        
        # Step 1: Create bot and send to meeting
        print("Step 1: Creating bot and sending to meeting...")
        response = client.post(
            "/meeting_bots/send-bot",
            json={
                "meeting_url": meeting_url,
                "user_id": 1
            }
        )
        
        assert response.status_code == 200, f"Failed to create bot: {response.json()}"
        meeting_data = response.json()
        meeting_id = meeting_data["id"]
        bot_id = meeting_data["bot_id"]
        
        print(f"✓ Bot created: {bot_id}")
        print(f"✓ Meeting ID: {meeting_id}")
        print(f"✓ Status: {meeting_data['status']}")
        
        # Step 2: Wait for bot to join meeting
        print("\nStep 2: Waiting for bot to join meeting...")
        in_meeting = await self._wait_for_bot_in_meeting(meeting_id, timeout=120)
        assert in_meeting, "Bot did not join meeting within 2 minutes"
        print("✓ Bot successfully joined meeting")
        
        # Step 3: Monitor meeting
        print("\nStep 3: Bot is in meeting. Monitoring...")
        print("You can now:")
        print("  - Have a conversation in the meeting")
        print("  - End the meeting naturally")
        print("  - Or wait for this test to timeout")
        print("\nWaiting for meeting to end (timeout: 15 minutes)...")
        
        meeting_completed = await self._wait_for_meeting_completion(meeting_id, timeout=900)
        
        if not meeting_completed:
            print("\n⚠ Meeting did not complete within timeout")
            print("This is normal if the meeting is still ongoing")
            pytest.skip("Meeting timeout - test requires natural completion")
        
        print("✓ Meeting ended")
        
        # Step 4: Wait for webhook processing to complete
        print("\nStep 4: Waiting for webhook processing...")
        final_meeting = await self._wait_for_status(meeting_id, MeetingStatus.DONE, timeout=180)
        assert final_meeting, "Meeting did not reach DONE status"
        print("✓ Webhook processed successfully")
        
        # Step 5: Verify all data is present
        print("\nStep 5: Verifying meeting data...")
        self._verify_meeting_data(final_meeting)
        print("✓ All meeting data verified")
        
        # Step 6: Verify bot is no longer in meeting
        print("\nStep 6: Verifying bot left meeting...")
        response = client.get(f"/meetings/{meeting_id}/bot-status")
        assert response.status_code == 200
        status_data = response.json()
        assert status_data["in_meeting"] is False, "Bot should no longer be in meeting"
        print("✓ Bot successfully left meeting")
        
        print(f"\n{'='*60}")
        print("INTEGRATION TEST PASSED ✓")
        print(f"{'='*60}\n")
        
        # Print summary
        print("\nMeeting Summary:")
        print(f"  Title: {final_meeting['title']}")
        print(f"  Duration: {final_meeting['duration']}")
        print(f"  Participants: {', '.join(final_meeting['participants'] or [])}")
        print(f"  Transcript segments: {len(final_meeting['transcript'] or [])}")
        print(f"  Has summary: {'Yes' if final_meeting['summary'] else 'No'}")

    async def _wait_for_bot_in_meeting(self, meeting_id: int, timeout: int = 120) -> bool:
        """
        Wait for bot to join meeting
        Returns True if bot joins, False if timeout
        """
        start_time = asyncio.get_event_loop().time()
        poll_interval = 5  # Check every 5 seconds
        
        while True:
            try:
                response = client.get(f"/meetings/{meeting_id}/bot-status")
                if response.status_code == 200:
                    status_data = response.json()
                    if status_data["in_meeting"]:
                        return True
            except Exception as e:
                print(f"  Error checking bot status: {e}")
            
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                return False
            
            remaining = timeout - elapsed
            print(f"  Waiting... ({remaining:.0f}s remaining)")
            await asyncio.sleep(poll_interval)

    async def _wait_for_meeting_completion(self, meeting_id: int, timeout: int = 900) -> bool:
        """
        Wait for meeting to complete (bot leaves or status changes)
        Returns True if completed, False if timeout
        """
        start_time = asyncio.get_event_loop().time()
        poll_interval = 10  # Check every 10 seconds
        
        while True:
            try:
                # Check if bot left meeting
                response = client.get(f"/meetings/{meeting_id}/bot-status")
                if response.status_code == 200:
                    status_data = response.json()
                    if not status_data["in_meeting"]:
                        return True
                
                # Also check meeting status
                response = client.get(f"/meetings/{meeting_id}")
                if response.status_code == 200:
                    meeting = response.json()
                    if meeting["status"] in ["processing", "done", "errored"]:
                        return True
            except Exception as e:
                print(f"  Error checking completion: {e}")
            
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                return False
            
            remaining = timeout - elapsed
            print(f"  Still in meeting... ({remaining:.0f}s remaining)")
            await asyncio.sleep(poll_interval)

    async def _wait_for_status(self, meeting_id: int, expected_status: MeetingStatus, timeout: int = 180):
        """
        Wait for meeting to reach specific status
        Returns meeting data if reached, None if timeout
        """
        start_time = asyncio.get_event_loop().time()
        poll_interval = 5
        
        while True:
            try:
                response = client.get(f"/meetings/{meeting_id}")
                if response.status_code == 200:
                    meeting = response.json()
                    if meeting["status"] == expected_status.value:
                        return meeting
                    print(f"  Current status: {meeting['status']}")
            except Exception as e:
                print(f"  Error checking status: {e}")
            
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                return None
            
            remaining = timeout - elapsed
            print(f"  Waiting for {expected_status.value}... ({remaining:.0f}s remaining)")
            await asyncio.sleep(poll_interval)

    def _verify_meeting_data(self, meeting_data: dict):
        """Verify that meeting has all expected data after processing"""
        assert meeting_data["status"] == "done", f"Expected status 'done', got '{meeting_data['status']}'"
        assert meeting_data["title"], "Missing title"
        assert meeting_data["bot_id"], "Missing bot_id"
        
        # These should be present for a real meeting
        assert meeting_data["transcript"] is not None, "Missing transcript"
        assert isinstance(meeting_data["transcript"], list), "Transcript should be a list"
        assert len(meeting_data["transcript"]) > 0, "Transcript should not be empty"
        
        assert meeting_data["participants"] is not None, "Missing participants"
        assert isinstance(meeting_data["participants"], list), "Participants should be a list"
        
        assert meeting_data["duration"], "Missing duration"
        
        # Summary should be generated
        assert meeting_data["summary"] is not None, "Missing summary"
        assert isinstance(meeting_data["summary"], dict), "Summary should be a dict"


class TestQuickIntegrationChecks:
    """
    Faster integration tests that don't require full meeting lifecycle
    These can be run more frequently to verify API connectivity
    """

    @pytest.mark.asyncio
    async def test_create_and_verify_bot_creation(self):
        """
        Quick test: Create a bot but don't wait for it to join
        This verifies API connectivity and bot creation works
        """
        meeting_url = os.getenv("TEST_MEETING_URL")
        if not meeting_url:
            pytest.skip("TEST_MEETING_URL not set")
        
        response = client.post(
            "/meeting_bots/send-bot",
            json={
                "meeting_url": meeting_url,
                "user_id": 1
            }
        )
        
        assert response.status_code == 200
        meeting_data = response.json()
        assert "bot_id" in meeting_data
        assert meeting_data["status"] == "in_progress"
        
        # Verify we can check bot status immediately
        meeting_id = meeting_data["id"]
        response = client.get(f"/meetings/{meeting_id}/bot-status")
        assert response.status_code == 200
        status_data = response.json()
        assert "in_meeting" in status_data
        assert isinstance(status_data["in_meeting"], bool)

    @pytest.mark.asyncio
    async def test_retrieve_existing_bot_data(self):
        """
        Test retrieving data for an existing bot
        Requires BOT_ID environment variable from a previous test
        """
        bot_id = os.getenv("TEST_BOT_ID")
        if not bot_id:
            pytest.skip("TEST_BOT_ID not set")
        
        from src.services.recall_service import RecallService
        
        bot_data = await RecallService.retrieve_bot_data(bot_id)
        assert bot_data is not None
        assert "id" in bot_data
        assert bot_data["id"] == bot_id
        print(f"\nBot status: {bot_data.get('status_changes', [])[-1] if bot_data.get('status_changes') else 'unknown'}")
