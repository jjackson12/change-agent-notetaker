# Testing Quick Reference

Quick reference for common testing tasks.

## Running Tests

```bash
# All mocked tests (fast)
pytest tests/test_meeting_workflow.py -v

# Integration tests (slow, requires env vars)
INTEGRATION_TEST=true RECALL_API_KEY=xxx TEST_MEETING_URL=xxx pytest tests/test_meeting_workflow_integration.py -v

# Specific test
pytest tests/test_examples.py::ExampleMockedTests::test_example_simple_workflow -v

# With output
pytest tests/ -v -s

# Last failed
pytest --lf
```

## Mock Data Creation

```python
from tests.test_utils import MockDataFactory

factory = MockDataFactory()

# Bot responses
bot = factory.create_bot_response(bot_id="bot123", status="ready")
bot_in_call = factory.create_bot_data_with_status(statuses=["ready", "in_call_recording"])
complete = factory.create_complete_bot_data(title="My Meeting", duration_minutes=45)

# Transcript & participants
transcript = factory.create_transcript_data(speakers=["Alice", "Bob"])
participants = factory.create_participants_data(names=["Alice", "Bob"])

# Summary & webhook
summary = factory.create_summary_data()
webhook = factory.create_webhook_payload(event="bot.done", bot_id="bot123")
```

## Mocking Recall.ai API

### Simple Mock
```python
from unittest.mock import patch, AsyncMock

with patch('src.services.recall_service.RecallService.create_bot',
           new=AsyncMock(return_value=mock_bot_data)):
    # Your test code
    response = client.post("/meeting_bots/send-bot", ...)
```

### Complete Mock (All API Calls)
```python
from tests.test_utils import MockRecallAPI, MockDataFactory

with MockRecallAPI(
    bot_data=MockDataFactory.create_complete_bot_data(),
    transcript_data=MockDataFactory.create_transcript_data()
):
    # All Recall.ai API calls are mocked
    response = client.post("/meeting_bots/send-bot", ...)
```

## Assertions

```python
from tests.test_utils import TestHelpers

# Status checks
TestHelpers.assert_meeting_status(meeting_data, "done")
TestHelpers.assert_bot_in_meeting(status_data, expected=True)
TestHelpers.assert_meeting_complete(meeting_data)

# Standard assertions
assert response.status_code == 200
assert meeting["bot_id"] == "expected_bot_id"
```

## Database Operations

```python
# Using fixture
def test_example(test_db, test_user):
    meeting = TestHelpers.create_meeting_in_db(
        db=test_db,
        bot_id="test_bot",
        status=MeetingStatus.IN_PROGRESS
    )
```

## Common Test Patterns

### Create Bot → Check Status
```python
@pytest.mark.asyncio
async def test_bot_creation():
    with patch('src.services.recall_service.RecallService.create_bot',
               new=AsyncMock(return_value=mock_factory.create_bot_response())):
        
        response = client.post("/meeting_bots/send-bot", json={
            "meeting_url": "https://meet.google.com/test",
            "user_id": 1
        })
        meeting_id = response.json()["id"]
    
    with patch('src.services.recall_service.RecallService.retrieve_bot_data',
               new=AsyncMock(return_value=mock_factory.create_bot_data_with_status(
                   statuses=["ready", "in_call_recording"]
               ))):
        
        response = client.get(f"/meetings/{meeting_id}/bot-status")
        TestHelpers.assert_bot_in_meeting(response.json(), expected=True)
```

### Send Webhook → Verify Processing
```python
@pytest.mark.asyncio
async def test_webhook():
    import asyncio
    
    # Create meeting first...
    
    webhook = mock_factory.create_webhook_payload(event="bot.done", bot_id=bot_id)
    
    with MockRecallAPI():
        response = client.post("/webhooks/webhook", json=webhook)
        assert response.status_code == 200
        
        await asyncio.sleep(0.5)  # Wait for background task
        
        response = client.get(f"/meetings/{meeting_id}")
        TestHelpers.assert_meeting_status(response.json(), "done")
```

### Test Error Cases
```python
def test_not_found():
    response = client.get("/meetings/999999/bot-status")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_bot_error():
    # Create meeting...
    
    error_webhook = mock_factory.create_webhook_payload(
        event="bot.error",
        bot_id=bot_id
    )
    response = client.post("/webhooks/webhook", json=error_webhook)
    
    await asyncio.sleep(0.5)
    
    response = client.get(f"/meetings/{meeting_id}")
    TestHelpers.assert_meeting_status(response.json(), "errored")
```

## Fixtures Available

```python
# From conftest.py
def test_example(
    test_client,        # TestClient for API requests
    test_db,           # Isolated test database
    test_user,         # Test user in database
    mock_factory,      # MockDataFactory instance
    test_helpers,      # TestHelpers instance
    mock_recall_api    # MockRecallAPI factory
):
    pass
```

## Troubleshooting

### Tests hanging?
- Add `await asyncio.sleep(0.1)` for background tasks
- Check for missing `await` on async functions

### Mock not working?
- Verify import path in patch: `'src.services.recall_service.RecallService...'`
- Use `AsyncMock` for async functions
- Ensure patch is active when code executes

### Database issues?
- Use `test_db` fixture for isolation
- Don't share data between tests
- Commit changes: `test_db.commit()`

### Import errors?
- Ensure `src/` is in PYTHONPATH
- Check relative imports
- Verify `__init__.py` files exist

## File Locations

- Mocked workflow tests: `tests/test_meeting_workflow.py`
- Integration tests: `tests/test_meeting_workflow_integration.py`
- Test utilities: `tests/test_utils.py`
- Examples: `tests/test_examples.py`
- Complete guide: `TESTING_GUIDE.md`
