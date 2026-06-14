from __future__ import annotations

import uuid
from datetime import date

from fastapi import HTTPException
from sqlalchemy import and_, select, delete
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
    """Lightweight list: teachers with mentee count only."""
    from sqlalchemy import func

    ay = await _get_current_academic_year(db, school_id)

    # Count mentees per staff
    count_query = (
        select(
            StudentMentor.staff_id,
            func.count(StudentMentor.id).label("mentee_count"),
        )
        .where(
            StudentMentor.school_id == school_id,
            StudentMentor.academic_year_id == ay.id,
            StudentMentor.is_active.is_(True),
        )
        .group_by(StudentMentor.staff_id)
    )
    count_result = await db.execute(count_query)
    counts = {row.staff_id: row.mentee_count for row in count_result.all()}

    if not counts:
        total_enrolled_result = await db.execute(
            select(func.count(StudentEnrollment.student_id)).where(
                StudentEnrollment.school_id == school_id,
                StudentEnrollment.academic_year_id == ay.id,
                StudentEnrollment.is_active.is_(True),
                StudentEnrollment.status == "Active",
            )
        )
        return {"mentors": [], "total_enrolled": total_enrolled_result.scalar() or 0, "total_mentees": 0}

    # Fetch staff details for those with assignments
    staff_result = await db.execute(
        select(Staff).where(Staff.id.in_(counts.keys()), Staff.is_active.is_(True))
    )
    staff_list = staff_result.scalars().all()

    mentors = []
    for s in staff_list:
        mentors.append({
            "staff_id": str(s.id),
            "staff_name": s.full_name,
            "designation": s.designation or "",
            "mentee_count": counts.get(s.id, 0),
        })

    mentors.sort(key=lambda m: m["staff_name"])

    # Total enrolled students for unassigned calculation
    total_enrolled_result = await db.execute(
        select(func.count(StudentEnrollment.student_id)).where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.academic_year_id == ay.id,
            StudentEnrollment.is_active.is_(True),
            StudentEnrollment.status == "Active",
        )
    )
    total_enrolled = total_enrolled_result.scalar() or 0
    total_mentees = sum(counts.values())

    return {"mentors": mentors, "total_enrolled": total_enrolled, "total_mentees": total_mentees}


async def get_mentor_students(db: AsyncSession, school_id: uuid.UUID, staff_id: uuid.UUID) -> dict:
    """Get detailed student list for a specific mentor/teacher."""
    from sqlalchemy.orm import selectinload

    ay = await _get_current_academic_year(db, school_id)

    result = await db.execute(
        select(StudentMentor)
        .options(selectinload(StudentMentor.student))
        .where(
            StudentMentor.school_id == school_id,
            StudentMentor.academic_year_id == ay.id,
            StudentMentor.staff_id == staff_id,
            StudentMentor.is_active.is_(True),
        )
    )
    assignments = result.scalars().all()

    students = []
    for a in assignments:
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

        students.append({
            "id": str(a.id),
            "student_id": str(a.student_id),
            "student_name": a.student.full_name if a.student else "",
            "class_section": class_section,
            "assigned_date": str(a.assigned_date) if a.assigned_date else None,
        })

    return {"students": students}


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
    # Validate required fields
    if not staff_id:
        raise HTTPException(status_code=400, detail="teacher_id must not be empty")
    if not student_ids:
        raise HTTPException(status_code=400, detail="student_ids must not be empty")

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


async def shuffle_auto_assign(db: AsyncSession, school_id: uuid.UUID, user_id: uuid.UUID) -> dict:
    """Shuffle all active students and distribute evenly across all active teachers."""
    import random

    ay = await _get_current_academic_year(db, school_id)

    # Get all active teachers
    teachers_result = await db.execute(
        select(Staff.id).where(
            Staff.school_id == school_id,
            Staff.is_teacher.is_(True),
            Staff.status == "Active",
            Staff.is_active.is_(True),
        )
    )
    teacher_ids = [r[0] for r in teachers_result.all()]
    if not teacher_ids:
        return {"message": "No active teachers found", "assigned": 0}

    # Get all active students
    students_result = await db.execute(
        select(StudentEnrollment.student_id).where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.academic_year_id == ay.id,
            StudentEnrollment.is_active.is_(True),
        )
    )
    student_ids = [r[0] for r in students_result.all()]
    if not student_ids:
        return {"message": "No active students found", "assigned": 0}

    # Remove all existing mentor assignments for this academic year
    await db.execute(
        delete(StudentMentor).where(
            StudentMentor.school_id == school_id,
            StudentMentor.academic_year_id == ay.id,
        )
    )

    # Shuffle students randomly
    random.shuffle(student_ids)

    # Distribute evenly
    count = 0
    for i, sid in enumerate(student_ids):
        teacher_id = teacher_ids[i % len(teacher_ids)]
        db.add(StudentMentor(
            school_id=school_id,
            staff_id=teacher_id,
            student_id=sid,
            academic_year_id=ay.id,
            assigned_date=date.today(),
            created_by=user_id,
        ))
        count += 1

    await db.commit()
    return {"message": f"Shuffled & assigned {count} students across {len(teacher_ids)} teachers", "assigned": count}
