from datetime import date
from typing import TYPE_CHECKING

from backend.models.classroom_teachers import ClassroomTeacher
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.models.classrooms import Classroom


class Teacher(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    division: str = Field(max_length=255)

    saint_name: str | None = Field(default=None, max_length=255)
    date_of_birth: date | None = Field(default=None)
    place_of_birth: str | None = Field(default=None, max_length=255)
    feast_day: str | None = Field(default=None, max_length=255)
    phone_number: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=255)

    classrooms: list[Classroom] = Relationship(
        back_populates="teachers",
        link_model=ClassroomTeacher,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
