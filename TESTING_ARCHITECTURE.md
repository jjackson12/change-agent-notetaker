# Meeting Workflow Testing Architecture

## Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         YOUR APPLICATION                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐             │
│  │   API Layer  │    │   Services   │    │   Database   │             │
│  │ (FastAPI)    │◄──►│ (Business    │◄──►│ (SQLAlchemy) │             │
│  │              │    │  Logic)      │    │              │             │
│  └──────────────┘    └──────────────┘    └──────────────┘             │
│         ▲                   ▲                                           │
└─────────┼───────────────────┼───────────────────────────────────────────┘
          │                   │
          │                   │
┌─────────┼───────────────────┼───────────────────────────────────────────┐
│         │  TEST FRAMEWORK   │                                           │
├─────────┼───────────────────┼───────────────────────────────────────────┤
│         │                   │                                           │
│         ▼                   ▼                                           │
│  ┌─────────────────────────────────────┐                               │
│  │     test_utils.py                   │                               │
│  │  ┌──────────────────────────────┐   │                               │
│  │  │  MockDataFactory             │   │                               │
│  │  │  - create_bot_response()     │   │                               │
│  │  │  - create_transcript_data()  │   │                               │
│  │  │  - create_webhook_payload()  │   │                               │
│  │  └──────────────────────────────┘   │                               │
│  │  ┌──────────────────────────────┐   │                               │
│  │  │  MockRecallAPI               │   │                               │
│  │  │  - Mock all Recall.ai calls  │   │                               │
│  │  └──────────────────────────────┘   │                               │
│  │  ┌──────────────────────────────┐   │                               │
│  │  │  TestHelpers                 │   │                               │
│  │  │  - assert_meeting_status()   │   │                               │
│  │  │  - assert_bot_in_meeting()   │   │                               │
│  │  └──────────────────────────────┘   │                               │
│  │  ┌──────────────────────────────┐   │                               │
│  │  │  Fixtures                    │   │                               │
│  │  │  - test_db (isolated DB)     │   │                               │
│  │  │  - test_client               │   │                               │
│  │  │  - test_user                 │   │                               │
│  │  └──────────────────────────────┘   │                               │
│  └─────────────────────────────────────┘                               │
│                    ▲                                                    │
│                    │                                                    │
│         ┌──────────┼──────────┬──────────────────────┐                 │
│         │          │          │                      │                 │
│         ▼          ▼          ▼                      ▼                 │
│  ┌───────────┐ ┌──────────┐ ┌──────────────┐ ┌─────────────────┐     │
│  │   Unit    │ │  Mocked  │ │ Integration  │ │    Examples     │     │
│  │   Tests   │ │ Workflow │ │    Tests     │ │                 │     │
│  │           │ │  Tests   │ │              │ │                 │     │
│  │ test_bot_ │ │ test_    │ │ test_*_      │ │ test_examples   │     │
│  │ status.py │ │ meeting_ │ │ integration  │ │ .py             │     │
│  │           │ │ workflow │ │ .py          │ │                 │     │
│  │           │ │ .py      │ │              │ │                 │     │
│  │ Fast      │ │ Fast     │ │ Slow         │ │ Reference       │     │
│  │ <100ms    │ │ 1-3s     │ │ 3-10min      │ │                 │     │
│  │ Fully     │ │ Mocked   │ │ Real API     │ │                 │     │
│  │ Mocked    │ │ E2E      │ │ Real Meeting │ │                 │     │
│  └───────────┘ └──────────┘ └──────────────┘ └─────────────────┘     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Workflow Test Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                    MOCKED WORKFLOW TEST                               │
└──────────────────────────────────────────────────────────────────────┘

Step 1: CREATE BOT
┌─────────────────┐
│  Test Code      │  POST /meeting_bots/send-bot
│                 │  ────────────────────────────►
│  with patch():  │
│    create_bot() │
│    returns mock │
└─────────────────┘
                      ┌────────────────────────┐
                      │ API creates meeting    │
                      │ Returns: meeting_id,   │
                      │          bot_id,       │
                      │          status        │
                      └────────────────────────┘

Step 2: CHECK STATUS (Not in meeting)
┌─────────────────┐
│  Test Code      │  GET /meetings/{id}/bot-status
│                 │  ────────────────────────────►
│  with patch():  │
│    retrieve()   │  ◄────────────────────────────
│    returns      │     in_meeting: false
│    "ready"      │
└─────────────────┘

Step 3: BOT JOINS (Status change)
┌─────────────────┐
│  Test Code      │  GET /meetings/{id}/bot-status
│                 │  ────────────────────────────►
│  with patch():  │
│    retrieve()   │  ◄────────────────────────────
│    returns      │     in_meeting: true
│    "in_call"    │
└─────────────────┘

Step 4: WEBHOOK (Meeting ends)
┌─────────────────┐
│  Test Code      │  POST /webhooks/webhook
│                 │  ────────────────────────────►
│  MockRecallAPI  │     event: "bot.done"
│  mocks all:     │
│  - retrieve()   │  ◄────────────────────────────
│  - transcript   │     200 OK (immediate)
│  - participants │
│  - summary      │  ┌──────────────────────────┐
└─────────────────┘  │ Background Task Starts   │
                     │ - Fetch bot data         │
         await       │ - Extract transcript     │
         sleep(0.5)  │ - Generate summary       │
                     │ - Update meeting         │
                     └──────────────────────────┘

Step 5: VERIFY NOT IN MEETING
┌─────────────────┐
│  Test Code      │  GET /meetings/{id}/bot-status
│                 │  ────────────────────────────►
│  with patch():  │
│    retrieve()   │  ◄────────────────────────────
│    returns      │     in_meeting: false
│    "done"       │
└─────────────────┘

Step 6: VERIFY DATA PROCESSED
┌─────────────────┐
│  Test Code      │  GET /meetings/{id}
│                 │  ────────────────────────────►
│  TestHelpers    │
│  .assert_       │  ◄────────────────────────────
│  meeting_       │     Meeting with:
│  complete()     │     - transcript ✓
│                 │     - summary ✓
└─────────────────┘     - participants ✓
                        - duration ✓
```

## Integration Test Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                    INTEGRATION TEST (REAL)                            │
└──────────────────────────────────────────────────────────────────────┘

Step 1: CREATE BOT (Real API)
┌─────────────────┐
│  Test Code      │  POST /meeting_bots/send-bot
│                 │  ────────────────────────────►
│  NO MOCKS!      │
│  Real URL       │          ┌──────────────────────┐
│  Real API Key   │          │  Real Recall.ai API  │
└─────────────────┘          │  - Creates real bot  │
                             │  - Joins real meeting│
                             └──────────────────────┘
                                       │
Step 2: POLL UNTIL BOT JOINS          ▼
┌─────────────────┐          ┌──────────────────────┐
│ loop:           │          │ Bot joins Google Meet│
│   GET /bot-     │◄─────────┤ or Zoom              │
│   status        │  Poll    │                      │
│   sleep(5s)     │  every   │ Status changes:      │
│   until         │  5 sec   │ ready → in_call      │
│   in_meeting    │          └──────────────────────┘
└─────────────────┘
       ⏱ Timeout: 2 min

Step 3: MONITOR MEETING
┌─────────────────┐          ┌──────────────────────┐
│ Print:          │          │  Real meeting        │
│ "Bot is in      │          │  happening...        │
│  meeting..."    │          │                      │
│                 │          │  Participants talk   │
│ "You can end    │          │  Bot records         │
│  the meeting"   │          │  Transcript created  │
│                 │          │                      │
│ Wait for        │          │  [Meeting ends]      │
│ completion      │          └──────────────────────┘
└─────────────────┘
       ⏱ Timeout: 15 min

Step 4: WEBHOOK RECEIVED (Real)
┌─────────────────┐          ┌──────────────────────┐
│ Recall.ai sends │          │  Recall.ai servers   │
│ real webhook to │◄─────────┤  POST to your        │
│ your endpoint   │  Real    │  /webhooks/webhook   │
│                 │  HTTP    │                      │
│ Background task │          │  event: "bot.done"   │
│ processes real  │          └──────────────────────┘
│ data            │
└─────────────────┘

Step 5: POLL UNTIL DONE
┌─────────────────┐
│ loop:           │
│   GET /meetings │
│   /{id}         │
│   sleep(5s)     │
│   until status  │
│   == "done"     │
└─────────────────┘
       ⏱ Timeout: 3 min

Step 6: VERIFY REAL DATA
┌─────────────────┐          ┌──────────────────────┐
│ Assert:         │          │ Real data verified:  │
│ - transcript    │◄─────────┤ - Real voices → text │
│   exists        │          │ - Real participants  │
│ - participants  │          │ - Real duration      │
│   not empty     │          │ - AI summary of      │
│ - duration set  │          │   real conversation  │
│ - summary       │          └──────────────────────┘
│   generated     │
└─────────────────┘

✅ FULL E2E VALIDATION COMPLETE
```

## Test Utilities Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      test_utils.py                               │
└──────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│  MockDataFactory                                              │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  create_bot_response()                                        │
│  ├─ bot_id, meeting_url, status                              │
│  └─ Returns: {"id": "...", "status_changes": [...]}          │
│                                                               │
│  create_bot_data_with_status(statuses)                       │
│  ├─ Input: ["ready", "in_call_recording", "done"]            │
│  └─ Returns: Full bot object with status history             │
│                                                               │
│  create_complete_bot_data()                                   │
│  ├─ Includes recordings, metadata                            │
│  └─ Returns: Bot with media_shortcuts URLs                   │
│                                                               │
│  create_transcript_data(speakers)                            │
│  └─ Returns: [{participant, words: [{text, timestamp}]}]     │
│                                                               │
│  create_webhook_payload(event, bot_id)                       │
│  └─ Returns: {event, data: {bot: {id}}}                      │
│                                                               │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│  MockRecallAPI (Context Manager)                              │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  __init__(bot_data, transcript_data, participants_data)       │
│                                                               │
│  __enter__():                                                 │
│  ├─ patch('RecallService.retrieve_bot_data')                 │
│  ├─ patch('httpx.AsyncClient.get')                           │
│  │  ├─ transcript URL → transcript_data                      │
│  │  └─ participants URL → participants_data                  │
│  └─ Returns: self                                            │
│                                                               │
│  __exit__():                                                  │
│  └─ Cleanup all patches                                      │
│                                                               │
│  Usage:                                                       │
│    with MockRecallAPI(bot_data=...):                         │
│        # All API calls mocked                                │
│        response = client.post(...)                           │
│                                                               │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│  TestHelpers                                                  │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  assert_meeting_status(meeting, expected_status)             │
│  └─ Semantic assertion with clear error messages            │
│                                                               │
│  assert_bot_in_meeting(status_data, expected=True)           │
│  └─ Check in_meeting boolean                                │
│                                                               │
│  assert_meeting_complete(meeting_data)                       │
│  └─ Verify all fields present: transcript, summary, etc.    │
│                                                               │
│  create_meeting_in_db(db, bot_id, status)                   │
│  └─ Direct database insertion for setup                     │
│                                                               │
│  wait_for_meeting_status(meeting_id, status, timeout)       │
│  └─ Poll until status reached (integration tests)           │
│                                                               │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│  Fixtures (pytest)                                            │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  @fixture test_db                                            │
│  ├─ Creates in-memory SQLite database                        │
│  ├─ Creates all tables                                       │
│  ├─ Yields session                                           │
│  └─ Drops all tables on cleanup                             │
│                                                               │
│  @fixture test_client(test_db)                               │
│  ├─ Overrides get_db() to use test_db                       │
│  ├─ Creates TestClient                                       │
│  └─ Clears overrides on cleanup                             │
│                                                               │
│  @fixture test_user(test_db)                                 │
│  └─ Creates user in test_db                                 │
│                                                               │
│  @fixture mock_factory                                       │
│  └─ Returns MockDataFactory instance                        │
│                                                               │
│  @fixture test_helpers                                       │
│  └─ Returns TestHelpers instance                            │
│                                                               │
│  @fixture mock_recall_api                                    │
│  └─ Returns MockRecallAPI class for instantiation           │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## File Dependencies

```
conftest.py
    │
    ├─ Imports test_utils fixtures
    │
    └─ Provides to all test files
            │
            ├──► test_bot_status.py
            │       (Unit tests)
            │
            ├──► test_meeting_workflow.py
            │       (Mocked workflow tests)
            │       Uses: MockDataFactory
            │             MockRecallAPI
            │             TestHelpers
            │
            ├──► test_meeting_workflow_integration.py
            │       (Real integration tests)
            │       Uses: TestHelpers only
            │       No mocks!
            │
            └──► test_examples.py
                    (Reference examples)
                    Uses: All utilities
```

## Documentation Flow

```
User wants to test
        │
        ├─ Quick start?
        │  └──► TESTING_QUICK_REF.md
        │       (Commands, snippets)
        │
        ├─ Learn how to write tests?
        │  └──► test_examples.py
        │       (Working examples)
        │
        ├─ Understand architecture?
        │  └──► TESTING_ARCHITECTURE.md (this file)
        │       (Visual diagrams)
        │
        ├─ Detailed information?
        │  └──► TESTING_GUIDE.md
        │       (Complete guide)
        │
        └─ Implementation details?
           └──► TESTING_IMPLEMENTATION_SUMMARY.md
                (What was built)
```
