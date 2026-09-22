from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session

from backend.models.classroom_teachers import ClassroomTeacher
from backend.models.classrooms import Classroom
from backend.models.students import Student
from backend.models.teachers import Teacher
from backend.repository.database import get_session
from backend.routers.classrooms import router as classrooms_router
from backend.routers.students import router as students_router
from backend.routers.teachers import router as teachers_router
from backend.tests.intergration.conftest import (
    create_test_engine,
    override_current_user_as,
    stub_teacher_user,
    stub_user,
)


@pytest.fixture
def env():
    engine = create_test_engine()

    with Session(engine) as session:
        classroom_a = Classroom(name="Physics 101", capacity=30, location="Building A")
        classroom_b = Classroom(
            name="Chemistry Lab", capacity=24, location="Building B"
        )
        teacher = Teacher(name="Alice Smith", division="Physics")
        other_teacher = Teacher(name="Bob Jones", division="Chemistry")
        session.add_all([classroom_a, classroom_b, teacher, other_teacher])
        session.commit()
        session.refresh(classroom_a)
        session.refresh(classroom_b)
        session.refresh(teacher)
        session.refresh(other_teacher)
        classroom_a_id = classroom_a.id
        classroom_b_id = classroom_b.id
        teacher_id = teacher.id
        other_teacher_id = other_teacher.id

        session.add(
            ClassroomTeacher(classroom_id=classroom_a_id, teacher_id=teacher_id)
        )
        student_a = Student(
            saint_name="Peter",
            first_name="John",
            last_name="Doe",
            division="A",
            classroom_id=classroom_a_id,
        )
        student_b = Student(
            saint_name="Paul",
            first_name="Jane",
            last_name="Doe",
            division="A",
            classroom_id=classroom_b_id,
        )
        session.add_all([student_a, student_b])
        session.commit()
        session.refresh(student_a)
        session.refresh(student_b)
        student_a_id = student_a.id
        student_b_id = student_b.id

    def override_get_session():
        with Session(engine) as session:
            yield session

    app = FastAPI()
    app.include_router(classrooms_router)
    app.include_router(teachers_router)
    app.include_router(students_router)
    app.dependency_overrides[get_session] = override_get_session

    yield SimpleNamespace(
        app=app,
        classroom_a_id=classroom_a_id,
        classroom_b_id=classroom_b_id,
        teacher_id=teacher_id,
        other_teacher_id=other_teacher_id,
        student_a_id=student_a_id,
        student_b_id=student_b_id,
    )

    app.dependency_overrides.clear()


_DEFAULT = object()


def admin_client(env):
    override_current_user_as(env.app, stub_user())
    return TestClient(env.app)


def teacher_client(env, teacher_id=_DEFAULT):
    if teacher_id is _DEFAULT:
        teacher_id = env.teacher_id
    override_current_user_as(env.app, stub_teacher_user(teacher_id))
    return TestClient(env.app)


# -- Classroom reads: open to every authenticated user -----------------------


def test_teacher_can_read_any_classroom(env):
    client = teacher_client(env)

    response = client.get("/classrooms/")
    assert response.status_code == 200
    assert response.json()["total"] == 2

    response = client.get(f"/classrooms/{env.classroom_b_id}")
    assert response.status_code == 200

    response = client.get(f"/classrooms/{env.classroom_b_id}/teachers")
    assert response.status_code == 200


# -- Classroom writes: admin, or a teacher assigned to that classroom --------


def test_teacher_cannot_create_classroom(env):
    payload = {"name": "New Room", "capacity": 10, "location": "Building C"}

    response = teacher_client(env).post("/classrooms/", json=payload)
    assert response.status_code == 403

    response = admin_client(env).post("/classrooms/", json=payload)
    assert response.status_code == 201


def test_teacher_can_update_own_classroom_but_not_others(env):
    client = teacher_client(env)

    response = client.patch(
        f"/classrooms/{env.classroom_a_id}", json={"name": "Physics 201"}
    )
    assert response.status_code == 200

    response = client.patch(
        f"/classrooms/{env.classroom_b_id}", json={"name": "Hacked"}
    )
    assert response.status_code == 403


def test_teacher_cannot_delete_classroom_not_assigned_to(env):
    response = teacher_client(env).delete(f"/classrooms/{env.classroom_b_id}")
    assert response.status_code == 403


def test_teacher_cannot_assign_or_unassign_teacher_on_unowned_classroom(env):
    client = teacher_client(env)

    response = client.post(
        f"/classrooms/{env.classroom_b_id}/teachers",
        json={"teacher_id": env.other_teacher_id},
    )
    assert response.status_code == 403

    response = client.post(
        f"/classrooms/{env.classroom_a_id}/teachers",
        json={"teacher_id": env.other_teacher_id},
    )
    assert response.status_code == 201

    response = client.delete(
        f"/classrooms/{env.classroom_b_id}/teachers/{env.other_teacher_id}"
    )
    assert response.status_code == 403


def test_teacher_cannot_view_students_of_unowned_classroom(env):
    client = teacher_client(env)

    response = client.get(f"/classrooms/{env.classroom_b_id}/students")
    assert response.status_code == 403

    response = client.get(f"/classrooms/{env.classroom_a_id}/students")
    assert response.status_code == 200


def test_teacher_without_teacher_link_cannot_manage_any_classroom(env):
    client = teacher_client(env, teacher_id=None)

    response = client.patch(f"/classrooms/{env.classroom_a_id}", json={"name": "Nope"})
    assert response.status_code == 403


# -- Teacher management router: admin only ------------------------------------


def test_teacher_router_requires_admin(env):
    response = teacher_client(env).get("/teachers/")
    assert response.status_code == 403

    response = admin_client(env).get("/teachers/")
    assert response.status_code == 200


# -- Student endpoints: scoped to the teacher's assigned classrooms ----------


def test_student_list_is_scoped_to_teacher_classrooms(env):
    response = teacher_client(env).get("/students/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == env.student_a_id

    response = admin_client(env).get("/students/")
    assert response.json()["total"] == 2


def test_student_list_rejects_unowned_classroom_filter(env):
    client = teacher_client(env)

    response = client.get("/students/", params={"classroom_id": env.classroom_b_id})
    assert response.status_code == 403

    response = client.get("/students/", params={"classroom_id": env.classroom_a_id})
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_student_get_by_id_is_scoped(env):
    client = teacher_client(env)

    response = client.get(f"/students/{env.student_a_id}")
    assert response.status_code == 200

    response = client.get(f"/students/{env.student_b_id}")
    assert response.status_code == 403


def test_student_create_is_scoped(env):
    client = teacher_client(env)
    payload = {
        "saint_name": "Joseph",
        "first_name": "David",
        "last_name": "Wilson",
        "division": "C",
    }

    response = client.post(
        "/students/", json={**payload, "classroom_id": env.classroom_b_id}
    )
    assert response.status_code == 403

    response = client.post(
        "/students/", json={**payload, "classroom_id": env.classroom_a_id}
    )
    assert response.status_code == 201


def test_student_update_is_scoped(env):
    client = teacher_client(env)

    response = client.patch(f"/students/{env.student_b_id}", json={"division": "B"})
    assert response.status_code == 403

    response = client.patch(
        f"/students/{env.student_a_id}", json={"classroom_id": env.classroom_b_id}
    )
    assert response.status_code == 403

    response = client.patch(f"/students/{env.student_a_id}", json={"division": "B"})
    assert response.status_code == 200


def test_student_delete_is_scoped(env):
    client = teacher_client(env)

    response = client.delete(f"/students/{env.student_b_id}")
    assert response.status_code == 403

    response = client.delete(f"/students/{env.student_a_id}")
    assert response.status_code == 204


def test_student_endpoints_empty_for_teacher_without_teacher_link(env):
    client = teacher_client(env, teacher_id=None)

    response = client.get("/students/")
    assert response.status_code == 200
    assert response.json()["total"] == 0

    response = client.get(f"/students/{env.student_a_id}")
    assert response.status_code == 403
