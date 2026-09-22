from typing import Annotated

from backend.models.users import User
from backend.repository.database import get_session
from backend.repository.errors import NotFoundError
from backend.repository.students import StudentRepo
from backend.schemas.students import (
    StudentCreateRequest,
    StudentResponse,
    StudentsResponse,
    StudentUpdateRequest,
)
from backend.security import (
    FORBIDDEN,
    accessible_classroom_ids,
    get_current_user,
    is_assigned_to_classroom,
)
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session

router = APIRouter(
    prefix="/students",
    tags=["students"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=StudentsResponse)
def get_students(
    student_name: Annotated[str | None, Query(min_length=1)] = None,
    classroom_id: Annotated[int | None, Query(gt=0)] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    repo: StudentRepo = Depends(StudentRepo),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    allowed_ids = accessible_classroom_ids(session, user)
    if classroom_id is not None:
        if allowed_ids is not None and classroom_id not in allowed_ids:
            raise FORBIDDEN
        classroom_ids = [classroom_id]
    else:
        classroom_ids = allowed_ids

    if student_name:
        rows = repo.get_by_name(
            student_name, limit, offset, classroom_ids=classroom_ids
        )
        total = len(rows)
    else:
        rows, total = repo.list(
            limit=limit,
            offset=offset,
            classroom_ids=classroom_ids,
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
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    student = repo.get_by_id(student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    if not is_assigned_to_classroom(session, user, student.classroom_id):
        raise FORBIDDEN
    return student


@router.post(
    "/",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_student(
    student: StudentCreateRequest,
    repo: StudentRepo = Depends(StudentRepo),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if not is_assigned_to_classroom(session, user, student.classroom_id):
        raise FORBIDDEN
    try:
        return repo.create(student.model_dump())
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{student_id}",
    response_model=StudentResponse,
)
def update_student(
    student_id: Annotated[int, Path(gt=0)],
    student: StudentUpdateRequest,
    repo: StudentRepo = Depends(StudentRepo),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    updates = student.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates provided",
        )

    existing = repo.get_by_id(student_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    if not is_assigned_to_classroom(session, user, existing.classroom_id):
        raise FORBIDDEN
    if "classroom_id" in updates and not is_assigned_to_classroom(
        session, user, updates["classroom_id"]
    ):
        raise FORBIDDEN

    try:
        result = repo.update(
            student_id,
            updates,
        )
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
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
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    existing = repo.get_by_id(student_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    if not is_assigned_to_classroom(session, user, existing.classroom_id):
        raise FORBIDDEN
    repo.delete(student_id)
