"""Add applicable_to and members to leave_policies

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-05 09:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "b2c3d4e5f6g7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("leave_policies", sa.Column("applicable_to", sa.String(255), nullable=True, server_default="all"))
    op.add_column("leave_policies", sa.Column("members", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("leave_policies", "members")
    op.drop_column("leave_policies", "applicable_to")
