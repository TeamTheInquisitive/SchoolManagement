from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.pagination import PaginationParams

# Database session dependency
SessionDep = Annotated[AsyncSession, Depends(get_db)]

# Pagination dependency
PaginationDep = Annotated[PaginationParams, Depends()]


# Note: CurrentUser, AdminUser, TeacherUser, StudentUser, and SchoolDep
# are defined after auth dependencies are available to avoid circular imports.
# They are re-exported from src.auth.dependencies for convenience.
