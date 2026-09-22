from backend.schemas.summaries import ClassroomSummary
from pydantic import BaseModel, ConfigDict, Field


class TeacherCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    subject: str = Field(min_length=1, max_length=255)


class TeacherUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    subject: str | None = Field(default=None, min_length=1, max_length=255)


class TeacherResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    subject: str
    classrooms: list[ClassroomSummary] = []


class TeachersResponse(BaseModel):
    items: list[TeacherResponse]
    limit: int
    offset: int
    total: int
