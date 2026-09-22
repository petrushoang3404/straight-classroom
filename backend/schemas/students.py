from datetime import date

from backend.schemas.summaries import ClassroomSummary
from pydantic import BaseModel, ConfigDict, Field


class StudentCreateRequest(BaseModel):
    saint_name: str = Field(min_length=1, max_length=255)
    first_name: str = Field(min_length=1, max_length=255)
    last_name: str = Field(min_length=1, max_length=255)
    division: str = Field(min_length=1, max_length=255)
    classroom_id: int = Field(gt=0)

    date_of_birth: date | None = None
    place_of_birth: str | None = Field(default=None, max_length=255)
    date_of_baptism: date | None = None
    place_of_baptism: str | None = Field(default=None, max_length=255)
    date_of_first_communion: date | None = None
    place_of_first_communion: str | None = Field(default=None, max_length=255)
    date_of_confirmation: date | None = None
    place_of_confirmation: str | None = Field(default=None, max_length=255)
    father_name: str | None = Field(default=None, max_length=255)
    father_phone_number: str | None = Field(default=None, max_length=255)
    mother_name: str | None = Field(default=None, max_length=255)
    mother_phone_number: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=255)


class StudentUpdateRequest(BaseModel):
    saint_name: str | None = Field(default=None, min_length=1, max_length=255)
    first_name: str | None = Field(default=None, min_length=1, max_length=255)
    last_name: str | None = Field(default=None, min_length=1, max_length=255)
    division: str | None = Field(default=None, min_length=1, max_length=255)
    classroom_id: int | None = Field(default=None, gt=0)

    date_of_birth: date | None = None
    place_of_birth: str | None = Field(default=None, max_length=255)
    date_of_baptism: date | None = None
    place_of_baptism: str | None = Field(default=None, max_length=255)
    date_of_first_communion: date | None = None
    place_of_first_communion: str | None = Field(default=None, max_length=255)
    date_of_confirmation: date | None = None
    place_of_confirmation: str | None = Field(default=None, max_length=255)
    father_name: str | None = Field(default=None, max_length=255)
    father_phone_number: str | None = Field(default=None, max_length=255)
    mother_name: str | None = Field(default=None, max_length=255)
    mother_phone_number: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=255)


class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    saint_name: str
    first_name: str
    last_name: str
    division: str
    classroom_id: int
    classroom: ClassroomSummary

    date_of_birth: date | None
    place_of_birth: str | None
    date_of_baptism: date | None
    place_of_baptism: str | None
    date_of_first_communion: date | None
    place_of_first_communion: str | None
    date_of_confirmation: date | None
    place_of_confirmation: str | None
    father_name: str | None
    father_phone_number: str | None
    mother_name: str | None
    mother_phone_number: str | None
    address: str | None


class StudentsResponse(BaseModel):
    items: list[StudentResponse]
    limit: int
    offset: int
    total: int
