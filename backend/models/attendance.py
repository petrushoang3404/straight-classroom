from datetime import UTC, date, datetime

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel


class AttendanceSession(SQLModel, table=True):
    """One roll call for a classroom.

    `detected_count` is how many faces the model found in the class photo; it
    is a cross-check on the roster, not a substitute for it.
    """

    __tablename__ = "attendance_session"

    id: int | None = Field(default=None, primary_key=True)
    classroom_id: int = Field(
        foreign_key="classroom.id",
        index=True,
        ondelete="CASCADE",
    )
    session_date: date
    photo_object_key: str | None = Field(default=None, max_length=1024)
    detected_count: int | None = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
    )

    records: list[AttendanceRecord] = Relationship(
        cascade_delete=True,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    @property
    def total_count(self) -> int:
        return len(self.records)

    @property
    def present_count(self) -> int:
        return sum(record.present for record in self.records)


class AttendanceRecord(SQLModel, table=True):
    __tablename__ = "attendance_record"

    session_id: int = Field(
        foreign_key="attendance_session.id",
        primary_key=True,
        ondelete="CASCADE",
    )
    student_id: int = Field(
        foreign_key="student.id",
        primary_key=True,
        ondelete="CASCADE",
    )
    present: bool
