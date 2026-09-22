"""rename teacher subject to division and add personal details fields

Revision ID: 7da8f671accb
Revises: b8c087fcbc26
Create Date: 2026-09-22 15:33:24.055809

"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7da8f671accb"
down_revision: str | Sequence[str] | None = "b8c087fcbc26"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("teacher", "subject", new_column_name="division")
    op.add_column(
        "teacher",
        sa.Column(
            "saint_name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True
        ),
    )
    op.add_column("teacher", sa.Column("date_of_birth", sa.Date(), nullable=True))
    op.add_column(
        "teacher",
        sa.Column(
            "place_of_birth",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=True,
        ),
    )
    op.add_column(
        "teacher",
        sa.Column(
            "feast_day", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True
        ),
    )
    op.add_column(
        "teacher",
        sa.Column(
            "phone_number",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=True,
        ),
    )
    op.add_column(
        "teacher",
        sa.Column(
            "address", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("teacher", "address")
    op.drop_column("teacher", "phone_number")
    op.drop_column("teacher", "feast_day")
    op.drop_column("teacher", "place_of_birth")
    op.drop_column("teacher", "date_of_birth")
    op.drop_column("teacher", "saint_name")
    op.alter_column("teacher", "division", new_column_name="subject")
