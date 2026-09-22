import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session

from backend.models.classrooms import Classroom
from backend.models.students import Student
from backend.models.teachers import Teacher
from backend.repository.database import get_session
from backend.routers.classrooms import router
from backend.routers.teachers import router as teachers_router
from backend.tests.intergration.conftest import (
    create_test_engine,
    override_current_user,
)


@pytest.fixture
def client():
    engine = create_test_engine()

    with Session(engine) as session:
        session.add_all(
            [
                Classroom(name="Physics 101", capacity=30, location="Building A"),
                Classroom(name="Chemistry Lab", capacity=24, location="Building B"),
                Classroom(name="History Room", capacity=40, location="Building C"),
            ]
        )
        session.commit()

    def override_get_session():
        with Session(engine) as session:
            yield session

    app = FastAPI()
    override_current_user(app)
    app.include_router(router)
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_get_classrooms_returns_paginated_classrooms(client):
    response = client.get("/classrooms/", params={"limit": 2, "offset": 1})

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": 2,
                "name": "Chemistry Lab",
                "capacity": 24,
                "location": "Building B",
                "teachers": [],
            },
            {
                "id": 3,
                "name": "History Room",
                "capacity": 40,
                "location": "Building C",
                "teachers": [],
            },
        ],
        "limit": 2,
        "offset": 1,
        "total": 3,
    }


def test_get_classrooms_uses_default_pagination(client):
    response = client.get("/classrooms/")

    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 20
    assert data["offset"] == 0
    assert data["total"] == 3
    assert [item["name"] for item in data["items"]] == [
        "Physics 101",
        "Chemistry Lab",
        "History Room",
    ]


@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},
        {"limit": 101},
        {"offset": -1},
    ],
)
def test_get_classrooms_validates_pagination_params(client, params):
    response = client.get("/classrooms/", params=params)

    assert response.status_code == 422


def test_create_classroom_returns_created_classroom(client):
    payload = {
        "name": "Math Studio",
        "capacity": 35,
        "location": "Building D",
    }

    response = client.post("/classrooms/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data == {
        "id": 4,
        "teachers": [],
        **payload,
    }

    get_response = client.get("/classrooms/")
    assert get_response.status_code == 200
    classrooms = get_response.json()
    assert classrooms["total"] == 4
    assert classrooms["items"][-1] == data


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "", "capacity": 35, "location": "Building D"},
        {"name": "Math Studio", "capacity": 0, "location": "Building D"},
        {"name": "Math Studio", "capacity": 35, "location": ""},
    ],
)
def test_create_classroom_validates_payload(client, payload):
    response = client.post("/classrooms/", json=payload)

    assert response.status_code == 422


def test_get_classroom_by_id_returns_classroom(client):
    response = client.get("/classrooms/2")

    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "name": "Chemistry Lab",
        "capacity": 24,
        "location": "Building B",
        "teachers": [],
    }


def test_get_classroom_by_id_returns_404_when_missing(client):
    response = client.get("/classrooms/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Classroom not found"}


def test_get_classroom_by_id_validates_id(client):
    response = client.get("/classrooms/0")

    assert response.status_code == 422


def test_update_classroom_updates_provided_fields(client):
    payload = {
        "capacity": 28,
        "location": "Building B - Renovated",
    }

    response = client.patch("/classrooms/2", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "name": "Chemistry Lab",
        "capacity": 28,
        "location": "Building B - Renovated",
        "teachers": [],
    }

    get_response = client.get("/classrooms/2")
    assert get_response.status_code == 200
    assert get_response.json() == response.json()


def test_update_classroom_returns_404_when_missing(client):
    response = client.patch("/classrooms/999", json={"name": "Unknown Room"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Classroom not found"}


def test_update_classroom_rejects_empty_payload(client):
    response = client.patch("/classrooms/2", json={})

    assert response.status_code == 400
    assert response.json() == {"detail": "At least one field must be provided"}


@pytest.mark.parametrize(
    "payload",
    [
        {"name": ""},
        {"capacity": 0},
        {"location": ""},
    ],
)
def test_update_classroom_validates_payload(client, payload):
    response = client.patch("/classrooms/2", json=payload)

    assert response.status_code == 422


def test_delete_classroom_deletes_classroom(client):
    response = client.delete("/classrooms/3")

    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get("/classrooms/3")
    assert get_response.status_code == 404


def test_delete_classroom_returns_404_when_missing(client):
    response = client.delete("/classrooms/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Classroom not found"}


@pytest.fixture
def client_with_relations():
    engine = create_test_engine()

    with Session(engine) as session:
        classroom = Classroom(name="Physics 101", capacity=30, location="Building A")
        other_classroom = Classroom(
            name="Chemistry Lab", capacity=24, location="Building B"
        )
        teacher = Teacher(name="Alice Smith", subject="Physics")
        other_teacher = Teacher(name="Bob Jones", subject="Chemistry")
        session.add_all([classroom, other_classroom, teacher, other_teacher])
        session.commit()
        session.refresh(classroom)

        session.add(
            Student(
                saint_name="Peter",
                first_name="John",
                last_name="Doe",
                division="A",
                classroom_id=classroom.id,
            )
        )
        session.commit()

    def override_get_session():
        with Session(engine) as session:
            yield session

    app = FastAPI()
    override_current_user(app)
    app.include_router(router)
    app.include_router(teachers_router)
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_delete_classroom_with_students_returns_409(client_with_relations):
    response = client_with_relations.delete("/classrooms/1")

    assert response.status_code == 409
    assert response.json() == {"detail": "Classroom has students and cannot be deleted"}

    get_response = client_with_relations.get("/classrooms/1")
    assert get_response.status_code == 200


def test_delete_classroom_without_students_succeeds(client_with_relations):
    response = client_with_relations.delete("/classrooms/2")

    assert response.status_code == 204


def test_get_classroom_students_returns_its_students(client_with_relations):
    response = client_with_relations.get("/classrooms/1/students")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["first_name"] == "John"


def test_get_classroom_students_returns_404_when_classroom_missing(
    client_with_relations,
):
    response = client_with_relations.get("/classrooms/999/students")

    assert response.status_code == 404


def test_assign_teacher_adds_teacher_to_classroom(client_with_relations):
    response = client_with_relations.post(
        "/classrooms/1/teachers", json={"teacher_id": 1}
    )

    assert response.status_code == 201
    data = response.json()
    assert [teacher["id"] for teacher in data["teachers"]] == [1]

    teachers_response = client_with_relations.get("/classrooms/1/teachers")
    assert teachers_response.status_code == 200
    assert [teacher["id"] for teacher in teachers_response.json()] == [1]


def test_assign_teacher_returns_404_when_classroom_missing(client_with_relations):
    response = client_with_relations.post(
        "/classrooms/999/teachers", json={"teacher_id": 1}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Classroom not found"}


def test_assign_teacher_returns_404_when_teacher_missing(client_with_relations):
    response = client_with_relations.post(
        "/classrooms/1/teachers", json={"teacher_id": 999}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Teacher not found"}


def test_assign_teacher_twice_returns_409(client_with_relations):
    client_with_relations.post("/classrooms/1/teachers", json={"teacher_id": 1})

    response = client_with_relations.post(
        "/classrooms/1/teachers", json={"teacher_id": 1}
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Teacher is already assigned to this classroom"
    }


def test_unassign_teacher_removes_assignment(client_with_relations):
    client_with_relations.post("/classrooms/1/teachers", json={"teacher_id": 1})

    response = client_with_relations.delete("/classrooms/1/teachers/1")

    assert response.status_code == 204
    teachers_response = client_with_relations.get("/classrooms/1/teachers")
    assert teachers_response.json() == []


def test_unassign_teacher_returns_404_when_not_assigned(client_with_relations):
    response = client_with_relations.delete("/classrooms/1/teachers/1")

    assert response.status_code == 404


def test_deleting_teacher_removes_the_assignment_but_keeps_classroom(
    client_with_relations,
):
    client_with_relations.post("/classrooms/1/teachers", json={"teacher_id": 1})

    delete_response = client_with_relations.delete("/teachers/1")

    assert delete_response.status_code == 204

    classroom_response = client_with_relations.get("/classrooms/1")
    assert classroom_response.status_code == 200
    assert classroom_response.json()["teachers"] == []
