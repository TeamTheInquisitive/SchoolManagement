from __future__ import annotations

import math
import uuid
from datetime import date, timedelta

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import hash_password
from src.models.core import School, Settings, User
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
         "phone": u.phone, "is_active": u.is_active, "last_login_at": u.last_login_at,
         "allowed_modules": u.allowed_modules}
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

    # Auto-derive id_prefix from school name if not provided
    if "id_prefix" not in data or not data.get("id_prefix"):
        name = data.get("name", "")
        prefix = ''.join(name.split()).upper()[:3]
        # Check uniqueness, append number if collision
        base_prefix = prefix
        suffix = 1
        while True:
            existing = await db.execute(
                select(School).where(School.id_prefix == prefix)
            )
            if not existing.scalar_one_or_none():
                break
            prefix = f"{base_prefix}{suffix}"[:6]
            suffix += 1
        data["id_prefix"] = prefix

    school = School(**data)
    db.add(school)
    await db.flush()

    # Seed ID generation config using the school's prefix
    prefix = data["id_prefix"]
    id_config = {
        "student": {"enabled": True, "pattern": f"{prefix}" + "{YY}{SEQ:4}", "next_seq": 1},
        "teacher": {"enabled": True, "pattern": f"{prefix}T" + "{YY}{SEQ:4}", "next_seq": 1},
        "staff": {"enabled": True, "pattern": f"{prefix}S" + "{YY}{SEQ:4}", "next_seq": 1},
    }
    id_setting = Settings(
        school_id=school.id,
        category="id_generation",
        key="config",
        value=id_config,
    )
    db.add(id_setting)

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
        allowed_modules=data.get("allowed_modules"),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_admin_for_school(db: AsyncSession, school_id: uuid.UUID, admin_id: uuid.UUID, data: dict) -> User | None:
    result = await db.execute(
        select(User).where(User.id == admin_id, User.school_id == school_id, User.role == "admin")
    )
    user = result.scalar_one_or_none()
    if not user:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(user, k, v)
    await db.commit()
    await db.refresh(user)
    return user


async def reset_admin_password(db: AsyncSession, school_id: uuid.UUID, admin_id: uuid.UUID, new_password: str) -> User | None:
    result = await db.execute(
        select(User).where(User.id == admin_id, User.school_id == school_id, User.role == "admin")
    )
    user = result.scalar_one_or_none()
    if not user:
        return None
    user.password_hash = hash_password(new_password)
    user.password_changed = False
    user.failed_login_attempts = 0
    user.is_locked = False
    await db.commit()
    await db.refresh(user)
    return user


async def delete_admin_for_school(db: AsyncSession, school_id: uuid.UUID, admin_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(User).where(User.id == admin_id, User.school_id == school_id, User.role == "admin")
    )
    user = result.scalar_one_or_none()
    if not user:
        return False
    await db.delete(user)
    await db.commit()
    return True


async def get_school_classes(db: AsyncSession, school_id: uuid.UUID) -> dict:
    from src.models.academic import Class, ClassSection, Section

    result = await db.execute(
        select(Class).where(Class.school_id == school_id).order_by(Class.sort_order, Class.name)
    )
    classes = result.scalars().all()

    items = []
    for cls in classes:
        cs_result = await db.execute(
            select(ClassSection).where(
                ClassSection.school_id == school_id,
                ClassSection.class_id == cls.id,
            )
        )
        sections = []
        for cs in cs_result.scalars().all():
            if cs.section:
                sections.append({"id": cs.section.id, "section_name": cs.section.name})
        items.append({
            "id": cls.id,
            "name": cls.name,
            "display_name": cls.display_name or cls.name,
            "sections": sections,
        })
    return {"classes": items}


async def get_users(
    db: AsyncSession,
    role: str | None = None,
    school_id: uuid.UUID | None = None,
    search: str | None = None,
    class_name: str | None = None,
    section: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    from src.models.student import StudentEnrollment
    from src.models.academic import ClassSection, Class, Section

    query = select(User).where(User.is_active.is_(True))
    if role:
        query = query.where(User.role == role)
    if school_id:
        query = query.where(User.school_id == school_id)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            (User.full_name.ilike(pattern)) | (User.email.ilike(pattern))
        )
    if (class_name or section) and school_id:
        query = query.where(User.role == "student")
        enrollment_query = select(StudentEnrollment.student_id).join(
            ClassSection, StudentEnrollment.class_section_id == ClassSection.id
        ).join(Class, ClassSection.class_id == Class.id)
        if class_name:
            enrollment_query = enrollment_query.where(Class.name == class_name)
        if section:
            enrollment_query = enrollment_query.join(
                Section, ClassSection.section_id == Section.id
            ).where(Section.name == section)
        enrollment_query = enrollment_query.where(ClassSection.school_id == school_id)
        student_ids = (await db.execute(enrollment_query)).scalars().all()
        query = query.where(User.student_id.in_(student_ids))

    query = query.order_by(User.full_name)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    users = result.scalars().all()

    student_user_ids = [u.student_id for u in users if u.role == "student" and u.student_id]
    roll_map = {}
    if student_user_ids:
        enrollment_result = await db.execute(
            select(StudentEnrollment).where(
                StudentEnrollment.student_id.in_(student_user_ids)
            ).order_by(StudentEnrollment.created_at.desc())
        )
        for e in enrollment_result.scalars().all():
            if e.student_id not in roll_map:
                roll_map[e.student_id] = e.roll_number

    items = []
    for u in users:
        school_name = u.school.name if u.school else None
        roll_number = roll_map.get(u.student_id) if u.role == "student" else None
        items.append({
            "id": u.id, "email": u.email, "full_name": u.full_name,
            "role": u.role, "phone": u.phone, "is_active": u.is_active,
            "is_locked": u.is_locked, "failed_login_attempts": u.failed_login_attempts,
            "school_name": school_name, "last_login_at": u.last_login_at,
            "roll_number": roll_number,
        })

    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return {"users": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}


async def hard_delete_school(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """
    Permanently delete ALL data related to a school from every table.
    Deletes in correct FK order (leaf tables first, school last).
    Uses raw SQL for efficiency. Wrapped in a transaction (all-or-nothing).
    """
    # Verify school exists
    result = await db.execute(select(School).where(School.id == school_id))
    school = result.scalar_one_or_none()
    if not school:
        return None

    school_name = school.name

    # Deletion order: leaf/child tables first, parent tables last.
    # All tables with school_id (direct column) are deleted using school_id.
    # Order respects FK constraints — children before parents.
    deletion_order = [
        # --- Deepest leaf tables (no other table references these) ---
        "notification_recipients",    # FK -> notifications, users
        "attendance_records",         # FK -> attendance_sessions, students
        "assignment_submissions",     # FK -> assignments, students
        "exam_results",               # FK -> exams, students
        "grade_scales",               # FK -> grade_systems
        "fee_payments",               # FK -> fee_records, users
        "fee_penalties",              # FK -> fee_records, users
        "fee_reminders",              # FK -> academic_years, users
        "library_issues",             # FK -> library_books, users
        "student_transport",          # FK -> students, routes, academic_years
        "route_assignments",          # FK -> routes, vehicles, drivers, helpers
        "student_parents",            # FK -> students, parents
        "student_mentors",            # FK -> students, staff, academic_years
        "student_enrollments",        # FK -> students, class_sections, academic_years
        "timetable_slots",            # FK -> class_sections, period_configs, subjects, staff
        "adhoc_classes",              # FK -> staff, class_sections, subjects, academic_years
        "staff_subjects",             # FK -> staff, subjects
        "class_assignments",          # FK -> staff, class_sections, subjects, academic_years
        "parent_meetings",            # FK -> students, staff, parents, academic_years
        "activities",                 # FK -> students, staff, academic_years
        "awards",                     # FK -> students, staff, academic_years
        "disciplinary_records",       # FK -> students, staff, academic_years
        "leave_applications",         # FK -> staff, users, academic_years
        "leave_balances",             # FK -> staff, academic_years
        "payslips",                   # FK -> staff, academic_years, users
        "salary_advances",            # FK -> staff, users
        "salary_revisions",           # FK -> staff, academic_years, users
        "salary_structures",          # FK -> staff, academic_years

        # --- Mid-level tables ---
        "notifications",              # FK -> users
        "attendance_sessions",        # FK -> class_sections, subjects, staff, academic_years
        "assignments",                # FK -> class_sections, subjects, staff, academic_years
        "exams",                      # FK -> class_sections, subjects, staff, academic_years
        "fee_records",                # FK -> students, fee_structures, academic_years
        "fee_structures",             # FK -> classes, class_sections, academic_years
        "grade_systems",              # FK -> academic_years
        "leave_policies",             # FK -> academic_years
        "period_configs",             # FK -> academic_years
        "library_books",              # no FK to other school tables
        "subscription_payments",      # FK -> subscriptions
        "subscriptions",              # FK -> schools (direct)

        # --- Core entity tables ---
        "class_subjects",             # FK -> classes, subjects, academic_years
        "class_sections",             # FK -> classes, sections, academic_years
        "subjects",                   # no FK to other school tables
        "sections",                   # no FK to other school tables
        "classes",                    # no FK to other school tables

        # --- Transport entities ---
        "routes",
        "vehicles",
        "drivers",
        "helpers",

        # --- Users and People tables (circular FKs NULLed out above) ---
        "users",
        "parents",
        "students",
        "staff",

        # --- Config tables ---
        "enum_configs",
        "settings",
        "academic_years",

        # --- Finally, the school itself ---
        "schools",
    ]

    deleted_counts = {}

    # First: NULL out circular FK references in users (users → students, staff, parents)
    # and staff (staff → users) to break circular dependencies
    await db.execute(
        text("UPDATE users SET student_id = NULL, staff_id = NULL, parent_id = NULL WHERE school_id = :school_id"),
        {"school_id": str(school_id)},
    )
    await db.execute(
        text("UPDATE staff SET user_id = NULL WHERE school_id = :school_id"),
        {"school_id": str(school_id)},
    )

    for table in deletion_order:
        if table == "schools":
            result = await db.execute(
                text("DELETE FROM schools WHERE id = :school_id"),
                {"school_id": str(school_id)},
            )
            deleted_counts["schools"] = result.rowcount
        else:
            result = await db.execute(
                text(f"DELETE FROM `{table}` WHERE school_id = :school_id"),
                {"school_id": str(school_id)},
            )
            if result.rowcount > 0:
                deleted_counts[table] = result.rowcount

    await db.commit()

    total_deleted = sum(deleted_counts.values())
    return {
        "school_id": school_id,
        "school_name": school_name,
        "deleted_tables": deleted_counts,
        "total_records_deleted": total_deleted,
    }
