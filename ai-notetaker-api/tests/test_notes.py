from fastapi.testclient import TestClient
from src.main import app
from src.models.note import Note
from src.schemas.note import NoteCreate, NoteUpdate

client = TestClient(app)

def test_create_note():
    note_data = {"meeting_id": 1, "content": "This is a test note."}
    response = client.post("/notes/", json=note_data)
    assert response.status_code == 201
    assert response.json()["content"] == note_data["content"]

def test_read_note():
    response = client.get("/notes/1")
    assert response.status_code == 200
    assert "content" in response.json()

def test_update_note():
    update_data = {"content": "Updated test note."}
    response = client.put("/notes/1", json=update_data)
    assert response.status_code == 200
    assert response.json()["content"] == update_data["content"]

def test_delete_note():
    response = client.delete("/notes/1")
    assert response.status_code == 204
    response = client.get("/notes/1")
    assert response.status_code == 404

def test_list_notes():
    response = client.get("/notes/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)