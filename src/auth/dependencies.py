from __future__ import annotations

from typing import Annotated

from fastapi import Cookie, Depends, Request
from jose import JWTError
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.exceptions import (
    AccessDenied,
    AuthenticationError,
    TokenExpiredError,
    TokenInvalidError,
)
from src.core.redis import get_redis
from src.core.security import decode_token, is_token_blacklisted
from src.models.core import School, User


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    access_token: str | None = Cookie(default=None),
) -> User:
    """Extract and validate the current user from the access token cookie."""
    if not access_token:
        raise AuthenticationError("Not authenticated")

    try:
        payload = decode_token(access_token)
    except JWTError:
        raise TokenInvalidError()

    if payload.get("type") != "access":
        raise TokenInvalidError()

    # Check blacklist if jti exists
    jti = payload.get("jti")
    if jti and await is_token_blacklisted(redis, jti):
        raise TokenExpiredError()

    user_id = payload.get("sub")
    if not user_id:
        raise TokenInvalidError()

    result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()

    if not user:
        raise AuthenticationError("User not found or inactive")

    if user.is_locked:
        raise AuthenticationError("Account is locked")

    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require the current user to have admin role."""
    if user.role != "admin":
        raise AccessDenied("Admin access required")
    return user


async def require_teacher(user: User = Depends(get_current_user)) -> User:
    """Require the current user to have teacher role."""
    if user.role not in ("teacher", "admin"):
        raise AccessDenied("Teacher access required")
    return user


async def require_student(user: User = Depends(get_current_user)) -> User:
    """Require the current user to have student role."""
    if user.role != "student":
        raise AccessDenied("Student access required")
    return user


async def get_current_school(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> School:
    """Get the current school from the authenticated user's school_id."""
    result = await db.execute(
        select(School).where(School.id == user.school_id, School.is_active.is_(True))
    )
    school = result.scalar_one_or_none()
    if not school:
        raise AuthenticationError("School not found or inactive")
    return school


# Annotated type aliases for use in route signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]
TeacherUser = Annotated[User, Depends(require_teacher)]
StudentUser = Annotated[User, Depends(require_student)]
SchoolDep = Annotated[School, Depends(get_current_school)]
