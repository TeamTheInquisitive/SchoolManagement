"""merge_heads

Revision ID: 4756d4a567f9
Revises: c3d4e5f6g7h8, a3e7f2c91d01
Create Date: 2026-06-10 23:28:17.989023

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4756d4a567f9'
down_revision: Union[str, None] = ('c3d4e5f6g7h8', 'a3e7f2c91d01')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
