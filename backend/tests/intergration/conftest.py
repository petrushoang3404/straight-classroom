from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

# Import every model module so their tables are registered on SQLModel.metadata
# before create_all() runs -- otherwise it silently creates nothing for them.
import backend.models.classroom_teachers
import backend.models.classrooms
import backend.models.students
import backend.models.teachers
import backend.models.users  # noqa: F401
from backend.models.users import User
from backend.security import get_current_user


def stub_user() -> User:
    return User(
        id=1,
        username="tester",
        hashed_password="",
        display_name="Tester",
        role="admin",
    )


def stub_teacher_user(teacher_id: int | None) -> User:
    return User(
        id=2,
        username="teacher",
        hashed_password="",
        display_name="Teacher",
        role="teacher",
        teacher_id=teacher_id,
    )


def override_current_user(app):
    """Bypass the classrooms/teachers/students auth dependency in tests.

    Auth itself has its own dedicated tests (test_auth.py); resource tests
    only care that a logged-in user can reach the endpoint.
    """
    app.dependency_overrides[get_current_user] = stub_user


def override_current_user_as(app, user: User):
    app.dependency_overrides[get_current_user] = lambda: user


def create_test_engine():
    """An in-memory SQLite engine with foreign keys enforced.

    SQLite ignores FK constraints unless PRAGMA foreign_keys=ON is set on each
    connection -- without this, RESTRICT/CASCADE behavior would pass tests here
    even if the migration defined them wrong.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    SQLModel.metadata.create_all(engine)
    return engine
