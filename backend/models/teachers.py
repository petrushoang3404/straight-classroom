from typing import TYPE_CHECKING

from backend.models.classroom_teachers import ClassroomTeacher
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.models.classrooms import Classroom


class Teacher(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    subject: str = Field(max_length=255)

    classrooms: list[Classroom] = Relationship(
        back_populates="teachers",
        link_model=ClassroomTeacher,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
