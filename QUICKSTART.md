# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.9 or higher
- [Recall.ai API key](https://www.recall.ai/)
- [ngrok](https://ngrok.com/) installed

### Step 1: Clone and Setup
```bash
git clone <your-repo-url>
cd change-agent-notetaker
./setup.sh
```

### Step 2: Configure API Keys
Edit `.env` file:
```bash
RECALL_API_KEY=your_actual_recall_api_key_here
SECRET_KEY=any_random_secret_string_here
```

### Step 3: Start the Server
```bash
# Activate virtual environment
source venv/bin/activate

# Start the API
uvicorn src.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 4: Setup Webhooks (Essential!)

In a **new terminal**:
```bash
ngrok http 8000
```

Copy the `Forwarding` URL (e.g., `https://abc123.ngrok-free.app`)

Then:
1. Go to [Recall.ai Dashboard → Webhooks](https://us-west-2.recall.ai/dashboard/webhooks)
2. Click "Add Webhook"
3. Paste: `https://abc123.ngrok-free.app/api/webhook`
4. Select event: `bot.done`
5. Save

### Step 5: Test It!

#### Send a Bot to a Meeting

1. Create or join a test meeting (Google Meet or Zoom)
2. Get the meeting URL
3. Send the bot:

```bash
curl -X POST "http://localhost:8000/api/send-bot" \
  -H "Content-Type: application/json" \
  -d '{"meeting_url": "YOUR_MEETING_URL_HERE"}'
```

Example response:
```json
{
  "id": 1,
  "meeting_url": "https://meet.google.com/xxx-yyyy-zzz",
  "bot_id": "abc123",
  "status": "in_progress",
  "title": "Meeting in Progress",
  ...
}
```

#### Check Status

```bash
curl http://localhost:8000/api/meetings/1
```

Keep checking until `"status": "done"`

#### Get the Notes

```bash
curl http://localhost:8000/api/notes/1
```

You'll get:
- Full transcript with timestamps
- AI-generated summary
- Participant list
- Meeting duration

### Step 6: View API Docs

Open your browser to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Common Issues

### Bot Not Joining?
- ✅ Check your `RECALL_API_KEY` is valid
- ✅ Verify meeting URL is correct
- ✅ Some meetings require host approval - check the actual meeting

### No Webhook Received?
- ✅ Is ngrok still running?
- ✅ Did you configure the webhook in Recall.ai dashboard?
- ✅ Check API logs for incoming requests

### Database Error?
```bash
rm notetaker.db
alembic upgrade head
```

## What's Next?

1. **Integrate Change Agent**: Update `src/services/change_agent_service.py` with your actual API
2. **Add Authentication**: Implement user auth if needed
3. **Deploy**: Move from ngrok to a real server with HTTPS
4. **Scale**: Add background workers for better webhook processing

## Testing Without a Real Meeting

You can test the API without joining a meeting using the test suite:

```bash
pytest tests/
```

## Need Help?

- 📖 Read the [README.md](README.md) for full documentation
- 📋 Check [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for architecture details
- 🐛 Check server logs for error messages
- 💬 Open an issue on GitHub

## Production Checklist

Before deploying to production:
- [ ] Change `DATABASE_URL` to PostgreSQL
- [ ] Set strong `SECRET_KEY`
- [ ] Configure proper CORS origins
- [ ] Set up monitoring and logging
- [ ] Configure webhook with production URL
- [ ] Test error handling
- [ ] Set up backup strategy
- [ ] Review security settings

---

**🎉 Congratulations!** Your AI Notetaker is running!
