from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFound
from src.models.core import AcademicYear
from src.models.staff import Staff
from src.models.student import Student, StudentEnrollment, StudentMentor


async def _get_current_academic_year(db: AsyncSession, school_id: uuid.UUID) -> AcademicYear:
    result = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
            AcademicYear.is_active.is_(True),
        )
    )
    ay = result.scalar_one_or_none()
    if not ay:
        raise NotFound("Current academic year")
    return ay


async def list_mentors(db: AsyncSession, school_id: uuid.UUID) -> dict:
    ay = await _get_current_academic_year(db, school_id)

    from sqlalchemy.orm import selectinload

    # Get all mentor assignments for current year with eager loading
    result = await db.execute(
        select(StudentMentor)
        .options(selectinload(StudentMentor.staff), selectinload(StudentMentor.student))
        .where(
            StudentMentor.school_id == school_id,
            StudentMentor.academic_year_id == ay.id,
            StudentMentor.is_active.is_(True),
        )
    )
    assignments = result.scalars().all()

    # Group by staff
    staff_map: dict[uuid.UUID, dict] = {}
    for a in assignments:
        if a.staff_id not in staff_map:
            staff = a.staff
            staff_map[a.staff_id] = {
                "staff_id": str(a.staff_id),
                "staff_name": staff.full_name if staff else "",
                "designation": staff.designation or "" if staff else "",
                "students": [],
            }
        # Get student enrollment for class-section
        enroll_result = await db.execute(
            select(StudentEnrollment).where(
                StudentEnrollment.student_id == a.student_id,
                StudentEnrollment.academic_year_id == ay.id,
                StudentEnrollment.is_active.is_(True),
            )
        )
        enrollment = enroll_result.scalar_one_or_none()
        class_section = ""
        if enrollment and enrollment.class_section:
            cs = enrollment.class_section
            class_section = f"{cs.class_.name}-{cs.section.name}" if cs.class_ and cs.section else ""

        staff_map[a.staff_id]["students"].append({
            "id": str(a.id),
            "student_id": str(a.student_id),
            "student_name": a.student.full_name if a.student else "",
            "class_section": class_section,
            "assigned_date": str(a.assigned_date) if a.assigned_date else None,
        })

    return {"mentors": list(staff_map.values())}


async def list_teachers(db: AsyncSession, school_id: uuid.UUID) -> dict:
    result = await db.execute(
        select(Staff).where(
            Staff.school_id == school_id,
            Staff.is_teacher.is_(True),
            Staff.status == "Active",
            Staff.is_active.is_(True),
        ).order_by(Staff.full_name)
    )
    teachers = result.scalars().all()
    return {
        "teachers": [
            {"id": str(t.id), "name": t.full_name, "designation": t.designation or ""}
            for t in teachers
        ]
    }


async def list_students(db: AsyncSession, school_id: uuid.UUID, class_section_id: uuid.UUID | None = None) -> dict:
    ay = await _get_current_academic_year(db, school_id)

    from sqlalchemy.orm import selectinload

    query = (
        select(StudentEnrollment)
        .options(selectinload(StudentEnrollment.student))
        .where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.academic_year_id == ay.id,
            StudentEnrollment.status == "Active",
            StudentEnrollment.is_active.is_(True),
        )
    )
    if class_section_id:
        query = query.where(StudentEnrollment.class_section_id == class_section_id)

    query = query.order_by(StudentEnrollment.roll_number)
    result = await db.execute(query)
    enrollments = result.scalars().all()

    students = []
    for e in enrollments:
        cs = e.class_section
        class_section = f"{cs.class_.name}-{cs.section.name}" if cs and cs.class_ and cs.section else ""
        students.append({
            "id": str(e.student_id),
            "name": e.student.full_name if e.student else "",
            "class_section": class_section,
            "class_section_id": str(e.class_section_id),
        })

    return {"students": students}


async def assign_mentor(db: AsyncSession, school_id: uuid.UUID, staff_id: uuid.UUID, student_ids: list[uuid.UUID], user_id: uuid.UUID) -> dict:
    ay = await _get_current_academic_year(db, school_id)

    # Validate staff exists and is teacher
    staff_result = await db.execute(
        select(Staff).where(Staff.id == staff_id, Staff.school_id == school_id, Staff.is_active.is_(True))
    )
    if not staff_result.scalar_one_or_none():
        raise NotFound("Teacher")

    created = 0
    for sid in student_ids:
        # Check if already assigned
        existing = await db.execute(
            select(StudentMentor).where(
                StudentMentor.school_id == school_id,
                StudentMentor.academic_year_id == ay.id,
                StudentMentor.student_id == sid,
            )
        )
        if existing.scalar_one_or_none():
            continue
        mentor = StudentMentor(
            school_id=school_id,
            academic_year_id=ay.id,
            student_id=sid,
            staff_id=staff_id,
            assigned_date=date.today(),
            created_by=user_id,
        )
        db.add(mentor)
        created += 1

    await db.commit()
    return {"assigned": created}


async def remove_assignment(db: AsyncSession, school_id: uuid.UUID, assignment_id: uuid.UUID) -> dict:
    result = await db.execute(
        select(StudentMentor).where(StudentMentor.id == assignment_id, StudentMentor.school_id == school_id)
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise NotFound("Mentor assignment")
    await db.delete(assignment)
    await db.commit()
    return {"deleted": True}
