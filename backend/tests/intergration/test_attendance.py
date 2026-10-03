"""Attendance sessions and the photo face-count preview.

MinIO and the YOLO model are both faked: the model has its own test
(tests/unit/test_inference.py), so here it only has to hand back a known count.
"""

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from backend import storage
from backend.inference import Detection, Face, InvalidImageError
from backend.models.attendance import AttendanceRecord
from backend.models.classroom_teachers import ClassroomTeacher
from backend.models.classrooms import Classroom
from backend.models.students import Student
from backend.models.teachers import Teacher
from backend.repository.database import get_session
from backend.routers import attendance
from backend.tests.intergration.conftest import (
    create_test_engine,
    override_current_user,
    override_current_user_as,
    stub_teacher_user,
)

FACES = [Face(10, 20, 110, 140, 0.9), Face(200, 30, 290, 150, 0.8)]


class FakeStore:
    def __init__(self, monkeypatch):
        self.objects: dict[str, bytes] = {}
        self.removed: list[str] = []
        monkeypatch.setattr(
            storage, "presigned_put_url", lambda key: f"https://o/{key}"
        )
        monkeypatch.setattr(
            storage,
            "stat_object",
            lambda key: (
                SimpleNamespace(size=len(self.objects[key]))
                if key in self.objects
                else None
            ),
        )
        monkeypatch.setattr(storage, "read_object", self.objects.get)
        monkeypatch.setattr(storage, "remove_object", self.removed.append)

        def fake_detect(image: bytes):
            if image != b"photo":
                raise InvalidImageError("Not a readable image")
            return Detection(width=400, height=300, faces=FACES)

        monkeypatch.setattr(attendance, "detect_faces", fake_detect)


@pytest.fixture
def env(monkeypatch):
    engine = create_test_engine()

    with Session(engine) as session:
        classroom = Classroom(name="Physics 101", capacity=30, location="Building A")
        other = Classroom(name="Chemistry Lab", capacity=24, location="Building B")
        teacher = Teacher(name="Alice Smith", division="Physics")
        session.add_all([classroom, other, teacher])
        session.commit()
        students = [
            Student(
                saint_name="Anna",
                first_name=name,
                last_name="Nguyen",
                division="A",
                classroom_id=room.id,
            )
            for name, room in [("An", classroom), ("Binh", classroom), ("Chi", other)]
        ]
        session.add_all(students)
        session.add(ClassroomTeacher(classroom_id=classroom.id, teacher_id=teacher.id))
        session.commit()
        ids = SimpleNamespace(
            classroom_id=classroom.id,
            other_classroom_id=other.id,
            teacher_id=teacher.id,
            students=[s.id for s in students[:2]],
            outsider=students[2].id,
        )

    def override_get_session():
        with Session(engine) as session:
            yield session

    app = FastAPI()
    override_current_user(app)
    app.include_router(attendance.router)
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        yield SimpleNamespace(
            app=app,
            client=client,
            engine=engine,
            store=FakeStore(monkeypatch),
            **vars(ids),
        )


def url(env, path="", classroom=None):
    return f"/classrooms/{classroom or env.classroom_id}/attendance{path}"


def put_photo(env, content=b"photo"):
    key = env.client.post(
        url(env, "/photo-upload-url"),
        json={"filename": "class.JPG", "content_type": "image/jpeg", "size_bytes": 5},
    ).json()["object_key"]
    env.store.objects[key] = content
    return key


def payload(env, **overrides):
    return {
        "session_date": "2026-10-03",
        "records": [
            {"student_id": env.students[0], "present": True},
            {"student_id": env.students[1], "present": False},
        ],
    } | overrides


def test_photo_upload_url_is_namespaced_by_classroom_and_images_only(env):
    response = env.client.post(
        url(env, "/photo-upload-url"),
        json={"filename": "class.JPG", "content_type": "image/jpeg", "size_bytes": 5},
    )
    assert response.status_code == 200
    assert response.json()["object_key"].startswith(f"attendance/{env.classroom_id}/")
    assert response.json()["object_key"].endswith(".jpg")

    pdf = env.client.post(
        url(env, "/photo-upload-url"),
        json={"filename": "a.pdf", "content_type": "application/pdf", "size_bytes": 5},
    )
    assert pdf.status_code == 422


def test_detect_returns_count_and_boxes(env):
    response = env.client.post(url(env, "/detect"), json={"object_key": put_photo(env)})

    assert response.status_code == 200
    body = response.json()
    assert (body["count"], body["width"], body["height"]) == (2, 400, 300)
    assert body["faces"][0] == {
        "x1": 10,
        "y1": 20,
        "x2": 110,
        "y2": 140,
        "confidence": 0.9,
    }


@pytest.mark.parametrize(
    ("make_key", "status"),
    [
        (lambda env: f"attendance/{env.other_classroom_id}/x.jpg", 400),
        (lambda env: f"classrooms/{env.classroom_id}/x.jpg", 400),
        (lambda env: f"attendance/{env.classroom_id}/missing.jpg", 400),
        (lambda env: put_photo(env, b"not an image"), 415),
    ],
)
def test_detect_rejects_bad_photos(env, make_key, status):
    response = env.client.post(url(env, "/detect"), json={"object_key": make_key(env)})
    assert response.status_code == status


def test_create_session_stores_records_and_counts_faces(env):
    response = env.client.post(
        url(env), json=payload(env, photo_object_key=put_photo(env))
    )

    assert response.status_code == 201
    body = response.json()
    assert (body["present_count"], body["total_count"], body["detected_count"]) == (
        1,
        2,
        2,
    )
    assert body["records"] == [
        {"student_id": env.students[0], "present": True},
        {"student_id": env.students[1], "present": False},
    ]
    assert env.client.get(url(env)).json()["items"] == [body]


def test_create_session_without_a_photo_has_no_detected_count(env):
    response = env.client.post(url(env), json=payload(env))

    assert response.status_code == 201
    assert response.json()["detected_count"] is None


def test_create_session_rejects_a_student_from_another_classroom(env):
    records = [{"student_id": env.outsider, "present": True}]

    response = env.client.post(url(env), json=payload(env, records=records))

    assert response.status_code == 400


def test_create_session_rejects_a_student_listed_twice(env):
    records = [{"student_id": env.students[0], "present": p} for p in (True, False)]

    response = env.client.post(url(env), json=payload(env, records=records))

    assert response.status_code == 422


def test_list_is_newest_first_and_scoped_to_the_classroom(env):
    for day in ("2026-09-26", "2026-10-03"):
        env.client.post(url(env), json=payload(env, session_date=day))

    body = env.client.get(url(env)).json()

    assert body["total"] == 2
    assert [item["session_date"] for item in body["items"]] == [
        "2026-10-03",
        "2026-09-26",
    ]
    assert (
        env.client.get(url(env, classroom=env.other_classroom_id)).json()["total"] == 0
    )


def test_delete_removes_session_records_and_photo(env):
    key = put_photo(env)
    session_id = env.client.post(
        url(env), json=payload(env, photo_object_key=key)
    ).json()["id"]

    assert env.client.delete(url(env, f"/{session_id}")).status_code == 204

    assert env.client.get(url(env)).json()["total"] == 0
    assert env.store.removed == [key]
    with Session(env.engine) as session:
        assert session.exec(select(AttendanceRecord)).all() == []


def test_session_of_another_classroom_is_not_found(env):
    session_id = env.client.post(url(env), json=payload(env)).json()["id"]

    other = url(env, f"/{session_id}", classroom=env.other_classroom_id)

    assert env.client.delete(other).status_code == 404


def test_teacher_cannot_touch_a_classroom_they_are_not_assigned_to(env):
    override_current_user_as(env.app, stub_teacher_user(env.teacher_id))

    assert env.client.get(url(env)).status_code == 200
    assert env.client.get(url(env, classroom=env.other_classroom_id)).status_code == 403
    assert (
        env.client.post(
            url(env, classroom=env.other_classroom_id), json=payload(env)
        ).status_code
        == 403
    )


def test_unknown_classroom_is_not_found(env):
    assert env.client.get(url(env, classroom=999)).status_code == 404
