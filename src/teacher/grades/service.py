from __future__ import annotations

import csv
import io
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AccessDenied, NotFound, ValidationError
from src.core.pagination import PaginationParams, paginate
from src.models.academic import Class, ClassSection, Section, Subject
from src.models.core import AcademicYear, User
from src.models.examination import Exam, ExamResult, GradeScale, GradeSystem
from src.models.staff import ClassAssignment, Staff
from src.models.student import Student, StudentEnrollment, StudentMentor

from src.teacher.grades.schemas import (
    SubmitGradesRequest,
    UpdateGradesRequest,
)


async def _get_academic_year(
    db: AsyncSession, school_id: uuid.UUID, name: str | None = None
) -> AcademicYear:
    """Get academic year by name or current."""
    if name:
        result = await db.execute(
            select(AcademicYear).where(
                AcademicYear.school_id == school_id,
                AcademicYear.name == name,
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


async def _verify_teacher_assignment(
    db: AsyncSession,
    school_id: uuid.UUID,
    staff_id: uuid.UUID,
    class_section_id: uuid.UUID,
    subject_id: uuid.UUID,
    academic_year_id: uuid.UUID,
) -> None:
    """Verify teacher is assigned to teach this subject in this class."""
    result = await db.execute(
        select(ClassAssignment).where(
            ClassAssignment.school_id == school_id,
            ClassAssignment.staff_id == staff_id,
            ClassAssignment.class_section_id == class_section_id,
            ClassAssignment.subject_id == subject_id,
            ClassAssignment.academic_year_id == academic_year_id,
            ClassAssignment.is_active.is_(True),
        )
    )
    if not result.scalar_one_or_none():
        raise AccessDenied("You are not assigned to teach this subject in this class")


async def _get_active_grade_system(
    db: AsyncSession, school_id: uuid.UUID
) -> GradeSystem | None:
    """Get the default/active grade system."""
    result = await db.execute(
        select(GradeSystem).where(
            GradeSystem.school_id == school_id,
            GradeSystem.is_default.is_(True),
            GradeSystem.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


def _compute_grade(percentage: float, scales: list[GradeScale]) -> str | None:
    """Compute grade from percentage using grade scales."""
    for scale in sorted(scales, key=lambda s: s.min_percentage, reverse=True):
        if float(scale.min_percentage) <= percentage <= float(scale.max_percentage):
            return scale.grade
    return None


def _compute_ranks(results: list[ExamResult]) -> None:
    """Compute ranks for results in-place."""
    scorable = [r for r in results if r.marks_obtained is not None and r.attendance == "Present"]
    scorable.sort(key=lambda r: float(r.marks_obtained), reverse=True)  # type: ignore[arg-type]
    for idx, result in enumerate(scorable, start=1):
        result.rank = idx


async def _is_class_teacher_for_section(
    db: AsyncSession,
    school_id: uuid.UUID,
    staff_id: uuid.UUID,
    class_section_id: uuid.UUID,
    academic_year_id: uuid.UUID,
) -> bool:
    """Check if teacher is class teacher for the given section."""
    result = await db.execute(
        select(ClassAssignment).where(
            ClassAssignment.school_id == school_id,
            ClassAssignment.staff_id == staff_id,
            ClassAssignment.class_section_id == class_section_id,
            ClassAssignment.academic_year_id == academic_year_id,
            ClassAssignment.is_class_teacher.is_(True),
            ClassAssignment.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none() is not None


async def _is_subject_teacher_for_exam(
    db: AsyncSession,
    school_id: uuid.UUID,
    staff_id: uuid.UUID,
    class_section_id: uuid.UUID,
    subject_id: uuid.UUID,
    academic_year_id: uuid.UUID,
) -> bool:
    """Check if teacher is the subject teacher for this exam's subject."""
    result = await db.execute(
        select(ClassAssignment).where(
            ClassAssignment.school_id == school_id,
            ClassAssignment.staff_id == staff_id,
            ClassAssignment.class_section_id == class_section_id,
            ClassAssignment.subject_id == subject_id,
            ClassAssignment.academic_year_id == academic_year_id,
            ClassAssignment.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none() is not None


async def _get_mentored_section_ids(
    db: AsyncSession,
    school_id: uuid.UUID,
    staff_id: uuid.UUID,
    academic_year_id: uuid.UUID,
) -> set[uuid.UUID]:
    """Return class_section_ids of students this staff mentors (current AY)."""
    mentor_result = await db.execute(
        select(StudentMentor.student_id).where(
            StudentMentor.school_id == school_id,
            StudentMentor.staff_id == staff_id,
            StudentMentor.academic_year_id == academic_year_id,
            StudentMentor.is_active.is_(True),
        )
    )
    student_ids = [r[0] for r in mentor_result.all()]
    if not student_ids:
        return set()

    enroll_result = await db.execute(
        select(StudentEnrollment.class_section_id).where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.student_id.in_(student_ids),
            StudentEnrollment.academic_year_id == academic_year_id,
            StudentEnrollment.is_active.is_(True),
        )
    )
    return {r[0] for r in enroll_result.all() if r[0] is not None}


async def _is_mentor_for_section(
    db: AsyncSession,
    school_id: uuid.UUID,
    staff_id: uuid.UUID,
    class_section_id: uuid.UUID,
    academic_year_id: uuid.UUID,
) -> bool:
    """Check if teacher mentors at least one student in the given section."""
    section_ids = await _get_mentored_section_ids(
        db, school_id, staff_id, academic_year_id
    )
    return class_section_id in section_ids


async def _assert_can_view_exam(
    db: AsyncSession,
    school_id: uuid.UUID,
    staff_id: uuid.UUID,
    exam: Exam,
    academic_year_id: uuid.UUID,
) -> None:
    """Allow read access if the teacher is the subject teacher, the class
    teacher, or a mentor of a student in the exam's section."""
    is_subject_teacher = await _is_subject_teacher_for_exam(
        db, school_id, staff_id, exam.class_section_id, exam.subject_id, academic_year_id
    )
    if is_subject_teacher:
        return
    is_class_teacher = await _is_class_teacher_for_section(
        db, school_id, staff_id, exam.class_section_id, academic_year_id
    )
    if is_class_teacher:
        return
    is_mentor = await _is_mentor_for_section(
        db, school_id, staff_id, exam.class_section_id, academic_year_id
    )
    if is_mentor:
        return
    raise AccessDenied(
        "You do not have access to this exam. Only the subject teacher, "
        "class teacher, or assigned mentor can view it."
    )


async def get_grades(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    pagination: PaginationParams,
    class_id: uuid.UUID | None = None,
    exam_id: uuid.UUID | None = None,
) -> dict:
    """Get grades for a class + exam with KPI stats."""
    staff = await _get_staff_for_user(db, school_id, user)

    if not exam_id:
        raise ValidationError("exam_id is required")

    # Get exam
    exam_result = await db.execute(
        select(Exam).where(
            Exam.id == exam_id,
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
        )
    )
    exam = exam_result.scalar_one_or_none()
    if not exam:
        raise NotFound("Exam", str(exam_id))

    ay = exam.academic_year

    # Check access: teacher must be subject teacher, class teacher, or mentor
    is_subject_teacher = await _is_subject_teacher_for_exam(
        db, school_id, staff.id, exam.class_section_id, exam.subject_id, ay.id
    )
    is_class_teacher = await _is_class_teacher_for_section(
        db, school_id, staff.id, exam.class_section_id, ay.id
    )
    is_mentor = False
    if not is_subject_teacher and not is_class_teacher:
        is_mentor = await _is_mentor_for_section(
            db, school_id, staff.id, exam.class_section_id, ay.id
        )

    if not is_subject_teacher and not is_class_teacher and not is_mentor:
        raise AccessDenied(
            "You do not have access to this exam. Only the subject teacher, "
            "class teacher, or assigned mentor can view it."
        )

    # can_grade is True only if subject teacher and exam is not published
    can_grade = is_subject_teacher and exam.status != "Published"

    cs = exam.class_section
    cls_result = await db.execute(select(Class).where(Class.id == cs.class_id))
    cls = cls_result.scalar_one()
    sec_result = await db.execute(select(Section).where(Section.id == cs.section_id))
    sec = sec_result.scalar_one()

    # Get enrolled students
    enrollments_result = await db.execute(
        select(StudentEnrollment)
        .where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.class_section_id == exam.class_section_id,
            StudentEnrollment.academic_year_id == ay.id,
            StudentEnrollment.is_active.is_(True),
        )
    )
    enrollments = list(enrollments_result.scalars().all())

    # Get existing results
    results_query = await db.execute(
        select(ExamResult).where(
            ExamResult.exam_id == exam_id,
            ExamResult.school_id == school_id,
            ExamResult.is_active.is_(True),
        )
    )
    results_map: dict[uuid.UUID, ExamResult] = {
        r.student_id: r for r in results_query.scalars().all()
    }

    total_marks = float(exam.total_marks)
    items = []
    marks_list = []

    for enrollment in enrollments:
        student_result = await db.execute(
            select(Student).where(Student.id == enrollment.student_id)
        )
        student = student_result.scalar_one()

        result = results_map.get(student.id)
        marks = float(result.marks_obtained) if result and result.marks_obtained is not None else None
        pct = round(marks / total_marks * 100, 1) if marks is not None else None
        grade = result.grade if result else None
        status_str = "Graded" if marks is not None else "Pending"

        if marks is not None:
            marks_list.append(marks)

        items.append({
            "student_id": student.id,
            "roll_number": enrollment.roll_number or student.admission_number,
            "full_name": student.full_name,
            "marks": marks,
            "total_marks": total_marks,
            "percentage": pct,
            "grade": grade or "Pending",
            "status": status_str,
        })

    # Stats
    graded_count = len(marks_list)
    passing_marks = float(exam.passing_marks) if exam.passing_marks else None
    pass_count = 0
    if passing_marks is not None:
        pass_count = len([m for m in marks_list if m >= passing_marks])

    stats = {
        "class_average": round(sum(marks_list) / len(marks_list), 1) if marks_list else 0,
        "highest_score": max(marks_list) if marks_list else 0,
        "lowest_score": min(marks_list) if marks_list else 0,
        "pass_rate": round(pass_count / graded_count * 100, 1) if graded_count else 0,
        "total_students": len(enrollments),
        "graded_count": graded_count,
    }

    # Paginate
    total = len(items)
    start = pagination.offset
    end = start + pagination.page_size
    paginated_items = items[start:end]

    return {
        "count": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
        "total_pages": (total + pagination.page_size - 1) // pagination.page_size,
        "class_section": f"{cls.name}-{sec.name}",
        "exam_name": exam.name,
        "exam_type": exam.exam_type,
        "subject": exam.subject.name if exam.subject else "",
        "max_marks": total_marks,
        "is_published": exam.status == "Published",
        "can_grade": can_grade,
        "stats": stats,
        "results": paginated_items,
    }


async def submit_grades(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    data: SubmitGradesRequest,
) -> dict:
    """Submit grades bulk for a class and exam."""
    staff = await _get_staff_for_user(db, school_id, user)
    ay = await _get_academic_year(db, school_id, data.academic_year)

    # Get exam
    exam_result = await db.execute(
        select(Exam).where(
            Exam.id == data.exam_id,
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
        )
    )
    exam = exam_result.scalar_one_or_none()
    if not exam:
        raise NotFound("Exam", str(data.exam_id))

    # Reject if exam is already published
    if exam.status == "Published":
        raise ValidationError("Cannot modify grades for a published exam")

    # Verify teacher is the subject teacher (not just class teacher)
    await _verify_teacher_assignment(
        db, school_id, staff.id, exam.class_section_id, exam.subject_id, ay.id
    )

    total_marks = float(exam.total_marks)
    passing_marks = float(exam.passing_marks) if exam.passing_marks else None

    # Validate marks
    for entry in data.grades:
        if entry.marks > total_marks:
            raise ValidationError(f"Marks cannot exceed max_marks ({total_marks})")

    # Get grade system
    grade_system = await _get_active_grade_system(db, school_id)
    scales = grade_system.scales if grade_system else []

    marks_values = []
    for entry in data.grades:
        pct = entry.marks / total_marks * 100
        grade = _compute_grade(pct, scales)
        is_pass = entry.marks >= passing_marks if passing_marks is not None else None

        # Upsert
        existing = await db.execute(
            select(ExamResult).where(
                ExamResult.exam_id == data.exam_id,
                ExamResult.student_id == entry.student_id,
                ExamResult.school_id == school_id,
            )
        )
        exam_res = existing.scalar_one_or_none()
        if exam_res:
            exam_res.marks_obtained = Decimal(str(entry.marks))
            exam_res.grade = grade
            exam_res.is_pass = is_pass
            exam_res.attendance = "Present"
            exam_res.updated_by = user.id
        else:
            exam_res = ExamResult(
                school_id=school_id,
                exam_id=data.exam_id,
                student_id=entry.student_id,
                marks_obtained=Decimal(str(entry.marks)),
                grade=grade,
                is_pass=is_pass,
                attendance="Present",
                created_by=user.id,
            )
            db.add(exam_res)

        marks_values.append(entry.marks)

    await db.flush()

    # Recompute ranks
    all_results_query = await db.execute(
        select(ExamResult).where(
            ExamResult.exam_id == data.exam_id,
            ExamResult.school_id == school_id,
            ExamResult.is_active.is_(True),
        )
    )
    all_results = list(all_results_query.scalars().all())
    _compute_ranks(all_results)

    await db.commit()

    cs = exam.class_section
    cls_result = await db.execute(select(Class).where(Class.id == cs.class_id))
    cls = cls_result.scalar_one()
    sec_result = await db.execute(select(Section).where(Section.id == cs.section_id))
    sec = sec_result.scalar_one()

    return {
        "message": "Grades saved successfully",
        "class_section": f"{cls.name}-{sec.name}",
        "exam_name": exam.name,
        "subject": exam.subject.name if exam.subject else "",
        "total_graded": len(data.grades),
        "summary": {
            "highest": max(marks_values) if marks_values else 0,
            "lowest": min(marks_values) if marks_values else 0,
            "average": round(sum(marks_values) / len(marks_values), 1) if marks_values else 0,
            "max_marks": total_marks,
        },
        "saved_at": datetime.now(timezone.utc),
    }


async def update_grades(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    data: UpdateGradesRequest,
) -> dict:
    """Update existing grades for a class and exam."""
    staff = await _get_staff_for_user(db, school_id, user)

    # Get exam
    exam_result = await db.execute(
        select(Exam).where(
            Exam.id == data.exam_id,
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
        )
    )
    exam = exam_result.scalar_one_or_none()
    if not exam:
        raise NotFound("Exam", str(data.exam_id))

    # Reject if exam is already published
    if exam.status == "Published":
        raise ValidationError("Cannot modify grades for a published exam")

    ay = exam.academic_year

    # Verify teacher is the subject teacher
    await _verify_teacher_assignment(
        db, school_id, staff.id, exam.class_section_id, exam.subject_id, ay.id
    )

    total_marks = float(exam.total_marks)
    passing_marks = float(exam.passing_marks) if exam.passing_marks else None

    grade_system = await _get_active_grade_system(db, school_id)
    scales = grade_system.scales if grade_system else []

    updated_count = 0
    for entry in data.grades:
        if entry.marks > total_marks:
            raise ValidationError(f"Marks cannot exceed max_marks ({total_marks})")

        existing = await db.execute(
            select(ExamResult).where(
                ExamResult.exam_id == data.exam_id,
                ExamResult.student_id == entry.student_id,
                ExamResult.school_id == school_id,
                ExamResult.is_active.is_(True),
            )
        )
        exam_res = existing.scalar_one_or_none()
        if not exam_res:
            continue

        pct = entry.marks / total_marks * 100
        exam_res.marks_obtained = Decimal(str(entry.marks))
        exam_res.grade = _compute_grade(pct, scales)
        exam_res.is_pass = entry.marks >= passing_marks if passing_marks is not None else None
        exam_res.updated_by = user.id
        updated_count += 1

    await db.flush()

    # Recompute ranks
    all_results_query = await db.execute(
        select(ExamResult).where(
            ExamResult.exam_id == data.exam_id,
            ExamResult.school_id == school_id,
            ExamResult.is_active.is_(True),
        )
    )
    all_results = list(all_results_query.scalars().all())
    _compute_ranks(all_results)

    await db.commit()

    cs = exam.class_section
    cls_result = await db.execute(select(Class).where(Class.id == cs.class_id))
    cls = cls_result.scalar_one()
    sec_result = await db.execute(select(Section).where(Section.id == cs.section_id))
    sec = sec_result.scalar_one()

    return {
        "message": "Grades updated successfully",
        "class_section": f"{cls.name}-{sec.name}",
        "exam_name": exam.name,
        "updated_count": updated_count,
        "updated_at": datetime.now(timezone.utc),
    }


async def get_exams_for_grading(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    pagination: PaginationParams,
    class_id: uuid.UUID | None = None,
    academic_year: str | None = None,
    status: str | None = None,
    search: str | None = None,
    role: str | None = None,
    class_section_filter: str | None = None,
    subject_filter: str | None = None,
    exam_type_filter: str | None = None,
) -> dict:
    """List exams available for grading by this teacher.

    Returns exams where the teacher is:
    - Subject teacher (can_grade=True)  — can edit/submit grades
    - Class teacher  (can_grade=False) — read-only view of all subjects
    - Mentor         (can_grade=False) — read-only view of mentored students' sections

    Supports server-side filtering by status, search, role, class_section, subject, exam_type.
    Status values: 'upcoming', 'unpublished', 'completed'
    """
    from datetime import date as date_mod

    staff = await _get_staff_for_user(db, school_id, user)
    ay = await _get_academic_year(db, school_id, academic_year)

    # Get teacher's class assignments
    assignments_result = await db.execute(
        select(ClassAssignment).where(
            ClassAssignment.school_id == school_id,
            ClassAssignment.staff_id == staff.id,
            ClassAssignment.academic_year_id == ay.id,
            ClassAssignment.is_active.is_(True),
        )
    )
    assignments = list(assignments_result.scalars().all())

    # Build subject teacher pairs: (class_section_id, subject_id)
    subject_teacher_pairs = set()
    # Build class teacher section ids
    class_teacher_section_ids = set()

    for a in assignments:
        if a.subject_id:
            subject_teacher_pairs.add((a.class_section_id, a.subject_id))
        if a.is_class_teacher:
            class_teacher_section_ids.add(a.class_section_id)

    # Sections where the teacher is a mentor (via mentored students' enrollments)
    mentor_section_ids = await _get_mentored_section_ids(db, school_id, staff.id, ay.id)

    # Filter by class_id if provided
    if class_id:
        subject_teacher_pairs = {(cs_id, subj_id) for cs_id, subj_id in subject_teacher_pairs if cs_id == class_id}
        class_teacher_section_ids = {cs_id for cs_id in class_teacher_section_ids if cs_id == class_id}
        mentor_section_ids = {cs_id for cs_id in mentor_section_ids if cs_id == class_id}

    # Collect all class_section_ids we need exams for
    all_section_ids = (
        {cs_id for cs_id, _ in subject_teacher_pairs}
        | class_teacher_section_ids
        | mentor_section_ids
    )

    if not all_section_ids:
        return {"count": 0, "page": pagination.page, "page_size": pagination.page_size, "total_pages": 0, "results": []}

    # Batch fetch all exams for relevant sections in one query
    exams_result = await db.execute(
        select(Exam).where(
            Exam.school_id == school_id,
            Exam.academic_year_id == ay.id,
            Exam.class_section_id.in_(all_section_ids),
            Exam.is_active.is_(True),
            Exam.status != "Cancelled",
        ).order_by(Exam.date.desc())
    )
    all_exams = list(exams_result.scalars().all())

    # Batch fetch class/section names for all relevant sections
    cs_name_map: dict[uuid.UUID, str] = {}
    if all_section_ids:
        cs_rows = await db.execute(
            select(ClassSection.id, Class.name, Section.name).join(
                Class, Class.id == ClassSection.class_id
            ).join(
                Section, Section.id == ClassSection.section_id
            ).where(ClassSection.id.in_(all_section_ids))
        )
        for cs_id_val, cls_name, sec_name in cs_rows.all():
            cs_name_map[cs_id_val] = f"{cls_name}-{sec_name}"

    # Batch fetch student counts per section
    enrollment_counts: dict[uuid.UUID, int] = {}
    if all_section_ids:
        count_rows = await db.execute(
            select(
                StudentEnrollment.class_section_id,
                func.count(StudentEnrollment.id),
            ).where(
                StudentEnrollment.school_id == school_id,
                StudentEnrollment.class_section_id.in_(all_section_ids),
                StudentEnrollment.academic_year_id == ay.id,
                StudentEnrollment.is_active.is_(True),
            ).group_by(StudentEnrollment.class_section_id)
        )
        for cs_id_val, cnt in count_rows.all():
            enrollment_counts[cs_id_val] = cnt

    today = date_mod.today()

    # First pass: build all accessible items (with role/class/subject/search/type filters)
    # to compute tab counts, then apply status filter for final results.
    all_items = []

    for exam in all_exams:
        is_subject_teacher = (exam.class_section_id, exam.subject_id) in subject_teacher_pairs
        is_class_teacher_sec = exam.class_section_id in class_teacher_section_ids
        is_mentor_sec = exam.class_section_id in mentor_section_ids

        if not (is_subject_teacher or is_class_teacher_sec or is_mentor_sec):
            continue

        if is_subject_teacher:
            relationship = "subject_teacher"
        elif is_class_teacher_sec:
            relationship = "class_teacher"
        else:
            relationship = "mentor"

        is_published = exam.status == "Published"
        can_grade = is_subject_teacher and not is_published

        # Role filter
        if role == "teaching" and not is_subject_teacher:
            continue
        if role == "class_teacher" and not is_class_teacher_sec:
            continue
        if role == "mentoring" and not is_mentor_sec:
            continue

        cs_name = cs_name_map.get(exam.class_section_id, "")
        subject_name = exam.subject.name if exam.subject else ""

        # Class section filter
        if class_section_filter and cs_name != class_section_filter:
            continue

        # Subject filter
        if subject_filter and subject_name != subject_filter:
            continue

        # Exam type filter
        if exam_type_filter and exam.exam_type != exam_type_filter:
            continue

        # Search filter
        if search:
            q = search.lower()
            if q not in (exam.name or "").lower() and q not in subject_name.lower():
                continue

        is_upcoming = exam.date is not None and exam.date >= today
        graded_count = len([r for r in exam.results if r.is_active and r.marks_obtained is not None])
        total_students = enrollment_counts.get(exam.class_section_id, 0)

        item = {
            "id": exam.id,
            "name": exam.name,
            "exam_type": exam.exam_type,
            "class_section": cs_name,
            "class_section_id": exam.class_section_id,
            "subject": subject_name,
            "date": exam.date,
            "start_time": str(exam.start_time) if exam.start_time else None,
            "end_time": str(exam.end_time) if exam.end_time else None,
            "max_marks": float(exam.total_marks),
            "total_marks": float(exam.total_marks),
            "is_graded": graded_count >= total_students and total_students > 0,
            "graded_count": graded_count,
            "total_students": total_students,
            "can_grade": can_grade,
            "is_published": is_published,
            "relationship": relationship,
            "_is_upcoming": is_upcoming,
        }
        all_items.append(item)

    # Compute tab counts from all filtered items (before status filter)
    tab_counts = {"upcoming": 0, "unpublished": 0, "completed": 0}
    for item in all_items:
        if item["_is_upcoming"]:
            tab_counts["upcoming"] += 1
        elif not item["is_published"] and item["can_grade"]:
            tab_counts["unpublished"] += 1
        else:
            tab_counts["completed"] += 1

    # Apply status filter
    items = []
    for item in all_items:
        if status == "upcoming" and not item["_is_upcoming"]:
            continue
        if status == "unpublished" and (item["_is_upcoming"] or item["is_published"] or not item["can_grade"]):
            continue
        if status == "completed" and (item["_is_upcoming"] or (not item["is_published"] and item["can_grade"])):
            continue
        del item["_is_upcoming"]
        items.append(item)

    # Paginate
    total = len(items)
    start = pagination.offset
    end = start + pagination.page_size
    paginated_items = items[start:end]

    return {
        "count": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
        "total_pages": (total + pagination.page_size - 1) // pagination.page_size if total > 0 else 0,
        "tab_counts": tab_counts,
        "results": paginated_items,
    }


async def get_exam_detail(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    exam_id: uuid.UUID,
) -> dict:
    """Get single exam metadata for grading page."""
    staff = await _get_staff_for_user(db, school_id, user)

    exam_result = await db.execute(
        select(Exam).where(
            Exam.id == exam_id,
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
        )
    )
    exam = exam_result.scalar_one_or_none()
    if not exam:
        raise NotFound("Exam", str(exam_id))

    ay = exam.academic_year
    await _assert_can_view_exam(db, school_id, staff.id, exam, ay.id)

    cs = exam.class_section
    cls_result = await db.execute(select(Class).where(Class.id == cs.class_id))
    cls = cls_result.scalar_one()
    sec_result = await db.execute(select(Section).where(Section.id == cs.section_id))
    sec = sec_result.scalar_one()

    is_subject_teacher = await _is_subject_teacher_for_exam(
        db, school_id, staff.id, exam.class_section_id, exam.subject_id, ay.id
    )
    is_class_teacher = await _is_class_teacher_for_section(
        db, school_id, staff.id, exam.class_section_id, ay.id
    )

    if is_subject_teacher:
        relationship = "subject_teacher"
    elif is_class_teacher:
        relationship = "class_teacher"
    else:
        relationship = "mentor"

    is_published = exam.status == "Published"
    can_grade = is_subject_teacher and not is_published

    graded_count = len([r for r in exam.results if r.is_active and r.marks_obtained is not None])

    total_result = await db.execute(
        select(func.count(StudentEnrollment.id)).where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.class_section_id == exam.class_section_id,
            StudentEnrollment.academic_year_id == ay.id,
            StudentEnrollment.is_active.is_(True),
        )
    )
    total_students = total_result.scalar() or 0

    return {
        "id": exam.id,
        "name": exam.name,
        "exam_type": exam.exam_type,
        "class_section": f"{cls.name}-{sec.name}",
        "class_section_id": exam.class_section_id,
        "subject": exam.subject.name if exam.subject else "",
        "date": exam.date,
        "start_time": str(exam.start_time) if exam.start_time else None,
        "end_time": str(exam.end_time) if exam.end_time else None,
        "max_marks": float(exam.total_marks),
        "total_students": total_students,
        "graded_count": graded_count,
        "can_grade": can_grade,
        "is_published": is_published,
        "relationship": relationship,
    }


async def get_report(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    class_id: uuid.UUID | None = None,
    exam_id: uuid.UUID | None = None,
) -> dict:
    """Get exam report with marks and grade distribution."""
    staff = await _get_staff_for_user(db, school_id, user)

    if not exam_id:
        raise ValidationError("exam_id is required")

    exam_result = await db.execute(
        select(Exam).where(
            Exam.id == exam_id,
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
        )
    )
    exam = exam_result.scalar_one_or_none()
    if not exam:
        raise NotFound("Exam", str(exam_id))

    ay = exam.academic_year
    await _assert_can_view_exam(
        db, school_id, staff.id, exam, ay.id
    )

    cs = exam.class_section
    cls_result = await db.execute(select(Class).where(Class.id == cs.class_id))
    cls = cls_result.scalar_one()
    sec_result = await db.execute(select(Section).where(Section.id == cs.section_id))
    sec = sec_result.scalar_one()

    total_marks = float(exam.total_marks)
    passing_marks = float(exam.passing_marks) if exam.passing_marks else None

    results_list = [r for r in exam.results if r.is_active]
    scored = [r for r in results_list if r.marks_obtained is not None and r.attendance == "Present"]
    marks_list = [float(r.marks_obtained) for r in scored]

    # Total students
    total_students_result = await db.execute(
        select(func.count(StudentEnrollment.id)).where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.class_section_id == exam.class_section_id,
            StudentEnrollment.academic_year_id == ay.id,
            StudentEnrollment.is_active.is_(True),
        )
    )
    total_students = total_students_result.scalar() or 0

    pass_count = 0
    if passing_marks is not None:
        pass_count = len([m for m in marks_list if m >= passing_marks])

    stats = {
        "class_average": round(sum(marks_list) / len(marks_list), 1) if marks_list else 0,
        "highest_score": max(marks_list) if marks_list else 0,
        "lowest_score": min(marks_list) if marks_list else 0,
        "graded_count": len(scored),
        "total_students": total_students,
        "pass_rate": round(pass_count / len(scored) * 100, 1) if scored else 0,
    }

    # Marks distribution
    ranges = [(0, 20), (21, 40), (41, 60), (61, 80), (81, 100)]
    marks_distribution = []
    for low, high in ranges:
        # Normalize to actual marks using percentage
        count = len([m for m in marks_list if low <= (m / total_marks * 100) <= high])
        marks_distribution.append({"range": f"{low}-{high}", "count": count})

    # Grade distribution
    grade_dist: dict[str, int] = {}
    for r in scored:
        g = r.grade or "N/A"
        grade_dist[g] = grade_dist.get(g, 0) + 1
    grade_distribution = [
        {"grade": g, "count": c, "percentage": round(c / len(scored) * 100, 1) if scored else 0}
        for g, c in grade_dist.items()
    ]

    return {
        "exam_name": exam.name,
        "class_section": f"{cls.name}-{sec.name}",
        "subject": exam.subject.name if exam.subject else "",
        "max_marks": total_marks,
        "stats": stats,
        "marks_distribution": marks_distribution,
        "grade_distribution": grade_distribution,
    }


async def get_leaderboard(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    class_id: uuid.UUID | None = None,
    exam_id: uuid.UUID | None = None,
    limit: int = 20,
) -> dict:
    """Get ranked leaderboard for an exam."""
    staff = await _get_staff_for_user(db, school_id, user)

    if not exam_id:
        raise ValidationError("exam_id is required")

    exam_result = await db.execute(
        select(Exam).where(
            Exam.id == exam_id,
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
        )
    )
    exam = exam_result.scalar_one_or_none()
    if not exam:
        raise NotFound("Exam", str(exam_id))

    ay = exam.academic_year
    await _assert_can_view_exam(
        db, school_id, staff.id, exam, ay.id
    )

    cs = exam.class_section
    cls_result = await db.execute(select(Class).where(Class.id == cs.class_id))
    cls = cls_result.scalar_one()
    sec_result = await db.execute(select(Section).where(Section.id == cs.section_id))
    sec = sec_result.scalar_one()

    total_marks = float(exam.total_marks)
    results_list = [r for r in exam.results if r.is_active and r.marks_obtained is not None and r.attendance == "Present"]
    results_list.sort(key=lambda r: float(r.marks_obtained), reverse=True)  # type: ignore[arg-type]

    leaderboard = []
    for idx, r in enumerate(results_list[:limit], start=1):
        student = r.student
        enrollment_result = await db.execute(
            select(StudentEnrollment).where(
                StudentEnrollment.student_id == student.id,
                StudentEnrollment.academic_year_id == ay.id,
                StudentEnrollment.is_active.is_(True),
            )
        )
        enrollment = enrollment_result.scalar_one_or_none()
        marks = float(r.marks_obtained)
        leaderboard.append({
            "rank": idx,
            "roll_number": enrollment.roll_number if enrollment else student.admission_number,
            "student_name": student.full_name,
            "marks": marks,
            "percentage": round(marks / total_marks * 100, 1),
            "grade": r.grade or "",
        })

    return {
        "exam_name": exam.name,
        "class_section": f"{cls.name}-{sec.name}",
        "subject": exam.subject.name if exam.subject else "",
        "max_marks": total_marks,
        "leaderboard": leaderboard,
    }


async def import_grades(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    class_id: uuid.UUID,
    exam_id: uuid.UUID,
    file_content: str,
) -> dict:
    """Import grades from CSV."""
    staff = await _get_staff_for_user(db, school_id, user)

    exam_result = await db.execute(
        select(Exam).where(
            Exam.id == exam_id,
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
        )
    )
    exam = exam_result.scalar_one_or_none()
    if not exam:
        raise NotFound("Exam", str(exam_id))

    ay = exam.academic_year
    await _verify_teacher_assignment(
        db, school_id, staff.id, exam.class_section_id, exam.subject_id, ay.id
    )

    total_marks = float(exam.total_marks)
    passing_marks = float(exam.passing_marks) if exam.passing_marks else None

    grade_system = await _get_active_grade_system(db, school_id)
    scales = grade_system.scales if grade_system else []

    reader = csv.DictReader(io.StringIO(file_content))
    imported = 0
    skipped = 0
    errors: list[dict] = []

    for row_num, row in enumerate(reader, start=2):
        roll_number = row.get("roll_number", "").strip()
        marks_str = row.get("marks", "").strip()

        if not roll_number or not marks_str:
            errors.append({"row": row_num, "roll_number": roll_number, "error": "Missing data"})
            skipped += 1
            continue

        try:
            marks = float(marks_str)
        except ValueError:
            errors.append({"row": row_num, "roll_number": roll_number, "error": "Invalid marks"})
            skipped += 1
            continue

        if marks > total_marks:
            errors.append({"row": row_num, "roll_number": roll_number, "error": f"Marks exceed max ({total_marks})"})
            skipped += 1
            continue

        # Find student
        enrollment_result = await db.execute(
            select(StudentEnrollment).where(
                StudentEnrollment.school_id == school_id,
                StudentEnrollment.class_section_id == exam.class_section_id,
                StudentEnrollment.academic_year_id == ay.id,
                StudentEnrollment.roll_number == roll_number,
                StudentEnrollment.is_active.is_(True),
            )
        )
        enrollment = enrollment_result.scalar_one_or_none()
        if not enrollment:
            errors.append({"row": row_num, "roll_number": roll_number, "error": "Student not found in class"})
            skipped += 1
            continue

        pct = marks / total_marks * 100
        grade = _compute_grade(pct, scales)
        is_pass = marks >= passing_marks if passing_marks is not None else None

        existing = await db.execute(
            select(ExamResult).where(
                ExamResult.exam_id == exam_id,
                ExamResult.student_id == enrollment.student_id,
                ExamResult.school_id == school_id,
            )
        )
        exam_res = existing.scalar_one_or_none()
        if exam_res:
            exam_res.marks_obtained = Decimal(str(marks))
            exam_res.grade = grade
            exam_res.is_pass = is_pass
            exam_res.attendance = "Present"
            exam_res.updated_by = user.id
        else:
            exam_res = ExamResult(
                school_id=school_id,
                exam_id=exam_id,
                student_id=enrollment.student_id,
                marks_obtained=Decimal(str(marks)),
                grade=grade,
                is_pass=is_pass,
                attendance="Present",
                created_by=user.id,
            )
            db.add(exam_res)
        imported += 1

    await db.flush()

    # Recompute ranks
    all_results_query = await db.execute(
        select(ExamResult).where(
            ExamResult.exam_id == exam_id,
            ExamResult.school_id == school_id,
            ExamResult.is_active.is_(True),
        )
    )
    all_results = list(all_results_query.scalars().all())
    _compute_ranks(all_results)

    await db.commit()

    return {
        "imported": imported,
        "skipped": skipped,
        "errors": errors,
        "message": f"{imported} grades imported. Grades auto-computed.",
    }


async def export_grades(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    class_id: uuid.UUID | None = None,
    exam_id: uuid.UUID | None = None,
) -> str:
    """Export grades as CSV content."""
    staff = await _get_staff_for_user(db, school_id, user)

    if not exam_id:
        raise ValidationError("exam_id is required")

    exam_result = await db.execute(
        select(Exam).where(
            Exam.id == exam_id,
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
        )
    )
    exam = exam_result.scalar_one_or_none()
    if not exam:
        raise NotFound("Exam", str(exam_id))

    ay = exam.academic_year
    await _verify_teacher_assignment(
        db, school_id, staff.id, exam.class_section_id, exam.subject_id, ay.id
    )

    total_marks = float(exam.total_marks)
    results_list = [r for r in exam.results if r.is_active]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Roll Number", "Student Name", "Marks Obtained", "Total Marks", "Percentage", "Grade"])

    for r in sorted(results_list, key=lambda x: x.rank or 9999):
        student = r.student
        enrollment_result = await db.execute(
            select(StudentEnrollment).where(
                StudentEnrollment.student_id == student.id,
                StudentEnrollment.academic_year_id == ay.id,
                StudentEnrollment.is_active.is_(True),
            )
        )
        enrollment = enrollment_result.scalar_one_or_none()
        roll = enrollment.roll_number if enrollment else student.admission_number
        marks = float(r.marks_obtained) if r.marks_obtained is not None else ""
        pct = round(float(r.marks_obtained) / total_marks * 100, 1) if r.marks_obtained is not None else ""
        writer.writerow([roll, student.full_name, marks, total_marks, pct, r.grade or ""])

    return output.getvalue()


async def publish_exam(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    exam_id: uuid.UUID,
) -> dict:
    """Publish exam results after verifying all students are graded.

    Only the subject teacher can publish. All students must have marks.
    """
    staff = await _get_staff_for_user(db, school_id, user)

    # Get exam
    exam_result = await db.execute(
        select(Exam).where(
            Exam.id == exam_id,
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
        )
    )
    exam = exam_result.scalar_one_or_none()
    if not exam:
        raise NotFound("Exam", str(exam_id))

    if exam.status == "Published":
        raise ValidationError("Exam results are already published")

    ay = exam.academic_year

    # Verify teacher is the subject teacher (not just class teacher)
    await _verify_teacher_assignment(
        db, school_id, staff.id, exam.class_section_id, exam.subject_id, ay.id
    )

    # Count total enrolled students
    total_result = await db.execute(
        select(func.count(StudentEnrollment.id)).where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.class_section_id == exam.class_section_id,
            StudentEnrollment.academic_year_id == ay.id,
            StudentEnrollment.is_active.is_(True),
        )
    )
    total_students = total_result.scalar() or 0

    if total_students == 0:
        raise ValidationError("No students enrolled in this class section")

    # Count graded students
    graded_count = len([r for r in exam.results if r.is_active and r.marks_obtained is not None])

    if graded_count < total_students:
        raise ValidationError(
            f"Cannot publish: {total_students - graded_count} student(s) still pending grades. "
            f"All {total_students} students must have marks before publishing."
        )

    # Publish
    now = datetime.now(timezone.utc)
    exam.status = "Published"
    exam.published_at = now

    await db.commit()

    return {
        "message": "Exam results published successfully",
        "exam_id": exam.id,
        "exam_name": exam.name,
        "published_at": now,
    }
