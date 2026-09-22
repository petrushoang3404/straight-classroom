from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

# Import every model module so their tables are registered on SQLModel.metadata
# before create_all() runs -- otherwise it silently creates nothing for them.
import backend.models.classroom_teachers
import backend.models.classrooms
import backend.models.students
import backend.models.teachers  # noqa: F401


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
