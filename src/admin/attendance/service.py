"""Admin attendance service — same logic as teacher but no class-assignment restriction."""
from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.exceptions import NotFound
from src.models.academic import Class, ClassSection, ClassSubject, Section, Subject
from src.models.attendance import AttendanceRecord, AttendanceSession
from src.models.core import AcademicYear, User
from src.models.staff import Staff
from src.models.student import Student, StudentEnrollment
from src.models.timetable import TimetableSlot
from src.teacher.attendance.exceptions import AttendanceAlreadySubmitted
from src.teacher.attendance.schemas import SubmitAttendanceRequest, UpdateAttendanceRequest


async def _get_current_academic_year(db: AsyncSession, school_id: uuid.UUID, name: str | None = None) -> AcademicYear:
    q = select(AcademicYear).where(AcademicYear.school_id == school_id, AcademicYear.is_active.is_(True))
    if name:
        q = q.where(AcademicYear.name == name)
    else:
        q = q.where(AcademicYear.is_current.is_(True))
    ay = (await db.execute(q)).scalar_one_or_none()
    if not ay:
        raise NotFound("AcademicYear")
    return ay


async def _get_class_section(db: AsyncSession, school_id: uuid.UUID, cs_id: uuid.UUID) -> ClassSection:
    result = await db.execute(
        select(ClassSection)
        .options(selectinload(ClassSection.class_), selectinload(ClassSection.section))
        .where(ClassSection.id == cs_id, ClassSection.school_id == school_id, ClassSection.is_active.is_(True))
    )
    cs = result.scalar_one_or_none()
    if not cs:
        raise NotFound("ClassSection", str(cs_id))
    return cs


async def _cs_label(db: AsyncSession, cs: ClassSection) -> tuple[str, str, str]:
    cls = (await db.execute(select(Class).where(Class.id == cs.class_id))).scalar_one_or_none()
    sec = (await db.execute(select(Section).where(Section.id == cs.section_id))).scalar_one_or_none()
    cn, sn = cls.name if cls else "", sec.name if sec else ""
    return cn, sn, f"{cn}-{sn}"


async def get_attendance(
    db: AsyncSession, school_id: uuid.UUID, user: User,
    class_section_id: uuid.UUID, target_date: date,
    subject_id: uuid.UUID | None = None, period_number: int | None = None,
) -> dict:
    ay = await _get_current_academic_year(db, school_id)
    cs = await _get_class_section(db, school_id, class_section_id)
    class_name, section_name, label = await _cs_label(db, cs)

    session_query = select(AttendanceSession).where(
        AttendanceSession.school_id == school_id,
        AttendanceSession.class_section_id == class_section_id,
        AttendanceSession.date == target_date,
        AttendanceSession.academic_year_id == ay.id,
        AttendanceSession.status == "Submitted",
        AttendanceSession.is_active.is_(True),
    )
    if subject_id:
        session_query = session_query.where(AttendanceSession.subject_id == subject_id)
    else:
        session_query = session_query.where(AttendanceSession.subject_id.is_(None))
    if period_number is not None:
        session_query = session_query.where(AttendanceSession.period_number == period_number)
    else:
        session_query = session_query.where(AttendanceSession.period_number.is_(None))

    session = (await db.execute(session_query)).scalar_one_or_none()

    enrollments = (await db.execute(
        select(StudentEnrollment).where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.class_section_id == class_section_id,
            StudentEnrollment.academic_year_id == ay.id,
            StudentEnrollment.is_active.is_(True),
        )
    )).scalars().all()
    student_ids = [e.student_id for e in enrollments]

    students = (await db.execute(
        select(Student).where(Student.id.in_(student_ids), Student.is_active.is_(True))
    )).scalars().all()
    smap = {s.id: s for s in students}

    if session:
        records = (await db.execute(
            select(AttendanceRecord).where(AttendanceRecord.attendance_session_id == session.id, AttendanceRecord.is_active.is_(True))
        )).scalars().all()
        rmap = {r.student_id: r.status for r in records}
        present = sum(1 for r in records if r.status == "Present")
        absent = sum(1 for r in records if r.status == "Absent")
        late = sum(1 for r in records if r.status == "Late")
        total = len(records)
        return {
            "class_section": label, "class_name": class_name, "section": section_name,
            "date": target_date, "is_submitted": True, "submitted_at": session.submitted_at,
            "subject_id": str(subject_id) if subject_id else None,
            "period_number": period_number,
            "summary": {"total_students": total, "present": present, "absent": absent, "late": late, "attendance_rate": round((present + late) / total * 100, 1) if total else 0.0},
            "records": [{"student_id": sid, "roll_number": smap[sid].admission_number if smap.get(sid) else None, "full_name": smap[sid].full_name if smap.get(sid) else None, "status": rmap.get(sid, "Not Marked")} for sid in student_ids if smap.get(sid)],
        }

    return {
        "class_section": label, "class_name": class_name, "section": section_name,
        "date": target_date, "is_submitted": False, "submitted_at": None,
        "subject_id": str(subject_id) if subject_id else None,
        "period_number": period_number,
        "summary": None,
        "records": [{"student_id": sid, "roll_number": smap[sid].admission_number, "full_name": smap[sid].full_name, "status": "Not Marked"} for sid in student_ids if smap.get(sid)],
    }


async def submit_attendance(db: AsyncSession, school_id: uuid.UUID, user: User, data: SubmitAttendanceRequest) -> dict:
    ay = await _get_current_academic_year(db, school_id, data.academic_year)
    cs = await _get_class_section(db, school_id, data.class_id)
    _, _, label = await _cs_label(db, cs)

    existing_query = select(AttendanceSession).where(
        AttendanceSession.school_id == school_id,
        AttendanceSession.class_section_id == data.class_id,
        AttendanceSession.date == data.date,
        AttendanceSession.academic_year_id == ay.id,
        AttendanceSession.status == "Submitted",
        AttendanceSession.is_active.is_(True),
    )
    if data.subject_id:
        existing_query = existing_query.where(AttendanceSession.subject_id == data.subject_id)
    else:
        existing_query = existing_query.where(AttendanceSession.subject_id.is_(None))
    if data.period_number is not None:
        existing_query = existing_query.where(AttendanceSession.period_number == data.period_number)
    else:
        existing_query = existing_query.where(AttendanceSession.period_number.is_(None))

    existing = (await db.execute(existing_query)).scalar_one_or_none()
    if existing:
        raise AttendanceAlreadySubmitted(label, str(data.date))

    now = datetime.now(timezone.utc)
    present = sum(1 for r in data.records if r.status.value == "Present")
    absent = sum(1 for r in data.records if r.status.value == "Absent")
    late = sum(1 for r in data.records if r.status.value == "Late")
    total = len(data.records)

    session = AttendanceSession(
        school_id=school_id, academic_year_id=ay.id, class_section_id=data.class_id,
        date=data.date, subject_id=data.subject_id, period_number=data.period_number,
        submitted_by=None, submitted_at=now, status="Submitted",
        total_present=present, total_absent=absent, total_late=late, created_by=user.id,
    )
    db.add(session)
    await db.flush()

    for record in data.records:
        db.add(AttendanceRecord(
            school_id=school_id, attendance_session_id=session.id,
            student_id=record.student_id, status=record.status.value, created_by=user.id,
        ))
    await db.commit()

    return {
        "message": "Attendance submitted successfully", "class_section": label, "date": data.date,
        "summary": {"total_students": total, "present": present, "absent": absent, "late": late, "attendance_rate": round((present + late) / total * 100, 1) if total else 0.0},
        "submitted_at": now,
    }


async def update_attendance(db: AsyncSession, school_id: uuid.UUID, user: User, data: UpdateAttendanceRequest) -> dict:
    ay = await _get_current_academic_year(db, school_id)
    cs = await _get_class_section(db, school_id, data.class_id)
    _, _, label = await _cs_label(db, cs)

    session_query = select(AttendanceSession).where(
        AttendanceSession.school_id == school_id,
        AttendanceSession.class_section_id == data.class_id,
        AttendanceSession.date == data.date,
        AttendanceSession.academic_year_id == ay.id,
        AttendanceSession.status == "Submitted",
        AttendanceSession.is_active.is_(True),
    )
    if data.subject_id:
        session_query = session_query.where(AttendanceSession.subject_id == data.subject_id)
    else:
        session_query = session_query.where(AttendanceSession.subject_id.is_(None))
    if data.period_number is not None:
        session_query = session_query.where(AttendanceSession.period_number == data.period_number)
    else:
        session_query = session_query.where(AttendanceSession.period_number.is_(None))

    session = (await db.execute(session_query)).scalar_one_or_none()
    if not session:
        raise NotFound("AttendanceSession")

    # Update records
    for record in data.records:
        existing_record = (await db.execute(
            select(AttendanceRecord).where(
                AttendanceRecord.attendance_session_id == session.id,
                AttendanceRecord.student_id == record.student_id,
                AttendanceRecord.is_active.is_(True),
            )
        )).scalar_one_or_none()
        if existing_record:
            existing_record.status = record.status.value
        else:
            db.add(AttendanceRecord(
                school_id=school_id, attendance_session_id=session.id,
                student_id=record.student_id, status=record.status.value, created_by=user.id,
            ))

    # Recalculate
    all_records = (await db.execute(
        select(AttendanceRecord).where(AttendanceRecord.attendance_session_id == session.id, AttendanceRecord.is_active.is_(True))
    )).scalars().all()
    present = sum(1 for r in all_records if r.status == "Present")
    absent = sum(1 for r in all_records if r.status == "Absent")
    late = sum(1 for r in all_records if r.status == "Late")
    total = len(all_records)
    session.total_present = present
    session.total_absent = absent
    session.total_late = late
    now = datetime.now(timezone.utc)
    await db.commit()

    return {
        "message": "Attendance updated successfully", "class_section": label, "date": data.date,
        "summary": {"total_students": total, "present": present, "absent": absent, "late": late, "attendance_rate": round((present + late) / total * 100, 1) if total else 0.0},
        "updated_at": now,
    }


async def get_class_subjects_status(
    db: AsyncSession, school_id: uuid.UUID, class_section_id: uuid.UUID, target_date: date
) -> dict:
    """Get all subjects for a class section with their attendance status for the day."""
    ay = await _get_current_academic_year(db, school_id)
    cs = await _get_class_section(db, school_id, class_section_id)
    class_name, section_name, label = await _cs_label(db, cs)

    # Get the day of week for the given date
    day_of_week = target_date.strftime("%A")

    # Get all timetable slots for this class on this day
    slots_result = await db.execute(
        select(TimetableSlot).where(
            TimetableSlot.school_id == school_id,
            TimetableSlot.academic_year_id == ay.id,
            TimetableSlot.class_section_id == class_section_id,
            TimetableSlot.day_of_week == day_of_week,
            TimetableSlot.is_active.is_(True),
        )
    )
    slots = slots_result.scalars().all()

    # Get attendance sessions for this class on this date (subject-wise only)
    sessions_result = await db.execute(
        select(AttendanceSession).where(
            AttendanceSession.school_id == school_id,
            AttendanceSession.class_section_id == class_section_id,
            AttendanceSession.date == target_date,
            AttendanceSession.academic_year_id == ay.id,
            AttendanceSession.status == "Submitted",
            AttendanceSession.is_active.is_(True),
            AttendanceSession.subject_id.isnot(None),
        )
    )
    sessions = sessions_result.scalars().all()

    # Build a lookup: subject_id -> session info
    session_map = {}
    for sess in sessions:
        key = sess.subject_id
        session_map[key] = {
            "is_submitted": True,
            "submitted_at": sess.submitted_at,
            "total_present": sess.total_present or 0,
            "total_absent": sess.total_absent or 0,
            "total_late": sess.total_late or 0,
            "period_number": sess.period_number,
        }

    # Build subjects list from timetable slots
    subjects = []
    for idx, slot in enumerate(sorted(slots, key=lambda s: s.period_config.start_time if s.period_config else ""), start=1):
        if not slot.subject_id:
            continue
        subject_name = slot.subject.name if slot.subject else "Unknown"
        teacher_name = slot.staff.full_name if slot.staff else None
        teacher_id = slot.staff_id
        period = slot.period_config
        period_start = period.start_time.strftime("%H:%M") if period else None
        period_end = period.end_time.strftime("%H:%M") if period else None
        period_name = period.name if period else f"Period {idx}"

        att_info = session_map.get(slot.subject_id)
        subjects.append({
            "subject_id": str(slot.subject_id),
            "subject_name": subject_name,
            "teacher_name": teacher_name,
            "teacher_id": str(teacher_id) if teacher_id else None,
            "period_number": idx,
            "period_name": period_name,
            "period_start": period_start,
            "period_end": period_end,
            "is_submitted": att_info["is_submitted"] if att_info else False,
            "submitted_at": att_info["submitted_at"] if att_info else None,
            "total_present": att_info["total_present"] if att_info else 0,
            "total_absent": att_info["total_absent"] if att_info else 0,
            "total_late": att_info["total_late"] if att_info else 0,
        })

    # Overall summary
    total_subjects = len(subjects)
    subjects_marked = sum(1 for s in subjects if s["is_submitted"])
    total_present_all = sum(s["total_present"] for s in subjects)
    total_absent_all = sum(s["total_absent"] for s in subjects)

    return {
        "class_section": label,
        "class_name": class_name,
        "section": section_name,
        "class_section_id": str(class_section_id),
        "date": target_date,
        "day_of_week": day_of_week,
        "summary": {
            "total_subjects": total_subjects,
            "subjects_marked": subjects_marked,
            "subjects_pending": total_subjects - subjects_marked,
            "total_present": total_present_all,
            "total_absent": total_absent_all,
        },
        "subjects": subjects,
    }
