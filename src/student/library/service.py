from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.pagination import PaginationParams, paginate
from src.models.core import User


async def get_my_books(db: AsyncSession, school_id: uuid.UUID, user: User) -> dict:
    """
    Get student's currently borrowed books and summary.

    Note: Library is a V2 feature on the admin side. This endpoint reads
    from whatever data exists. Returns empty/stub data if no library tables exist.
    """
    # Stub implementation - library tables are V2
    return {
        "summary": {
            "total_borrowed": 0,
            "currently_holding": 0,
            "overdue": 0,
            "total_fines": 0,
        },
        "books": [],
    }


async def get_catalog(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    pagination: PaginationParams,
    search: str | None = None,
    category: str | None = None,
) -> dict:
    """
    Browse the library catalog.

    Note: Library is a V2 feature. Returns empty results.
    """
    return paginate([], 0, pagination)


async def get_borrowing_history(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    pagination: PaginationParams,
) -> dict:
    """
    Get borrowing history for the student.

    Note: Library is a V2 feature. Returns empty results.
    """
    return paginate([], 0, pagination)


async def get_fines(db: AsyncSession, school_id: uuid.UUID, user: User) -> dict:
    """
    Get fine details for the student.

    Note: Library is a V2 feature. Returns empty results.
    """
    return {
        "total_fines": 0,
        "total_paid": 0,
        "total_pending": 0,
        "items": [],
    }
