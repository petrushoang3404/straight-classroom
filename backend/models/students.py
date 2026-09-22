from datetime import date
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

    date_of_birth: date | None = Field(default=None)
    place_of_birth: str | None = Field(default=None, max_length=255)
    date_of_baptism: date | None = Field(default=None)
    place_of_baptism: str | None = Field(default=None, max_length=255)
    date_of_first_communion: date | None = Field(default=None)
    place_of_first_communion: str | None = Field(default=None, max_length=255)
    date_of_confirmation: date | None = Field(default=None)
    place_of_confirmation: str | None = Field(default=None, max_length=255)
    father_name: str | None = Field(default=None, max_length=255)
    father_phone_number: str | None = Field(default=None, max_length=255)
    mother_name: str | None = Field(default=None, max_length=255)
    mother_phone_number: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=255)

    classroom: Classroom = Relationship(
        back_populates="students",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
