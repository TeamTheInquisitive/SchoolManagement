from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=False,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def set_audit_context(db: AsyncSession, user_id: uuid.UUID | None) -> None:
    """Set the @current_user_id MySQL session variable for trigger-based auditing."""
    if user_id:
        await db.execute(text("SET @current_user_id = :uid"), {"uid": str(user_id)})


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Async generator that yields a database session."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_db_with_audit(request) -> AsyncGenerator[AsyncSession, None]:
    """Async generator that yields a DB session with @current_user_id set from request state."""
    async with async_session_factory() as session:
        try:
            # Set the MySQL session variable if we have a user context
            audit_user_id = getattr(getattr(request, "state", None), "audit_user_id", None)
            if audit_user_id:
                await session.execute(
                    text("SET @current_user_id = :uid"), {"uid": str(audit_user_id)}
                )
            yield session
        finally:
            await session.close()
