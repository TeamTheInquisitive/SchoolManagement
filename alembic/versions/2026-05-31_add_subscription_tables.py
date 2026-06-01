"""Add subscription tables and fields to schools

Revision ID: a1b2c3d4e5f6
Revises: 2026-05-26_add_max_periods_to_classes
Create Date: 2026-05-31 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add subscription columns to schools table
    op.add_column("schools", sa.Column("enrollment_date", sa.Date(), nullable=True))
    op.add_column("schools", sa.Column("subscription_status", sa.String(20), nullable=False, server_default="trial"))
    op.add_column("schools", sa.Column("trial_start_date", sa.Date(), nullable=True))
    op.add_column("schools", sa.Column("trial_end_date", sa.Date(), nullable=True))

    # Create subscriptions table
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("school_id", sa.CHAR(36), sa.ForeignKey("schools.id"), nullable=False, index=True),
        sa.Column("plan_type", sa.String(20), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("auto_renew", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Create subscription_payments table
    op.create_table(
        "subscription_payments",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("subscription_id", sa.CHAR(36), sa.ForeignKey("subscriptions.id"), nullable=False, index=True),
        sa.Column("school_id", sa.CHAR(36), sa.ForeignKey("schools.id"), nullable=False, index=True),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="paid"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("subscription_payments")
    op.drop_table("subscriptions")
    op.drop_column("schools", "trial_end_date")
    op.drop_column("schools", "trial_start_date")
    op.drop_column("schools", "subscription_status")
    op.drop_column("schools", "enrollment_date")
