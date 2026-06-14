from __future__ import annotations

import uuid
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import hash_password
from src.models.core import School, User
from src.models.staff import Staff
from src.models.student import Student
from src.models.subscription import Subscription, SubscriptionPayment


async def get_dashboard_stats(db: AsyncSession) -> dict:
    today = date.today()

    total_schools = (await db.execute(select(func.count(School.id)).where(School.is_active.is_(True)))).scalar() or 0
    total_students = (await db.execute(select(func.count(Student.id)).where(Student.is_active.is_(True)))).scalar() or 0
    total_staff = (await db.execute(select(func.count(Staff.id)).where(Staff.is_active.is_(True)))).scalar() or 0
    total_income = (await db.execute(
        select(func.coalesce(func.sum(SubscriptionPayment.amount), 0)).where(SubscriptionPayment.status == "paid")
    )).scalar() or 0

    active_subscriptions = (await db.execute(
        select(func.count(Subscription.id)).where(Subscription.is_active.is_(True))
    )).scalar() or 0

    # MRR: sum of monthly amounts for active subscriptions
    # For yearly plans, divide by 12
    monthly_sum = (await db.execute(
        select(func.coalesce(func.sum(Subscription.amount), 0)).where(
            Subscription.is_active.is_(True), Subscription.plan_type == "monthly"
        )
    )).scalar() or 0
    yearly_sum = (await db.execute(
        select(func.coalesce(func.sum(Subscription.amount), 0)).where(
            Subscription.is_active.is_(True), Subscription.plan_type == "yearly"
        )
    )).scalar() or 0
    mrr = float(monthly_sum) + float(yearly_sum) / 12

    # Schools expiring soon
    expiring_in_7 = (await db.execute(
        select(func.count(Subscription.id)).where(
            Subscription.is_active.is_(True),
            Subscription.end_date <= today + timedelta(days=7),
            Subscription.end_date >= today,
        )
    )).scalar() or 0

    expiring_in_30 = (await db.execute(
        select(func.count(Subscription.id)).where(
            Subscription.is_active.is_(True),
            Subscription.end_date <= today + timedelta(days=30),
            Subscription.end_date >= today,
        )
    )).scalar() or 0

    return {
        "total_schools": total_schools,
        "total_students": total_students,
        "total_staff": total_staff,
        "total_income": float(total_income),
        "active_subscriptions": active_subscriptions,
        "mrr": mrr,
        "expiring_in_7_days": expiring_in_7,
        "expiring_in_30_days": expiring_in_30,
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
            "is_active": s.is_active, "subscription_status": s.subscription_status,
            "enrollment_date": s.enrollment_date, "trial_end_date": s.trial_end_date,
            "created_at": s.created_at,
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

    # Get active subscription
    sub_result = await db.execute(
        select(Subscription).where(Subscription.school_id == school_id, Subscription.is_active.is_(True))
        .order_by(Subscription.created_at.desc())
    )
    sub = sub_result.scalar_one_or_none()
    subscription = None
    if sub:
        subscription = {
            "id": sub.id, "plan_type": sub.plan_type, "amount": float(sub.amount),
            "start_date": sub.start_date, "end_date": sub.end_date,
            "auto_renew": sub.auto_renew, "is_active": sub.is_active,
            "created_at": sub.created_at,
        }

    return {
        "id": school.id, "name": school.name, "code": school.code,
        "logo_url": school.logo_url,
        "city": school.city, "state": school.state, "address_line1": school.address_line1,
        "phone": school.phone, "email": school.email,
        "board_affiliation": school.board_affiliation, "principal_name": school.principal_name,
        "is_active": school.is_active, "created_at": school.created_at,
        "enrollment_date": school.enrollment_date,
        "subscription_status": school.subscription_status,
        "trial_start_date": school.trial_start_date,
        "trial_end_date": school.trial_end_date,
        "student_count": student_count, "staff_count": staff_count,
        "admin_users": admin_users,
        "subscription": subscription,
    }


async def create_school(db: AsyncSession, data: dict) -> School:
    if "code" not in data or not data["code"]:
        last_count = (await db.execute(select(func.count(School.id)))).scalar() or 0
        data["code"] = f"SCH{last_count + 1:03d}"
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


async def update_subscription_status(db: AsyncSession, school_id: uuid.UUID, data: dict) -> School | None:
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


async def create_subscription(db: AsyncSession, school_id: uuid.UUID, data: dict) -> Subscription:
    # Deactivate any existing active subscription
    existing = await db.execute(
        select(Subscription).where(Subscription.school_id == school_id, Subscription.is_active.is_(True))
    )
    for sub in existing.scalars().all():
        sub.is_active = False

    subscription = Subscription(school_id=school_id, **data)
    db.add(subscription)

    # Update school status to active
    school_result = await db.execute(select(School).where(School.id == school_id))
    school = school_result.scalar_one_or_none()
    if school:
        school.subscription_status = "active"

    await db.commit()
    await db.refresh(subscription)
    return subscription


async def update_subscription(db: AsyncSession, school_id: uuid.UUID, data: dict) -> Subscription | None:
    result = await db.execute(
        select(Subscription).where(Subscription.school_id == school_id, Subscription.is_active.is_(True))
    )
    subscription = result.scalar_one_or_none()
    if not subscription:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(subscription, k, v)
    await db.commit()
    await db.refresh(subscription)
    return subscription


async def get_subscription(db: AsyncSession, school_id: uuid.UUID) -> Subscription | None:
    result = await db.execute(
        select(Subscription).where(Subscription.school_id == school_id, Subscription.is_active.is_(True))
    )
    return result.scalar_one_or_none()


async def get_subscription_history(db: AsyncSession, school_id: uuid.UUID) -> dict:
    result = await db.execute(
        select(Subscription).where(Subscription.school_id == school_id)
        .order_by(Subscription.created_at.desc())
    )
    subs = result.scalars().all()
    items = [
        {
            "id": s.id, "plan_type": s.plan_type, "amount": float(s.amount),
            "start_date": s.start_date, "end_date": s.end_date,
            "auto_renew": s.auto_renew, "is_active": s.is_active,
            "created_at": s.created_at,
        }
        for s in subs
    ]
    return {"subscriptions": items, "total": len(items)}


async def create_payment(db: AsyncSession, school_id: uuid.UUID, data: dict) -> SubscriptionPayment:
    # Find active subscription
    sub_result = await db.execute(
        select(Subscription).where(Subscription.school_id == school_id, Subscription.is_active.is_(True))
    )
    subscription = sub_result.scalar_one_or_none()
    if not subscription:
        raise ValueError("No active subscription found")

    payment = SubscriptionPayment(
        subscription_id=subscription.id,
        school_id=school_id,
        **data,
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment


async def get_payments(db: AsyncSession, school_id: uuid.UUID) -> dict:
    result = await db.execute(
        select(SubscriptionPayment)
        .where(SubscriptionPayment.school_id == school_id)
        .order_by(SubscriptionPayment.payment_date.desc())
    )
    payments = result.scalars().all()
    items = [
        {
            "id": p.id, "subscription_id": p.subscription_id, "amount": float(p.amount),
            "payment_date": p.payment_date, "period_start": p.period_start,
            "period_end": p.period_end, "status": p.status, "notes": p.notes,
            "created_at": p.created_at,
        }
        for p in payments
    ]
    return {"payments": items, "total": len(items)}


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
            "is_locked": u.is_locked, "failed_login_attempts": u.failed_login_attempts,
            "school_name": school_name, "last_login_at": u.last_login_at,
        })
    return {"users": items, "total": len(items)}
