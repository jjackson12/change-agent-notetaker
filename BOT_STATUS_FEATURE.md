# Bot Status Checking

This feature allows you to check if a meeting bot is currently in an active meeting by querying the Recall.ai API.

## New Endpoints

### 1. Check Bot Status by Bot ID
```
GET /meeting_bots/bot-status/{bot_id}
```

Check if a specific bot (by Recall.ai bot ID) is currently in a meeting.

**Parameters:**
- `bot_id` (path): The Recall.ai bot ID

**Response:**
```json
{
  "bot_id": "abc123",
  "in_meeting": true
}
```

**Example Usage:**
```bash
curl http://localhost:8000/meeting_bots/bot-status/abc123
```

### 2. Check Bot Status by Meeting ID
```
GET /meetings/{meeting_id}/bot-status
```

Check if the bot associated with a specific meeting is currently in the meeting.

**Parameters:**
- `meeting_id` (path): The internal meeting ID

**Response:**
```json
{
  "meeting_id": 123,
  "bot_id": "abc123",
  "in_meeting": true
}
```

**Example Usage:**
```bash
curl http://localhost:8000/meetings/123/bot-status
```

## Implementation Details

### RecallService.is_bot_in_meeting()

The core functionality is implemented in the `RecallService` class:

```python
async def is_bot_in_meeting(bot_id: str) -> bool:
    """
    Check if a bot is currently in a meeting
    
    Returns True if the bot's current status is:
    - in_call_not_recording
    - in_call_recording
    
    Returns False for any other status (ready, done, fatal, etc.)
    """
```

The method:
1. Retrieves the bot data from Recall.ai API
2. Checks the `status_changes` field for the most recent status
3. Returns `True` if the status indicates the bot is in an active call
4. Returns `False` otherwise

### Bot Status Codes

According to Recall.ai documentation, the relevant status codes are:

- **ready**: Bot is ready but not yet in a call
- **in_call_not_recording**: Bot has joined but not recording yet
- **in_call_recording**: Bot is actively recording the meeting
- **done**: Bot has left the meeting and processing is complete
- **fatal**: An error occurred

## Use Cases

1. **Real-time monitoring**: Check if a bot is still actively in a meeting
2. **Status dashboard**: Display which bots are currently in meetings
3. **Cleanup operations**: Identify bots that should be cleaned up
4. **Meeting validation**: Verify a bot successfully joined before proceeding

## Error Handling

Both endpoints will return appropriate HTTP error codes:

- `404 Not Found`: Meeting doesn't exist (for meeting-based endpoint)
- `400 Bad Request`: Meeting has no associated bot
- `500 Internal Server Error`: Failed to communicate with Recall.ai API

## Testing

Tests are available in `tests/test_bot_status.py` covering:
- Bot in meeting (in_call_recording status)
- Bot not in meeting (done status)
- Bot with no status changes
- Direct RecallService method testing
- API endpoint testing with mocks
