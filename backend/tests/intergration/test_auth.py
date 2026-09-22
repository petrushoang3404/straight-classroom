import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session

from backend.models.classrooms import Classroom
from backend.models.users import User
from backend.repository.database import get_session
from backend.routers.auth import router as auth_router
from backend.routers.classrooms import router as classrooms_router
from backend.security import hash_password
from backend.tests.intergration.conftest import create_test_engine


@pytest.fixture
def client():
    engine = create_test_engine()

    with Session(engine) as session:
        session.add(
            User(
                username="admin",
                hashed_password=hash_password("secret123"),
                display_name="Admin",
            )
        )
        session.add(Classroom(name="Physics 101", capacity=30, location="Building A"))
        session.commit()

    def override_get_session():
        with Session(engine) as session:
            yield session

    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(classrooms_router)
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_login_returns_token_for_valid_credentials(client):
    response = client.post(
        "/auth/login", json={"username": "admin", "password": "secret123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert data["displayName"] == "Admin"
    assert data["provider"] == "password"
    assert isinstance(data["token"], str) and data["token"]


def test_login_rejects_wrong_password(client):
    response = client.post(
        "/auth/login", json={"username": "admin", "password": "wrong"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password"}


def test_login_rejects_unknown_username(client):
    response = client.post(
        "/auth/login", json={"username": "nobody", "password": "secret123"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password"}


@pytest.mark.parametrize(
    "payload",
    [
        {"username": "", "password": "secret123"},
        {"username": "admin", "password": ""},
    ],
)
def test_login_validates_payload(client, payload):
    response = client.post("/auth/login", json=payload)

    assert response.status_code == 422


def test_protected_endpoint_rejects_missing_token(client):
    response = client.get("/classrooms/")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_protected_endpoint_rejects_invalid_token(client):
    response = client.get("/classrooms/", headers={"Authorization": "Bearer garbage"})

    assert response.status_code == 401


def test_protected_endpoint_accepts_valid_token(client):
    login_response = client.post(
        "/auth/login", json={"username": "admin", "password": "secret123"}
    )
    token = login_response.json()["token"]

    response = client.get("/classrooms/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["total"] == 1
