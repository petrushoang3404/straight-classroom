from fastapi import FastAPI

app = FastAPI()


@app.get("/classrooms")
async def root():
    return {"message": "Hello World"}