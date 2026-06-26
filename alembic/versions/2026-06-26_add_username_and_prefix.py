"""Add username to users and id_prefix to schools

Revision ID: b1c2d3e4f5a6
Revises: 4756d4a567f9
Create Date: 2026-06-26 10:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, None] = '4756d4a567f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(inspector, table: str, column: str) -> bool:
    columns = [c["name"] for c in inspector.get_columns(table)]
    return column in columns


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    # Add username column to users table
    if not _column_exists(inspector, "users", "username"):
        op.add_column("users", sa.Column("username", sa.String(50), nullable=True))

    # Add id_prefix column to schools table
    if not _column_exists(inspector, "schools", "id_prefix"):
        op.add_column("schools", sa.Column("id_prefix", sa.String(6), nullable=True))

    # Backfill username from admission_number for student users
    op.execute(
        """
        UPDATE users
        SET username = (SELECT admission_number FROM students WHERE students.id = users.student_id)
        WHERE users.role = 'student' AND users.student_id IS NOT NULL
        """
    )

    # Add unique constraint on username (only non-null values)
    op.create_unique_constraint("uq_users_username", "users", ["username"])

    # Add unique constraint on id_prefix (only non-null values)
    op.create_unique_constraint("uq_schools_id_prefix", "schools", ["id_prefix"])


def downgrade() -> None:
    op.drop_constraint("uq_schools_id_prefix", "schools", type_="unique")
    op.drop_constraint("uq_users_username", "users", type_="unique")
    op.drop_column("schools", "id_prefix")
    op.drop_column("users", "username")
