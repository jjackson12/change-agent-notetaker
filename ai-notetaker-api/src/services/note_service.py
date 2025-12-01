from typing import List
from sqlalchemy.orm import Session
from models.note import Note
from schemas.note import NoteCreate, NoteUpdate

class NoteService:
    def __init__(self, db: Session):
        self.db = db

    def create_note(self, note_data: NoteCreate) -> Note:
        new_note = Note(**note_data.dict())
        self.db.add(new_note)
        self.db.commit()
        self.db.refresh(new_note)
        return new_note

    def get_notes_by_meeting(self, meeting_id: int) -> List[Note]:
        return self.db.query(Note).filter(Note.meeting_id == meeting_id).all()

    def update_note(self, note_id: int, note_data: NoteUpdate) -> Note:
        note = self.db.query(Note).filter(Note.id == note_id).first()
        if note:
            for key, value in note_data.dict(exclude_unset=True).items():
                setattr(note, key, value)
            self.db.commit()
            self.db.refresh(note)
        return note

    def delete_note(self, note_id: int) -> bool:
        note = self.db.query(Note).filter(Note.id == note_id).first()
        if note:
            self.db.delete(note)
            self.db.commit()
            return True
        return False

    def summarize_notes(self, meeting_id: int) -> str:
        notes = self.get_notes_by_meeting(meeting_id)
        return "\n".join(note.content for note in notes) if notes else "No notes available."