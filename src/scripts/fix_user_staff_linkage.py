"""
One-time migration script: Fix User.staff_id linkage for all teachers.

Problem: When teachers were created, only Staff.user_id was set but User.staff_id was NOT.
This script finds all Staff records with a linked user_id and ensures the reverse
link (User.staff_id) is also set.

Run: python -m src.scripts.fix_user_staff_linkage
"""
import asyncio

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_maker
from src.models.core import User
from src.models.staff import Staff


async def fix_linkage():
    async with async_session_maker() as db:
        # Find all staff with user_id set
        result = await db.execute(
            select(Staff.id, Staff.user_id, Staff.email)
            .where(Staff.user_id.isnot(None), Staff.is_active.is_(True))
        )
        staff_records = result.all()

        fixed = 0
        already_ok = 0
        not_found = 0

        for staff_id, user_id, staff_email in staff_records:
            # Check if User.staff_id is already set
            user_result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()

            if not user:
                not_found += 1
                continue

            if user.staff_id == staff_id:
                already_ok += 1
                continue

            # Fix: set User.staff_id
            user.staff_id = staff_id
            fixed += 1
            print(f"  Fixed: {user.email} → staff_id={staff_id}")

        # Also fix by email match where Staff.user_id is NULL
        result2 = await db.execute(
            select(Staff.id, Staff.email)
            .where(Staff.user_id.is_(None), Staff.email.isnot(None), Staff.is_active.is_(True))
        )
        unlinked_staff = result2.all()

        for staff_id, email in unlinked_staff:
            user_result = await db.execute(
                select(User).where(User.email == email, User.is_active.is_(True))
            )
            user = user_result.scalar_one_or_none()
            if user and not user.staff_id:
                user.staff_id = staff_id
                fixed += 1
                print(f"  Fixed (by email): {email} → staff_id={staff_id}")

        await db.commit()

        print(f"\nDone!")
        print(f"  Fixed: {fixed}")
        print(f"  Already OK: {already_ok}")
        print(f"  User not found: {not_found}")


if __name__ == "__main__":
    asyncio.run(fix_linkage())
