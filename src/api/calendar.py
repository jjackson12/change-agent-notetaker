from fastapi import APIRouter, Depends
from typing import List
from src.schemas.calendar import CalendarCreate, CalendarResponse
from src.services.calendar_service import CalendarService

router = APIRouter()
calendar_service = CalendarService()

@router.post("/calendars/", response_model=CalendarResponse)
async def create_calendar(calendar: CalendarCreate):
    return await calendar_service.create_calendar(calendar)

@router.get("/calendars/", response_model=List[CalendarResponse])
async def get_calendars(user_id: int):
    return await calendar_service.get_calendars(user_id)

@router.get("/calendars/{calendar_id}", response_model=CalendarResponse)
async def get_calendar(calendar_id: int):
    return await calendar_service.get_calendar(calendar_id)

@router.delete("/calendars/{calendar_id}")
async def delete_calendar(calendar_id: int):
    await calendar_service.delete_calendar(calendar_id)
    return {"message": "Calendar deleted successfully."}