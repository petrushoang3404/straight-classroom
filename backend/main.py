from contextlib import asynccontextmanager

from fastapi import FastAPI
from backend.repository.database import create_db_and_tables, engine, ping_db
from backend.routers.classrooms import router


app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not ping_db():
        raise RuntimeError("Could not connect to the database on startup")
    create_db_and_tables()
    yield
    engine.dispose()

app = FastAPI(lifespan=lifespan)

app.include_router(router)