from typing import Annotated

from backend.repository.students import StudentRepo
from backend.schemas.students import (
    StudentCreateRequest,
    StudentResponse,
    StudentsResponse,
    StudentUpdateRequest,
)
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/", response_model=StudentsResponse)
def get_students(
    student_name: Annotated[str | None, Query(min_length=1)] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    repo: StudentRepo = Depends(StudentRepo),
):
    if student_name:
        rows = repo.get_by_name(student_name, limit, offset)
        total = len(rows)
    else:
        rows, total = repo.list(
            limit=limit,
            offset=offset,
        )
    return StudentsResponse(
        items=rows,
        limit=limit,
        offset=offset,
        total=total,
    )


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: Annotated[int, Path(gt=0)],
    repo: StudentRepo = Depends(StudentRepo),
):
    student = repo.get_by_id(student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    return student


@router.post(
    "/",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_student(
    student: StudentCreateRequest,
    repo: StudentRepo = Depends(StudentRepo),
):
    return repo.create(student.model_dump())


@router.patch(
    "/{student_id}",
    response_model=StudentResponse,
)
def update_student(
    student_id: Annotated[int, Path(gt=0)],
    student: StudentUpdateRequest,
    repo: StudentRepo = Depends(StudentRepo),
):
    updates = student.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates provided",
        )
    result = repo.update(
        student_id,
        updates,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    return result


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: Annotated[int, Path(gt=0)],
    repo: StudentRepo = Depends(StudentRepo),
):
    result = repo.delete(student_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
