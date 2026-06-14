from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFound
from src.core.pagination import PaginationParams, paginate
from src.models.academic import ClassSection, Subject
from src.models.attendance import AttendanceRecord, AttendanceSession
from src.models.core import AcademicYear, User
from src.models.staff import Staff
from src.models.student import Student, StudentEnrollment


ATTENDANCE_THRESHOLD = 75
ATTENDANCE_MIN_DAYS = 30


async def _get_attendance_settings(db: AsyncSession, school_id: uuid.UUID) -> tuple[int, int]:
    """Get attendance threshold and min days from school settings."""
    from src.models.core import Settings
    result = await db.execute(
        select(Settings.value).where(
            Settings.school_id == school_id,
            Settings.category == "attendance",
            Settings.key == "config",
            Settings.is_active.is_(True),
        )
    )
    row = result.scalar_one_or_none()
    if row and isinstance(row, dict):
        return row.get("threshold", ATTENDANCE_THRESHOLD), row.get("min_days", ATTENDANCE_MIN_DAYS)
    return ATTENDANCE_THRESHOLD, ATTENDANCE_MIN_DAYS


async def _get_current_academic_year(
    db: AsyncSession, school_id: uuid.UUID, academic_year_name: str | None = None
) -> AcademicYear:
    """Get the academic year by name or the current one."""
    if academic_year_name:
        result = await db.execute(
            select(AcademicYear).where(
                AcademicYear.school_id == school_id,
                AcademicYear.name == academic_year_name,
                AcademicYear.is_active.is_(True),
            )
        )
    else:
        result = await db.execute(
            select(AcademicYear).where(
                AcademicYear.school_id == school_id,
                AcademicYear.is_current.is_(True),
                AcademicYear.is_active.is_(True),
            )
        )
    ay = result.scalar_one_or_none()
    if not ay:
        raise NotFound("AcademicYear")
    return ay


async def _get_student_for_user(
    db: AsyncSession, school_id: uuid.UUID, user: User
) -> Student:
    """Get the Student record linked to the user."""
    if not user.student_id:
        raise NotFound("Student", "No student record linked to this user")
    result = await db.execute(
        select(Student).where(
            Student.id == user.student_id,
            Student.school_id == school_id,
            Student.is_active.is_(True),
        )
    )
    student = result.scalar_one_or_none()
    if not student:
        raise NotFound("Student", str(user.student_id))
    return student


async def _get_student_enrollment(
    db: AsyncSession,
    school_id: uuid.UUID,
    student_id: uuid.UUID,
    academic_year_id: uuid.UUID,
) -> StudentEnrollment | None:
    """Get the student's enrollment for the academic year."""
    result = await db.execute(
        select(StudentEnrollment).where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.student_id == student_id,
            StudentEnrollment.academic_year_id == academic_year_id,
            StudentEnrollment.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


def _get_color_for_percentage(percentage: float) -> str:
    """Return color based on attendance percentage."""
    if percentage >= 75:
        return "green"
    elif percentage >= 60:
        return "yellow"
    else:
        return "red"


async def get_attendance_overview(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    academic_year_name: str | None = None,
    month: str | None = None,
) -> dict:
    """Get overall attendance summary with stats, distribution, subject-wise, warning."""
    student = await _get_student_for_user(db, school_id, user)
    ay = await _get_current_academic_year(db, school_id, academic_year_name)

    # Get all attendance records for this student in this academic year
    query = (
        select(AttendanceRecord)
        .join(AttendanceSession, AttendanceRecord.attendance_session_id == AttendanceSession.id)
        .where(
            AttendanceRecord.student_id == student.id,
            AttendanceRecord.is_active.is_(True),
            AttendanceSession.school_id == school_id,
            AttendanceSession.academic_year_id == ay.id,
            AttendanceSession.status == "Submitted",
            AttendanceSession.is_active.is_(True),
        )
    )

    # Apply month filter if provided (format: YYYY-MM)
    if month:
        try:
            year_val, month_val = month.split("-")
            from datetime import date as date_type
            first_day = date_type(int(year_val), int(month_val), 1)
            if int(month_val) == 12:
                last_day = date_type(int(year_val) + 1, 1, 1)
            else:
                last_day = date_type(int(year_val), int(month_val) + 1, 1)
            query = query.where(
                AttendanceSession.date >= first_day,
                AttendanceSession.date < last_day,
            )
        except (ValueError, IndexError):
            pass

    result = await db.execute(query)
    records = result.scalars().all()

    # Calculate overall stats
    present = sum(1 for r in records if r.status == "Present")
    absent = sum(1 for r in records if r.status == "Absent")
    late = sum(1 for r in records if r.status == "Late")
    excused = sum(1 for r in records if r.status == "Excused")
    total = len(records)

    percentage = round((present + late) / total * 100, 1) if total > 0 else 0.0
    threshold, min_days = await _get_attendance_settings(db, school_id)
    status = "above_threshold" if percentage >= threshold else "below_threshold"

    # Subject-wise breakdown - get session -> subject mapping
    # We need the sessions with their subject info (from class_assignments or timetable)
    # For simplicity, we aggregate by session's class_section (general attendance)
    # A more detailed implementation would query per-subject sessions
    # For now, return the overall as a single subject grouping

    # Get sessions with records for subject-wise
    session_ids = list({r.attendance_session_id for r in records})
    subject_wise: list[dict] = []

    if session_ids:
        sessions_result = await db.execute(
            select(AttendanceSession).where(
                AttendanceSession.id.in_(session_ids),
            )
        )
        sessions = sessions_result.scalars().all()
        session_map = {s.id: s for s in sessions}

        # Group records by subject (from session metadata or general)
        # Since our attendance model is class-level (general), we provide overall stats
        # Subject-wise would require subject_id on session; provide a simplified view
        subject_wise = [
            {
                "subject": "Overall",
                "percentage": percentage,
                "present": present + late,
                "total": total,
                "color": _get_color_for_percentage(percentage),
                "metadata": {},
            }
        ]

    # Warning - only after minimum days threshold
    warning = None
    if percentage < threshold and total >= min_days:
        warning = {
            "active": True,
            "type": "low_attendance",
            "message": f"Your attendance is below {threshold}%. You need to maintain at least {threshold}% attendance to be eligible for exams.",
            "severity": "critical",
        }

    # Recent records (last 10)
    recent_query = (
        select(AttendanceRecord)
        .join(AttendanceSession, AttendanceRecord.attendance_session_id == AttendanceSession.id)
        .where(
            AttendanceRecord.student_id == student.id,
            AttendanceRecord.is_active.is_(True),
            AttendanceSession.school_id == school_id,
            AttendanceSession.academic_year_id == ay.id,
            AttendanceSession.status == "Submitted",
            AttendanceSession.is_active.is_(True),
        )
        .order_by(AttendanceSession.date.desc())
        .limit(10)
    )
    recent_result = await db.execute(recent_query)
    recent_records_raw = recent_result.scalars().all()

    # Get session details for recent records
    recent_session_ids = [r.attendance_session_id for r in recent_records_raw]
    recent_sessions_map: dict[uuid.UUID, AttendanceSession] = {}
    if recent_session_ids:
        rs_result = await db.execute(
            select(AttendanceSession).where(
                AttendanceSession.id.in_(recent_session_ids)
            )
        )
        for s in rs_result.scalars().all():
            recent_sessions_map[s.id] = s

    recent_records = []
    for r in recent_records_raw:
        sess = recent_sessions_map.get(r.attendance_session_id)
        recent_records.append({
            "date": sess.date if sess else None,
            "subject": None,
            "status": r.status.lower(),
            "period": None,
            "metadata": {},
        })

    return {
        "academic_year": ay.name,
        "overall": {
            "percentage": percentage,
            "present_days": present,
            "absent_days": absent,
            "late_days": late,
            "excused_days": excused,
            "total_days": total,
            "threshold": threshold,
            "min_days": min_days,
            "status": status,
        },
        "stats": {
            "present": present,
            "absent": absent,
            "late": late,
            "excused": excused,
        },
        "distribution": {
            "present": present,
            "absent": absent,
            "late": late,
            "excused": excused,
        },
        "warning": warning,
        "subject_wise": subject_wise,
        "recent_records": recent_records,
        "metadata": {},
    }


async def get_attendance_history(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    pagination: PaginationParams,
    subject: str | None = None,
    month: str | None = None,
    status_filter: str | None = None,
) -> dict:
    """Get detailed attendance history for the student (paginated, filterable)."""
    student = await _get_student_for_user(db, school_id, user)
    ay = await _get_current_academic_year(db, school_id)

    query = (
        select(AttendanceRecord)
        .join(AttendanceSession, AttendanceRecord.attendance_session_id == AttendanceSession.id)
        .where(
            AttendanceRecord.student_id == student.id,
            AttendanceRecord.is_active.is_(True),
            AttendanceSession.school_id == school_id,
            AttendanceSession.academic_year_id == ay.id,
            AttendanceSession.status == "Submitted",
            AttendanceSession.is_active.is_(True),
        )
    )

    # Apply month filter (format: YYYY-MM)
    if month:
        try:
            from datetime import date as date_type
            year_val, month_val = month.split("-")
            first_day = date_type(int(year_val), int(month_val), 1)
            if int(month_val) == 12:
                last_day = date_type(int(year_val) + 1, 1, 1)
            else:
                last_day = date_type(int(year_val), int(month_val) + 1, 1)
            query = query.where(
                AttendanceSession.date >= first_day,
                AttendanceSession.date < last_day,
            )
        except (ValueError, IndexError):
            pass

    # Apply status filter
    if status_filter:
        query = query.where(
            func.lower(AttendanceRecord.status) == status_filter.lower()
        )

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Paginated results
    query = query.order_by(AttendanceSession.date.desc())
    query = query.offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    records = result.scalars().all()

    # Get session details
    session_ids = list({r.attendance_session_id for r in records})
    session_map: dict[uuid.UUID, AttendanceSession] = {}
    if session_ids:
        sess_result = await db.execute(
            select(AttendanceSession).where(
                AttendanceSession.id.in_(session_ids)
            )
        )
        for s in sess_result.scalars().all():
            session_map[s.id] = s

    items = []
    for record in records:
        sess = session_map.get(record.attendance_session_id)
        marked_by_name = None
        if sess and sess.staff:
            marked_by_name = sess.staff.full_name

        items.append({
            "id": record.id,
            "date": sess.date if sess else None,
            "subject": None,
            "period": None,
            "status": record.status.lower(),
            "marked_by": marked_by_name,
            "remarks": record.remarks,
            "metadata": {},
        })

    paginated = paginate(items, total, pagination)
    paginated["filters"] = {
        "subject": subject,
        "month": month,
        "status": status_filter,
    }
    paginated["metadata"] = {}
    return paginated


async def get_attendance_warnings(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    academic_year_name: str | None = None,
) -> dict:
    """Get attendance warnings and compliance status for the student."""
    student = await _get_student_for_user(db, school_id, user)
    ay = await _get_current_academic_year(db, school_id, academic_year_name)

    # Get all attendance records for this student
    query = (
        select(AttendanceRecord)
        .join(AttendanceSession, AttendanceRecord.attendance_session_id == AttendanceSession.id)
        .where(
            AttendanceRecord.student_id == student.id,
            AttendanceRecord.is_active.is_(True),
            AttendanceSession.school_id == school_id,
            AttendanceSession.academic_year_id == ay.id,
            AttendanceSession.status == "Submitted",
            AttendanceSession.is_active.is_(True),
        )
    )
    result = await db.execute(query)
    records = result.scalars().all()

    present = sum(1 for r in records if r.status == "Present")
    late = sum(1 for r in records if r.status == "Late")
    total = len(records)

    threshold, min_days = await _get_attendance_settings(db, school_id)
    percentage = round((present + late) / total * 100, 1) if total > 0 else 100.0
    status = "above_threshold" if percentage >= threshold else "below_threshold"

    warnings = []
    if percentage < threshold and total >= min_days:
        warnings.append({
            "id": f"warn-{student.id}",
            "type": "low_attendance",
            "severity": "critical",
            "message": f"Your attendance is below {threshold}%. You need to maintain at least {threshold}% attendance to be eligible for exams.",
            "issued_date": date.today(),
            "active": True,
            "acknowledged": False,
            "metadata": {},
        })

    # Subjects at risk - simplified (since our model is class-level)
    subjects_at_risk: list[dict] = []

    return {
        "academic_year": ay.name,
        "threshold": threshold,
        "min_days": min_days,
        "current_percentage": percentage,
        "status": status,
        "warnings": warnings,
        "subjects_at_risk": subjects_at_risk,
        "metadata": {},
    }
