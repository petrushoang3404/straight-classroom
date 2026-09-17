from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, SQLModel, create_engine, text

from backend.config import settings

DATABASE_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@localhost/{settings.postgres_db}"

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    # Importing the model modules registers their tables on SQLModel.metadata;
    # without this, create_all() silently creates nothing.
    import backend.models.classrooms  # noqa: F401
    import backend.models.students  # noqa: F401
    import backend.models.teachers  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def ping_db() -> bool:
    """Check DB connectivity. Returns True if reachable, False otherwise."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False
