from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..schemas.note import NoteCreate, NoteRead
from ..services.note_service import NoteService
from ..dependencies import get_note_service

router = APIRouter()

@router.post("/", response_model=NoteRead)
async def create_note(note: NoteCreate, note_service: NoteService = Depends(get_note_service)):
    created_note = await note_service.create_note(note)
    if not created_note:
        raise HTTPException(status_code=400, detail="Error creating note")
    return created_note

@router.get("/{note_id}", response_model=NoteRead)
async def read_note(note_id: int, note_service: NoteService = Depends(get_note_service)):
    note = await note_service.get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.get("/", response_model=List[NoteRead])
async def read_notes(note_service: NoteService = Depends(get_note_service)):
    notes = await note_service.get_all_notes()
    return notes

@router.delete("/{note_id}", response_model=dict)
async def delete_note(note_id: int, note_service: NoteService = Depends(get_note_service)):
    success = await note_service.delete_note(note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"detail": "Note deleted successfully"}