# Meeting Workflow Testing Guide

This guide explains how to test the complete meeting lifecycle: bot creation → in meeting → webhook processing → data extraction.

## Test Strategy Overview

We provide **three levels of testing**:

### 1. **Unit Tests** (Fast, Isolated)
- Test individual components with mocks
- No external dependencies
- Run in milliseconds
- Located in: `tests/test_bot_status.py`

### 2. **Mocked Workflow Tests** (Fast, Complete)
- Test complete workflows with mocked Recall.ai responses
- No API calls or real meetings needed
- Run in seconds
- Located in: `tests/test_meeting_workflow.py`

### 3. **Integration Tests** (Slow, Real)
- Test with real Recall.ai API and real meetings
- Requires valid API keys and actual meeting URLs
- Takes several minutes per test
- Located in: `tests/test_meeting_workflow_integration.py`

---

## Running Tests

### Quick Tests (Mocked - Recommended for Development)

```bash
# Run all mocked workflow tests
pytest tests/test_meeting_workflow.py -v

# Run specific test
pytest tests/test_meeting_workflow.py::TestMeetingWorkflowMocked::test_complete_meeting_workflow -v

# Run with output
pytest tests/test_meeting_workflow.py -v -s
```

### Integration Tests (Real Meetings)

**⚠️ WARNING**: Integration tests will:
- Create real bots on Recall.ai
- Join real meetings
- Consume API credits
- Take several minutes to complete

```bash
# Set up environment
export INTEGRATION_TEST=true
export RECALL_API_KEY=your_actual_api_key
export TEST_MEETING_URL=https://meet.google.com/your-test-meeting

# Run integration tests
pytest tests/test_meeting_workflow_integration.py -v -s

# Run quick connectivity check (no full meeting needed)
pytest tests/test_meeting_workflow_integration.py::TestQuickIntegrationChecks -v -s
```

### Run All Tests

```bash
# All tests except integration
pytest tests/ -v

# Everything including integration (if env vars set)
INTEGRATION_TEST=true pytest tests/ -v -s
```

---

## Test Workflow Details

### Complete Meeting Workflow Test

The main workflow test covers:

#### 1. **Bot Creation & Joining**
```python
# Create bot
response = client.post("/meeting_bots/send-bot", json={
    "meeting_url": "https://meet.google.com/...",
    "user_id": 1
})

meeting_id = response.json()["id"]
bot_id = response.json()["bot_id"]
```

#### 2. **Verify Bot Status - Not Yet In Meeting**
```python
response = client.get(f"/meetings/{meeting_id}/bot-status")
assert response.json()["in_meeting"] == False  # Still "ready"
```

#### 3. **Verify Bot Status - In Meeting**
```python
# After status changes to "in_call_recording"
response = client.get(f"/meetings/{meeting_id}/bot-status")
assert response.json()["in_meeting"] == True
```

#### 4. **Simulate Webhook (Meeting Ends)**
```python
webhook_payload = {
    "event": "bot.done",
    "data": {
        "bot": {"id": bot_id},
        "meeting_metadata": {
            "title": "Team Standup",
            "participants": ["Alice", "Bob"]
        }
    }
}

response = client.post("/webhooks/webhook", json=webhook_payload)
```

#### 5. **Verify Bot No Longer In Meeting**
```python
response = client.get(f"/meetings/{meeting_id}/bot-status")
assert response.json()["in_meeting"] == False
```

#### 6. **Verify Data Processing**
```python
response = client.get(f"/meetings/{meeting_id}")
meeting = response.json()

assert meeting["status"] == "done"
assert meeting["title"] is not None
assert meeting["transcript"] is not None
assert meeting["participants"] is not None
assert meeting["duration"] is not None
assert meeting["summary"] is not None
```

---

## Using Test Utilities

### MockDataFactory

Create consistent mock data easily:

```python
from tests.test_utils import MockDataFactory

# Create bot response
bot_data = MockDataFactory.create_bot_response(
    bot_id="my_bot_123",
    status="in_call_recording"
)

# Create complete bot data with recordings
complete_data = MockDataFactory.create_complete_bot_data(
    title="Sprint Planning",
    duration_minutes=45
)

# Create transcript
transcript = MockDataFactory.create_transcript_data(
    speakers=["Alice", "Bob", "Charlie"],
    messages_per_speaker=3
)

# Create webhook payload
webhook = MockDataFactory.create_webhook_payload(
    event="bot.done",
    bot_id="my_bot_123"
)
```

### MockRecallAPI Context Manager

Mock multiple Recall.ai API calls at once:

```python
from tests.test_utils import MockRecallAPI, MockDataFactory

def test_my_workflow():
    # Create mock data
    bot_data = MockDataFactory.create_complete_bot_data()
    transcript = MockDataFactory.create_transcript_data()
    
    # Use context manager to mock all API calls
    with MockRecallAPI(
        bot_data=bot_data,
        transcript_data=transcript
    ):
        # All Recall.ai API calls are now mocked
        # Test your workflow here
        response = client.post("/meeting_bots/send-bot", ...)
        # ...
```

### Test Helpers

```python
from tests.test_utils import TestHelpers

# Assert meeting status
TestHelpers.assert_meeting_status(meeting_data, "done")

# Assert bot in meeting
TestHelpers.assert_bot_in_meeting(status_data, expected=True)

# Assert complete meeting data
TestHelpers.assert_meeting_complete(meeting_data)

# Create test meeting in database
meeting = TestHelpers.create_meeting_in_db(
    db=test_db,
    bot_id="test_bot",
    status=MeetingStatus.IN_PROGRESS
)
```

### Database Isolation

Use test database fixtures for isolation:

```python
def test_with_isolated_db(test_db, test_client):
    # test_db is a clean database for this test only
    # test_client uses this isolated database
    
    response = test_client.post("/meeting_bots/send-bot", ...)
    # Database changes don't affect other tests
```

---

## Writing New Tests

### Example: Test New Feature

```python
import pytest
from tests.test_utils import MockDataFactory, MockRecallAPI, TestHelpers

class TestMyNewFeature:
    
    @pytest.mark.asyncio
    async def test_feature_workflow(self, test_client, mock_factory):
        # 1. Set up mock data
        bot_data = mock_factory.create_complete_bot_data(
            title="My Test Meeting"
        )
        
        # 2. Mock Recall.ai API
        with MockRecallAPI(bot_data=bot_data):
            
            # 3. Create bot and meeting
            response = test_client.post("/meeting_bots/send-bot", json={
                "meeting_url": "https://meet.google.com/test",
                "user_id": 1
            })
            meeting_id = response.json()["id"]
            
            # 4. Test your feature
            response = test_client.get(f"/my-new-endpoint/{meeting_id}")
            assert response.status_code == 200
            
            # 5. Verify results
            data = response.json()
            TestHelpers.assert_meeting_status(data, "in_progress")
```

---

## Troubleshooting Tests

### Mocked Tests Failing

1. **Check mock data structure**: Ensure mock data matches Recall.ai API format
2. **Verify status codes**: Check that endpoints return expected status codes
3. **Check async/await**: Ensure async functions are properly awaited
4. **Background tasks**: Add small delays for background task processing:
   ```python
   import asyncio
   await asyncio.sleep(0.5)  # Wait for background task
   ```

### Integration Tests Failing

1. **API Key**: Verify `RECALL_API_KEY` is valid
2. **Meeting URL**: Ensure meeting URL is active and accessible
3. **Network**: Check internet connectivity and firewall settings
4. **Timeouts**: Increase timeout values if tests fail due to slow network
5. **Rate Limits**: Recall.ai may rate limit; space out tests

### Database Issues

1. **Use test fixtures**: Always use `test_db` and `test_client` fixtures
2. **Clean state**: Each test should start with clean database
3. **Transactions**: Ensure database transactions are committed

---

## Best Practices

### 1. **Use Mocked Tests for Development**
- Fast feedback loop
- No API costs
- Reliable and repeatable

### 2. **Use Integration Tests for Validation**
- Run before major releases
- Verify real-world scenarios
- Catch integration issues

### 3. **Test Error Cases**
```python
def test_bot_error_webhook():
    webhook = {
        "event": "bot.error",
        "data": {"bot": {"id": "error_bot"}}
    }
    response = client.post("/webhooks/webhook", json=webhook)
    # Verify error handling
```

### 4. **Test Edge Cases**
- Missing webhook data
- Invalid bot IDs
- Meetings without bots
- Timeout scenarios

### 5. **Keep Tests Independent**
- Each test should work in isolation
- Don't rely on test execution order
- Use fixtures for setup/teardown

---

## Performance

### Test Execution Times

| Test Type | Time per Test | When to Run |
|-----------|--------------|-------------|
| Unit | < 100ms | Always (CI/CD) |
| Mocked Workflow | 1-3s | Always (CI/CD) |
| Integration | 3-10min | Before releases |

### Optimizing Test Speed

1. **Parallel execution**:
   ```bash
   pytest tests/ -v -n auto  # Requires pytest-xdist
   ```

2. **Skip slow tests during development**:
   ```bash
   pytest tests/ -v -m "not slow"
   ```

3. **Run only changed tests**:
   ```bash
   pytest --lf  # Last failed
   pytest --ff  # Failed first
   ```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    
    - name: Run unit and mocked tests
      run: pytest tests/ -v --ignore=tests/test_meeting_workflow_integration.py
    
    - name: Run integration tests (main branch only)
      if: github.ref == 'refs/heads/main'
      env:
        INTEGRATION_TEST: true
        RECALL_API_KEY: ${{ secrets.RECALL_API_KEY }}
        TEST_MEETING_URL: ${{ secrets.TEST_MEETING_URL }}
      run: pytest tests/test_meeting_workflow_integration.py::TestQuickIntegrationChecks -v
```

---

## Additional Resources

- **Recall.ai API Docs**: https://docs.recall.ai/
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **Pytest Documentation**: https://docs.pytest.org/
- **pytest-asyncio**: https://pytest-asyncio.readthedocs.io/

---

## Support

If you encounter issues with the tests:

1. Check this guide first
2. Review test output for specific errors
3. Enable verbose output: `pytest -v -s`
4. Check logs in the application
5. Verify environment variables are set correctly
