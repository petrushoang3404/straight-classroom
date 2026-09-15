from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from backend.models.classrooms import Classroom
from backend.repository.database import get_session
from backend.routers.classrooms import router


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

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
            },
            {
                "id": 3,
                "name": "History Room",
                "capacity": 40,
                "location": "Building C",
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
