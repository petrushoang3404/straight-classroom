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
