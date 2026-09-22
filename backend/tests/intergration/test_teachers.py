import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session

from backend.models.classroom_teachers import ClassroomTeacher
from backend.models.classrooms import Classroom
from backend.models.teachers import Teacher
from backend.repository.database import get_session
from backend.routers.teachers import router
from backend.tests.intergration.conftest import create_test_engine


@pytest.fixture
def client():
    engine = create_test_engine()

    with Session(engine) as session:
        session.add_all(
            [
                Teacher(name="Alice Smith", subject="Physics"),
                Teacher(name="Bob Jones", subject="Chemistry"),
                Teacher(name="Carol Brown", subject="History"),
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


def test_get_teachers_returns_paginated_teachers(client):
    response = client.get("/teachers/", params={"limit": 2, "offset": 1})

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {"id": 2, "name": "Bob Jones", "subject": "Chemistry", "classrooms": []},
            {
                "id": 3,
                "name": "Carol Brown",
                "subject": "History",
                "classrooms": [],
            },
        ],
        "limit": 2,
        "offset": 1,
        "total": 3,
    }


def test_get_teachers_uses_default_pagination(client):
    response = client.get("/teachers/")

    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 20
    assert data["offset"] == 0
    assert data["total"] == 3
    assert [item["name"] for item in data["items"]] == [
        "Alice Smith",
        "Bob Jones",
        "Carol Brown",
    ]


def test_get_teachers_filters_by_name(client):
    response = client.get("/teachers/", params={"teacher_name": "Bob Jones"})

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {"id": 2, "name": "Bob Jones", "subject": "Chemistry", "classrooms": []}
        ],
        "limit": 20,
        "offset": 0,
        "total": 1,
    }


@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},
        {"limit": 101},
        {"offset": -1},
        {"teacher_name": ""},
    ],
)
def test_get_teachers_validates_query_params(client, params):
    response = client.get("/teachers/", params=params)

    assert response.status_code == 422


def test_create_teacher_returns_created_teacher(client):
    payload = {"name": "David Wilson", "subject": "Mathematics"}

    response = client.post("/teachers/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data == {"id": 4, "classrooms": [], **payload}

    get_response = client.get("/teachers/")
    assert get_response.status_code == 200
    teachers = get_response.json()
    assert teachers["total"] == 4
    assert teachers["items"][-1] == data


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "", "subject": "Mathematics"},
        {"name": "David Wilson", "subject": ""},
    ],
)
def test_create_teacher_validates_payload(client, payload):
    response = client.post("/teachers/", json=payload)

    assert response.status_code == 422


def test_get_teacher_by_id_returns_teacher(client):
    response = client.get("/teachers/2")

    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "name": "Bob Jones",
        "subject": "Chemistry",
        "classrooms": [],
    }


def test_get_teacher_by_id_returns_404_when_missing(client):
    response = client.get("/teachers/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Teacher not found"}


def test_get_teacher_by_id_validates_id(client):
    response = client.get("/teachers/0")

    assert response.status_code == 422


def test_update_teacher_updates_provided_fields(client):
    payload = {"subject": "Advanced Chemistry"}

    response = client.patch("/teachers/2", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "name": "Bob Jones",
        "subject": "Advanced Chemistry",
        "classrooms": [],
    }

    get_response = client.get("/teachers/2")
    assert get_response.status_code == 200
    assert get_response.json() == response.json()


def test_update_teacher_returns_404_when_missing(client):
    response = client.patch("/teachers/999", json={"name": "Unknown Teacher"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Teacher not found"}


def test_update_teacher_rejects_empty_payload(client):
    response = client.patch("/teachers/2", json={})

    assert response.status_code == 400
    assert response.json() == {"detail": "No updates provided"}


@pytest.mark.parametrize(
    "payload",
    [
        {"name": ""},
        {"subject": ""},
    ],
)
def test_update_teacher_validates_payload(client, payload):
    response = client.patch("/teachers/2", json=payload)

    assert response.status_code == 422


def test_delete_teacher_deletes_teacher(client):
    response = client.delete("/teachers/2")

    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get("/teachers/2")
    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "Teacher not found"}


def test_delete_teacher_returns_404_when_missing(client):
    response = client.delete("/teachers/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Teacher not found"}


def test_delete_teacher_validates_id(client):
    response = client.delete("/teachers/0")

    assert response.status_code == 422


def test_get_teacher_classrooms_returns_404_when_missing(client):
    response = client.get("/teachers/999/classrooms")

    assert response.status_code == 404
    assert response.json() == {"detail": "Teacher not found"}


@pytest.fixture
def client_with_classroom():
    engine = create_test_engine()

    with Session(engine) as session:
        teacher = Teacher(name="Alice Smith", subject="Physics")
        classroom = Classroom(name="Physics 101", capacity=30, location="Building A")
        session.add_all([teacher, classroom])
        session.commit()
        session.add(ClassroomTeacher(classroom_id=classroom.id, teacher_id=teacher.id))
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


def test_get_teacher_classrooms_lists_assigned_classroom(client_with_classroom):
    response = client_with_classroom.get("/teachers/1/classrooms")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "Physics 101", "location": "Building A"}
    ]

    teacher_response = client_with_classroom.get("/teachers/1")
    assert teacher_response.json()["classrooms"] == [
        {"id": 1, "name": "Physics 101", "location": "Building A"}
    ]
