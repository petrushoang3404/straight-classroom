from typing import Annotated

from backend.repository.classrooms import ClassroomRepo
from backend.repository.errors import ConflictError, NotFoundError
from backend.schemas.classrooms import (
    ClassroomCreateRequest,
    ClassroomResponse,
    ClassroomsResponse,
    ClassroomUpdateRequest,
    TeacherAssignmentRequest,
)
from backend.schemas.students import StudentsResponse
from backend.schemas.summaries import TeacherSummary
from backend.security import get_current_user, require_admin, require_classroom_access
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

router = APIRouter(
    prefix="/classrooms",
    tags=["classrooms"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=ClassroomsResponse)
def get_classrooms(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    repo: ClassroomRepo = Depends(ClassroomRepo),
):
    rows, total = repo.list(
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
def get_classroom(
    classroom_id: Annotated[int, Path(gt=0)],
    repo: ClassroomRepo = Depends(ClassroomRepo),
):
    classroom = repo.get_by_id(classroom_id)
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
    dependencies=[Depends(require_admin)],
)
def create_classroom(
    classroom: ClassroomCreateRequest,
    repo: ClassroomRepo = Depends(ClassroomRepo),
):
    return repo.create(classroom.model_dump())


@router.patch(
    "/{classroom_id}",
    response_model=ClassroomResponse,
    dependencies=[Depends(require_classroom_access)],
)
def update_classroom(
    classroom_id: Annotated[int, Path(gt=0)],
    classroom: ClassroomUpdateRequest,
    repo: ClassroomRepo = Depends(ClassroomRepo),
):
    updates = classroom.model_dump(
        exclude_unset=True,
    )
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided",
        )
    result = repo.update(
        classroom_id,
        updates,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found",
        )
    return result


@router.delete(
    "/{classroom_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_classroom_access)],
)
def delete_classroom(
    classroom_id: Annotated[int, Path(gt=0)],
    repo: ClassroomRepo = Depends(ClassroomRepo),
):
    try:
        result = repo.delete(classroom_id)
    except ConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found",
        )


@router.get(
    "/{classroom_id}/students",
    response_model=StudentsResponse,
    dependencies=[Depends(require_classroom_access)],
)
def get_classroom_students(
    classroom_id: Annotated[int, Path(gt=0)],
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    repo: ClassroomRepo = Depends(ClassroomRepo),
):
    try:
        rows, total = repo.list_students(classroom_id, limit=limit, offset=offset)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return StudentsResponse(items=rows, limit=limit, offset=offset, total=total)


@router.get("/{classroom_id}/teachers", response_model=list[TeacherSummary])
def get_classroom_teachers(
    classroom_id: Annotated[int, Path(gt=0)],
    repo: ClassroomRepo = Depends(ClassroomRepo),
):
    try:
        return repo.list_teachers(classroom_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/{classroom_id}/teachers",
    response_model=ClassroomResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_classroom_access)],
)
def assign_classroom_teacher(
    classroom_id: Annotated[int, Path(gt=0)],
    assignment: TeacherAssignmentRequest,
    repo: ClassroomRepo = Depends(ClassroomRepo),
):
    try:
        return repo.assign_teacher(classroom_id, assignment.teacher_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{classroom_id}/teachers/{teacher_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_classroom_access)],
)
def unassign_classroom_teacher(
    classroom_id: Annotated[int, Path(gt=0)],
    teacher_id: Annotated[int, Path(gt=0)],
    repo: ClassroomRepo = Depends(ClassroomRepo),
):
    try:
        repo.unassign_teacher(classroom_id, teacher_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
