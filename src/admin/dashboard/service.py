from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.attendance import AttendanceRecord, AttendanceSession
from src.models.core import AcademicYear, User
from src.models.examination import Exam, ExamResult
from src.models.fee import FeeRecord, FeePayment, FeeStructure
from src.models.leave import LeaveApplication
from src.models.staff import Staff
from src.models.student import Student, StudentEnrollment
from src.models.timetable import TimetableSlot
from src.models.academic import Class, ClassSection, Section, Subject
from src.models.transport import Route, RouteAssignment, StudentTransport, Vehicle


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
                func.coalesce(func.sum(FeeRecord.paid), 0),
                func.coalesce(func.sum(FeeRecord.total_amount), 0),
                func.coalesce(func.sum(FeeRecord.concession_amount), 0),
            ).where(
                FeeRecord.school_id == school_id,
                FeeRecord.academic_year_id == ay.id,
                FeeRecord.is_active.is_(True),
            )
        )).one_or_none()
        if fee_stats:
            total_paid = float(fee_stats[0])
            total_payable = float(fee_stats[1])
            total_concession = float(fee_stats[2])
            total_original = total_payable + total_concession
            if total_payable > 0:
                fee_pct = round(total_paid / total_payable * 100, 1)

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
    """Get fee pie chart data based on amounts."""
    ay = await _get_current_academic_year(db, school_id)
    if not ay:
        return {"data": []}

    fee_stats = (await db.execute(
        select(
            func.coalesce(func.sum(FeeRecord.paid), 0),
            func.coalesce(func.sum(FeeRecord.pending), 0),
            func.coalesce(func.sum(FeeRecord.concession_amount), 0),
        ).where(
            FeeRecord.school_id == school_id,
            FeeRecord.academic_year_id == ay.id,
            FeeRecord.is_active.is_(True),
        )
    )).one_or_none()

    total_paid = float(fee_stats[0]) if fee_stats else 0
    total_pending = float(fee_stats[1]) if fee_stats else 0
    total_concession = float(fee_stats[2]) if fee_stats else 0

    data = [
        {"name": "Collected", "value": round(total_paid), "color": "#22c55e"},
        {"name": "Pending", "value": round(total_pending), "color": "#f59e0b"},
    ]
    if total_concession > 0:
        data.append({"name": "Concession", "value": round(total_concession), "color": "#3b82f6"})

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
        .group_by(Class.name, Class.sort_order)
        .order_by(Class.sort_order)
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
            LeaveApplication.from_date <= today,
            LeaveApplication.to_date >= today,
        )
    )).scalar() or 0

    # Upcoming leaves
    upcoming = (await db.execute(
        select(func.count(LeaveApplication.id)).where(
            base_filter,
            LeaveApplication.status == "Approved",
            LeaveApplication.from_date > today,
        )
    )).scalar() or 0

    # Pending approvals detail
    pending_result = await db.execute(
        select(
            LeaveApplication.id,
            Staff.full_name,
            LeaveApplication.leave_type,
            LeaveApplication.days,
            LeaveApplication.from_date,
            LeaveApplication.to_date,
        )
        .join(Staff, LeaveApplication.staff_id == Staff.id)
        .where(base_filter, LeaveApplication.status == "Pending")
        .order_by(LeaveApplication.applied_on.desc())
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
    db: AsyncSession, school_id: uuid.UUID, threshold: int = 75, limit: int = 10, min_days: int = 30
) -> dict:
    """Get students below attendance threshold, only after min_days of attendance recorded."""
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
        .having(func.count(AttendanceRecord.id) >= min_days)
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


# ──────────────────────────────────────────────────────────────────────────────
# Analytics endpoints
# ──────────────────────────────────────────────────────────────────────────────


async def get_attendance_by_class(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get attendance percentage per class for the current academic year."""
    ay = await _get_current_academic_year(db, school_id)
    if not ay:
        return {"data": []}

    result = await db.execute(
        select(
            Class.name,
            func.count(AttendanceRecord.id).label("total_days"),
            func.count(
                case((AttendanceRecord.status.in_(["Present", "Late"]), 1))
            ).label("present_days"),
        )
        .select_from(AttendanceRecord)
        .join(AttendanceSession, AttendanceRecord.attendance_session_id == AttendanceSession.id)
        .join(ClassSection, AttendanceSession.class_section_id == ClassSection.id)
        .join(Class, ClassSection.class_id == Class.id)
        .where(
            AttendanceSession.school_id == school_id,
            AttendanceSession.is_active.is_(True),
            AttendanceSession.academic_year_id == ay.id,
        )
        .group_by(Class.name, Class.sort_order)
        .order_by(Class.sort_order)
    )
    rows = result.all()

    data = []
    for row in rows:
        total = row[1]
        present = row[2]
        pct = round((present / total) * 100, 1) if total > 0 else 0.0
        data.append({
            "class_name": row[0],
            "attendance_pct": pct,
            "total_days": total,
            "present_days": present,
        })

    return {"data": data}


async def get_fee_collection_trend(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get monthly fee collection amounts for the last 6 months."""
    today = date.today()
    months_data = []

    for i in range(5, -1, -1):
        # Calculate the first day of the target month
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1

        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)

        # Collected: sum of payments in this month
        collected = (await db.execute(
            select(func.coalesce(func.sum(FeePayment.amount), 0))
            .join(FeeRecord, FeePayment.fee_record_id == FeeRecord.id)
            .where(
                FeeRecord.school_id == school_id,
                FeeRecord.is_active.is_(True),
                FeePayment.payment_date >= start_date,
                FeePayment.payment_date < end_date,
            )
        )).scalar() or 0

        # Pending: sum of pending amounts for records with due_date in this month
        pending = (await db.execute(
            select(func.coalesce(func.sum(FeeRecord.pending), 0))
            .where(
                FeeRecord.school_id == school_id,
                FeeRecord.is_active.is_(True),
                FeeRecord.due_date >= start_date,
                FeeRecord.due_date < end_date,
                FeeRecord.status.in_(["Pending", "Partial"]),
            )
        )).scalar() or 0

        month_name = start_date.strftime("%b")
        months_data.append({
            "month": month_name,
            "year": year,
            "collected": float(collected),
            "pending": float(pending),
        })

    return {"data": months_data}


async def get_exam_performance(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get average marks percentage per class across all exams for current academic year."""
    ay = await _get_current_academic_year(db, school_id)
    if not ay:
        return {"data": []}

    result = await db.execute(
        select(
            Class.name,
            func.avg(
                ExamResult.marks_obtained * 100 / func.nullif(Exam.total_marks, 0)
            ).label("avg_percentage"),
            func.count(func.distinct(Exam.id)).label("total_exams"),
            func.count(
                case((ExamResult.is_pass.is_(True), 1))
            ).label("pass_count"),
            func.count(ExamResult.id).label("total_results"),
        )
        .select_from(ExamResult)
        .join(Exam, ExamResult.exam_id == Exam.id)
        .join(ClassSection, Exam.class_section_id == ClassSection.id)
        .join(Class, ClassSection.class_id == Class.id)
        .where(
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
            Exam.academic_year_id == ay.id,
            ExamResult.is_active.is_(True),
        )
        .group_by(Class.name, Class.sort_order)
        .order_by(Class.sort_order)
    )
    rows = result.all()

    data = []
    for row in rows:
        avg_pct = round(float(row[1]), 1) if row[1] else 0.0
        total_exams = row[2]
        pass_count = row[3]
        total_results = row[4]
        pass_rate = round((pass_count / total_results) * 100, 1) if total_results > 0 else 0.0
        data.append({
            "class_name": row[0],
            "avg_percentage": avg_pct,
            "total_exams": total_exams,
            "pass_rate": pass_rate,
        })

    return {"data": data}


async def get_teacher_workload(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get teacher workload distribution (periods assigned vs max)."""
    ay = await _get_current_academic_year(db, school_id)
    if not ay:
        return {"data": []}

    result = await db.execute(
        select(
            Staff.full_name,
            func.count(TimetableSlot.id).label("assigned_periods"),
            Staff.max_workload_hours,
        )
        .select_from(Staff)
        .outerjoin(
            TimetableSlot,
            and_(
                TimetableSlot.staff_id == Staff.id,
                TimetableSlot.academic_year_id == ay.id,
                TimetableSlot.is_active.is_(True),
            ),
        )
        .where(
            Staff.school_id == school_id,
            Staff.is_active.is_(True),
            Staff.is_teacher.is_(True),
            Staff.status == "Active",
        )
        .group_by(Staff.id, Staff.full_name, Staff.max_workload_hours)
        .order_by(Staff.full_name)
    )
    rows = result.all()

    data = []
    for row in rows:
        name = row[0]
        assigned = row[1]
        max_periods = row[2] if row[2] else 25  # default max if not set
        utilization = round((assigned / max_periods) * 100, 1) if max_periods > 0 else 0.0
        data.append({
            "name": name,
            "assigned_periods": assigned,
            "max_periods": max_periods,
            "utilization_pct": utilization,
        })

    return {"data": data}


async def get_enrollment_trend(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get student enrollment count per academic year (historical)."""
    result = await db.execute(
        select(
            AcademicYear.name,
            func.count(StudentEnrollment.id).label("count"),
        )
        .select_from(StudentEnrollment)
        .join(AcademicYear, StudentEnrollment.academic_year_id == AcademicYear.id)
        .where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.is_active.is_(True),
        )
        .group_by(AcademicYear.name, AcademicYear.start_date)
        .order_by(AcademicYear.start_date)
    )
    rows = result.all()

    data = [
        {"academic_year": row[0], "count": row[1]}
        for row in rows
    ]

    return {"data": data}


async def get_fee_defaulters_by_class(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get count of fee defaulters per class for the current academic year."""
    ay = await _get_current_academic_year(db, school_id)
    if not ay:
        return {"data": []}

    today = date.today()

    result = await db.execute(
        select(
            Class.name,
            func.count(func.distinct(
                case(
                    (
                        and_(
                            FeeRecord.status.in_(["Pending", "Partial"]),
                            FeeRecord.due_date < today,
                        ),
                        FeeRecord.student_id,
                    ),
                )
            )).label("defaulter_count"),
            func.count(func.distinct(StudentEnrollment.student_id)).label("total_students"),
        )
        .select_from(StudentEnrollment)
        .join(ClassSection, StudentEnrollment.class_section_id == ClassSection.id)
        .join(Class, ClassSection.class_id == Class.id)
        .outerjoin(
            FeeRecord,
            and_(
                FeeRecord.student_id == StudentEnrollment.student_id,
                FeeRecord.academic_year_id == ay.id,
                FeeRecord.school_id == school_id,
                FeeRecord.is_active.is_(True),
            ),
        )
        .where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.academic_year_id == ay.id,
            StudentEnrollment.is_active.is_(True),
        )
        .group_by(Class.name, Class.sort_order)
        .order_by(Class.sort_order)
    )
    rows = result.all()

    data = []
    for row in rows:
        defaulter_count = row[1]
        total_students = row[2]
        defaulter_pct = round((defaulter_count / total_students) * 100, 1) if total_students > 0 else 0.0
        data.append({
            "class_name": row[0],
            "defaulter_count": defaulter_count,
            "total_students": total_students,
            "defaulter_pct": defaulter_pct,
        })

    return {"data": data}


async def get_attendance_monthly_comparison(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get this month vs last month attendance percentage by class."""
    today = date.today()
    this_month_start = today.replace(day=1)
    if this_month_start.month == 1:
        last_month_start = date(this_month_start.year - 1, 12, 1)
    else:
        last_month_start = date(this_month_start.year, this_month_start.month - 1, 1)
    last_month_end = this_month_start

    ay = await _get_current_academic_year(db, school_id)
    if not ay:
        return {"data": []}

    async def _get_month_attendance(start: date, end: date) -> dict:
        """Return {class_name: pct} for the given date range."""
        res = await db.execute(
            select(
                Class.name,
                func.count(AttendanceRecord.id).label("total"),
                func.count(
                    case((AttendanceRecord.status.in_(["Present", "Late"]), 1))
                ).label("present"),
            )
            .select_from(AttendanceRecord)
            .join(AttendanceSession, AttendanceRecord.attendance_session_id == AttendanceSession.id)
            .join(ClassSection, AttendanceSession.class_section_id == ClassSection.id)
            .join(Class, ClassSection.class_id == Class.id)
            .where(
                AttendanceSession.school_id == school_id,
                AttendanceSession.is_active.is_(True),
                AttendanceSession.academic_year_id == ay.id,
                AttendanceSession.date >= start,
                AttendanceSession.date < end,
            )
            .group_by(Class.name, Class.sort_order)
            .order_by(Class.sort_order)
        )
        rows = res.all()
        return {
            row[0]: round((row[2] / row[1]) * 100, 1) if row[1] > 0 else 0.0
            for row in rows
        }

    this_month_data = await _get_month_attendance(this_month_start, today + timedelta(days=1))
    last_month_data = await _get_month_attendance(last_month_start, last_month_end)

    # Merge all class names
    all_classes = sorted(
        set(list(this_month_data.keys()) + list(last_month_data.keys()))
    )

    data = []
    for cls_name in all_classes:
        this_pct = this_month_data.get(cls_name, 0.0)
        last_pct = last_month_data.get(cls_name, 0.0)
        change = round(this_pct - last_pct, 1)
        data.append({
            "class_name": cls_name,
            "this_month": this_pct,
            "last_month": last_pct,
            "change": change,
        })

    return {"data": data}


async def get_student_type_ratio(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get dayscholar/hostler ratio for active students."""
    result = await db.execute(
        select(
            Student.id,
            Student.metadata_,
        )
        .where(
            Student.school_id == school_id,
            Student.is_active.is_(True),
            Student.status == "Active",
        )
    )
    rows = result.all()
    total = len(rows)
    hostler = 0
    dayscholar = 0
    for row in rows:
        meta = row[1] or {}
        student_type = meta.get("student_type", "").lower() if isinstance(meta, dict) else ""
        if student_type in ("hosteller", "hostler", "boarding"):
            hostler += 1
        else:
            dayscholar += 1

    return {
        "dayscholar": dayscholar,
        "hostler": hostler,
        "total": total,
    }


async def get_subject_performance(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get average score and pass rate per subject across all classes."""
    ay = await _get_current_academic_year(db, school_id)
    if not ay:
        return {"data": []}

    result = await db.execute(
        select(
            Subject.name,
            func.avg(ExamResult.marks_obtained * 100 / func.nullif(Exam.total_marks, 0)).label("avg_score"),
            func.count(case((ExamResult.is_pass.is_(True), 1))).label("pass_count"),
            func.count(ExamResult.id).label("total_results"),
        )
        .select_from(ExamResult)
        .join(Exam, ExamResult.exam_id == Exam.id)
        .join(Subject, Exam.subject_id == Subject.id)
        .where(
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
            Exam.academic_year_id == ay.id,
            ExamResult.is_active.is_(True),
        )
        .group_by(Subject.name)
        .order_by(Subject.name)
    )
    rows = result.all()

    data = []
    for row in rows:
        avg_score = round(float(row[1]), 1) if row[1] else 0
        pass_count = row[2]
        total_results = row[3]
        pass_rate = round((pass_count / total_results) * 100, 1) if total_results > 0 else 0
        data.append({
            "subject": row[0],
            "avg_score": avg_score,
            "pass_rate": pass_rate,
        })

    return {"data": data}


async def get_class_toppers(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get top scoring student per class from latest exam."""
    ay = await _get_current_academic_year(db, school_id)
    if not ay:
        return {"data": []}

    # Get the latest exam per class section
    latest_exam_subq = (
        select(
            Exam.class_section_id,
            func.max(Exam.date).label("latest_date"),
        )
        .where(
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
            Exam.academic_year_id == ay.id,
            Exam.status == "Published",
        )
        .group_by(Exam.class_section_id)
        .subquery()
    )

    # Get the top student per class
    result = await db.execute(
        select(
            Student.full_name,
            Class.name.label("class_name"),
            Exam.name.label("exam_name"),
            func.sum(ExamResult.marks_obtained).label("total_marks"),
            func.sum(Exam.total_marks).label("total_possible"),
        )
        .select_from(ExamResult)
        .join(Exam, ExamResult.exam_id == Exam.id)
        .join(Student, ExamResult.student_id == Student.id)
        .join(ClassSection, Exam.class_section_id == ClassSection.id)
        .join(Class, ClassSection.class_id == Class.id)
        .join(
            latest_exam_subq,
            and_(
                Exam.class_section_id == latest_exam_subq.c.class_section_id,
                Exam.date == latest_exam_subq.c.latest_date,
            ),
        )
        .where(
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
            Exam.academic_year_id == ay.id,
            ExamResult.is_active.is_(True),
            Student.is_active.is_(True),
        )
        .group_by(Student.full_name, Class.name, Exam.name, Class.sort_order)
        .order_by(Class.sort_order)
    )
    rows = result.all()

    # Find top scorer per class
    class_toppers: dict = {}
    for row in rows:
        name = row[0]
        class_name = row[1]
        exam_name = row[2]
        marks = float(row[3]) if row[3] else 0
        total = float(row[4]) if row[4] else 0
        percentage = round((marks / total) * 100, 1) if total > 0 else 0

        if class_name not in class_toppers or marks > class_toppers[class_name]["marks"]:
            class_toppers[class_name] = {
                "name": name,
                "class_name": class_name,
                "exam": exam_name,
                "percentage": percentage,
                "marks": marks,
                "total": total,
            }

    data = list(class_toppers.values())
    return {"data": data}


async def get_attendance_marks_correlation(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get per-student attendance % and exam avg % for correlation analysis."""
    ay = await _get_current_academic_year(db, school_id)
    if not ay:
        return {"data": []}

    # Attendance percentage per student
    attendance_subq = (
        select(
            AttendanceRecord.student_id,
            (
                func.count(case((AttendanceRecord.status.in_(["Present", "Late"]), 1))) * 100
                / func.nullif(func.count(AttendanceRecord.id), 0)
            ).label("attendance_pct"),
        )
        .join(AttendanceSession, AttendanceRecord.attendance_session_id == AttendanceSession.id)
        .where(
            AttendanceSession.school_id == school_id,
            AttendanceSession.is_active.is_(True),
            AttendanceSession.academic_year_id == ay.id,
        )
        .group_by(AttendanceRecord.student_id)
        .subquery()
    )

    # Exam average percentage per student
    exam_subq = (
        select(
            ExamResult.student_id,
            func.avg(
                ExamResult.marks_obtained * 100 / func.nullif(Exam.total_marks, 0)
            ).label("marks_pct"),
        )
        .join(Exam, ExamResult.exam_id == Exam.id)
        .where(
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
            Exam.academic_year_id == ay.id,
            ExamResult.is_active.is_(True),
        )
        .group_by(ExamResult.student_id)
        .subquery()
    )

    result = await db.execute(
        select(
            attendance_subq.c.attendance_pct,
            exam_subq.c.marks_pct,
        )
        .select_from(attendance_subq)
        .join(exam_subq, attendance_subq.c.student_id == exam_subq.c.student_id)
    )
    rows = result.all()

    data = [
        {
            "attendance": round(float(row[0]), 1) if row[0] else 0,
            "marks": round(float(row[1]), 1) if row[1] else 0,
        }
        for row in rows
    ]

    return {"data": data}


async def get_revenue_vs_target(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get monthly collected vs expected (target) fee amounts."""
    ay = await _get_current_academic_year(db, school_id)
    if not ay:
        return {"data": []}

    # Calculate total target from FeeStructure for the academic year
    total_target_result = await db.execute(
        select(func.coalesce(func.sum(FeeStructure.amount), 0)).where(
            FeeStructure.school_id == school_id,
            FeeStructure.academic_year_id == ay.id,
            FeeStructure.is_active.is_(True),
        )
    )
    total_target = float(total_target_result.scalar() or 0)
    monthly_target = round(total_target / 12, 2) if total_target > 0 else 0

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    today = date.today()
    data = []

    for i, month_name in enumerate(months, 1):
        year = today.year
        start_date = date(year, i, 1)
        if i == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, i + 1, 1)

        collected = (await db.execute(
            select(func.coalesce(func.sum(FeePayment.amount), 0))
            .join(FeeRecord, FeePayment.fee_record_id == FeeRecord.id)
            .where(
                FeeRecord.school_id == school_id,
                FeeRecord.is_active.is_(True),
                FeePayment.payment_date >= start_date,
                FeePayment.payment_date < end_date,
            )
        )).scalar() or 0

        data.append({
            "month": month_name,
            "target": monthly_target,
            "collected": float(collected),
        })

    return {"data": data}


async def get_teacher_leave_patterns(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get monthly leave days by department (Teaching vs Non-Teaching)."""
    ay = await _get_current_academic_year(db, school_id)
    if not ay:
        return {"data": []}

    result = await db.execute(
        select(
            func.extract("month", LeaveApplication.from_date).label("month_num"),
            Staff.is_teacher,
            func.sum(LeaveApplication.days).label("total_days"),
        )
        .select_from(LeaveApplication)
        .join(Staff, LeaveApplication.staff_id == Staff.id)
        .where(
            LeaveApplication.school_id == school_id,
            LeaveApplication.is_active.is_(True),
            LeaveApplication.academic_year_id == ay.id,
            LeaveApplication.status == "Approved",
            Staff.is_active.is_(True),
        )
        .group_by(func.extract("month", LeaveApplication.from_date), Staff.is_teacher)
        .order_by(func.extract("month", LeaveApplication.from_date))
    )
    rows = result.all()

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_data: dict = {i: {"teaching": 0, "non_teaching": 0} for i in range(1, 13)}

    for row in rows:
        month_num = int(row[0])
        is_teacher = row[1]
        total_days = float(row[2]) if row[2] else 0
        if is_teacher:
            month_data[month_num]["teaching"] = total_days
        else:
            month_data[month_num]["non_teaching"] = total_days

    data = [
        {
            "month": months[i - 1],
            "teaching": month_data[i]["teaching"],
            "non_teaching": month_data[i]["non_teaching"],
        }
        for i in range(1, 13)
    ]

    return {"data": data}


async def get_transport_utilization(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get occupied vs capacity per route."""
    ay = await _get_current_academic_year(db, school_id)
    if not ay:
        return {"data": []}

    try:
        result = await db.execute(
            select(
                Route.name,
                Vehicle.capacity,
                func.count(StudentTransport.id).label("occupied"),
            )
            .select_from(Route)
            .join(RouteAssignment, and_(
                RouteAssignment.route_id == Route.id,
                RouteAssignment.is_active.is_(True),
                RouteAssignment.status == "Active",
            ))
            .join(Vehicle, RouteAssignment.vehicle_id == Vehicle.id)
            .outerjoin(StudentTransport, and_(
                StudentTransport.route_id == Route.id,
                StudentTransport.academic_year_id == ay.id,
                StudentTransport.is_active.is_(True),
            ))
            .where(
                Route.school_id == school_id,
                Route.is_active.is_(True),
                Route.status == "Active",
            )
            .group_by(Route.name, Vehicle.capacity)
            .order_by(Route.name)
        )
        rows = result.all()

        data = [
            {
                "route": row[0],
                "occupied": row[2],
                "capacity": row[1],
            }
            for row in rows
        ]
    except Exception:
        data = []

    return {"data": data}


async def get_concession_summary(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get total concession amount grouped by fee category."""
    ay = await _get_current_academic_year(db, school_id)
    if not ay:
        return {"data": []}

    result = await db.execute(
        select(
            FeeRecord.fee_category,
            func.sum(FeeRecord.concession_amount).label("amount"),
        )
        .where(
            FeeRecord.school_id == school_id,
            FeeRecord.academic_year_id == ay.id,
            FeeRecord.is_active.is_(True),
            FeeRecord.concession_amount > 0,
        )
        .group_by(FeeRecord.fee_category)
        .order_by(func.sum(FeeRecord.concession_amount).desc())
    )
    rows = result.all()

    data = [
        {
            "name": row[0] if row[0] else "Other",
            "amount": float(row[1]) if row[1] else 0,
        }
        for row in rows
    ]

    return {"data": data}


async def get_growth_rate(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get year-over-year student count change percentage."""
    result = await db.execute(
        select(
            AcademicYear.name,
            func.count(StudentEnrollment.id).label("count"),
        )
        .select_from(StudentEnrollment)
        .join(AcademicYear, StudentEnrollment.academic_year_id == AcademicYear.id)
        .where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.is_active.is_(True),
        )
        .group_by(AcademicYear.name, AcademicYear.start_date)
        .order_by(AcademicYear.start_date)
    )
    rows = result.all()

    data = []
    for i, row in enumerate(rows):
        if i == 0:
            data.append({"year": row[0], "growth_pct": 0.0})
        else:
            prev_count = rows[i - 1][1]
            current_count = row[1]
            if prev_count > 0:
                growth = round(((current_count - prev_count) / prev_count) * 100, 1)
            else:
                growth = 0.0
            data.append({"year": row[0], "growth_pct": growth})

    return {"data": data}


async def get_fee_collection_rate(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get monthly percentage of expected fees actually collected."""
    ay = await _get_current_academic_year(db, school_id)
    if not ay:
        return {"data": []}

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    today = date.today()
    data = []

    for i, month_name in enumerate(months, 1):
        year = today.year
        start_date = date(year, i, 1)
        if i == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, i + 1, 1)

        # Expected: sum of total_amount for fee records due in this month
        expected = (await db.execute(
            select(func.coalesce(func.sum(FeeRecord.total_amount), 0)).where(
                FeeRecord.school_id == school_id,
                FeeRecord.academic_year_id == ay.id,
                FeeRecord.is_active.is_(True),
                FeeRecord.due_date >= start_date,
                FeeRecord.due_date < end_date,
            )
        )).scalar() or 0

        # Collected: sum of payments in this month
        collected = (await db.execute(
            select(func.coalesce(func.sum(FeePayment.amount), 0))
            .join(FeeRecord, FeePayment.fee_record_id == FeeRecord.id)
            .where(
                FeeRecord.school_id == school_id,
                FeeRecord.is_active.is_(True),
                FeePayment.payment_date >= start_date,
                FeePayment.payment_date < end_date,
            )
        )).scalar() or 0

        rate = round((float(collected) / float(expected)) * 100, 1) if float(expected) > 0 else 0
        data.append({
            "month": month_name,
            "rate": rate,
        })

    return {"data": data}
