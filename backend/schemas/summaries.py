"""Lightweight nested representations used when embedding one resource inside another.

Keeping these separate from the full *Response schemas avoids circular imports
between schemas/classrooms.py and schemas/teachers.py, and keeps nested payloads
small (no recursively-nested relations).
"""

from pydantic import BaseModel, ConfigDict


class ClassroomSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    location: str


class TeacherSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    division: str
