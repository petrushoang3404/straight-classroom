from sqlmodel import Field, SQLModel


class ClassroomTeacher(SQLModel, table=True):
    """Association table for the many-to-many Classroom <-> Teacher relation."""

    __tablename__ = "classroom_teacher"

    classroom_id: int = Field(
        foreign_key="classroom.id",
        primary_key=True,
        ondelete="CASCADE",
    )
    teacher_id: int = Field(
        foreign_key="teacher.id",
        primary_key=True,
        ondelete="CASCADE",
    )
