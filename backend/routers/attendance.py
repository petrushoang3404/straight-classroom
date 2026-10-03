"""Attendance for a classroom, checked against a photo of the class.

The photo goes through the same presigned-upload handshake as materials. The
face detector (`backend.inference`) is called in-process on the stored image:
it counts faces so the teacher can sanity-check the roster they tick. It does
not recognise anyone.
"""

from typing import Annotated

from backend import storage
from backend.inference import InvalidImageError, detect_faces
from backend.repository.attendance import AttendanceRepo
from backend.repository.errors import NotFoundError
from backend.schemas.attendance import (
    MAX_PHOTO_SIZE,
    AttendanceCreateRequest,
    AttendanceSessionResponse,
    AttendanceSessionsResponse,
    DetectionResponse,
    DetectRequest,
    PhotoUploadUrlRequest,
)
from backend.schemas.materials import UploadUrlResponse
from backend.security import require_classroom_access
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

router = APIRouter(
    prefix="/classrooms/{classroom_id}/attendance",
    tags=["attendance"],
    dependencies=[Depends(require_classroom_access)],
)

EXPIRES_IN_SECONDS = int(storage.PRESIGNED_URL_TTL.total_seconds())

SESSION_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Attendance session not found",
)


def _detect_in_photo(classroom_id: int, object_key: str):
    """Run the face detector on an uploaded photo of this classroom."""
    if not object_key.startswith(storage.attendance_prefix(classroom_id)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Object key does not belong to this classroom",
        )
    stat = storage.stat_object(object_key)
    if stat is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload was not completed",
        )
    if stat.size > MAX_PHOTO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Photo exceeds the 10 MB limit",
        )
    try:
        return detect_faces(storage.read_object(object_key))
    except InvalidImageError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(exc),
        ) from exc


@router.get("", response_model=AttendanceSessionsResponse)
def get_sessions(
    classroom_id: Annotated[int, Path(gt=0)],
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    repo: AttendanceRepo = Depends(AttendanceRepo),
):
    try:
        rows, total = repo.list(classroom_id, limit=limit, offset=offset)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return AttendanceSessionsResponse(
        items=rows, limit=limit, offset=offset, total=total
    )


@router.post("/photo-upload-url", response_model=UploadUrlResponse)
def create_photo_upload_url(
    classroom_id: Annotated[int, Path(gt=0)],
    upload: PhotoUploadUrlRequest,
):
    object_key = storage.build_attendance_key(classroom_id, upload.filename)
    return UploadUrlResponse(
        object_key=object_key,
        upload_url=storage.presigned_put_url(object_key),
        expires_in_seconds=EXPIRES_IN_SECONDS,
    )


@router.post("/detect", response_model=DetectionResponse)
def detect(
    classroom_id: Annotated[int, Path(gt=0)],
    request: DetectRequest,
):
    """Preview: count and locate faces in an uploaded photo. Saves nothing."""
    return _detect_in_photo(classroom_id, request.object_key)


@router.post(
    "",
    response_model=AttendanceSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_session(
    classroom_id: Annotated[int, Path(gt=0)],
    request: AttendanceCreateRequest,
    repo: AttendanceRepo = Depends(AttendanceRepo),
):
    # Counted again here rather than taken from the client, so the stored
    # number is always what the model saw.
    detected_count = None
    if request.photo_object_key is not None:
        detected_count = _detect_in_photo(classroom_id, request.photo_object_key).count

    try:
        return repo.create(
            {
                "classroom_id": classroom_id,
                "session_date": request.session_date,
                "photo_object_key": request.photo_object_key,
                "detected_count": detected_count,
            },
            [record.model_dump() for record in request.records],
        )
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    classroom_id: Annotated[int, Path(gt=0)],
    session_id: Annotated[int, Path(gt=0)],
    repo: AttendanceRepo = Depends(AttendanceRepo),
):
    attendance = repo.get_by_id(classroom_id, session_id)
    if attendance is None:
        raise SESSION_NOT_FOUND

    photo_key = attendance.photo_object_key
    repo.delete(attendance)
    # Row first, same reasoning as materials: a leftover object is harmless.
    if photo_key is not None:
        storage.remove_object(photo_key)
