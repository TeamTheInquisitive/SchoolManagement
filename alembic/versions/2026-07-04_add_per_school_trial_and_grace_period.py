"""Add per-school trial_duration_days and grace_period_days

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-07-04 15:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("schools", sa.Column("trial_duration_days", sa.Integer(), nullable=False, server_default="14"))
    op.add_column("schools", sa.Column("grace_period_days", sa.Integer(), nullable=False, server_default="2"))


def downgrade() -> None:
    op.drop_column("schools", "grace_period_days")
    op.drop_column("schools", "trial_duration_days")
