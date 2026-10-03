"""add attendance tables

Revision ID: a3f1c9d27b40
Revises: d02675572d3b
Create Date: 2026-10-03 10:20:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a3f1c9d27b40"
down_revision: str | Sequence[str] | None = "d02675572d3b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "attendance_session",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("classroom_id", sa.Integer(), nullable=False),
        sa.Column("session_date", sa.Date(), nullable=False),
        sa.Column(
            "photo_object_key",
            sqlmodel.sql.sqltypes.AutoString(length=1024),
            nullable=True,
        ),
        sa.Column("detected_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["classroom_id"], ["classroom.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_attendance_session_classroom_id"),
        "attendance_session",
        ["classroom_id"],
        unique=False,
    )
    op.create_table(
        "attendance_record",
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("present", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"], ["attendance_session.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["student_id"], ["student.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("session_id", "student_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("attendance_record")
    op.drop_index(
        op.f("ix_attendance_session_classroom_id"), table_name="attendance_session"
    )
    op.drop_table("attendance_session")
