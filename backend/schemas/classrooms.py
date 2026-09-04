from pydantic import BaseModel, Field

class Classroom(BaseModel):
    name: str = Field(min_length=1, max_length=255) 
    capacity: int = Field(gt=0)
    location: str = Field(min_length=1, max_length=255)