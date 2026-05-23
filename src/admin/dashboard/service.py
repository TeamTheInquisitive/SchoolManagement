from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.attendance import AttendanceRecord, AttendanceSession
from src.models.core import AcademicYear, User
from src.models.fee import FeeRecord
from src.models.leave import LeaveApplication
from src.models.staff import Staff
from src.models.student import Student, StudentEnrollment
from src.models.academic import Class, ClassSection, Section


async def _get_current_academic_year(db: AsyncSession, school_id: uuid.UUID) -> AcademicYear | None:
    result = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
            AcademicYear.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


async def get_dashboard_stats(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get KPI stats for admin dashboard."""
    # Total active students
    student_count = (await db.execute(
        select(func.count(Student.id)).where(
            Student.school_id == school_id,
            Student.is_active.is_(True),
            Student.status == "Active",
        )
    )).scalar() or 0

    # Total active teachers
    teacher_count = (await db.execute(
        select(func.count(Staff.id)).where(
            Staff.school_id == school_id,
            Staff.is_active.is_(True),
            Staff.is_teacher.is_(True),
            Staff.status == "Active",
        )
    )).scalar() or 0

    # Active class sections
    class_count = (await db.execute(
        select(func.count(ClassSection.id)).where(
            ClassSection.school_id == school_id,
            ClassSection.is_active.is_(True),
        )
    )).scalar() or 0

    # Fee collection percentage
    ay = await _get_current_academic_year(db, school_id)
    fee_pct = 0.0
    if ay:
        fee_stats = (await db.execute(
            select(
                func.coalesce(func.sum(FeeRecord.paid_amount), 0),
                func.coalesce(func.sum(FeeRecord.net_amount), 0),
            ).where(
                FeeRecord.school_id == school_id,
                FeeRecord.academic_year_id == ay.id,
                FeeRecord.is_active.is_(True),
            )
        )).one_or_none()
        if fee_stats and fee_stats[1] > 0:
            fee_pct = round((fee_stats[0] / fee_stats[1]) * 100, 1)

    return {
        "total_students": student_count,
        "total_teachers": teacher_count,
        "active_classes": class_count,
        "fee_collection_percentage": fee_pct,
        "students_change": "+0%",
        "teachers_change": "+0%",
        "classes_change": "+0",
        "fee_change": "+0%",
    }


async def get_attendance_trends(db: AsyncSession, school_id: uuid.UUID, year: int | None = None) -> dict:
    """Get monthly attendance trends."""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    data = []

    current_year = year or datetime.now().year

    for i, month_name in enumerate(months, 1):
        start_date = date(current_year, i, 1)
        if i == 12:
            end_date = date(current_year + 1, 1, 1)
        else:
            end_date = date(current_year, i + 1, 1)

        total_records = (await db.execute(
            select(func.count(AttendanceRecord.id))
            .join(AttendanceSession, AttendanceRecord.attendance_session_id == AttendanceSession.id)
            .where(
                AttendanceSession.school_id == school_id,
                AttendanceSession.date >= start_date,
                AttendanceSession.date < end_date,
                AttendanceSession.is_active.is_(True),
            )
        )).scalar() or 0

        present_records = (await db.execute(
            select(func.count(AttendanceRecord.id))
            .join(AttendanceSession, AttendanceRecord.attendance_session_id == AttendanceSession.id)
            .where(
                AttendanceSession.school_id == school_id,
                AttendanceSession.date >= start_date,
                AttendanceSession.date < end_date,
                AttendanceSession.is_active.is_(True),
                AttendanceRecord.status.in_(["Present", "Late"]),
            )
        )).scalar() or 0

        pct = round((present_records / total_records) * 100, 1) if total_records > 0 else 0
        data.append({"month": month_name, "value": pct})

    return {"data": data}


async def get_fee_collection_status(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get fee pie chart data."""
    ay = await _get_current_academic_year(db, school_id)
    if not ay:
        return {"data": []}

    statuses = {
        "Paid": {"color": "#22c55e"},
        "Pending": {"color": "#3b82f6"},
        "Partially Paid": {"color": "#f59e0b"},
        "Overdue": {"color": "#ef4444"},
    }

    data = []
    for status_name, config in statuses.items():
        count = (await db.execute(
            select(func.count(FeeRecord.id)).where(
                FeeRecord.school_id == school_id,
                FeeRecord.academic_year_id == ay.id,
                FeeRecord.is_active.is_(True),
                FeeRecord.status == status_name,
            )
        )).scalar() or 0
        data.append({"name": status_name, "value": count, "color": config["color"]})

    return {"data": data}


async def get_student_distribution(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get student distribution by class and gender."""
    ay = await _get_current_academic_year(db, school_id)
    if not ay:
        return {"data": []}

    result = await db.execute(
        select(
            Class.name,
            func.count(case((Student.gender == "Male", 1))).label("male"),
            func.count(case((Student.gender == "Female", 1))).label("female"),
        )
        .select_from(StudentEnrollment)
        .join(Student, StudentEnrollment.student_id == Student.id)
        .join(ClassSection, StudentEnrollment.class_section_id == ClassSection.id)
        .join(Class, ClassSection.class_id == Class.id)
        .where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.academic_year_id == ay.id,
            StudentEnrollment.is_active.is_(True),
            Student.is_active.is_(True),
        )
        .group_by(Class.name, Class.numeric_order)
        .order_by(Class.numeric_order)
    )
    rows = result.all()

    data = [
        {"class_name": f"Class {row[0]}", "male": row[1], "female": row[2]}
        for row in rows
    ]
    return {"data": data}


async def get_recent_activities(db: AsyncSession, school_id: uuid.UUID, limit: int = 10) -> dict:
    """Get recent activity feed (recent students, notifications, etc.)."""
    # Stub: return recently enrolled students as activities
    result = await db.execute(
        select(Student.id, Student.full_name, Student.created_at)
        .where(
            Student.school_id == school_id,
            Student.is_active.is_(True),
        )
        .order_by(Student.created_at.desc())
        .limit(limit)
    )
    rows = result.all()

    data = [
        {
            "id": str(row[0]),
            "title": "Student Record",
            "description": f"{row[1]}",
            "date": row[2].strftime("%Y-%m-%d") if row[2] else "",
            "tag": "Student",
            "category": "student",
        }
        for row in rows
    ]
    return {"data": data}


async def get_leave_overview(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get teacher leave summary + pending approvals."""
    ay = await _get_current_academic_year(db, school_id)
    today = date.today()

    base_filter = and_(
        LeaveApplication.school_id == school_id,
        LeaveApplication.is_active.is_(True),
    )
    if ay:
        base_filter = and_(base_filter, LeaveApplication.academic_year_id == ay.id)

    # Pending count
    pending_count = (await db.execute(
        select(func.count(LeaveApplication.id)).where(base_filter, LeaveApplication.status == "Pending")
    )).scalar() or 0

    # Approved count
    approved_count = (await db.execute(
        select(func.count(LeaveApplication.id)).where(base_filter, LeaveApplication.status == "Approved")
    )).scalar() or 0

    # On leave today
    on_leave_today = (await db.execute(
        select(func.count(LeaveApplication.id)).where(
            base_filter,
            LeaveApplication.status == "Approved",
            LeaveApplication.start_date <= today,
            LeaveApplication.end_date >= today,
        )
    )).scalar() or 0

    # Upcoming leaves
    upcoming = (await db.execute(
        select(func.count(LeaveApplication.id)).where(
            base_filter,
            LeaveApplication.status == "Approved",
            LeaveApplication.start_date > today,
        )
    )).scalar() or 0

    # Pending approvals detail
    pending_result = await db.execute(
        select(
            LeaveApplication.id,
            Staff.full_name,
            LeaveApplication.leave_type,
            LeaveApplication.total_days,
            LeaveApplication.start_date,
            LeaveApplication.end_date,
        )
        .join(Staff, LeaveApplication.staff_id == Staff.id)
        .where(base_filter, LeaveApplication.status == "Pending")
        .order_by(LeaveApplication.applied_at.desc())
        .limit(5)
    )
    pending_rows = pending_result.all()

    pending_approvals = [
        {
            "id": row[0],
            "employee_name": row[1],
            "leave_type": row[2],
            "duration_days": float(row[3]) if row[3] else 0,
            "from_date": row[4].isoformat() if row[4] else "",
            "to_date": row[5].isoformat() if row[5] else "",
        }
        for row in pending_rows
    ]

    return {
        "pending_requests": pending_count,
        "approved": approved_count,
        "on_leave_today": on_leave_today,
        "upcoming_leaves": upcoming,
        "pending_approvals": pending_approvals,
    }


async def get_low_attendance(
    db: AsyncSession, school_id: uuid.UUID, threshold: int = 75, limit: int = 10
) -> dict:
    """Get students below attendance threshold."""
    ay = await _get_current_academic_year(db, school_id)
    if not ay:
        return {"data": []}

    # Get attendance stats per student
    subq = (
        select(
            AttendanceRecord.student_id,
            func.count(AttendanceRecord.id).label("total"),
            func.count(
                case((AttendanceRecord.status.in_(["Present", "Late"]), 1))
            ).label("present"),
        )
        .join(AttendanceSession, AttendanceRecord.attendance_session_id == AttendanceSession.id)
        .where(
            AttendanceSession.school_id == school_id,
            AttendanceSession.is_active.is_(True),
        )
        .group_by(AttendanceRecord.student_id)
        .subquery()
    )

    result = await db.execute(
        select(
            Student.id,
            Student.full_name,
            subq.c.total,
            subq.c.present,
        )
        .join(subq, Student.id == subq.c.student_id)
        .where(
            Student.school_id == school_id,
            Student.is_active.is_(True),
        )
        .order_by((subq.c.present * 100 / func.nullif(subq.c.total, 0)).asc())
        .limit(limit)
    )
    rows = result.all()

    data = []
    for row in rows:
        pct = round((row[3] / row[2]) * 100, 1) if row[2] > 0 else 0
        if pct < threshold:
            data.append({
                "student_id": row[0],
                "name": row[1],
                "class_section": "",
                "attendance_percentage": pct,
            })

    return {"data": data}
