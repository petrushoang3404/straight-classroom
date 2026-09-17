import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from backend.models.classrooms import Classroom
from backend.models.students import Student
from backend.repository.database import get_session
from backend.routers.students import router


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(Classroom(name="Physics 101", capacity=30, location="Building A"))
        session.commit()
        session.add_all(
            [
                Student(
                    saint_name="Peter",
                    first_name="John",
                    last_name="Doe",
                    division="A",
                    classroom_id=1,
                ),
                Student(
                    saint_name="Paul",
                    first_name="Jane",
                    last_name="Doe",
                    division="A",
                    classroom_id=1,
                ),
                Student(
                    saint_name="Mary",
                    first_name="Anna",
                    last_name="Smith",
                    division="B",
                    classroom_id=1,
                ),
            ]
        )
        session.commit()

    def override_get_session():
        with Session(engine) as session:
            yield session

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_get_students_returns_paginated_students(client):
    response = client.get("/students/", params={"limit": 2, "offset": 1})

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": 2,
                "saint_name": "Paul",
                "first_name": "Jane",
                "last_name": "Doe",
                "division": "A",
                "classroom_id": 1,
            },
            {
                "id": 3,
                "saint_name": "Mary",
                "first_name": "Anna",
                "last_name": "Smith",
                "division": "B",
                "classroom_id": 1,
            },
        ],
        "limit": 2,
        "offset": 1,
        "total": 3,
    }


def test_get_students_uses_default_pagination(client):
    response = client.get("/students/")

    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 20
    assert data["offset"] == 0
    assert data["total"] == 3
    assert [item["first_name"] for item in data["items"]] == ["John", "Jane", "Anna"]


def test_get_students_filters_by_name(client):
    response = client.get("/students/", params={"student_name": "Doe"})

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert [item["first_name"] for item in data["items"]] == ["John", "Jane"]


@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},
        {"limit": 101},
        {"offset": -1},
        {"student_name": ""},
    ],
)
def test_get_students_validates_query_params(client, params):
    response = client.get("/students/", params=params)

    assert response.status_code == 422


def test_create_student_returns_created_student(client):
    payload = {
        "saint_name": "Joseph",
        "first_name": "David",
        "last_name": "Wilson",
        "division": "C",
        "classroom_id": 1,
    }

    response = client.post("/students/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data == {"id": 4, **payload}

    get_response = client.get("/students/")
    assert get_response.status_code == 200
    students = get_response.json()
    assert students["total"] == 4
    assert students["items"][-1] == data


@pytest.mark.parametrize(
    "payload",
    [
        {"saint_name": "", "first_name": "David", "last_name": "Wilson", "division": "C", "classroom_id": 1},
        {"saint_name": "Joseph", "first_name": "", "last_name": "Wilson", "division": "C", "classroom_id": 1},
        {"saint_name": "Joseph", "first_name": "David", "last_name": "", "division": "C", "classroom_id": 1},
        {"saint_name": "Joseph", "first_name": "David", "last_name": "Wilson", "division": "", "classroom_id": 1},
        {"saint_name": "Joseph", "first_name": "David", "last_name": "Wilson", "division": "C", "classroom_id": 0},
    ],
)
def test_create_student_validates_payload(client, payload):
    response = client.post("/students/", json=payload)

    assert response.status_code == 422


def test_get_student_by_id_returns_student(client):
    response = client.get("/students/2")

    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "saint_name": "Paul",
        "first_name": "Jane",
        "last_name": "Doe",
        "division": "A",
        "classroom_id": 1,
    }


def test_get_student_by_id_returns_404_when_missing(client):
    response = client.get("/students/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Student not found"}


def test_get_student_by_id_validates_id(client):
    response = client.get("/students/0")

    assert response.status_code == 422


def test_update_student_updates_provided_fields(client):
    payload = {"division": "D"}

    response = client.patch("/students/2", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "saint_name": "Paul",
        "first_name": "Jane",
        "last_name": "Doe",
        "division": "D",
        "classroom_id": 1,
    }

    get_response = client.get("/students/2")
    assert get_response.status_code == 200
    assert get_response.json() == response.json()


def test_update_student_returns_404_when_missing(client):
    response = client.patch("/students/999", json={"division": "D"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Student not found"}


def test_update_student_rejects_empty_payload(client):
    response = client.patch("/students/2", json={})

    assert response.status_code == 400
    assert response.json() == {"detail": "No updates provided"}


@pytest.mark.parametrize(
    "payload",
    [
        {"saint_name": ""},
        {"first_name": ""},
        {"last_name": ""},
        {"division": ""},
        {"classroom_id": 0},
    ],
)
def test_update_student_validates_payload(client, payload):
    response = client.patch("/students/2", json=payload)

    assert response.status_code == 422


def test_delete_student_deletes_student(client):
    response = client.delete("/students/2")

    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get("/students/2")
    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "Student not found"}


def test_delete_student_returns_404_when_missing(client):
    response = client.delete("/students/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Student not found"}


def test_delete_student_validates_id(client):
    response = client.delete("/students/0")

    assert response.status_code == 422
