from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.exceptions import NotFound
from src.core.pagination import PaginationParams, paginate
from src.models.academic import ClassSection
from src.models.attendance import AttendanceRecord, AttendanceSession
from src.models.core import AcademicYear, User
from src.models.staff import ClassAssignment, Staff
from src.models.student import Student, StudentEnrollment
from src.teacher.attendance.exceptions import AttendanceAlreadySubmitted, ClassNotAssigned
from src.teacher.attendance.schemas import SubmitAttendanceRequest, UpdateAttendanceRequest


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


async def _get_staff_for_user(
    db: AsyncSession, school_id: uuid.UUID, user: User
) -> Staff:
    """Get the Staff record linked to the user."""
    if not user.staff_id:
        raise NotFound("Staff", "No staff record linked to this user")
    result = await db.execute(
        select(Staff).where(
            Staff.id == user.staff_id,
            Staff.school_id == school_id,
            Staff.is_active.is_(True),
        )
    )
    staff = result.scalar_one_or_none()
    if not staff:
        raise NotFound("Staff", str(user.staff_id))
    return staff


async def _verify_class_assignment(
    db: AsyncSession,
    school_id: uuid.UUID,
    staff_id: uuid.UUID,
    class_section_id: uuid.UUID,
    academic_year_id: uuid.UUID,
) -> None:
    """Verify teacher is assigned to the class. Raises ClassNotAssigned if not."""
    result = await db.execute(
        select(ClassAssignment).where(
            ClassAssignment.school_id == school_id,
            ClassAssignment.staff_id == staff_id,
            ClassAssignment.class_section_id == class_section_id,
            ClassAssignment.academic_year_id == academic_year_id,
            ClassAssignment.is_active.is_(True),
        ).limit(1)
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise ClassNotAssigned()


async def _get_class_section(
    db: AsyncSession, school_id: uuid.UUID, class_section_id: uuid.UUID
) -> ClassSection:
    """Get class section with eager-loaded class_ and section relationships."""
    from src.models.academic import Class, Section
    result = await db.execute(
        select(ClassSection)
        .options(selectinload(ClassSection.class_), selectinload(ClassSection.section))
        .where(
            ClassSection.id == class_section_id,
            ClassSection.school_id == school_id,
            ClassSection.is_active.is_(True),
        )
    )
    cs = result.scalar_one_or_none()
    if not cs:
        raise NotFound("ClassSection", str(class_section_id))
    return cs


async def _get_class_section_label(db: AsyncSession, cs: ClassSection) -> tuple[str, str, str]:
    """Return (class_name, section_name, class_section) from a ClassSection."""
    from src.models.academic import Class, Section
    cls_result = await db.execute(select(Class).where(Class.id == cs.class_id))
    sec_result = await db.execute(select(Section).where(Section.id == cs.section_id))
    cls = cls_result.scalar_one_or_none()
    sec = sec_result.scalar_one_or_none()
    class_name = cls.name if cls else ""
    section_name = sec.name if sec else ""
    class_section = f"{class_name}-{section_name}"
    return class_name, section_name, class_section


async def get_attendance(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    class_section_id: uuid.UUID,
    target_date: date,
) -> dict:
    """Get attendance for a class + date (form data or already submitted)."""
    staff = await _get_staff_for_user(db, school_id, user)
    ay = await _get_current_academic_year(db, school_id)
    await _verify_class_assignment(db, school_id, staff.id, class_section_id, ay.id)

    cs = await _get_class_section(db, school_id, class_section_id)
    class_name, section_name, class_section_label = await _get_class_section_label(db, cs)

    # Check if attendance session already exists
    session_result = await db.execute(
        select(AttendanceSession).where(
            AttendanceSession.school_id == school_id,
            AttendanceSession.class_section_id == class_section_id,
            AttendanceSession.date == target_date,
            AttendanceSession.academic_year_id == ay.id,
            AttendanceSession.status == "Submitted",
            AttendanceSession.is_active.is_(True),
        )
    )
    session = session_result.scalar_one_or_none()

    # Get enrolled students for this class
    enrollment_result = await db.execute(
        select(StudentEnrollment).where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.class_section_id == class_section_id,
            StudentEnrollment.academic_year_id == ay.id,
            StudentEnrollment.is_active.is_(True),
        )
    )
    enrollments = enrollment_result.scalars().all()
    student_ids = [e.student_id for e in enrollments]

    # Get student details
    students_result = await db.execute(
        select(Student).where(
            Student.id.in_(student_ids),
            Student.is_active.is_(True),
        )
    )
    students = students_result.scalars().all()
    student_map = {s.id: s for s in students}

    if session:
        # Already submitted - return submitted records
        records_result = await db.execute(
            select(AttendanceRecord).where(
                AttendanceRecord.attendance_session_id == session.id,
                AttendanceRecord.is_active.is_(True),
            )
        )
        records = records_result.scalars().all()
        record_map = {r.student_id: r.status for r in records}

        present = sum(1 for r in records if r.status == "Present")
        absent = sum(1 for r in records if r.status == "Absent")
        late = sum(1 for r in records if r.status == "Late")
        total = len(records)

        response_records = []
        for sid in student_ids:
            student = student_map.get(sid)
            if student:
                response_records.append({
                    "student_id": sid,
                    "roll_number": student.admission_number,
                    "full_name": student.full_name,
                    "status": record_map.get(sid, "Not Marked"),
                })

        return {
            "class_section": class_section_label,
            "class_name": class_name,
            "section": section_name,
            "date": target_date,
            "is_submitted": True,
            "submitted_at": session.submitted_at,
            "summary": {
                "total_students": total,
                "present": present,
                "absent": absent,
                "late": late,
                "attendance_rate": round((present + late) / total * 100, 1) if total > 0 else 0.0,
            },
            "records": response_records,
        }
    else:
        # Not submitted - return blank form
        response_records = []
        for sid in student_ids:
            student = student_map.get(sid)
            if student:
                response_records.append({
                    "student_id": sid,
                    "roll_number": student.admission_number,
                    "full_name": student.full_name,
                    "status": "Not Marked",
                })

        return {
            "class_section": class_section_label,
            "class_name": class_name,
            "section": section_name,
            "date": target_date,
            "is_submitted": False,
            "submitted_at": None,
            "summary": None,
            "records": response_records,
        }


async def submit_attendance(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    data: SubmitAttendanceRequest,
) -> dict:
    """Submit attendance for a class on a specific date."""
    from datetime import date as date_type
    if data.date > date_type.today():
        from src.core.exceptions import ValidationError
        raise ValidationError("Cannot submit attendance for future dates")

    staff = await _get_staff_for_user(db, school_id, user)
    ay = await _get_current_academic_year(db, school_id, data.academic_year)
    await _verify_class_assignment(db, school_id, staff.id, data.class_id, ay.id)

    cs = await _get_class_section(db, school_id, data.class_id)
    class_name, section_name, class_section_label = await _get_class_section_label(db, cs)

    # Check for existing session
    existing_result = await db.execute(
        select(AttendanceSession).where(
            AttendanceSession.school_id == school_id,
            AttendanceSession.class_section_id == data.class_id,
            AttendanceSession.date == data.date,
            AttendanceSession.academic_year_id == ay.id,
            AttendanceSession.status == "Submitted",
            AttendanceSession.is_active.is_(True),
        )
    )
    if existing_result.scalar_one_or_none():
        raise AttendanceAlreadySubmitted(class_section_label, str(data.date))

    now = datetime.now(timezone.utc)

    # Calculate counts
    present = sum(1 for r in data.records if r.status.value == "Present")
    absent = sum(1 for r in data.records if r.status.value == "Absent")
    late = sum(1 for r in data.records if r.status.value == "Late")
    total = len(data.records)

    # Create session
    session = AttendanceSession(
        school_id=school_id,
        academic_year_id=ay.id,
        class_section_id=data.class_id,
        date=data.date,
        submitted_by=staff.id,
        submitted_at=now,
        status="Submitted",
        total_present=present,
        total_absent=absent,
        total_late=late,
        created_by=user.id,
    )
    db.add(session)
    await db.flush()

    # Create attendance records
    for record in data.records:
        attendance_record = AttendanceRecord(
            school_id=school_id,
            attendance_session_id=session.id,
            student_id=record.student_id,
            status=record.status.value,
            created_by=user.id,
        )
        db.add(attendance_record)

    await db.commit()

    return {
        "message": "Attendance submitted successfully",
        "class_section": class_section_label,
        "date": data.date,
        "summary": {
            "total_students": total,
            "present": present,
            "absent": absent,
            "late": late,
            "attendance_rate": round((present + late) / total * 100, 1) if total > 0 else 0.0,
        },
        "submitted_at": now,
    }


async def update_attendance(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    data: UpdateAttendanceRequest,
) -> dict:
    """Update attendance for a class on a specific date (corrections)."""
    from datetime import date as date_type
    if data.date > date_type.today():
        from src.core.exceptions import ValidationError
        raise ValidationError("Cannot update attendance for future dates")

    staff = await _get_staff_for_user(db, school_id, user)
    ay = await _get_current_academic_year(db, school_id)
    await _verify_class_assignment(db, school_id, staff.id, data.class_id, ay.id)

    cs = await _get_class_section(db, school_id, data.class_id)
    class_name, section_name, class_section_label = await _get_class_section_label(db, cs)

    # Find existing session
    session_result = await db.execute(
        select(AttendanceSession).where(
            AttendanceSession.school_id == school_id,
            AttendanceSession.class_section_id == data.class_id,
            AttendanceSession.date == data.date,
            AttendanceSession.academic_year_id == ay.id,
            AttendanceSession.status == "Submitted",
            AttendanceSession.is_active.is_(True),
        )
    )
    session = session_result.scalar_one_or_none()
    if not session:
        raise NotFound("AttendanceSession", f"{class_section_label} on {data.date}")

    now = datetime.now(timezone.utc)

    # Update records
    for record_input in data.records:
        record_result = await db.execute(
            select(AttendanceRecord).where(
                AttendanceRecord.attendance_session_id == session.id,
                AttendanceRecord.student_id == record_input.student_id,
                AttendanceRecord.is_active.is_(True),
            )
        )
        record = record_result.scalar_one_or_none()
        if record:
            record.status = record_input.status.value
            record.updated_by = user.id
        else:
            # Create new record if not exists
            new_record = AttendanceRecord(
                school_id=school_id,
                attendance_session_id=session.id,
                student_id=record_input.student_id,
                status=record_input.status.value,
                created_by=user.id,
            )
            db.add(new_record)

    # Recount after update
    await db.flush()
    records_result = await db.execute(
        select(AttendanceRecord).where(
            AttendanceRecord.attendance_session_id == session.id,
            AttendanceRecord.is_active.is_(True),
        )
    )
    all_records = records_result.scalars().all()
    present = sum(1 for r in all_records if r.status == "Present")
    absent = sum(1 for r in all_records if r.status == "Absent")
    late = sum(1 for r in all_records if r.status == "Late")
    total = len(all_records)

    # Update session counts
    session.total_present = present
    session.total_absent = absent
    session.total_late = late
    session.updated_by = user.id

    await db.commit()

    return {
        "message": "Attendance updated successfully",
        "class_section": class_section_label,
        "date": data.date,
        "summary": {
            "total_students": total,
            "present": present,
            "absent": absent,
            "late": late,
            "attendance_rate": round((present + late) / total * 100, 1) if total > 0 else 0.0,
        },
        "updated_at": now,
    }


async def get_attendance_history(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    pagination: PaginationParams,
    class_section_id: uuid.UUID | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> dict:
    """Get past attendance submissions by this teacher."""
    staff = await _get_staff_for_user(db, school_id, user)

    from src.models.attendance import AttendanceSession as AS
    base_filter = [
        AttendanceSession.school_id == school_id,
        AttendanceSession.submitted_by == staff.id,
        AttendanceSession.is_active.is_(True),
    ]

    if class_section_id:
        base_filter.append(AttendanceSession.class_section_id == class_section_id)
    if from_date:
        base_filter.append(AttendanceSession.date >= from_date)
    if to_date:
        base_filter.append(AttendanceSession.date <= to_date)

    # Count
    count_query = select(func.count()).select_from(
        select(AttendanceSession).where(*base_filter).subquery()
    )
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Paginated results with eager loading
    query = (
        select(AttendanceSession)
        .options(
            selectinload(AttendanceSession.class_section).selectinload(ClassSection.class_),
            selectinload(AttendanceSession.class_section).selectinload(ClassSection.section),
        )
        .where(*base_filter)
        .order_by(AttendanceSession.date.desc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    )
    result = await db.execute(query)
    sessions = result.scalars().all()

    items = []
    for session in sessions:
        cs = session.class_section
        if cs:
            class_name, section_name, class_section_label = await _get_class_section_label(db, cs)
        else:
            class_name, section_name, class_section_label = "", "", ""

        # Get record counts
        present = session.total_present or 0
        absent = session.total_absent or 0
        late_count = session.total_late or 0
        total_students = present + absent + late_count

        items.append({
            "id": session.id,
            "class_name": class_name,
            "section": section_name,
            "class_section": class_section_label,
            "date": session.date,
            "status": session.status,
            "total_students": total_students,
            "present": present,
            "absent": absent,
            "late": late_count,
            "submitted_at": session.submitted_at,
        })

    return paginate(items, total, pagination)


async def cancel_attendance(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    session_id: uuid.UUID,
) -> dict:
    """Cancel an attendance session (set status to Cancelled)."""
    staff = await _get_staff_for_user(db, school_id, user)

    result = await db.execute(
        select(AttendanceSession).where(
            AttendanceSession.id == session_id,
            AttendanceSession.school_id == school_id,
            AttendanceSession.is_active.is_(True),
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise NotFound("AttendanceSession", str(session_id))

    now = datetime.now(timezone.utc)
    session.status = "Cancelled"
    session.cancelled_at = now
    session.cancelled_by = staff.id
    session.updated_by = user.id

    await db.commit()

    cs = session.class_section
    class_name = cs.class_.name if cs and cs.class_ else ""
    section_name = cs.section.name if cs and cs.section else ""
    class_section_label = f"{class_name}-{section_name}"

    return {
        "id": session.id,
        "class_section": class_section_label,
        "date": session.date,
        "status": "Cancelled",
        "cancelled_on": now.date(),
        "message": "Attendance record cancelled.",
    }


async def get_attendance_summary(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    class_section_id: uuid.UUID,
    month: int,
    year: int,
    academic_year_name: str | None = None,
) -> dict:
    """Get attendance summary stats for a class over a month."""
    staff = await _get_staff_for_user(db, school_id, user)
    ay = await _get_current_academic_year(db, school_id, academic_year_name)
    await _verify_class_assignment(db, school_id, staff.id, class_section_id, ay.id)

    cs = await _get_class_section(db, school_id, class_section_id)
    class_name, section_name, class_section_label = await _get_class_section_label(db, cs)

    # Get all sessions for this class in this month
    from datetime import date as date_type

    first_day = date_type(year, month, 1)
    if month == 12:
        last_day = date_type(year + 1, 1, 1)
    else:
        last_day = date_type(year, month + 1, 1)

    sessions_result = await db.execute(
        select(AttendanceSession).where(
            AttendanceSession.school_id == school_id,
            AttendanceSession.class_section_id == class_section_id,
            AttendanceSession.academic_year_id == ay.id,
            AttendanceSession.date >= first_day,
            AttendanceSession.date < last_day,
            AttendanceSession.status == "Submitted",
            AttendanceSession.is_active.is_(True),
        )
    )
    sessions = sessions_result.scalars().all()
    days_marked = len(sessions)

    # Compute working days (approximate as 22 for a typical month)
    # In a real system, this would come from a calendar/holiday config
    working_days = 22

    # Aggregate per student
    student_attendance: dict[uuid.UUID, dict] = {}
    for session in sessions:
        records_result = await db.execute(
            select(AttendanceRecord).where(
                AttendanceRecord.attendance_session_id == session.id,
                AttendanceRecord.is_active.is_(True),
            )
        )
        records = records_result.scalars().all()
        for record in records:
            if record.student_id not in student_attendance:
                student_attendance[record.student_id] = {"present": 0, "absent": 0, "late": 0, "total": 0}
            student_attendance[record.student_id]["total"] += 1
            if record.status == "Present":
                student_attendance[record.student_id]["present"] += 1
            elif record.status == "Absent":
                student_attendance[record.student_id]["absent"] += 1
            elif record.status == "Late":
                student_attendance[record.student_id]["late"] += 1

    # Calculate average attendance percentage
    if student_attendance:
        percentages = []
        for sid, counts in student_attendance.items():
            if counts["total"] > 0:
                pct = (counts["present"] + counts["late"]) / counts["total"] * 100
                percentages.append(pct)
        avg_percentage = round(sum(percentages) / len(percentages), 1) if percentages else 0.0
    else:
        avg_percentage = 0.0

    # Find students below 75%
    students_below = []
    for sid, counts in student_attendance.items():
        if counts["total"] > 0:
            pct = (counts["present"] + counts["late"]) / counts["total"] * 100
            if pct < 75:
                # Fetch student details
                student_result = await db.execute(
                    select(Student).where(Student.id == sid, Student.is_active.is_(True))
                )
                student = student_result.scalar_one_or_none()
                if student:
                    students_below.append({
                        "student_id": sid,
                        "full_name": student.full_name,
                        "roll_number": student.admission_number,
                        "attendance_percentage": round(pct, 1),
                    })

    return {
        "class_section": class_section_label,
        "month": month,
        "year": year,
        "academic_year": ay.name,
        "working_days": working_days,
        "days_marked": days_marked,
        "average_attendance_percentage": avg_percentage,
        "students_below_75": students_below,
    }
