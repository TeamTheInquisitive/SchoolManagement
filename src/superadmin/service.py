from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import hash_password
from src.models.core import School, User
from src.models.staff import Staff
from src.models.student import Student
from src.models.fee import FeePayment


async def get_dashboard_stats(db: AsyncSession) -> dict:
    total_schools = (await db.execute(select(func.count(School.id)).where(School.is_active.is_(True)))).scalar() or 0
    total_students = (await db.execute(select(func.count(Student.id)).where(Student.is_active.is_(True)))).scalar() or 0
    total_staff = (await db.execute(select(func.count(Staff.id)).where(Staff.is_active.is_(True)))).scalar() or 0
    total_revenue = (await db.execute(select(func.coalesce(func.sum(FeePayment.amount), 0)))).scalar() or 0
    return {
        "total_schools": total_schools,
        "total_students": total_students,
        "total_staff": total_staff,
        "total_revenue": float(total_revenue),
    }


async def get_schools(db: AsyncSession) -> dict:
    result = await db.execute(select(School).where(School.is_active.is_(True)).order_by(School.name))
    schools = result.scalars().all()

    items = []
    for s in schools:
        student_count = (await db.execute(
            select(func.count(Student.id)).where(Student.school_id == s.id, Student.is_active.is_(True))
        )).scalar() or 0
        staff_count = (await db.execute(
            select(func.count(Staff.id)).where(Staff.school_id == s.id, Staff.is_active.is_(True))
        )).scalar() or 0
        items.append({
            "id": s.id, "name": s.name, "code": s.code, "city": s.city,
            "student_count": student_count, "staff_count": staff_count,
            "is_active": s.is_active, "created_at": s.created_at,
        })
    return {"schools": items, "total": len(items)}


async def get_school_detail(db: AsyncSession, school_id: uuid.UUID) -> dict | None:
    result = await db.execute(select(School).where(School.id == school_id))
    school = result.scalar_one_or_none()
    if not school:
        return None

    student_count = (await db.execute(
        select(func.count(Student.id)).where(Student.school_id == school_id, Student.is_active.is_(True))
    )).scalar() or 0
    staff_count = (await db.execute(
        select(func.count(Staff.id)).where(Staff.school_id == school_id, Staff.is_active.is_(True))
    )).scalar() or 0

    admins_result = await db.execute(
        select(User).where(User.school_id == school_id, User.role == "admin", User.is_active.is_(True))
    )
    admin_users = [
        {"id": u.id, "email": u.email, "full_name": u.full_name, "role": u.role,
         "phone": u.phone, "is_active": u.is_active, "last_login_at": u.last_login_at}
        for u in admins_result.scalars().all()
    ]

    return {
        "id": school.id, "name": school.name, "code": school.code,
        "city": school.city, "state": school.state, "address_line1": school.address_line1,
        "phone": school.phone, "email": school.email,
        "board_affiliation": school.board_affiliation, "principal_name": school.principal_name,
        "is_active": school.is_active, "created_at": school.created_at,
        "student_count": student_count, "staff_count": staff_count,
        "admin_users": admin_users,
    }


async def create_school(db: AsyncSession, data: dict) -> School:
    school = School(**data)
    db.add(school)
    await db.commit()
    await db.refresh(school)
    return school


async def update_school(db: AsyncSession, school_id: uuid.UUID, data: dict) -> School | None:
    result = await db.execute(select(School).where(School.id == school_id))
    school = result.scalar_one_or_none()
    if not school:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(school, k, v)
    await db.commit()
    await db.refresh(school)
    return school


async def create_admin_for_school(db: AsyncSession, school_id: uuid.UUID, data: dict) -> User:
    user = User(
        school_id=school_id,
        email=data["email"],
        full_name=data["full_name"],
        password_hash=hash_password(data["password"]),
        role="admin",
        phone=data.get("phone"),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_users(db: AsyncSession, role: str | None = None, school_id: uuid.UUID | None = None) -> dict:
    query = select(User).where(User.is_active.is_(True))
    if role:
        query = query.where(User.role == role)
    if school_id:
        query = query.where(User.school_id == school_id)
    query = query.order_by(User.full_name)

    result = await db.execute(query)
    users = result.scalars().all()

    items = []
    for u in users:
        school_name = u.school.name if u.school else None
        items.append({
            "id": u.id, "email": u.email, "full_name": u.full_name,
            "role": u.role, "phone": u.phone, "is_active": u.is_active,
            "school_name": school_name, "last_login_at": u.last_login_at,
        })
    return {"users": items, "total": len(items)}
