from backend.schemas.summaries import TeacherSummary
from pydantic import BaseModel, ConfigDict, Field


class ClassroomCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    capacity: int = Field(gt=0)
    location: str = Field(min_length=1, max_length=255)


class ClassroomUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    capacity: int | None = Field(default=None, gt=0)
    location: str | None = Field(default=None, min_length=1, max_length=255)


class ClassroomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    capacity: int
    location: str
    teachers: list[TeacherSummary] = []


class ClassroomsResponse(BaseModel):
    items: list[ClassroomResponse]
    limit: int
    offset: int
    total: int


class TeacherAssignmentRequest(BaseModel):
    teacher_id: int = Field(gt=0)
