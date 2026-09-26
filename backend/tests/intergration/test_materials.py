"""The presigned upload/download handshake for classroom materials.

MinIO is replaced by FakeObjectStore so these stay hermetic like the rest of
the suite. The fake matters more than a usual stub: the router deliberately
reads size and content type back from storage instead of trusting the request
body, so the fake has to be able to hold something different from what the
client claimed.
"""

from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from backend import storage
from backend.models.classroom_teachers import ClassroomTeacher
from backend.models.classrooms import Classroom
from backend.models.materials import Material
from backend.models.teachers import Teacher
from backend.repository.database import get_session
from backend.routers.materials import router
from backend.tests.intergration.conftest import (
    create_test_engine,
    override_current_user,
    override_current_user_as,
    stub_teacher_user,
)

PDF = "application/pdf"
PNG = "image/png"
MAX_FILE_SIZE = 50 * 1024 * 1024


class FakeObjectStore:
    """An in-memory stand-in for MinIO.

    `put` is what the browser does out-of-band against the presigned URL, so
    tests call it directly between reserving a slot and registering the upload.
    """

    def __init__(self):
        self.objects: dict[str, SimpleNamespace] = {}
        self.removed: list[str] = []

    def put(self, key: str, *, size: int = 1024, content_type: str = PDF):
        self.objects[key] = SimpleNamespace(size=size, content_type=content_type)

    def install(self, monkeypatch):
        # build_object_key and classroom_prefix are pure, so the real ones run.
        monkeypatch.setattr(
            storage, "presigned_put_url", lambda key: f"https://objects.test/{key}?put"
        )
        monkeypatch.setattr(
            storage,
            "presigned_get_url",
            lambda key, *, filename: f"https://objects.test/{key}?get&as={filename}",
        )
        monkeypatch.setattr(storage, "stat_object", self.objects.get)
        monkeypatch.setattr(storage, "remove_object", self._remove)
        return self

    def _remove(self, key: str):
        self.removed.append(key)
        self.objects.pop(key, None)


@pytest.fixture
def env(monkeypatch):
    engine = create_test_engine()

    with Session(engine) as session:
        classroom = Classroom(name="Physics 101", capacity=30, location="Building A")
        other = Classroom(name="Chemistry Lab", capacity=24, location="Building B")
        teacher = Teacher(name="Alice Smith", division="Physics")
        session.add_all([classroom, other, teacher])
        session.commit()
        session.refresh(classroom)
        session.refresh(other)
        session.refresh(teacher)
        classroom_id, other_id, teacher_id = classroom.id, other.id, teacher.id
        session.add(ClassroomTeacher(classroom_id=classroom_id, teacher_id=teacher_id))
        session.commit()

    def override_get_session():
        with Session(engine) as session:
            yield session

    app = FastAPI()
    override_current_user(app)
    app.include_router(router)
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        yield SimpleNamespace(
            app=app,
            client=client,
            engine=engine,
            store=FakeObjectStore().install(monkeypatch),
            classroom_id=classroom_id,
            other_classroom_id=other_id,
            teacher_id=teacher_id,
        )

    app.dependency_overrides.clear()


def reserve(env, *, filename="lesson.pdf", content_type=PDF, size=1024, classroom=None):
    classroom_id = classroom or env.classroom_id
    return env.client.post(
        f"/classrooms/{classroom_id}/materials/upload-url",
        json={
            "filename": filename,
            "content_type": content_type,
            "size_bytes": size,
        },
    )


def upload(
    env,
    *,
    filename="lesson.pdf",
    content_type=PDF,
    size=1024,
    stored_size=None,
    stored_type=None,
    description=None,
    classroom=None,
):
    """The full three-step handshake a browser performs.

    `stored_size`/`stored_type` let a test make what actually landed in storage
    differ from what the client declared up front.
    """
    classroom_id = classroom or env.classroom_id
    key = reserve(
        env,
        filename=filename,
        content_type=content_type,
        size=size,
        classroom=classroom_id,
    ).json()["object_key"]
    env.store.put(
        key,
        size=stored_size if stored_size is not None else size,
        content_type=stored_type or content_type,
    )
    response = env.client.post(
        f"/classrooms/{classroom_id}/materials",
        json={
            "object_key": key,
            "filename": filename,
            "description": description,
        },
    )
    return key, response


# --- reserving an upload slot -------------------------------------------


def test_upload_url_returns_a_key_scoped_to_the_classroom(env):
    response = reserve(env, filename="Ke hoach.pdf")

    assert response.status_code == 200
    body = response.json()
    assert body["object_key"].startswith(f"classrooms/{env.classroom_id}/")
    assert body["object_key"].endswith(".pdf")
    assert body["upload_url"] == f"https://objects.test/{body['object_key']}?put"
    assert body["expires_in_seconds"] == 900


def test_upload_url_keys_are_unique_per_request(env):
    first = reserve(env).json()["object_key"]
    second = reserve(env).json()["object_key"]

    assert first != second


@pytest.mark.parametrize("content_type", [PDF, "image/jpeg", PNG])
def test_upload_url_accepts_supported_types(env, content_type):
    assert reserve(env, content_type=content_type).status_code == 200


@pytest.mark.parametrize(
    "content_type",
    [
        "application/msword",
        "application/vnd.ms-excel",
        "text/plain",
        "image/gif",
        "application/x-msdownload",
        "",
    ],
)
def test_upload_url_rejects_unsupported_types(env, content_type):
    assert reserve(env, content_type=content_type).status_code == 422


@pytest.mark.parametrize("size", [MAX_FILE_SIZE + 1, 0, -1])
def test_upload_url_rejects_invalid_sizes(env, size):
    assert reserve(env, size=size).status_code == 422


def test_upload_url_accepts_the_size_limit_exactly(env):
    assert reserve(env, size=MAX_FILE_SIZE).status_code == 200


def test_upload_url_strips_directories_from_the_filename(env):
    response = reserve(env, filename="../../../etc/passwd.pdf")

    key = response.json()["object_key"]
    assert key.startswith(f"classrooms/{env.classroom_id}/")
    assert ".." not in key


# --- registering the finished upload ------------------------------------


def test_register_stores_the_material(env):
    key, response = upload(env, filename="Bai doc.pdf", size=2048, description="Scan")

    assert response.status_code == 201
    body = response.json()
    assert body == {
        "id": body["id"],
        "classroom_id": env.classroom_id,
        "description": "Scan",
        "filename": "Bai doc.pdf",
        "content_type": PDF,
        "size_bytes": 2048,
        "created_at": body["created_at"],
    }

    with Session(env.engine) as session:
        material = session.get(Material, body["id"])
        assert material.object_key == key


def test_register_trusts_storage_over_the_client(env):
    """The client declared 1 KB of PDF; storage holds 9 KB of PNG."""
    _, response = upload(
        env,
        filename="claimed.pdf",
        content_type=PDF,
        size=1024,
        stored_size=9000,
        stored_type=PNG,
    )

    assert response.status_code == 201
    assert response.json()["size_bytes"] == 9000
    assert response.json()["content_type"] == PNG


def test_register_defaults_description_to_null(env):
    _, response = upload(env)

    assert response.json()["description"] is None


def test_register_rejects_a_key_from_another_classroom(env):
    key = reserve(env, classroom=env.other_classroom_id).json()["object_key"]
    env.store.put(key)

    response = env.client.post(
        f"/classrooms/{env.classroom_id}/materials",
        json={"object_key": key, "filename": "lesson.pdf"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Object key does not belong to this classroom"


def test_register_rejects_an_unfinished_upload(env):
    key = reserve(env).json()["object_key"]  # never put into storage

    response = env.client.post(
        f"/classrooms/{env.classroom_id}/materials",
        json={"object_key": key, "filename": "lesson.pdf"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Upload was not completed"


def test_register_rejects_and_removes_an_oversized_object(env):
    key, response = upload(env, size=1024, stored_size=MAX_FILE_SIZE + 1)

    assert response.status_code == 413
    assert key in env.store.removed
    assert key not in env.store.objects
    assert list_materials(env)["total"] == 0


def test_register_rejects_and_removes_an_unsupported_object(env):
    key, response = upload(env, content_type=PDF, stored_type="application/zip")

    assert response.status_code == 415
    assert key in env.store.removed
    assert list_materials(env)["total"] == 0


# --- listing -------------------------------------------------------------


def list_materials(env, classroom=None, **params):
    classroom_id = classroom or env.classroom_id
    return env.client.get(f"/classrooms/{classroom_id}/materials", params=params).json()


def test_list_is_empty_for_a_new_classroom(env):
    response = env.client.get(f"/classrooms/{env.classroom_id}/materials")

    assert response.status_code == 200
    assert response.json() == {"items": [], "limit": 20, "offset": 0, "total": 0}


def test_list_returns_newest_first(env):
    for name in ("first.pdf", "second.pdf", "third.pdf"):
        upload(env, filename=name)

    items = list_materials(env)["items"]

    assert [item["filename"] for item in items] == [
        "third.pdf",
        "second.pdf",
        "first.pdf",
    ]


def test_list_breaks_created_at_ties_by_id(env):
    """created_at has microsecond resolution and two writes can share one, so
    the newest-first order has to stay total."""
    minted = datetime(2026, 9, 26, 8, 0, tzinfo=UTC)
    with Session(env.engine) as session:
        session.add_all(
            [
                Material(
                    classroom_id=env.classroom_id,
                    filename=f"tie-{n}.pdf",
                    content_type=PDF,
                    size_bytes=10,
                    object_key=f"classrooms/{env.classroom_id}/tie-{n}.pdf",
                    created_at=minted,
                )
                for n in range(3)
            ]
        )
        session.commit()

    items = list_materials(env)["items"]

    assert [i["filename"] for i in items] == ["tie-2.pdf", "tie-1.pdf", "tie-0.pdf"]


def test_list_is_scoped_to_one_classroom(env):
    upload(env, filename="mine.pdf")
    upload(env, filename="theirs.pdf", classroom=env.other_classroom_id)

    assert [i["filename"] for i in list_materials(env)["items"]] == ["mine.pdf"]
    other = list_materials(env, classroom=env.other_classroom_id)
    assert [i["filename"] for i in other["items"]] == ["theirs.pdf"]


def test_list_paginates(env):
    for name in ("a.pdf", "b.pdf", "c.pdf"):
        upload(env, filename=name)

    page = list_materials(env, limit=2, offset=1)

    assert page["total"] == 3
    assert page["limit"] == 2
    assert page["offset"] == 1
    assert [i["filename"] for i in page["items"]] == ["b.pdf", "a.pdf"]


def test_list_404s_for_an_unknown_classroom(env):
    response = env.client.get("/classrooms/9999/materials")

    assert response.status_code == 404
    assert response.json()["detail"] == "Classroom not found"


# --- downloading ---------------------------------------------------------


def test_download_url_preserves_the_original_filename(env):
    key, created = upload(env, filename="Giay chung nhan.pdf")

    response = env.client.get(
        f"/classrooms/{env.classroom_id}/materials/{created.json()['id']}/download-url"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["download_url"] == (
        f"https://objects.test/{key}?get&as=Giay chung nhan.pdf"
    )
    assert body["expires_in_seconds"] == 900


def test_download_url_404s_for_an_unknown_material(env):
    response = env.client.get(
        f"/classrooms/{env.classroom_id}/materials/9999/download-url"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Material not found"


def test_download_url_404s_across_classrooms(env):
    _, created = upload(env)
    material_id = created.json()["id"]

    response = env.client.get(
        f"/classrooms/{env.other_classroom_id}/materials/{material_id}/download-url"
    )

    assert response.status_code == 404


# --- deleting ------------------------------------------------------------


def test_delete_removes_the_row_and_the_object(env):
    key, created = upload(env)
    material_id = created.json()["id"]

    response = env.client.delete(
        f"/classrooms/{env.classroom_id}/materials/{material_id}"
    )

    assert response.status_code == 204
    assert key in env.store.removed
    assert key not in env.store.objects
    assert list_materials(env)["total"] == 0
    with Session(env.engine) as session:
        assert session.get(Material, material_id) is None


def test_delete_404s_for_an_unknown_material(env):
    response = env.client.delete(f"/classrooms/{env.classroom_id}/materials/9999")

    assert response.status_code == 404


def test_delete_404s_across_classrooms_and_keeps_the_object(env):
    key, created = upload(env)
    material_id = created.json()["id"]

    response = env.client.delete(
        f"/classrooms/{env.other_classroom_id}/materials/{material_id}"
    )

    assert response.status_code == 404
    assert key in env.store.objects
    assert list_materials(env)["total"] == 1


def test_deleting_a_classroom_cascades_to_its_materials(env):
    upload(env)

    with Session(env.engine) as session:
        session.delete(session.get(Classroom, env.classroom_id))
        session.commit()
        assert session.exec(select(Material)).all() == []


# --- authorization -------------------------------------------------------


@pytest.fixture
def unassigned_teacher(env):
    """A teacher with no ClassroomTeacher row for env.classroom_id."""
    override_current_user_as(env.app, stub_teacher_user(teacher_id=999))
    return env


def test_assigned_teacher_may_use_the_flow(env):
    override_current_user_as(env.app, stub_teacher_user(env.teacher_id))

    _, created = upload(env)

    assert created.status_code == 201
    assert (
        env.client.get(f"/classrooms/{env.classroom_id}/materials").status_code == 200
    )


def test_unassigned_teacher_cannot_list(unassigned_teacher):
    env = unassigned_teacher
    assert (
        env.client.get(f"/classrooms/{env.classroom_id}/materials").status_code == 403
    )


def test_unassigned_teacher_cannot_reserve_an_upload(unassigned_teacher):
    assert reserve(unassigned_teacher).status_code == 403


def test_unassigned_teacher_cannot_register(unassigned_teacher):
    env = unassigned_teacher
    response = env.client.post(
        f"/classrooms/{env.classroom_id}/materials",
        json={"object_key": "classrooms/1/x.pdf", "filename": "x.pdf"},
    )

    assert response.status_code == 403


def test_unassigned_teacher_cannot_download_or_delete(unassigned_teacher):
    env = unassigned_teacher
    assert (
        env.client.get(
            f"/classrooms/{env.classroom_id}/materials/1/download-url"
        ).status_code
        == 403
    )
    assert (
        env.client.delete(f"/classrooms/{env.classroom_id}/materials/1").status_code
        == 403
    )
