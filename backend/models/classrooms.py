from typing import TYPE_CHECKING

from backend.models.classroom_teachers import ClassroomTeacher
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.models.students import Student
    from backend.models.teachers import Teacher


class Classroom(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    capacity: int
    location: str

    students: list[Student] = Relationship(back_populates="classroom")
    teachers: list[Teacher] = Relationship(
        back_populates="classrooms",
        link_model=ClassroomTeacher,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
