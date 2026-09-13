from fastapi import APIRouter, Query, Depends, status
from backend.schemas.classrooms import (
    ClassroomCreateRequest,
    ClassroomResponse,
    ClassroomsResponse,
)
from backend.repository.classrooms import ClassroomRepo 

router = APIRouter(
    prefix="/classrooms",
    tags=["classrooms"])

@router.get("/", response_model=ClassroomsResponse)
async def get_classrooms(
    limit: int = Query(default=20, ge=1, le=100), 
    offset: int = Query(default=0, ge=0),
    repo: ClassroomRepo = Depends(ClassroomRepo)
):
    rows, total = await repo.list(
        limit=limit,
        offset=offset,
    )
    return ClassroomsResponse(
        items=rows,
        limit=limit,
        offset=offset,
        total=total,
    )

@router.get("/{classroom_id}")
async def get_classroom(classroom_id: int):
    return {"message": f"Details for classroom {classroom_id}"}

@router.post(
    "/",
    response_model=ClassroomResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_classroom(
    classroom: ClassroomCreateRequest,
    repo: ClassroomRepo = Depends(ClassroomRepo),
):
    return await repo.create(classroom.model_dump())
