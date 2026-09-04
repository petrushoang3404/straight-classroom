from fastapi import FastAPI
from routers.classrooms import router

app = FastAPI()


app.include_router(router=router)