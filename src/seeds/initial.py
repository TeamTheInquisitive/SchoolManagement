"""
Seed script: Creates a default school and admin user.

Usage:
    python -m src.seeds.initial
"""
from __future__ import annotations

import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory, engine
from src.core.security import hash_password
from src.models.core import School, User


async def seed_initial_data() -> None:
    """Create the platform super admin user (no school required)."""
    async with async_session_factory() as db:
        result = await db.execute(
            select(User).where(User.role == "super_admin")
        )
        superadmin = result.scalar_one_or_none()

        if not superadmin:
            superadmin = User(
                id=uuid.uuid4(),
                school_id=None,
                email="superadmin@erp.com",
                password_hash=hash_password("admin@123"),
                full_name="Super Admin",
                role="super_admin",
            )
            db.add(superadmin)
            await db.commit()
            print("Created super_admin: superadmin@erp.com / admin@123")
        else:
            print(f"Super admin already exists: {superadmin.email}")


async def main() -> None:
    try:
        await seed_initial_data()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
