from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timedelta, timezone

from redis.asyncio import Redis
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.exceptions import (
    AuthenticationError,
    NotFound,
    TokenExpiredError,
    TokenInvalidError,
    ValidationError,
)
from src.core.security import (
    blacklist_token,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    is_token_blacklisted,
    verify_password,
)
from src.models.core import User


async def authenticate_user(
    db: AsyncSession, email: str, password: str, school_id: uuid.UUID | None = None
) -> User:
    """Authenticate a user by email and password."""
    query = select(User).where(User.email == email, User.is_active.is_(True))
    if school_id:
        query = query.where(User.school_id == school_id)

    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise AuthenticationError("Invalid email or password")

    if user.is_locked:
        raise AuthenticationError("Account is locked due to too many failed attempts")

    if not verify_password(password, user.password_hash):
        # Increment failed login attempts
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.is_locked = True
        await db.commit()
        raise AuthenticationError("Invalid email or password")

    # Reset failed attempts on successful login
    user.failed_login_attempts = 0
    user.last_login_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)

    return user


def create_tokens(user: User) -> tuple[str, str]:
    """Create access and refresh tokens for the user."""
    token_data = {"sub": str(user.id), "school_id": str(user.school_id), "role": user.role}

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return access_token, refresh_token


async def refresh_access_token(
    db: AsyncSession, redis: Redis, refresh_token_value: str
) -> tuple[str, str]:
    """Validate refresh token and issue new token pair."""
    from jose import JWTError

    try:
        payload = decode_token(refresh_token_value)
    except JWTError:
        raise TokenInvalidError()

    if payload.get("type") != "refresh":
        raise TokenInvalidError()

    jti = payload.get("jti")
    if not jti:
        raise TokenInvalidError()

    if await is_token_blacklisted(redis, jti):
        raise TokenExpiredError()

    user_id = payload.get("sub")
    if not user_id:
        raise TokenInvalidError()

    result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()

    if not user:
        raise AuthenticationError("User not found or inactive")

    # Blacklist old refresh token
    exp = payload.get("exp", 0)
    ttl = max(int(exp - datetime.utcnow().timestamp()), 0)
    if ttl > 0:
        await blacklist_token(redis, jti, ttl)

    # Create new token pair
    access_token, new_refresh_token = create_tokens(user)
    return access_token, new_refresh_token


async def logout_user(redis: Redis, refresh_token_value: str) -> None:
    """Blacklist the refresh token on logout."""
    from jose import JWTError

    try:
        payload = decode_token(refresh_token_value)
        jti = payload.get("jti")
        if jti:
            exp = payload.get("exp", 0)
            ttl = max(int(exp - datetime.utcnow().timestamp()), 0)
            if ttl > 0:
                await blacklist_token(redis, jti, ttl)
    except JWTError:
        # If token is invalid, nothing to blacklist
        pass


async def initiate_password_reset(db: AsyncSession, email: str) -> str | None:
    """Generate a password reset token for the user."""
    result = await db.execute(select(User).where(User.email == email, User.is_active.is_(True)))
    user = result.scalar_one_or_none()

    if not user:
        # Return None but do not reveal if user exists
        return None

    token = secrets.token_urlsafe(32)
    user.password_reset_token = token
    user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
    await db.commit()
    return token


async def reset_password(
    db: AsyncSession, token: str, new_password: str, confirm_password: str
) -> None:
    """Reset password using a valid token."""
    if new_password != confirm_password:
        raise ValidationError("Passwords do not match")

    result = await db.execute(
        select(User).where(
            User.password_reset_token == token,
            User.is_active.is_(True),
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise ValidationError("Invalid or expired reset token")

    if user.password_reset_expires and user.password_reset_expires < datetime.utcnow():
        raise ValidationError("Invalid or expired reset token")

    user.password_hash = hash_password(new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    user.is_locked = False
    user.failed_login_attempts = 0
    await db.commit()


async def change_password(
    db: AsyncSession,
    user: User,
    current_password: str,
    new_password: str,
    confirm_password: str,
) -> None:
    """Change password for the currently authenticated user."""
    if new_password != confirm_password:
        raise ValidationError("Passwords do not match")

    if not verify_password(current_password, user.password_hash):
        raise ValidationError("Current password is incorrect")

    if current_password == new_password:
        raise ValidationError("New password must be different from current password")

    user.password_hash = hash_password(new_password)
    user.password_changed = True
    await db.commit()
