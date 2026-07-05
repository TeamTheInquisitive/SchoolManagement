"""Make email globally unique for users and staff tables

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-07-04 14:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old per-school unique constraint on users.email
    op.drop_constraint("uq_users_school_email", "users", type_="unique")
    # Create global unique constraint on users.email
    op.create_unique_constraint("uq_users_email", "users", ["email"])

    # Drop old per-school unique constraint on staff.email
    op.drop_constraint("uq_staff_school_email", "staff", type_="unique")
    # Create global unique constraint on staff.email
    op.create_unique_constraint("uq_staff_email", "staff", ["email"])


def downgrade() -> None:
    # Revert staff email constraint
    op.drop_constraint("uq_staff_email", "staff", type_="unique")
    op.create_unique_constraint("uq_staff_school_email", "staff", ["school_id", "email"])

    # Revert users email constraint
    op.drop_constraint("uq_users_email", "users", type_="unique")
    op.create_unique_constraint("uq_users_school_email", "users", ["school_id", "email"])
