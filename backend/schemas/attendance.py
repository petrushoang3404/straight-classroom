from datetime import date, datetime
from typing import Literal

from backend.schemas.materials import Filename
from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_PHOTO_SIZE = 10 * 1024 * 1024


class PhotoUploadUrlRequest(BaseModel):
    filename: Filename
    content_type: Literal["image/jpeg", "image/png"]
    size_bytes: int = Field(gt=0, le=MAX_PHOTO_SIZE)


class DetectRequest(BaseModel):
    object_key: str = Field(min_length=1, max_length=1024)


class FaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float


class DetectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    width: int
    height: int
    count: int
    faces: list[FaceResponse]


class AttendanceRecordInput(BaseModel):
    student_id: int = Field(gt=0)
    present: bool


class AttendanceCreateRequest(BaseModel):
    session_date: date
    photo_object_key: str | None = Field(default=None, min_length=1, max_length=1024)
    records: list[AttendanceRecordInput]

    @field_validator("records")
    @classmethod
    def _one_record_per_student(cls, records):
        ids = [record.student_id for record in records]
        if len(ids) != len(set(ids)):
            raise ValueError("Each student may appear only once")
        return records


class AttendanceRecordResponse(AttendanceRecordInput):
    model_config = ConfigDict(from_attributes=True)


class AttendanceSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    classroom_id: int
    session_date: date
    detected_count: int | None
    present_count: int
    total_count: int
    created_at: datetime
    records: list[AttendanceRecordResponse]


class AttendanceSessionsResponse(BaseModel):
    items: list[AttendanceSessionResponse]
    limit: int
    offset: int
    total: int
