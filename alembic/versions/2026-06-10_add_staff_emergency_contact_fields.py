"""add_staff_emergency_contact_fields

Revision ID: a3e7f2c91d01
Revises: 2026-06-05_add_payslip_components_and_paid_amount
Create Date: 2026-06-10 10:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect


revision: str = 'a3e7f2c91d01'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(inspector, table: str, column: str) -> bool:
    columns = [c["name"] for c in inspector.get_columns(table)]
    return column in columns


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not _column_exists(inspector, "staff", "emergency_contact_name"):
        op.add_column("staff", sa.Column("emergency_contact_name", sa.String(255), nullable=True))

    if not _column_exists(inspector, "staff", "emergency_contact_phone"):
        op.add_column("staff", sa.Column("emergency_contact_phone", sa.String(20), nullable=True))

    if not _column_exists(inspector, "staff", "emergency_contact_relationship"):
        op.add_column("staff", sa.Column("emergency_contact_relationship", sa.String(50), nullable=True))

    if not _column_exists(inspector, "staff", "blood_group"):
        op.add_column("staff", sa.Column("blood_group", sa.String(5), nullable=True))

    if not _column_exists(inspector, "users", "password_changed"):
        op.add_column("users", sa.Column("password_changed", sa.Boolean(), nullable=True, server_default="0"))

    # Parents table - ensure all columns exist
    if not _column_exists(inspector, "parents", "is_primary_contact"):
        op.add_column("parents", sa.Column("is_primary_contact", sa.Boolean(), nullable=True, server_default="0"))

    if not _column_exists(inspector, "parents", "relation"):
        op.add_column("parents", sa.Column("relation", sa.String(20), nullable=True))

    if not _column_exists(inspector, "parents", "occupation"):
        op.add_column("parents", sa.Column("occupation", sa.String(100), nullable=True))

    if not _column_exists(inspector, "parents", "annual_income"):
        op.add_column("parents", sa.Column("annual_income", sa.String(50), nullable=True))

    if not _column_exists(inspector, "parents", "alternate_phone"):
        op.add_column("parents", sa.Column("alternate_phone", sa.String(20), nullable=True))

    # Students table - ensure all columns exist
    if not _column_exists(inspector, "students", "blood_group"):
        op.add_column("students", sa.Column("blood_group", sa.String(5), nullable=True))

    if not _column_exists(inspector, "students", "religion"):
        op.add_column("students", sa.Column("religion", sa.String(50), nullable=True))

    if not _column_exists(inspector, "students", "nationality"):
        op.add_column("students", sa.Column("nationality", sa.String(50), nullable=True))

    if not _column_exists(inspector, "students", "caste"):
        op.add_column("students", sa.Column("caste", sa.String(50), nullable=True))

    if not _column_exists(inspector, "students", "mother_tongue"):
        op.add_column("students", sa.Column("mother_tongue", sa.String(50), nullable=True))

    if not _column_exists(inspector, "students", "medical_conditions"):
        op.add_column("students", sa.Column("medical_conditions", sa.Text(), nullable=True))

    if not _column_exists(inspector, "students", "allergies"):
        op.add_column("students", sa.Column("allergies", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("staff", "emergency_contact_name")
    op.drop_column("staff", "emergency_contact_phone")
    op.drop_column("staff", "emergency_contact_relationship")
    op.drop_column("staff", "blood_group")
    op.drop_column("users", "password_changed")
    op.drop_column("students", "blood_group")
    op.drop_column("students", "religion")
    op.drop_column("students", "nationality")
    op.drop_column("students", "caste")
    op.drop_column("students", "mother_tongue")
    op.drop_column("students", "medical_conditions")
    op.drop_column("students", "allergies")
