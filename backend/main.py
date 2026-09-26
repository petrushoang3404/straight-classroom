from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.repository.database import engine, ping_db
from backend.routers.auth import router as auth_router
from backend.routers.classrooms import router as classrooms_router
from backend.routers.materials import router as materials_router
from backend.routers.students import router as students_router
from backend.routers.teachers import router as teachers_router
from backend.storage import ensure_bucket

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not ping_db():
        raise RuntimeError("Could not connect to the database on startup")
    # Schema is managed by Alembic migrations (`make be-migrate`), not created here.
    ensure_bucket()
    yield
    engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(classrooms_router)
app.include_router(teachers_router)
app.include_router(students_router)
app.include_router(materials_router)
