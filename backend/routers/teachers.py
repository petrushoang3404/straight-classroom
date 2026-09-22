from typing import Annotated

from backend.repository.errors import NotFoundError
from backend.repository.teachers import TeacherRepo
from backend.schemas.summaries import ClassroomSummary
from backend.schemas.teachers import (
    TeacherCreateRequest,
    TeacherResponse,
    TeachersResponse,
    TeacherUpdateRequest,
)
from backend.security import get_current_user
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

router = APIRouter(
    prefix="/teachers",
    tags=["teachers"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=TeachersResponse)
def get_teachers(
    teacher_name: Annotated[str | None, Query(min_length=1)] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    repo: TeacherRepo = Depends(TeacherRepo),
):
    if teacher_name:
        rows = repo.get_by_name(teacher_name, limit, offset)
        total = len(rows)
    else:
        rows, total = repo.list(
            limit=limit,
            offset=offset,
        )
    return TeachersResponse(
        items=rows,
        limit=limit,
        offset=offset,
        total=total,
    )


@router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher(
    teacher_id: Annotated[int, Path(gt=0)],
    repo: TeacherRepo = Depends(TeacherRepo),
):
    teacher = repo.get_by_id(teacher_id)
    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found",
        )
    return teacher


@router.post(
    "/",
    response_model=TeacherResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_teacher(
    teacher: TeacherCreateRequest,
    repo: TeacherRepo = Depends(TeacherRepo),
):
    return repo.create(teacher.model_dump())


@router.patch("/{teacher_id}", response_model=TeacherResponse)
def update_teacher(
    teacher_id: Annotated[int, Path(gt=0)],
    teacher: TeacherUpdateRequest,
    repo: TeacherRepo = Depends(TeacherRepo),
):
    updates = teacher.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates provided",
        )
    result = repo.update(
        teacher_id,
        updates,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found",
        )
    return result


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(
    teacher_id: Annotated[int, Path(gt=0)],
    repo: TeacherRepo = Depends(TeacherRepo),
):
    result = repo.delete(teacher_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found",
        )


@router.get("/{teacher_id}/classrooms", response_model=list[ClassroomSummary])
def get_teacher_classrooms(
    teacher_id: Annotated[int, Path(gt=0)],
    repo: TeacherRepo = Depends(TeacherRepo),
):
    try:
        return repo.list_classrooms(teacher_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
