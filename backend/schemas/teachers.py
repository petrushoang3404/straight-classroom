from datetime import date

from backend.schemas.summaries import ClassroomSummary
from pydantic import BaseModel, ConfigDict, Field


class TeacherCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    division: str = Field(min_length=1, max_length=255)

    saint_name: str | None = Field(default=None, max_length=255)
    date_of_birth: date | None = None
    place_of_birth: str | None = Field(default=None, max_length=255)
    feast_day: str | None = Field(default=None, max_length=255)
    phone_number: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=255)


class TeacherUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    division: str | None = Field(default=None, min_length=1, max_length=255)

    saint_name: str | None = Field(default=None, max_length=255)
    date_of_birth: date | None = None
    place_of_birth: str | None = Field(default=None, max_length=255)
    feast_day: str | None = Field(default=None, max_length=255)
    phone_number: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=255)


class TeacherResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    division: str
    classrooms: list[ClassroomSummary] = []

    saint_name: str | None
    date_of_birth: date | None
    place_of_birth: str | None
    feast_day: str | None
    phone_number: str | None
    address: str | None


class TeachersResponse(BaseModel):
    items: list[TeacherResponse]
    limit: int
    offset: int
    total: int
