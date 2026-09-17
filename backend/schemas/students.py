from pydantic import BaseModel, Field


class StudentCreateRequest(BaseModel):
    saint_name: str = Field(min_length=1, max_length=255)
    first_name: str = Field(min_length=1, max_length=255)
    last_name: str = Field(min_length=1, max_length=255)
    division: str = Field(min_length=1, max_length=255)
    classroom_id: int = Field(gt=0)


class StudentUpdateRequest(BaseModel):
    saint_name: str | None = Field(default=None, min_length=1, max_length=255)
    first_name: str | None = Field(default=None, min_length=1, max_length=255)
    last_name: str | None = Field(default=None, min_length=1, max_length=255)
    division: str | None = Field(default=None, min_length=1, max_length=255)
    classroom_id: int | None = Field(default=None, gt=0)


class StudentResponse(BaseModel):
    id: int
    saint_name: str
    first_name: str
    last_name: str
    division: str
    classroom_id: int


class StudentsResponse(BaseModel):
    items: list[StudentResponse]
    limit: int
    offset: int
    total: int
