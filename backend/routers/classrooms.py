from fastapi import APIRouter
from backend.schemas.classrooms import Classroom

router = APIRouter(
    prefix="/classrooms",
    tags=["classrooms"])

@router.get("/")
async def get_classrooms():
    return {"message": "List of classrooms"}

@router.get("/{classroom_id}")
async def get_classroom(classroom_id: int):
    return {"message": f"Details for classroom {classroom_id}"}

@router.post("/")
async def create_classroom(classroom: Classroom):
    return {"message": f"Classroom {classroom.name} created successfully"}