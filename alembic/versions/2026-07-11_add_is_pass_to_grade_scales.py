"""Add is_pass to grade_scales

Revision ID: g8h9i0j1k2l3
Revises: f7a8b9c0d1e2
Create Date: 2026-07-11 10:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect


revision: str = 'g8h9i0j1k2l3'
down_revision: Union[str, None] = 'f7a8b9c0d1e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [c["name"] for c in inspector.get_columns("grade_scales")]

    if "is_pass" not in columns:
        op.add_column(
            "grade_scales",
            sa.Column("is_pass", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        )


def downgrade() -> None:
    op.drop_column("grade_scales", "is_pass")
