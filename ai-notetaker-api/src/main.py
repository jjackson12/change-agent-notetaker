from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import users, meetings, notes, meeting_bots, calendar
from src.config import settings

app = FastAPI()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(meetings.router, prefix="/meetings", tags=["meetings"])
app.include_router(notes.router, prefix="/notes", tags=["notes"])
app.include_router(meeting_bots.router, prefix="/meeting_bots", tags=["meeting_bots"])
app.include_router(calendar.router, prefix="/calendar", tags=["calendar"])

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Notetaker API"}