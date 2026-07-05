"""Add academic_year_id to staff_subjects, salary_advances, route_assignments

Revision ID: a7b8c9d0e1f2
Revises: b1c2d3e4f5a6
Create Date: 2026-07-04 10:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect, text


# revision identifiers, used by Alembic.
revision: str = 'a7b8c9d0e1f2'
down_revision: Union[str, None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(inspector, table: str, column: str) -> bool:
    columns = [c["name"] for c in inspector.get_columns(table)]
    return column in columns


def _index_exists(inspector, table: str, index_name: str) -> bool:
    indexes = inspector.get_indexes(table)
    return any(i["name"] == index_name for i in indexes)


def _constraint_exists(inspector, table: str, constraint_name: str) -> bool:
    uqs = inspector.get_unique_constraints(table)
    return any(c["name"] == constraint_name for c in uqs)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    # --- staff_subjects: add academic_year_id ---
    if not _column_exists(inspector, "staff_subjects", "academic_year_id"):
        # Add as nullable first for backfill
        op.add_column(
            "staff_subjects",
            sa.Column("academic_year_id", sa.CHAR(36), nullable=True),
        )

        # Backfill: set to the current academic year per school
        bind.execute(text("""
            UPDATE staff_subjects ss
            JOIN (
                SELECT id, school_id FROM academic_years WHERE is_current = 1
            ) ay ON ay.school_id = ss.school_id
            SET ss.academic_year_id = ay.id
            WHERE ss.academic_year_id IS NULL
        """))

        # For any remaining rows without a current academic year, use the latest one
        bind.execute(text("""
            UPDATE staff_subjects ss
            JOIN (
                SELECT school_id, MAX(id) as id FROM academic_years GROUP BY school_id
            ) ay ON ay.school_id = ss.school_id
            SET ss.academic_year_id = ay.id
            WHERE ss.academic_year_id IS NULL
        """))

        # Make NOT NULL
        op.alter_column("staff_subjects", "academic_year_id", nullable=False, existing_type=sa.CHAR(36))

        # Add FK
        op.create_foreign_key(
            "fk_staff_subjects_academic_year_id_academic_years",
            "staff_subjects",
            "academic_years",
            ["academic_year_id"],
            ["id"],
        )

    # Drop old unique constraint & add new one with academic_year_id
    if _constraint_exists(inspector, "staff_subjects", "uq_staff_subjects_staff_subject"):
        op.drop_constraint("uq_staff_subjects_staff_subject", "staff_subjects", type_="unique")

    if not _constraint_exists(inspector, "staff_subjects", "uq_staff_subjects_staff_subject_year"):
        op.create_unique_constraint(
            "uq_staff_subjects_staff_subject_year",
            "staff_subjects",
            ["school_id", "staff_id", "subject_id", "academic_year_id"],
        )

    if not _index_exists(inspector, "staff_subjects", "idx_staff_subjects_year"):
        op.create_index("idx_staff_subjects_year", "staff_subjects", ["school_id", "academic_year_id"])

    # --- salary_advances: add academic_year_id ---
    if not _column_exists(inspector, "salary_advances", "academic_year_id"):
        op.add_column(
            "salary_advances",
            sa.Column("academic_year_id", sa.CHAR(36), nullable=True),
        )

        # Backfill with current academic year per school
        bind.execute(text("""
            UPDATE salary_advances sa
            JOIN (
                SELECT id, school_id FROM academic_years WHERE is_current = 1
            ) ay ON ay.school_id = sa.school_id
            SET sa.academic_year_id = ay.id
            WHERE sa.academic_year_id IS NULL
        """))

        bind.execute(text("""
            UPDATE salary_advances sa
            JOIN (
                SELECT school_id, MAX(id) as id FROM academic_years GROUP BY school_id
            ) ay ON ay.school_id = sa.school_id
            SET sa.academic_year_id = ay.id
            WHERE sa.academic_year_id IS NULL
        """))

        op.alter_column("salary_advances", "academic_year_id", nullable=False, existing_type=sa.CHAR(36))

        op.create_foreign_key(
            "fk_salary_advances_academic_year_id_academic_years",
            "salary_advances",
            "academic_years",
            ["academic_year_id"],
            ["id"],
        )

    if not _index_exists(inspector, "salary_advances", "idx_salary_advances_year"):
        op.create_index("idx_salary_advances_year", "salary_advances", ["school_id", "academic_year_id"])

    # --- route_assignments: add academic_year_id ---
    if not _column_exists(inspector, "route_assignments", "academic_year_id"):
        op.add_column(
            "route_assignments",
            sa.Column("academic_year_id", sa.CHAR(36), nullable=True),
        )

        # Backfill with current academic year per school
        bind.execute(text("""
            UPDATE route_assignments ra
            JOIN (
                SELECT id, school_id FROM academic_years WHERE is_current = 1
            ) ay ON ay.school_id = ra.school_id
            SET ra.academic_year_id = ay.id
            WHERE ra.academic_year_id IS NULL
        """))

        bind.execute(text("""
            UPDATE route_assignments ra
            JOIN (
                SELECT school_id, MAX(id) as id FROM academic_years GROUP BY school_id
            ) ay ON ay.school_id = ra.school_id
            SET ra.academic_year_id = ay.id
            WHERE ra.academic_year_id IS NULL
        """))

        op.alter_column("route_assignments", "academic_year_id", nullable=False, existing_type=sa.CHAR(36))

        op.create_foreign_key(
            "fk_route_assignments_academic_year_id_academic_years",
            "route_assignments",
            "academic_years",
            ["academic_year_id"],
            ["id"],
        )

    # Drop old unique constraint & add new one with academic_year_id
    if _constraint_exists(inspector, "route_assignments", "uq_route_assignments_school_vehicle_active"):
        op.drop_constraint("uq_route_assignments_school_vehicle_active", "route_assignments", type_="unique")

    if not _constraint_exists(inspector, "route_assignments", "uq_route_assignments_school_vehicle_year_active"):
        op.create_unique_constraint(
            "uq_route_assignments_school_vehicle_year_active",
            "route_assignments",
            ["school_id", "vehicle_id", "academic_year_id", "is_active"],
        )

    if not _index_exists(inspector, "route_assignments", "idx_route_assignments_year"):
        op.create_index("idx_route_assignments_year", "route_assignments", ["school_id", "academic_year_id"])


def downgrade() -> None:
    # --- route_assignments ---
    op.drop_index("idx_route_assignments_year", table_name="route_assignments")
    op.drop_constraint("uq_route_assignments_school_vehicle_year_active", "route_assignments", type_="unique")
    op.create_unique_constraint(
        "uq_route_assignments_school_vehicle_active",
        "route_assignments",
        ["school_id", "vehicle_id", "is_active"],
    )
    op.drop_constraint("fk_route_assignments_academic_year_id_academic_years", "route_assignments", type_="foreignkey")
    op.drop_column("route_assignments", "academic_year_id")

    # --- salary_advances ---
    op.drop_index("idx_salary_advances_year", table_name="salary_advances")
    op.drop_constraint("fk_salary_advances_academic_year_id_academic_years", "salary_advances", type_="foreignkey")
    op.drop_column("salary_advances", "academic_year_id")

    # --- staff_subjects ---
    op.drop_index("idx_staff_subjects_year", table_name="staff_subjects")
    op.drop_constraint("uq_staff_subjects_staff_subject_year", "staff_subjects", type_="unique")
    op.create_unique_constraint(
        "uq_staff_subjects_staff_subject",
        "staff_subjects",
        ["school_id", "staff_id", "subject_id"],
    )
    op.drop_constraint("fk_staff_subjects_academic_year_id_academic_years", "staff_subjects", type_="foreignkey")
    op.drop_column("staff_subjects", "academic_year_id")
