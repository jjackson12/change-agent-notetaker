# AI Notetaker API

Backend API for AI-powered meeting transcription and note-taking using Recall.ai and Change Agent.

## Overview
The AI Notetaker API integrates with [Recall.ai](https://www.recall.ai/) to automatically join Zoom and Google Meet meetings, transcribe conversations in real-time, and generate intelligent summaries using Change Agent AI.

## Features
- 🤖 **Automated Bot Joining**: Send bots to join meetings via meeting URL
- 📝 **Real-time Transcription**: Automatic transcription powered by Recall.ai
- 🧠 **AI Summarization**: Intelligent meeting summaries using Change Agent
- 🎥 **Video Recording**: Access meeting recordings
- 📊 **Participant Tracking**: Track meeting participants and speaking time
- 🔔 **Webhook Integration**: Real-time status updates via webhooks
- 🗓️ **Future**: Calendar integration for automatic meeting scheduling

## Project Structure
```
ai-notetaker-api
├── src
│   ├── main.py                # Entry point of the FastAPI application
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database connection and ORM setup
│   ├── dependencies.py        # Dependency injection functions
│   ├── models                  # Database models
│   ├── schemas                 # Pydantic schemas for data validation
│   ├── api                     # API endpoints
│   ├── services                # Business logic
│   └── utils                   # Utility functions
├── tests                       # Unit tests
├── alembic                     # Database migrations
├── requirements.txt            # Project dependencies
├── alembic.ini                # Alembic configuration
├── .env.example                # Example environment variables
└── README.md                   # Project documentation
```

## Prerequisites

1. **Python 3.9+** - [Download Python](https://www.python.org/downloads/)
2. **Recall.ai API Key** - [Sign up at Recall.ai](https://www.recall.ai/)
3. **ngrok** (for webhook development) - [Download ngrok](https://ngrok.com/download)
4. **Change Agent API Key** - Contact your Change Agent admin

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd change-agent-notetaker
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
RECALL_API_KEY=your_recall_api_key_here
SECRET_KEY=your_secret_key_here
# Add other required variables
```

### 5. Initialize Database
```bash
# Create database tables
alembic upgrade head
```

## Running the Application

### Start the API Server
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Set Up Webhooks (Required for Production)

Recall.ai needs to send webhooks when meetings end. For local development:

1. **Start ngrok:**
```bash
ngrok http 8000
```

2. **Configure webhook in Recall.ai Dashboard:**
   - Go to [Recall.ai Dashboard > Webhooks](https://us-west-2.recall.ai/dashboard/webhooks)
   - Add endpoint: `https://your-ngrok-url.ngrok-free.app/api/webhook`
   - Subscribe to event: `bot.done`

3. **Note:** For production, use your actual domain instead of ngrok

## API Documentation

Interactive API documentation available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Quick Start Guide

### 1. Send a Bot to a Meeting
```bash
curl -X POST "http://localhost:8000/api/send-bot" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_url": "https://meet.google.com/xxx-xxxx-xxx"
  }'
```

Response:
```json
{
  "id": 1,
  "meeting_url": "https://meet.google.com/xxx-xxxx-xxx",
  "bot_id": "recall-bot-id-123",
  "status": "in_progress",
  "title": "Meeting in Progress",
  ...
}
```

### 2. Check Meeting Status
```bash
curl "http://localhost:8000/api/meetings/1"
```

### 3. Get Meeting Notes (after completion)
```bash
curl "http://localhost:8000/api/notes/1"
```

## Core Endpoints

### Bot Management
- `POST /api/send-bot` - Send bot to active meeting
- `POST /api/schedule-bot` - Schedule bot for future meeting (TODO)
- `DELETE /api/unschedule-bot/{meeting_id}` - Cancel scheduled bot (TODO)

### Meetings
- `GET /api/meetings` - List all meetings
- `GET /api/meetings/{meeting_id}` - Get meeting details
- `GET /api/meetings/{meeting_id}/video` - Get video URL
- `POST /api/meetings/{meeting_id}/summarize` - Regenerate summary
- `DELETE /api/meetings/{meeting_id}` - Delete meeting

### Notes
- `GET /api/notes` - List all completed meeting notes
- `GET /api/notes/{meeting_id}` - Get notes for specific meeting

### Webhooks
- `POST /api/webhook` - Receive Recall.ai webhooks (internal use)

## Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_meetings.py
```

## Architecture

### Data Flow

```
1. Client sends meeting URL → POST /api/send-bot
2. API creates bot via Recall.ai API
3. Bot joins meeting and records
4. Meeting ends → Recall.ai sends webhook to /api/webhook
5. API retrieves transcript and generates AI summary
6. Client polls GET /api/meetings/{id} to check status
7. When status = "done", transcript and summary are available
```

### Database Schema

**Meeting** (main table)
- `id`: Primary key
- `meeting_url`: Google Meet/Zoom URL
- `bot_id`: Recall.ai bot identifier
- `status`: scheduled | in_progress | processing | done | errored
- `title`: Meeting title
- `transcript`: JSON array of transcript segments
- `summary`: JSON object with AI-generated summary
- `participants`: JSON array of participant names
- `duration`: String like "45 min"
- `created_at`, `updated_at`: Timestamps

### Status Flow

```
IN_PROGRESS → PROCESSING → DONE
                    ↓
                ERRORED
```

- **IN_PROGRESS**: Bot has joined meeting
- **PROCESSING**: Meeting ended, generating summary
- **DONE**: All data available
- **ERRORED**: Something went wrong

## Development

### Project Structure
```
change-agent-notetaker/
├── src/
│   ├── main.py              # FastAPI app and routes
│   ├── config.py            # Configuration and settings
│   ├── database.py          # SQLAlchemy setup
│   ├── models/              # Database models
│   │   ├── meeting.py       # Meeting model with status tracking
│   │   ├── user.py          # User model
│   │   └── ...
│   ├── schemas/             # Pydantic schemas
│   │   ├── meeting.py       # Meeting schemas, transcript, summary
│   │   ├── webhook.py       # Webhook payload schemas
│   │   └── ...
│   ├── api/                 # API endpoints
│   │   ├── meeting_bots.py  # Bot triggering endpoints
│   │   ├── meetings.py      # Meeting CRUD
│   │   ├── notes.py         # Notes access
│   │   ├── webhooks.py      # Recall.ai webhook handler
│   │   └── ...
│   ├── services/            # Business logic
│   │   ├── recall_service.py      # Recall.ai API integration
│   │   ├── change_agent_service.py # AI summarization
│   │   └── ...
│   └── utils/               # Helper functions
├── tests/                   # Unit and integration tests
├── alembic/                 # Database migrations
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variable template
└── README.md               # This file
```

### Adding a Database Migration
```bash
# Create a new migration
alembic revision --autogenerate -m "Add new field"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Quality
```bash
# Format code
black src/

# Sort imports
isort src/

# Type checking
mypy src/

# Linting
flake8 src/
```

## Troubleshooting

### Bot Not Joining Meeting
- Verify `RECALL_API_KEY` is correct
- Check meeting URL is valid and accessible
- Ensure meeting hasn't started yet (some platforms require waiting room approval)

### Webhook Not Receiving Data
- Confirm ngrok is running and URL is correct
- Check webhook is configured in Recall.ai dashboard
- Verify webhook URL includes `/api/webhook` path
- Check API server logs for incoming requests

### Summary Not Generating
- Verify Change Agent API credentials are configured
- Check `src/services/change_agent_service.py` implementation
- Review server logs for errors during summary generation

### Database Issues
```bash
# Reset database (WARNING: deletes all data)
rm notetaker.db
alembic upgrade head
```

## Future Enhancements

- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Automatic bot scheduling for calendar events
- [ ] Real-time status updates via WebSockets
- [ ] Multi-user authentication and authorization
- [ ] Meeting analytics and insights
- [ ] Export notes to various formats (PDF, Markdown, etc.)
- [ ] Search and filter meetings
- [ ] Custom AI prompts for summaries

## Testing

Comprehensive testing framework with mocked and real integration tests.

### Quick Start
```bash
# Run mocked workflow tests (fast - 3 seconds)
pytest tests/test_meeting_workflow.py -v

# Run all tests except integration
pytest tests/ --ignore=tests/test_meeting_workflow_integration.py -v

# See examples
pytest tests/test_examples.py -v
```

### Documentation
- **[Testing Guide](tests/docs/README.md)** - Complete guide & examples
- **[API Reference](tests/docs/API.md)** - Endpoints & utilities

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests (see [Testing Documentation](tests/docs/README.md))
5. Submit a pull request

## Support

For issues or questions:
- Open an issue on GitHub
- Contact the development team

## License

This project is licensed under the MIT License.