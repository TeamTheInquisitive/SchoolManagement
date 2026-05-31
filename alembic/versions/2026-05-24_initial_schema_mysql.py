"""initial_schema_mysql

Revision ID: f19fe354557b
Revises: 
Create Date: 2026-05-24 11:45:21.483996

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect

from src.core.base_model import Base


# revision identifiers, used by Alembic.
revision: str = 'f19fe354557b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables from model metadata."""
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = inspector.get_table_names()

    # Create tables that don't already exist
    tables_to_create = [
        table for table in Base.metadata.sorted_tables
        if table.name not in existing_tables
    ]
    Base.metadata.create_all(bind=bind, tables=tables_to_create)


def downgrade() -> None:
    """Drop all tables in reverse dependency order."""
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
