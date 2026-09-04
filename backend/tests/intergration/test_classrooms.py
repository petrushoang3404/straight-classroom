from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_classrooms():
    response = client.get("/classrooms/")
    assert response.status_code == 200
    assert response.json() == {"message": "List of classrooms"}

def test_get_classroom():
    response = client.get("/classrooms/1")
    assert response.status_code == 200
    assert response.json() == {"message": "Details for classroom 1"}

def test_create_classroom():
    response = client.post("/classrooms/", json={"name": "Test Classroom", "capacity": 30, "location": "Building A"})
    assert response.status_code == 200
    assert response.json() == {"message": "Classroom Test Classroom created successfully"}

