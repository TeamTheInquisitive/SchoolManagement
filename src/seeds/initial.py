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
    """Create default school and admin user if they don't exist."""
    async with async_session_factory() as db:
        # Check if default school exists
        result = await db.execute(select(School).where(School.code == "SCH001"))
        school = result.scalar_one_or_none()

        if not school:
            school = School(
                id=uuid.uuid4(),
                name="Default School",
                code="SCH001",
                address_line1="123 School Street",
                city="Bangalore",
                state="Karnataka",
                country="India",
                pincode="560001",
                phone="+91-9876543210",
                email="admin@defaultschool.com",
                board_affiliation="CBSE",
                established_year=2000,
                principal_name="Dr. Principal",
            )
            db.add(school)
            await db.flush()
            print(f"Created school: {school.name} (code: {school.code})")
        else:
            print(f"School already exists: {school.name} (code: {school.code})")

        # Create demo users
        demo_users = [
            {
                "email": "admin@school.com",
                "password": "password123",
                "full_name": "System Admin",
                "role": "admin",
                "phone": "+91-9876543210",
            },
            {
                "email": "jane@teacher.com",
                "password": "password123",
                "full_name": "Jane Smith",
                "role": "teacher",
                "phone": "+91-9876543211",
            },
            {
                "email": "john@student.com",
                "password": "password123",
                "full_name": "John Doe",
                "role": "student",
                "phone": "+91-9876543212",
            },
        ]

        for user_data in demo_users:
            result = await db.execute(
                select(User).where(
                    User.school_id == school.id,
                    User.email == user_data["email"],
                )
            )
            existing = result.scalar_one_or_none()

            if not existing:
                user = User(
                    id=uuid.uuid4(),
                    school_id=school.id,
                    email=user_data["email"],
                    password_hash=hash_password(user_data["password"]),
                    full_name=user_data["full_name"],
                    role=user_data["role"],
                    phone=user_data["phone"],
                )
                db.add(user)
                print(f"  Created {user_data['role']}: {user_data['email']} / {user_data['password']}")
            else:
                print(f"  Already exists: {user_data['email']}")

        await db.commit()
        print("\nSeed completed successfully!")
        print("\nDemo Credentials:")
        print("  Admin:   admin@school.com / password123")
        print("  Teacher: jane@teacher.com / password123")
        print("  Student: john@student.com / password123")


async def main() -> None:
    try:
        await seed_initial_data()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
