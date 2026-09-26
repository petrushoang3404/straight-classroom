from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


class Material(SQLModel, table=True):
    """A file uploaded to a classroom. The bytes live in MinIO under
    `object_key`; this row only carries what the UI needs to list them."""

    id: int | None = Field(default=None, primary_key=True)
    classroom_id: int = Field(
        foreign_key="classroom.id",
        index=True,
        ondelete="CASCADE",
    )
    description: str | None = Field(default=None, max_length=1000)

    filename: str = Field(max_length=255)
    content_type: str = Field(max_length=255)
    size_bytes: int
    object_key: str = Field(max_length=1024, unique=True)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
    )
