from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory, get_db
from src.core.pagination import PaginationParams


async def get_db_with_audit(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Yield a DB session with MySQL @current_user_id set from request state (middleware)."""
    async with async_session_factory() as session:
        try:
            audit_user_id = getattr(getattr(request, "state", None), "audit_user_id", None)
            if audit_user_id:
                await session.execute(
                    text("SET @current_user_id = :uid"), {"uid": str(audit_user_id)}
                )
            yield session
        finally:
            await session.close()


# Database session dependency (audit-aware: sets @current_user_id from middleware)
SessionDep = Annotated[AsyncSession, Depends(get_db_with_audit)]

# Plain session without audit context (for auth dependency internal use)
PlainSessionDep = Annotated[AsyncSession, Depends(get_db)]

# Pagination dependency
PaginationDep = Annotated[PaginationParams, Depends()]


# Note: CurrentUser, AdminUser, TeacherUser, StudentUser, and SchoolDep
# are defined after auth dependencies are available to avoid circular imports.
# They are re-exported from src.auth.dependencies for convenience.
