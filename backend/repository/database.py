from sqlmodel import SQLModel, create_engine, Session, text
from backend.config import settings
from backend.models.classroom import Classroom


DATABASE_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@localhost/{settings.postgres_db}"

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
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
    except Exception:
        return False