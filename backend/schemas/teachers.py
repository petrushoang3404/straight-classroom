from pydantic import BaseModel, Field

class TeacherCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255) 
    subject: str = Field(min_length=1, max_length=255)

class TeacherUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255) 
    subject: str | None = Field(default=None, min_length=1, max_length=255)

class TeacherResponse(BaseModel):
    id: int
    name: str 
    subject: str

class TeachersResponse(BaseModel):
    items: list[TeacherResponse]
    limit: int
    offset: int
    total: int