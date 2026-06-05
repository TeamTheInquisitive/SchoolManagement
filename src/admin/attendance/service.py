"""Admin attendance service — same logic as teacher but no class-assignment restriction."""
from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.exceptions import NotFound
from src.models.academic import Class, ClassSection, Section
from src.models.attendance import AttendanceRecord, AttendanceSession
from src.models.core import AcademicYear, User
from src.models.student import Student, StudentEnrollment
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


async def get_attendance(db: AsyncSession, school_id: uuid.UUID, user: User, class_section_id: uuid.UUID, target_date: date) -> dict:
    ay = await _get_current_academic_year(db, school_id)
    cs = await _get_class_section(db, school_id, class_section_id)
    class_name, section_name, label = await _cs_label(db, cs)

    session = (await db.execute(
        select(AttendanceSession).where(
            AttendanceSession.school_id == school_id,
            AttendanceSession.class_section_id == class_section_id,
            AttendanceSession.date == target_date,
            AttendanceSession.academic_year_id == ay.id,
            AttendanceSession.status == "Submitted",
            AttendanceSession.is_active.is_(True),
        )
    )).scalar_one_or_none()

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
            "summary": {"total_students": total, "present": present, "absent": absent, "late": late, "attendance_rate": round((present + late) / total * 100, 1) if total else 0.0},
            "records": [{"student_id": sid, "roll_number": smap[sid].admission_number if smap.get(sid) else None, "full_name": smap[sid].full_name if smap.get(sid) else None, "status": rmap.get(sid, "Not Marked")} for sid in student_ids if smap.get(sid)],
        }

    return {
        "class_section": label, "class_name": class_name, "section": section_name,
        "date": target_date, "is_submitted": False, "submitted_at": None, "summary": None,
        "records": [{"student_id": sid, "roll_number": smap[sid].admission_number, "full_name": smap[sid].full_name, "status": "Not Marked"} for sid in student_ids if smap.get(sid)],
    }


async def submit_attendance(db: AsyncSession, school_id: uuid.UUID, user: User, data: SubmitAttendanceRequest) -> dict:
    ay = await _get_current_academic_year(db, school_id, data.academic_year)
    cs = await _get_class_section(db, school_id, data.class_id)
    _, _, label = await _cs_label(db, cs)

    existing = (await db.execute(
        select(AttendanceSession).where(
            AttendanceSession.school_id == school_id,
            AttendanceSession.class_section_id == data.class_id,
            AttendanceSession.date == data.date,
            AttendanceSession.academic_year_id == ay.id,
            AttendanceSession.status == "Submitted",
            AttendanceSession.is_active.is_(True),
        )
    )).scalar_one_or_none()
    if existing:
        raise AttendanceAlreadySubmitted(label, str(data.date))

    now = datetime.now(timezone.utc)
    present = sum(1 for r in data.records if r.status.value == "Present")
    absent = sum(1 for r in data.records if r.status.value == "Absent")
    late = sum(1 for r in data.records if r.status.value == "Late")
    total = len(data.records)

    session = AttendanceSession(
        school_id=school_id, academic_year_id=ay.id, class_section_id=data.class_id,
        date=data.date, submitted_by=None, submitted_at=now, status="Submitted",
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

    session = (await db.execute(
        select(AttendanceSession).where(
            AttendanceSession.school_id == school_id,
            AttendanceSession.class_section_id == data.class_id,
            AttendanceSession.date == data.date,
            AttendanceSession.academic_year_id == ay.id,
            AttendanceSession.status == "Submitted",
            AttendanceSession.is_active.is_(True),
        )
    )).scalar_one_or_none()
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
