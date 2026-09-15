from pydantic import BaseModel, Field

class ClassroomCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255) 
    capacity: int = Field(gt=0)
    location: str = Field(min_length=1, max_length=255)

class ClassroomUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255) 
    capacity: int | None = Field(default=None, gt=0)
    location: str | None = Field(default=None, min_length=1, max_length=255)

class ClassroomResponse(BaseModel):
    id: int
    name: str 
    capacity: int
    location: str

class ClassroomsResponse(BaseModel):
    items: list[ClassroomResponse]
    limit: int
    offset: int
    total: int
