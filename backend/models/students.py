from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.models.classrooms import Classroom


class Student(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    saint_name: str = Field(max_length=255)
    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)
    division: str = Field(max_length=255)
    classroom_id: int = Field(
        foreign_key="classroom.id",
        index=True,
        ondelete="RESTRICT",
    )

    classroom: Classroom = Relationship(
        back_populates="students",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
