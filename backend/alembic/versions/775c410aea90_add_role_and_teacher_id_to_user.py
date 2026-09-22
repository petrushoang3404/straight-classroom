"""add role and teacher_id to user

Revision ID: 775c410aea90
Revises: 7da8f671accb
Create Date: 2026-09-22 17:21:37.471104

"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "775c410aea90"
down_revision: str | Sequence[str] | None = "7da8f671accb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "user",
        sa.Column(
            "role",
            sqlmodel.sql.sqltypes.AutoString(length=50),
            nullable=False,
            server_default="admin",
        ),
    )
    op.add_column("user", sa.Column("teacher_id", sa.Integer(), nullable=True))
    op.create_unique_constraint("uq_user_teacher_id", "user", ["teacher_id"])
    op.create_foreign_key(
        "fk_user_teacher_id_teacher",
        "user",
        "teacher",
        ["teacher_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_user_teacher_id_teacher", "user", type_="foreignkey")
    op.drop_constraint("uq_user_teacher_id", "user", type_="unique")
    op.drop_column("user", "teacher_id")
    op.drop_column("user", "role")
