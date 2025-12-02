from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.api import users, meetings, notes, meeting_bots, calendar, webhooks
from src.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Notetaker API",
    description="Backend API for AI-powered meeting transcription and note-taking",
    version="1.0.0"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(meetings.router, prefix="/api/meetings", tags=["meetings"])
app.include_router(notes.router, prefix="/api/notes", tags=["notes"])
app.include_router(meeting_bots.router, prefix="/api", tags=["bots"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
app.include_router(webhooks.router, prefix="/api", tags=["webhooks"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to the AI Notetaker API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Database initialization
@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI Notetaker API...")
    logger.info("API documentation available at /docs")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down AI Notetaker API...")