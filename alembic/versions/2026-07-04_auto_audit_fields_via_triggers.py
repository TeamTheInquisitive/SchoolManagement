"""Auto audit fields via DB triggers and timestamp defaults

Revision ID: c3d4e5f6a7b8
Revises: a7b8c9d0e1f2
Create Date: 2026-07-04 12:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'a7b8c9d0e1f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Tables that use BaseModel (have created_at, updated_at, created_by, updated_by)
BASEMODEL_TABLES = [
    "academic_years",
    "settings",
    "enum_configs",
    "classes",
    "sections",
    "class_sections",
    "subjects",
    "class_subjects",
    "students",
    "student_enrollments",
    "parents",
    "student_parents",
    "student_mentors",
    "staff",
    "staff_subjects",
    "class_assignments",
    "period_configs",
    "timetable_slots",
    "attendance_sessions",
    "attendance_records",
    "exams",
    "exam_results",
    "grade_systems",
    "grade_scales",
    "leave_policies",
    "leave_applications",
    "leave_balances",
    "fee_structures",
    "fee_records",
    "fee_payments",
    "fee_reminders",
    "fee_penalties",
    "salary_structures",
    "payslips",
    "salary_advances",
    "salary_revisions",
    "assignments",
    "assignment_submissions",
    "vehicles",
    "drivers",
    "helpers",
    "routes",
    "route_assignments",
    "student_transport",
    "library_books",
    "library_issues",
    "notifications",
    "notification_recipients",
    "activities",
    "awards",
    "disciplinary_records",
    "parent_meetings",
    "adhoc_classes",
]

# Tables that use TimestampMixin + AuditMixin directly (not BaseModel) but still have audit fields
AUDIT_TABLES_NON_BASEMODEL = [
    "schools",
    "users",
]

# All tables with audit triggers
ALL_AUDIT_TABLES = BASEMODEL_TABLES + AUDIT_TABLES_NON_BASEMODEL

# Tables with timestamps but no audit fields
TIMESTAMP_ONLY_TABLES = [
    "subscriptions",
    "subscription_payments",
]


def upgrade() -> None:
    # --- Step 1: Alter timestamp columns to use MySQL defaults ---
    all_timestamp_tables = BASEMODEL_TABLES + AUDIT_TABLES_NON_BASEMODEL + TIMESTAMP_ONLY_TABLES

    for table in all_timestamp_tables:
        # ALTER created_at to have DEFAULT CURRENT_TIMESTAMP
        op.execute(sa.text(
            f"ALTER TABLE `{table}` MODIFY COLUMN `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"
        ))
        # ALTER updated_at to have DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        op.execute(sa.text(
            f"ALTER TABLE `{table}` MODIFY COLUMN `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        ))

    # Also handle platform_settings (only has updated_at)
    op.execute(sa.text(
        "ALTER TABLE `platform_settings` MODIFY COLUMN `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
    ))

    # --- Step 2: Create BEFORE INSERT and BEFORE UPDATE triggers for audit fields ---
    for table in ALL_AUDIT_TABLES:
        # BEFORE INSERT trigger
        op.execute(sa.text(f"""
            CREATE TRIGGER `{table}_before_insert` BEFORE INSERT ON `{table}`
            FOR EACH ROW
            BEGIN
                IF NEW.created_by IS NULL AND @current_user_id IS NOT NULL THEN
                    SET NEW.created_by = @current_user_id;
                END IF;
                IF NEW.updated_by IS NULL THEN
                    SET NEW.updated_by = @current_user_id;
                END IF;
            END
        """))

        # BEFORE UPDATE trigger
        op.execute(sa.text(f"""
            CREATE TRIGGER `{table}_before_update` BEFORE UPDATE ON `{table}`
            FOR EACH ROW
            BEGIN
                IF @current_user_id IS NOT NULL THEN
                    SET NEW.updated_by = @current_user_id;
                END IF;
            END
        """))


def downgrade() -> None:
    # Drop all triggers
    for table in ALL_AUDIT_TABLES:
        op.execute(sa.text(f"DROP TRIGGER IF EXISTS `{table}_before_insert`"))
        op.execute(sa.text(f"DROP TRIGGER IF EXISTS `{table}_before_update`"))

    # Revert timestamp column defaults (remove ON UPDATE)
    all_timestamp_tables = BASEMODEL_TABLES + AUDIT_TABLES_NON_BASEMODEL + TIMESTAMP_ONLY_TABLES
    for table in all_timestamp_tables:
        op.execute(sa.text(
            f"ALTER TABLE `{table}` MODIFY COLUMN `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP"
        ))
        op.execute(sa.text(
            f"ALTER TABLE `{table}` MODIFY COLUMN `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP"
        ))

    op.execute(sa.text(
        "ALTER TABLE `platform_settings` MODIFY COLUMN `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP"
    ))
