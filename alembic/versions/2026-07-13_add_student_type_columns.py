"""Add student_type to students and fee_structures tables

Revision ID: h9i0j1k2l3m4
Revises: g8h9i0j1k2l3
Create Date: 2026-07-13 10:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect


revision: str = 'h9i0j1k2l3m4'
down_revision: Union[str, None] = 'g8h9i0j1k2l3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    # Add student_type to students table (default "Day Scholar" for existing rows)
    student_columns = [c["name"] for c in inspector.get_columns("students")]
    if "student_type" not in student_columns:
        op.add_column(
            "students",
            sa.Column(
                "student_type",
                sa.String(20),
                nullable=False,
                server_default=sa.text("'Day Scholar'"),
            ),
        )

    # Add student_type to fee_structures table (default "all" for existing rows)
    fee_columns = [c["name"] for c in inspector.get_columns("fee_structures")]
    if "student_type" not in fee_columns:
        op.add_column(
            "fee_structures",
            sa.Column(
                "student_type",
                sa.String(20),
                nullable=False,
                server_default=sa.text("'all'"),
            ),
        )

    # Update unique constraint to include student_type
    constraints = inspector.get_unique_constraints("fee_structures")
    old_constraint = next(
        (c for c in constraints if c["name"] == "uq_fee_structures_year_class_type"),
        None,
    )
    if old_constraint:
        op.drop_constraint("uq_fee_structures_year_class_type", "fee_structures", type_="unique")
    op.create_unique_constraint(
        "uq_fee_structures_year_class_type_stype",
        "fee_structures",
        ["school_id", "academic_year_id", "class_section_id", "fee_type", "student_type"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_fee_structures_year_class_type_stype", "fee_structures", type_="unique")
    op.create_unique_constraint(
        "uq_fee_structures_year_class_type",
        "fee_structures",
        ["school_id", "academic_year_id", "class_section_id", "fee_type"],
    )
    op.drop_column("fee_structures", "student_type")
    op.drop_column("students", "student_type")
