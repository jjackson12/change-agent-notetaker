from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.models.user import User
from src.services.user_service import UserService

app = FastAPI()
client = TestClient(app)

@app.post("/users/", response_model=User)
def create_user(user: User):
    return UserService.create_user(user)

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    return UserService.get_user(user_id)

def test_create_user():
    response = client.post("/users/", json={"name": "John Doe", "email": "john@example.com"})
    assert response.status_code == 201
    assert response.json()["name"] == "John Doe"
    assert response.json()["email"] == "john@example.com"

def test_get_user():
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_get_nonexistent_user():
    response = client.get("/users/999")
    assert response.status_code == 404