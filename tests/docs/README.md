# Testing Guide

Complete testing framework for the meeting bot workflow.

## Quick Start

```bash
# Run mocked tests (3 seconds)
pytest tests/test_meeting_workflow.py -v

# Run examples
pytest tests/test_examples.py -v

# Run all tests (skip integration)
pytest tests/ --ignore=tests/test_meeting_workflow_integration.py -v
```

## What Gets Tested

Complete meeting workflow:
1. Create bot & join meeting
2. Check bot is in meeting
3. Meeting ends, webhook received
4. Check bot left meeting
5. Verify data processed (transcript, summary, participants)

## Test Types

| Type | Speed | Use Case |
|------|-------|----------|
| **Mocked** | 3s | Daily development (recommended) |
| **Unit** | <100ms | Individual functions |
| **Integration** | 3-10min | Production validation |

## Writing Tests

### Basic Example

```python
import pytest
from tests.test_utils import MockDataFactory, MockRecallAPI

@pytest.mark.asyncio
async def test_bot_workflow(mock_factory):
    # Create mock data
    bot_data = mock_factory.create_complete_bot_data()
    
    # Mock API calls
    with MockRecallAPI(bot_data=bot_data):
        # Test your workflow
        response = client.post("/meeting_bots/send-bot", json={
            "meeting_url": "https://meet.google.com/test",
            "user_id": 1
        })
        
        assert response.status_code == 200
```

### Complete Workflow

```python
from tests.test_utils import MockRecallAPI, MockDataFactory, TestHelpers
import asyncio

@pytest.mark.asyncio
async def test_complete_workflow(mock_factory):
    with MockRecallAPI(bot_data=mock_factory.create_complete_bot_data()):
        # 1. Create bot
        response = client.post("/meeting_bots/send-bot", 
            json={"meeting_url": "https://meet.google.com/test", "user_id": 1})
        meeting_id = response.json()["id"]
        bot_id = response.json()["bot_id"]
        
        # 2. Check in meeting
        response = client.get(f"/meetings/{meeting_id}/bot-status")
        TestHelpers.assert_bot_in_meeting(response.json(), expected=True)
        
        # 3. Send webhook
        webhook = mock_factory.create_webhook_payload("bot.done", bot_id)
        client.post("/webhooks/webhook", json=webhook)
        
        # 4. Wait for processing
        await asyncio.sleep(0.5)
        
        # 5. Verify complete
        response = client.get(f"/meetings/{meeting_id}")
        TestHelpers.assert_meeting_complete(response.json())
```

## Test Utilities

### MockDataFactory

```python
from tests.test_utils import MockDataFactory

factory = MockDataFactory()

# Create test data
bot = factory.create_bot_response(bot_id="bot123")
complete = factory.create_complete_bot_data(duration_minutes=45)
transcript = factory.create_transcript_data(speakers=["Alice", "Bob"])
webhook = factory.create_webhook_payload("bot.done", "bot123")
```

### MockRecallAPI

```python
from tests.test_utils import MockRecallAPI

# Mock all Recall.ai API calls at once
with MockRecallAPI(bot_data=complete_data, transcript_data=transcript):
    # All API calls automatically mocked
    response = client.post(...)
```

### TestHelpers

```python
from tests.test_utils import TestHelpers

# Semantic assertions
TestHelpers.assert_meeting_status(meeting, "done")
TestHelpers.assert_bot_in_meeting(status_data, expected=True)
TestHelpers.assert_meeting_complete(meeting)
```

## Integration Tests (Real Meetings)

```bash
# Set environment variables
export INTEGRATION_TEST=true
export RECALL_API_KEY=your_actual_key
export TEST_MEETING_URL=https://meet.google.com/your-meeting

# Run integration tests
pytest tests/test_meeting_workflow_integration.py -v -s
```

**Note**: Integration tests create real bots, join real meetings, and consume API credits.

## Common Commands

```bash
# Run specific test
pytest tests/test_meeting_workflow.py::TestMeetingWorkflowMocked::test_complete_meeting_workflow -v

# Run with output
pytest tests/test_examples.py -v -s

# Last failed tests
pytest --lf

# Specific test file
pytest tests/test_bot_status.py -v
```

## Troubleshooting

**Tests hanging?**
```python
# Add delay for background tasks
await asyncio.sleep(0.5)
```

**Mock not working?**
```python
# Ensure correct import path
with patch('src.services.recall_service.RecallService.create_bot', ...):
```

**Database issues?**
```python
# Use test_db fixture for isolation
def test_example(test_db, test_client):
    # Each test gets clean database
```

## File Structure

```
tests/
├── test_meeting_workflow.py             # Main mocked tests ⭐
├── test_meeting_workflow_integration.py # Real integration tests
├── test_bot_status.py                   # Unit tests
├── test_examples.py                     # Example patterns
├── test_utils.py                        # Utilities & fixtures
└── docs/
    ├── README.md                        # This file
    └── API.md                           # API documentation
```

## Best Practices

1. **Use mocked tests for development** - Fast feedback
2. **Use integration tests before releases** - Validate production
3. **Write isolated tests** - Each test independent
4. **Mock external APIs** - Keep tests fast
5. **Test error cases** - Not just happy paths
6. **Use helpers** - Readable assertions

## Need More Help?

- Review `tests/test_examples.py` for working examples
- Check `tests/test_utils.py` for available utilities
- See `API.md` for endpoint documentation
