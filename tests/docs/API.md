# API Reference

Testing API endpoints and utilities.

## Bot Status Endpoints

### Check Bot Status by Bot ID
```
GET /meeting_bots/bot-status/{bot_id}
```

Check if a specific bot is currently in a meeting.

**Response:**
```json
{
  "bot_id": "abc123",
  "in_meeting": true
}
```

**Example:**
```bash
curl http://localhost:8000/meeting_bots/bot-status/abc123
```

### Check Bot Status by Meeting ID
```
GET /meetings/{meeting_id}/bot-status
```

Check if the bot for a specific meeting is currently in the meeting.

**Response:**
```json
{
  "meeting_id": 123,
  "bot_id": "abc123",
  "in_meeting": true
}
```

**Example:**
```bash
curl http://localhost:8000/meetings/123/bot-status
```

## RecallService Methods

### is_bot_in_meeting()

```python
await RecallService.is_bot_in_meeting(bot_id: str) -> bool
```

Check if a bot is currently in a meeting by querying Recall.ai API.

**Returns:** `True` if bot status is `in_call_not_recording` or `in_call_recording`, `False` otherwise.

**Example:**
```python
from src.services.recall_service import RecallService

is_active = await RecallService.is_bot_in_meeting("bot_abc123")
if is_active:
    print("Bot is in meeting")
```

## Test Utilities

### MockDataFactory

Factory for creating consistent test data.

**Methods:**

```python
# Bot responses
create_bot_response(bot_id="bot123", status="ready") -> Dict
create_bot_data_with_status(statuses=["ready", "in_call"]) -> Dict
create_complete_bot_data(title="Meeting", duration_minutes=45) -> Dict

# Transcript & participants
create_transcript_data(speakers=["Alice", "Bob"]) -> List[Dict]
create_participants_data(names=["Alice", "Bob"]) -> List[Dict]

# Summary & webhooks
create_summary_data() -> Dict
create_webhook_payload(event="bot.done", bot_id="bot123") -> Dict
```

### MockRecallAPI

Context manager for mocking all Recall.ai API calls.

**Usage:**
```python
from tests.test_utils import MockRecallAPI

with MockRecallAPI(
    bot_data=complete_bot_data,
    transcript_data=transcript,
    participants_data=participants
):
    # All Recall.ai API calls are mocked
    response = client.post("/meeting_bots/send-bot", ...)
```

### TestHelpers

Helper methods for common test assertions.

**Methods:**

```python
# Status assertions
assert_meeting_status(meeting_data, expected_status)
assert_bot_in_meeting(status_data, expected=True)
assert_meeting_complete(meeting_data)

# Database helpers
create_meeting_in_db(db, bot_id, status, user_id)

# Integration helpers
wait_for_meeting_status(meeting_id, expected_status, timeout=10)
```

## Fixtures

Available pytest fixtures:

```python
# Database
test_db              # Isolated test database
test_client          # TestClient with test_db
test_user            # Test user in database

# Utilities
mock_factory         # MockDataFactory instance
test_helpers         # TestHelpers instance
mock_recall_api      # MockRecallAPI class
```

## Bot Status Codes

Recall.ai bot status codes:

- `ready` - Bot ready, not in meeting
- `in_call_not_recording` - In meeting, not recording yet
- `in_call_recording` - In meeting, actively recording
- `done` - Meeting ended, processing complete
- `fatal` - Error occurred

## Webhook Events

```python
# Meeting ended successfully
{
  "event": "bot.done",
  "data": {
    "bot": {"id": "bot123"},
    "meeting_metadata": {
      "title": "Team Standup",
      "participants": ["Alice", "Bob"]
    }
  }
}

# Bot encountered error
{
  "event": "bot.error",
  "data": {
    "bot": {"id": "bot123"}
  }
}
```

## Meeting Model

```python
class Meeting(Base):
    id: int
    title: str
    meeting_url: str
    status: MeetingStatus  # in_progress, processing, done, errored
    bot_id: str
    transcript: JSON
    summary: JSON
    participants: JSON
    duration: str
    created_at: datetime
    updated_at: datetime
    user_id: int
```

## MeetingStatus Enum

```python
class MeetingStatus(enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    PROCESSING = "processing"
    DONE = "done"
    ERRORED = "errored"
```
