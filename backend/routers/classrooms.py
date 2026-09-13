from typing import Annotated
from fastapi import APIRouter, Path, Query, Depends, HTTPException, status
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

@router.get("/{classroom_id}", response_model=ClassroomResponse)
async def get_classroom(
    classroom_id: Annotated[int, Path(gt=0)],
    repo: ClassroomRepo = Depends(ClassroomRepo),
):
    classroom = await repo.get_by_id(classroom_id)
    if classroom is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found",
        )
    return classroom

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
