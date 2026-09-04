from contextlib import asynccontextmanager

from fastapi import FastAPI
from backend.repository.database import create_db_and_tables, engine
from routers.classrooms import router


app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    engine.dispose()

app = FastAPI(lifespan=lifespan)

app.include_router(router)