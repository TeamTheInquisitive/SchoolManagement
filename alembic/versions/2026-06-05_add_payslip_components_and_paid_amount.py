"""Add component columns and paid_amount to payslips

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2026-06-05 23:30:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "c3d4e5f6g7h8"
down_revision = "b2c3d4e5f6g7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("payslips", sa.Column("hra", sa.Numeric(10, 2), server_default="0", nullable=False))
    op.add_column("payslips", sa.Column("da", sa.Numeric(10, 2), server_default="0", nullable=False))
    op.add_column("payslips", sa.Column("transport_allowance", sa.Numeric(10, 2), server_default="0", nullable=False))
    op.add_column("payslips", sa.Column("paid_amount", sa.Numeric(10, 2), server_default="0", nullable=False))


def downgrade() -> None:
    op.drop_column("payslips", "paid_amount")
    op.drop_column("payslips", "transport_allowance")
    op.drop_column("payslips", "da")
    op.drop_column("payslips", "hra")
