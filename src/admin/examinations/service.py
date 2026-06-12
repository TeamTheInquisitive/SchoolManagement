from __future__ import annotations

import csv
import io
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AccessDenied, NotFound, ValidationError
from src.core.pagination import PaginationParams, paginate
from src.models.academic import Class, ClassSection, Section, Subject
from src.models.core import AcademicYear, School, User
from src.models.examination import Exam, ExamResult, GradeScale, GradeSystem
from src.models.staff import Staff
from src.models.student import Student, StudentEnrollment

from src.admin.examinations.schemas import (
    CreateExamRequest,
    EnterResultsRequest,
    GenerateReportCardsRequest,
    PublishResultsRequest,
    UpdateExamRequest,
    UpdateGradeSystemRequest,
    UpdateResultRequest,
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


async def _get_class_section(
    db: AsyncSession, school_id: uuid.UUID, class_name: str, section: str
) -> ClassSection:
    """Get ClassSection by class name and section name."""
    result = await db.execute(
        select(ClassSection)
        .join(Class, ClassSection.class_id == Class.id)
        .join(Section, ClassSection.section_id == Section.id)
        .where(
            ClassSection.school_id == school_id,
            ClassSection.is_active.is_(True),
            Class.name == class_name,
            Section.name == section,
        )
    )
    cs = result.scalar_one_or_none()
    if not cs:
        raise NotFound("ClassSection", f"{class_name}-{section}")
    return cs


async def _get_subject(
    db: AsyncSession, school_id: uuid.UUID, subject_name: str
) -> Subject:
    """Get Subject by name."""
    result = await db.execute(
        select(Subject).where(
            Subject.school_id == school_id,
            Subject.name == subject_name,
            Subject.is_active.is_(True),
        )
    )
    subj = result.scalar_one_or_none()
    if not subj:
        raise NotFound("Subject", subject_name)
    return subj


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
    """Compute ranks for results in-place (only for present students with marks)."""
    scorable = [r for r in results if r.marks_obtained is not None and r.attendance == "Present"]
    scorable.sort(key=lambda r: float(r.marks_obtained), reverse=True)  # type: ignore[arg-type]
    for idx, result in enumerate(scorable, start=1):
        result.rank = idx


async def _count_students_in_class(
    db: AsyncSession, school_id: uuid.UUID, class_section_id: uuid.UUID, academic_year_id: uuid.UUID
) -> int:
    """Count enrolled students in a class section."""
    result = await db.execute(
        select(func.count(StudentEnrollment.id)).where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.class_section_id == class_section_id,
            StudentEnrollment.academic_year_id == academic_year_id,
            StudentEnrollment.is_active.is_(True),
        )
    )
    return result.scalar() or 0


async def list_exams(
    db: AsyncSession,
    school_id: uuid.UUID,
    pagination: PaginationParams,
    exam_type: str | None = None,
    class_name: str | None = None,
    section: str | None = None,
    subject: str | None = None,
    status: str | None = None,
    academic_year: str | None = None,
) -> dict:
    """List exams with filters and summary."""
    ay = await _get_academic_year(db, school_id, academic_year)

    query = (
        select(Exam)
        .where(
            Exam.school_id == school_id,
            Exam.academic_year_id == ay.id,
            Exam.is_active.is_(True),
        )
    )

    if exam_type:
        query = query.where(Exam.exam_type == exam_type)
    if status:
        query = query.where(Exam.status == status)
    if class_name or section:
        query = query.join(ClassSection, Exam.class_section_id == ClassSection.id)
        if class_name:
            query = query.join(Class, ClassSection.class_id == Class.id).where(
                Class.name == class_name
            )
        if section:
            query = query.join(Section, ClassSection.section_id == Section.id).where(
                Section.name == section
            )
    if subject:
        query = query.join(Subject, Exam.subject_id == Subject.id).where(
            Subject.name == subject
        )

    # Count total distinct exam names (for group-based pagination)
    name_count_query = select(func.count(func.distinct(Exam.name))).where(
        Exam.school_id == school_id, Exam.academic_year_id == ay.id, Exam.is_active.is_(True),
    )
    total_names = (await db.execute(name_count_query)).scalar() or 0

    # Get paginated distinct exam names
    names_query = (
        select(func.distinct(Exam.name))
        .where(Exam.school_id == school_id, Exam.academic_year_id == ay.id, Exam.is_active.is_(True))
        .order_by(Exam.name)
        .offset(pagination.offset)
        .limit(pagination.page_size)
    )
    names_result = await db.execute(names_query)
    exam_names = [row[0] for row in names_result.all()]

    # Fetch ALL rows for those exam names (no row-level pagination)
    if exam_names:
        query = query.where(Exam.name.in_(exam_names))
    else:
        query = query.where(Exam.name.is_(None))  # return empty

    query = query.order_by(Exam.name, Exam.date.desc())
    result = await db.execute(query)
    exams = list(result.scalars().all())
    total = total_names  # pagination is by exam group count

    # Build response items
    items = []
    for exam in exams:
        cs = exam.class_section
        class_obj = cs.class_ if hasattr(cs, "class_") else None
        section_obj = cs.section if hasattr(cs, "section") else None

        # Get class/section names via relationship
        cls_result = await db.execute(select(Class).where(Class.id == cs.class_id))
        cls = cls_result.scalar_one_or_none()
        sec_result = await db.execute(select(Section).where(Section.id == cs.section_id))
        sec = sec_result.scalar_one_or_none()

        # Compute stats from results
        results_list = [r for r in exam.results if r.is_active]
        present_results = [r for r in results_list if r.attendance == "Present"]
        absent_count = len([r for r in results_list if r.attendance == "Absent"])
        scored = [r for r in present_results if r.marks_obtained is not None]
        pass_count = len([r for r in scored if r.is_pass])
        fail_count = len([r for r in scored if r.is_pass is False])

        total_students = await _count_students_in_class(db, school_id, exam.class_section_id, ay.id)
        marks_list = [float(r.marks_obtained) for r in scored]

        items.append({
            "id": exam.id,
            "name": exam.name,
            "type": exam.exam_type,
            "class_name": cls.name if cls else "",
            "section": sec.name if sec else "",
            "subject": exam.subject.name if exam.subject else "",
            "date": exam.date,
            "start_time": str(exam.start_time) if exam.start_time else None,
            "end_time": str(exam.end_time) if exam.end_time else None,
            "total_marks": float(exam.total_marks),
            "passing_marks": float(exam.passing_marks) if exam.passing_marks else None,
            "total_students": total_students,
            "present": len(present_results),
            "absent": absent_count,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_rate": round(pass_count / len(scored) * 100, 1) if scored else 0,
            "class_average": round(sum(marks_list) / len(marks_list), 1) if marks_list else 0,
            "highest_marks": max(marks_list) if marks_list else 0,
            "lowest_marks": min(marks_list) if marks_list else 0,
            "status": exam.status,
            "academic_year": ay.name,
            "term": exam.term,
            "examiner_id": exam.examiner_id,
            "examiner_name": exam.examiner.full_name if exam.examiner else None,
            "created_at": exam.created_at,
            "published_at": exam.published_at,
            "metadata": exam.metadata_ or {},
        })

    # Summary counts
    all_exams_result = await db.execute(
        select(Exam.status, func.count(Exam.id)).where(
            Exam.school_id == school_id,
            Exam.academic_year_id == ay.id,
            Exam.is_active.is_(True),
        ).group_by(Exam.status)
    )
    status_counts = dict(all_exams_result.all())
    published_count = status_counts.get("Published", 0)
    draft_count = status_counts.get("Draft", 0)
    upcoming_count = status_counts.get("Scheduled", 0)
    total_exams = sum(status_counts.values())

    paginated = paginate(items, total, pagination)
    paginated["summary"] = {
        "total_exams": total_exams,
        "published": published_count,
        "upcoming": upcoming_count,
        "draft": draft_count,
        "average_pass_rate": 0,
    }
    return paginated


async def create_exam(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    data: CreateExamRequest,
) -> dict:
    """Create a new exam."""
    ay = await _get_academic_year(db, school_id, data.academic_year)
    cs = await _get_class_section(db, school_id, data.class_name, data.section)
    subj = await _get_subject(db, school_id, data.subject)

    exam = Exam(
        school_id=school_id,
        academic_year_id=ay.id,
        name=data.name,
        exam_type=data.exam_type,
        class_section_id=cs.id,
        subject_id=subj.id,
        date=data.date,
        start_time=data.start_time,
        end_time=data.end_time,
        total_marks=Decimal(str(data.total_marks)),
        passing_marks=Decimal(str(data.passing_marks)) if data.passing_marks else None,
        status=data.status,
        term=data.term,
        examiner_id=data.examiner_id,
        metadata_=data.metadata,
        created_by=user.id,
    )
    db.add(exam)
    await db.commit()
    await db.refresh(exam)

    total_students = await _count_students_in_class(db, school_id, cs.id, ay.id)

    # Look up class/section names
    cls_result = await db.execute(select(Class).where(Class.id == cs.class_id))
    cls = cls_result.scalar_one()
    sec_result = await db.execute(select(Section).where(Section.id == cs.section_id))
    sec = sec_result.scalar_one()

    examiner_name = None
    if exam.examiner_id:
        ex_result = await db.execute(select(Staff).where(Staff.id == exam.examiner_id))
        examiner = ex_result.scalar_one_or_none()
        examiner_name = examiner.full_name if examiner else None

    return {
        "id": exam.id,
        "name": exam.name,
        "type": exam.exam_type,
        "class_name": cls.name,
        "section": sec.name,
        "subject": subj.name,
        "date": exam.date,
        "start_time": str(exam.start_time) if exam.start_time else None,
        "end_time": str(exam.end_time) if exam.end_time else None,
        "total_marks": float(exam.total_marks),
        "passing_marks": float(exam.passing_marks) if exam.passing_marks else None,
        "total_students": total_students,
        "status": exam.status,
        "academic_year": ay.name,
        "term": exam.term,
        "examiner_id": exam.examiner_id,
        "examiner_name": examiner_name,
        "created_at": exam.created_at,
        "metadata": exam.metadata_ or {},
    }


async def get_exam_detail(
    db: AsyncSession,
    school_id: uuid.UUID,
    exam_id: uuid.UUID,
) -> dict:
    """Get full exam details with result summary and analytics."""
    result = await db.execute(
        select(Exam).where(
            Exam.id == exam_id,
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
        )
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise NotFound("Exam", str(exam_id))

    ay = exam.academic_year
    cs = exam.class_section

    cls_result = await db.execute(select(Class).where(Class.id == cs.class_id))
    cls = cls_result.scalar_one()
    sec_result = await db.execute(select(Section).where(Section.id == cs.section_id))
    sec = sec_result.scalar_one()

    total_students = await _count_students_in_class(db, school_id, cs.id, ay.id)
    results_list = [r for r in exam.results if r.is_active]
    present_results = [r for r in results_list if r.attendance == "Present"]
    absent_count = len([r for r in results_list if r.attendance == "Absent"])
    scored = [r for r in present_results if r.marks_obtained is not None]
    pass_count = len([r for r in scored if r.is_pass])
    fail_count = len([r for r in scored if r.is_pass is False])
    marks_list = [float(r.marks_obtained) for r in scored]

    # Grade distribution
    grade_dist: dict[str, int] = {}
    for r in scored:
        g = r.grade or "N/A"
        grade_dist[g] = grade_dist.get(g, 0) + 1
    grade_distribution = [
        {"grade": g, "count": c, "percentage": round(c / len(scored) * 100, 1) if scored else 0}
        for g, c in grade_dist.items()
    ]

    # Toppers (top 3)
    toppers_list = sorted(scored, key=lambda r: float(r.marks_obtained), reverse=True)[:3]  # type: ignore[arg-type]
    toppers = []
    for r in toppers_list:
        student = r.student
        enrollment_result = await db.execute(
            select(StudentEnrollment).where(
                StudentEnrollment.student_id == student.id,
                StudentEnrollment.academic_year_id == ay.id,
                StudentEnrollment.is_active.is_(True),
            )
        )
        enrollment = enrollment_result.scalar_one_or_none()
        toppers.append({
            "student_id": student.id,
            "student_name": student.full_name,
            "roll_number": enrollment.roll_number if enrollment else student.admission_number,
            "marks": float(r.marks_obtained),
            "grade": r.grade or "",
            "rank": r.rank or 0,
        })

    return {
        "id": exam.id,
        "name": exam.name,
        "type": exam.exam_type,
        "class_name": cls.name,
        "section": sec.name,
        "subject": exam.subject.name if exam.subject else "",
        "date": exam.date,
        "start_time": str(exam.start_time) if exam.start_time else None,
        "end_time": str(exam.end_time) if exam.end_time else None,
        "total_marks": float(exam.total_marks),
        "passing_marks": float(exam.passing_marks) if exam.passing_marks else None,
        "total_students": total_students,
        "present": len(present_results),
        "absent": absent_count,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "pass_rate": round(pass_count / len(scored) * 100, 1) if scored else 0,
        "class_average": round(sum(marks_list) / len(marks_list), 1) if marks_list else 0,
        "highest_marks": max(marks_list) if marks_list else 0,
        "lowest_marks": min(marks_list) if marks_list else 0,
        "status": exam.status,
        "academic_year": ay.name,
        "term": exam.term,
        "examiner_id": exam.examiner_id,
        "examiner_name": exam.examiner.full_name if exam.examiner else None,
        "created_at": exam.created_at,
        "published_at": exam.published_at,
        "grade_distribution": grade_distribution,
        "toppers": toppers,
        "metadata": exam.metadata_ or {},
    }


async def update_exam(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    exam_id: uuid.UUID,
    data: UpdateExamRequest,
) -> dict:
    """Update an exam."""
    # Validate total_marks if provided
    update_fields = data.model_dump(exclude_unset=True)
    if "total_marks" in update_fields and update_fields["total_marks"] is not None:
        if update_fields["total_marks"] <= 0:
            raise HTTPException(status_code=400, detail="total_marks must be greater than 0")

    result = await db.execute(
        select(Exam).where(
            Exam.id == exam_id,
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
        )
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise NotFound("Exam", str(exam_id))

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "total_marks" and value is not None:
            setattr(exam, field, Decimal(str(value)))
        elif field == "passing_marks" and value is not None:
            setattr(exam, field, Decimal(str(value)))
        elif field == "metadata":
            exam.metadata_ = value
        else:
            setattr(exam, field, value)

    exam.updated_by = user.id
    await db.commit()
    await db.refresh(exam)

    return await get_exam_detail(db, school_id, exam_id)


async def cancel_exam(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    exam_id: uuid.UUID,
) -> dict:
    """Cancel (soft-delete) an exam. Only Draft/Scheduled allowed."""
    result = await db.execute(
        select(Exam).where(
            Exam.id == exam_id,
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
        )
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise NotFound("Exam", str(exam_id))

    if exam.status not in ("Draft", "Scheduled"):
        raise ValidationError(
            "Published exams cannot be cancelled. Create a re-evaluation instead."
        )

    now = datetime.now(timezone.utc)
    exam.status = "Cancelled"
    exam.cancelled_at = now
    exam.updated_by = user.id
    await db.commit()

    return {
        "id": exam.id,
        "name": exam.name,
        "status": "Cancelled",
        "cancelled_on": now.date(),
        "message": "Exam cancelled. Records preserved.",
    }


async def get_exam_results(
    db: AsyncSession,
    school_id: uuid.UUID,
    exam_id: uuid.UUID,
) -> dict:
    """Get all student results for an exam."""
    result = await db.execute(
        select(Exam).where(
            Exam.id == exam_id,
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
        )
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise NotFound("Exam", str(exam_id))

    ay = exam.academic_year
    cs = exam.class_section
    cls_result = await db.execute(select(Class).where(Class.id == cs.class_id))
    cls = cls_result.scalar_one()
    sec_result = await db.execute(select(Section).where(Section.id == cs.section_id))
    sec = sec_result.scalar_one()

    results_list = [r for r in exam.results if r.is_active]
    items = []
    for r in results_list:
        student = r.student
        enrollment_result = await db.execute(
            select(StudentEnrollment).where(
                StudentEnrollment.student_id == student.id,
                StudentEnrollment.academic_year_id == ay.id,
                StudentEnrollment.is_active.is_(True),
            )
        )
        enrollment = enrollment_result.scalar_one_or_none()
        pct = (
            round(float(r.marks_obtained) / float(exam.total_marks) * 100, 1)
            if r.marks_obtained is not None
            else None
        )
        status_str = "Absent" if r.attendance == "Absent" else ("Pass" if r.is_pass else "Fail")
        items.append({
            "id": r.id,
            "student_id": student.id,
            "student_name": student.full_name,
            "roll_number": enrollment.roll_number if enrollment else student.admission_number,
            "marks_obtained": float(r.marks_obtained) if r.marks_obtained is not None else None,
            "percentage": pct,
            "grade": r.grade,
            "rank": r.rank,
            "status": status_str,
            "attendance": r.attendance,
            "remarks": r.remarks,
        })

    # Sort by rank (present first, absent at end)
    items.sort(key=lambda x: (x["rank"] is None, x["rank"] or 9999))

    present = [r for r in results_list if r.attendance == "Present"]
    absent_count = len(results_list) - len(present)
    scored = [r for r in present if r.marks_obtained is not None]
    marks_list = [float(r.marks_obtained) for r in scored]
    pass_count = len([r for r in scored if r.is_pass])
    fail_count = len([r for r in scored if r.is_pass is False])

    return {
        "exam_id": exam.id,
        "exam_name": exam.name,
        "subject": exam.subject.name if exam.subject else "",
        "class_section": f"{cls.name}-{sec.name}",
        "total_marks": float(exam.total_marks),
        "passing_marks": float(exam.passing_marks) if exam.passing_marks else None,
        "results": items,
        "summary": {
            "total_students": len(results_list),
            "present": len(present),
            "absent": absent_count,
            "pass": pass_count,
            "fail": fail_count,
            "class_average": round(sum(marks_list) / len(marks_list), 1) if marks_list else 0,
            "highest": max(marks_list) if marks_list else 0,
            "lowest": min(marks_list) if marks_list else 0,
        },
    }


async def enter_results(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    exam_id: uuid.UUID,
    data: EnterResultsRequest,
) -> dict:
    """Enter results for students with auto grade/rank computation."""
    # Validate results not empty
    if not data.results:
        raise HTTPException(status_code=400, detail="results must not be empty")

    result = await db.execute(
        select(Exam).where(
            Exam.id == exam_id,
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
        )
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise NotFound("Exam", str(exam_id))

    # Get grade system
    grade_system = await _get_active_grade_system(db, school_id)
    scales = grade_system.scales if grade_system else []

    total_marks = float(exam.total_marks)
    passing_marks = float(exam.passing_marks) if exam.passing_marks else None

    # Validate marks
    for entry in data.results:
        if entry.marks_obtained is not None:
            if entry.marks_obtained < 0:
                raise ValidationError("Marks obtained must be >= 0")
            if entry.marks_obtained > total_marks:
                raise ValidationError(
                    f"Marks cannot exceed total_marks ({total_marks})"
                )

    created_results: list[ExamResult] = []
    for entry in data.results:
        # Check if result already exists
        existing = await db.execute(
            select(ExamResult).where(
                ExamResult.exam_id == exam_id,
                ExamResult.student_id == entry.student_id,
                ExamResult.school_id == school_id,
            )
        )
        exam_result = existing.scalar_one_or_none()

        # Compute grade and pass/fail
        grade = None
        is_pass = None
        if entry.marks_obtained is not None and entry.attendance == "Present":
            pct = entry.marks_obtained / total_marks * 100
            grade = _compute_grade(pct, scales)
            if passing_marks is not None:
                is_pass = entry.marks_obtained >= passing_marks

        if exam_result:
            exam_result.marks_obtained = Decimal(str(entry.marks_obtained)) if entry.marks_obtained is not None else None
            exam_result.attendance = entry.attendance
            exam_result.remarks = entry.remarks
            exam_result.grade = grade
            exam_result.is_pass = is_pass
            exam_result.updated_by = user.id
        else:
            exam_result = ExamResult(
                school_id=school_id,
                exam_id=exam_id,
                student_id=entry.student_id,
                marks_obtained=Decimal(str(entry.marks_obtained)) if entry.marks_obtained is not None else None,
                attendance=entry.attendance,
                remarks=entry.remarks,
                grade=grade,
                is_pass=is_pass,
                created_by=user.id,
            )
            db.add(exam_result)

        created_results.append(exam_result)

    await db.flush()

    # Recompute ranks for all results of this exam
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

    # Build response
    response_results = []
    for r in created_results:
        await db.refresh(r)
        status_str = "Absent" if r.attendance == "Absent" else ("Pass" if r.is_pass else "Fail")
        response_results.append({
            "student_id": r.student_id,
            "marks_obtained": float(r.marks_obtained) if r.marks_obtained is not None else None,
            "grade": r.grade or "-",
            "rank": r.rank,
            "status": status_str,
        })

    return {
        "exam_id": exam.id,
        "entered": len(created_results),
        "results": response_results,
        "message": f"Results entered for {len(created_results)} students. Ranks auto-computed.",
    }


async def bulk_upload_results(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    exam_id: uuid.UUID,
    file_content: str,
) -> dict:
    """Upload results via CSV content."""
    result = await db.execute(
        select(Exam).where(
            Exam.id == exam_id,
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
        )
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise NotFound("Exam", str(exam_id))

    ay = exam.academic_year
    grade_system = await _get_active_grade_system(db, school_id)
    scales = grade_system.scales if grade_system else []
    total_marks = float(exam.total_marks)
    passing_marks = float(exam.passing_marks) if exam.passing_marks else None

    reader = csv.DictReader(io.StringIO(file_content))
    imported = 0
    skipped = 0
    errors: list[dict] = []

    for row_num, row in enumerate(reader, start=2):
        roll_number = row.get("roll_number", "").strip()
        marks_str = row.get("marks_obtained", "").strip()
        attendance = row.get("attendance", "Present").strip()
        remarks = row.get("remarks", "").strip()

        # Find student by roll number in class
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

        marks_obtained = None
        if marks_str:
            try:
                marks_obtained = float(marks_str)
            except ValueError:
                errors.append({"row": row_num, "roll_number": roll_number, "error": "Invalid marks value"})
                skipped += 1
                continue

        if marks_obtained is not None and marks_obtained > total_marks:
            errors.append({"row": row_num, "roll_number": roll_number, "error": f"Marks exceed total ({total_marks})"})
            skipped += 1
            continue

        # Compute grade
        grade = None
        is_pass = None
        if marks_obtained is not None and attendance == "Present":
            pct = marks_obtained / total_marks * 100
            grade = _compute_grade(pct, scales)
            if passing_marks is not None:
                is_pass = marks_obtained >= passing_marks

        # Upsert
        existing = await db.execute(
            select(ExamResult).where(
                ExamResult.exam_id == exam_id,
                ExamResult.student_id == enrollment.student_id,
                ExamResult.school_id == school_id,
            )
        )
        exam_result = existing.scalar_one_or_none()
        if exam_result:
            exam_result.marks_obtained = Decimal(str(marks_obtained)) if marks_obtained is not None else None
            exam_result.attendance = attendance
            exam_result.remarks = remarks or None
            exam_result.grade = grade
            exam_result.is_pass = is_pass
            exam_result.updated_by = user.id
        else:
            exam_result = ExamResult(
                school_id=school_id,
                exam_id=exam_id,
                student_id=enrollment.student_id,
                marks_obtained=Decimal(str(marks_obtained)) if marks_obtained is not None else None,
                attendance=attendance,
                remarks=remarks or None,
                grade=grade,
                is_pass=is_pass,
                created_by=user.id,
            )
            db.add(exam_result)
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
        "exam_id": exam.id,
        "imported": imported,
        "skipped": skipped,
        "errors": errors,
        "message": f"{imported} results imported. Grades and ranks auto-computed.",
    }


async def update_result(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    exam_id: uuid.UUID,
    result_id: uuid.UUID,
    data: UpdateResultRequest,
) -> dict:
    """Update a single student result."""
    result = await db.execute(
        select(ExamResult).where(
            ExamResult.id == result_id,
            ExamResult.exam_id == exam_id,
            ExamResult.school_id == school_id,
            ExamResult.is_active.is_(True),
        )
    )
    exam_result = result.scalar_one_or_none()
    if not exam_result:
        raise NotFound("ExamResult", str(result_id))

    exam_query = await db.execute(select(Exam).where(Exam.id == exam_id))
    exam = exam_query.scalar_one()

    grade_system = await _get_active_grade_system(db, school_id)
    scales = grade_system.scales if grade_system else []
    total_marks = float(exam.total_marks)
    passing_marks = float(exam.passing_marks) if exam.passing_marks else None

    previous_marks = float(exam_result.marks_obtained) if exam_result.marks_obtained is not None else None
    previous_grade = exam_result.grade

    update_data = data.model_dump(exclude_unset=True)
    if "marks_obtained" in update_data:
        new_marks = update_data["marks_obtained"]
        if new_marks is not None:
            if new_marks < 0:
                raise ValidationError("Marks obtained must be >= 0")
            if new_marks > total_marks:
                raise ValidationError(f"Marks cannot exceed total_marks ({total_marks})")
        exam_result.marks_obtained = Decimal(str(new_marks)) if new_marks is not None else None
    if "attendance" in update_data:
        exam_result.attendance = update_data["attendance"]
    if "remarks" in update_data:
        exam_result.remarks = update_data["remarks"]

    # Recompute grade
    if exam_result.marks_obtained is not None and exam_result.attendance == "Present":
        pct = float(exam_result.marks_obtained) / total_marks * 100
        exam_result.grade = _compute_grade(pct, scales)
        if passing_marks is not None:
            exam_result.is_pass = float(exam_result.marks_obtained) >= passing_marks
    else:
        exam_result.grade = None
        exam_result.is_pass = None

    exam_result.updated_by = user.id

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
    await db.refresh(exam_result)

    student = exam_result.student
    status_str = "Absent" if exam_result.attendance == "Absent" else ("Pass" if exam_result.is_pass else "Fail")

    # Get user name
    user_name = None
    if user.staff_id:
        staff_result = await db.execute(select(Staff).where(Staff.id == user.staff_id))
        staff = staff_result.scalar_one_or_none()
        user_name = staff.full_name if staff else None

    return {
        "id": exam_result.id,
        "student_id": student.id,
        "student_name": student.full_name,
        "marks_obtained": float(exam_result.marks_obtained) if exam_result.marks_obtained is not None else None,
        "previous_marks": previous_marks,
        "grade": exam_result.grade,
        "previous_grade": previous_grade,
        "rank": exam_result.rank,
        "status": status_str,
        "updated_at": exam_result.updated_at,
        "updated_by": user_name,
        "update_reason": data.remarks,
    }


async def publish_results(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    exam_id: uuid.UUID,
    data: PublishResultsRequest,
) -> dict:
    """Publish results for an exam."""
    result = await db.execute(
        select(Exam).where(
            Exam.id == exam_id,
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
        )
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise NotFound("Exam", str(exam_id))

    if exam.status == "Published":
        raise ValidationError("Results are already published.")

    now = datetime.now(timezone.utc)
    exam.status = "Published"
    exam.published_at = now
    exam.updated_by = user.id

    await db.commit()

    # Get publisher name
    publisher_name = None
    if user.staff_id:
        staff_result = await db.execute(select(Staff).where(Staff.id == user.staff_id))
        staff = staff_result.scalar_one_or_none()
        publisher_name = staff.full_name if staff else None

    # Notifications placeholder (would integrate with notification system)
    notifications_sent = {}
    if data.notify_students:
        notifications_sent["students"] = 0
    if data.notify_parents:
        notifications_sent["parents"] = 0

    return {
        "exam_id": exam.id,
        "status": "Published",
        "published_at": now,
        "published_by": publisher_name,
        "notifications_sent": notifications_sent,
        "message": "Results published and notifications sent.",
    }


async def get_grade_system(
    db: AsyncSession,
    school_id: uuid.UUID,
) -> dict:
    """Get the active grade system."""
    grade_system = await _get_active_grade_system(db, school_id)
    if not grade_system:
        raise NotFound("GradeSystem", "No active grade system found")

    return {
        "id": grade_system.id,
        "name": grade_system.name,
        "academic_year": grade_system.academic_year.name if grade_system.academic_year else "",
        "is_active": grade_system.is_default,
        "grades": [
            {
                "grade": s.grade,
                "min_percentage": float(s.min_percentage),
                "max_percentage": float(s.max_percentage),
                "grade_point": float(s.grade_point) if s.grade_point else None,
                "description": s.description,
            }
            for s in sorted(grade_system.scales, key=lambda x: x.sort_order)
        ],
        "metadata": grade_system.metadata_ or {},
    }


async def update_grade_system(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    data: UpdateGradeSystemRequest,
) -> dict:
    """Update the grade system."""
    grade_system = await _get_active_grade_system(db, school_id)

    if not grade_system:
        # Create new grade system
        ay = await _get_academic_year(db, school_id)
        grade_system = GradeSystem(
            school_id=school_id,
            academic_year_id=ay.id,
            name=data.name or "Default Grade System",
            is_default=True,
            created_by=user.id,
        )
        db.add(grade_system)
        await db.flush()
    else:
        if data.name:
            grade_system.name = data.name
        grade_system.updated_by = user.id
        # Remove old scales
        old_scales_result = await db.execute(
            select(GradeScale).where(GradeScale.grade_system_id == grade_system.id)
        )
        for scale in old_scales_result.scalars().all():
            await db.delete(scale)
        await db.flush()

    # Validate no overlapping ranges
    sorted_grades = sorted(data.grades, key=lambda g: g.min_percentage)
    for i in range(len(sorted_grades) - 1):
        current = sorted_grades[i]
        next_grade = sorted_grades[i + 1]
        if current.max_percentage > next_grade.min_percentage:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail=f"Grade ranges overlap: '{current.grade}' ({current.min_percentage}%-{current.max_percentage}%) overlaps with '{next_grade.grade}' ({next_grade.min_percentage}%-{next_grade.max_percentage}%)",
            )

    # Add new scales
    for idx, g in enumerate(data.grades):
        scale = GradeScale(
            school_id=school_id,
            grade_system_id=grade_system.id,
            grade=g.grade,
            min_percentage=Decimal(str(g.min_percentage)),
            max_percentage=Decimal(str(g.max_percentage)),
            grade_point=Decimal(str(g.grade_point)) if g.grade_point is not None else None,
            description=g.description,
            sort_order=idx,
            created_by=user.id,
        )
        db.add(scale)

    await db.commit()
    await db.refresh(grade_system)

    return {
        "message": "Grade system updated. Applies to future publications only.",
        "id": grade_system.id,
        "grades": [
            {
                "grade": s.grade,
                "min_percentage": float(s.min_percentage),
                "max_percentage": float(s.max_percentage),
                "grade_point": float(s.grade_point) if s.grade_point else None,
                "description": s.description,
            }
            for s in sorted(grade_system.scales, key=lambda x: x.sort_order)
        ],
    }


async def get_analytics(
    db: AsyncSession,
    school_id: uuid.UUID,
    class_name: str | None = None,
    section: str | None = None,
    subject: str | None = None,
    academic_year: str | None = None,
    term: str | None = None,
) -> dict:
    """Get class/subject performance analytics."""
    ay = await _get_academic_year(db, school_id, academic_year)

    cs = None
    cls_name = class_name or ""
    sec_name = section or ""
    if class_name and section:
        cs = await _get_class_section(db, school_id, class_name, section)

    # Get exams matching filters
    query = select(Exam).where(
        Exam.school_id == school_id,
        Exam.academic_year_id == ay.id,
        Exam.is_active.is_(True),
        Exam.status == "Published",
    )
    if cs:
        query = query.where(Exam.class_section_id == cs.id)
    if term:
        query = query.where(Exam.term == term)
    if subject:
        query = query.join(Subject, Exam.subject_id == Subject.id).where(Subject.name == subject)

    exams_result = await db.execute(query.order_by(Exam.date.asc()))
    exams = list(exams_result.scalars().all())

    # Subject performance
    subject_data: dict[str, list[dict]] = {}
    for exam in exams:
        subj_name = exam.subject.name if exam.subject else "Unknown"
        scored = [r for r in exam.results if r.is_active and r.attendance == "Present" and r.marks_obtained is not None]
        if not scored:
            continue
        marks = [float(r.marks_obtained) for r in scored]
        total_m = float(exam.total_marks)
        avg = sum(marks) / len(marks)
        pass_count = len([r for r in scored if r.is_pass])
        pass_rate = round(pass_count / len(scored) * 100, 1) if scored else 0

        if subj_name not in subject_data:
            subject_data[subj_name] = []
        subject_data[subj_name].append({
            "exam_name": exam.name,
            "date": exam.date,
            "average": round(avg, 1),
            "pass_rate": pass_rate,
            "highest": max(marks),
            "lowest": min(marks),
        })

    subject_performance = []
    for subj_name, data_points in subject_data.items():
        averages = [d["average"] for d in data_points]
        pass_rates = [d["pass_rate"] for d in data_points]
        subject_performance.append({
            "subject": subj_name,
            "exams_conducted": len(data_points),
            "average_pass_rate": round(sum(pass_rates) / len(pass_rates), 1) if pass_rates else 0,
            "class_average": round(sum(averages) / len(averages), 1) if averages else 0,
            "highest_average": max(averages) if averages else 0,
            "lowest_average": min(averages) if averages else 0,
            "trend": [
                {"exam_name": d["exam_name"], "date": d["date"], "average": d["average"], "pass_rate": d["pass_rate"]}
                for d in data_points
            ],
        })

    # Grade distribution across all published exams
    grade_dist: dict[str, int] = {}
    for exam in exams:
        for r in exam.results:
            if r.is_active and r.grade:
                grade_dist[r.grade] = grade_dist.get(r.grade, 0) + 1
    total_graded = sum(grade_dist.values())
    grade_distribution = [
        {"grade": g, "count": c, "percentage": round(c / total_graded * 100, 1) if total_graded else 0}
        for g, c in grade_dist.items()
    ]

    return {
        "class_name": cls_name,
        "section": sec_name,
        "academic_year": ay.name,
        "subject_performance": subject_performance,
        "term_comparison": [],
        "student_rankings": [],
        "grade_distribution": grade_distribution,
        "at_risk_students": [],
    }


async def get_report_card(
    db: AsyncSession,
    school_id: uuid.UUID,
    student_id: uuid.UUID,
    academic_year: str | None = None,
    term: str | None = None,
) -> dict:
    """Generate report card data for a student."""
    # Validate student_id
    if not student_id:
        raise HTTPException(status_code=400, detail="student_id must not be empty")

    ay = await _get_academic_year(db, school_id, academic_year)

    # Get student
    student_result = await db.execute(
        select(Student).where(
            Student.id == student_id,
            Student.school_id == school_id,
            Student.is_active.is_(True),
        )
    )
    student = student_result.scalar_one_or_none()
    if not student:
        raise NotFound("Student", str(student_id))

    # Get enrollment
    enrollment_result = await db.execute(
        select(StudentEnrollment).where(
            StudentEnrollment.student_id == student_id,
            StudentEnrollment.academic_year_id == ay.id,
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.is_active.is_(True),
        )
    )
    enrollment = enrollment_result.scalar_one_or_none()
    if not enrollment:
        raise NotFound("StudentEnrollment", str(student_id))

    cs = enrollment.class_section_id
    cs_result = await db.execute(select(ClassSection).where(ClassSection.id == cs))
    class_section = cs_result.scalar_one()
    cls_result = await db.execute(select(Class).where(Class.id == class_section.class_id))
    cls = cls_result.scalar_one()
    sec_result = await db.execute(select(Section).where(Section.id == class_section.section_id))
    sec = sec_result.scalar_one()

    # Get school name
    school_result = await db.execute(select(School).where(School.id == school_id))
    school = school_result.scalar_one()

    # Get all published exam results for this student
    query = (
        select(ExamResult)
        .join(Exam, ExamResult.exam_id == Exam.id)
        .where(
            ExamResult.student_id == student_id,
            ExamResult.school_id == school_id,
            ExamResult.is_active.is_(True),
            Exam.academic_year_id == ay.id,
            Exam.class_section_id == cs,
            Exam.status == "Published",
            Exam.is_active.is_(True),
        )
    )
    if term:
        query = query.where(Exam.term == term)

    results = await db.execute(query)
    exam_results = list(results.scalars().all())

    # Group by subject
    subject_marks: dict[str, list[tuple[float, float]]] = {}
    for r in exam_results:
        exam = r.exam
        subj_name = exam.subject.name if exam.subject else "Unknown"
        if r.marks_obtained is not None:
            if subj_name not in subject_marks:
                subject_marks[subj_name] = []
            subject_marks[subj_name].append((float(r.marks_obtained), float(exam.total_marks)))

    # Build subjects
    grade_system = await _get_active_grade_system(db, school_id)
    scales = grade_system.scales if grade_system else []

    subjects = []
    total_weighted = 0.0
    total_max = 0.0
    for subj_name, marks_list in subject_marks.items():
        total_obtained = sum(m[0] for m in marks_list)
        total_possible = sum(m[1] for m in marks_list)
        pct = total_obtained / total_possible * 100 if total_possible else 0
        grade = _compute_grade(pct, scales)

        # Find grade point
        gp = None
        if grade and scales:
            for s in scales:
                if s.grade == grade:
                    gp = float(s.grade_point) if s.grade_point else None
                    break

        subjects.append({
            "subject": subj_name,
            "weighted_total": round(pct, 1),
            "grade": grade,
            "grade_point": gp,
            "remarks": None,
        })
        total_weighted += total_obtained
        total_max += total_possible

    overall_pct = total_weighted / total_max * 100 if total_max else 0
    overall_grade = _compute_grade(overall_pct, scales)
    overall_gp = None
    if overall_grade and scales:
        for s in scales:
            if s.grade == overall_grade:
                overall_gp = float(s.grade_point) if s.grade_point else None
                break

    # Count class strength
    class_strength = await _count_students_in_class(db, school_id, cs, ay.id)

    return {
        "student_id": student.id,
        "student_name": student.full_name,
        "roll_number": enrollment.roll_number or student.admission_number,
        "class_section": f"{cls.name}-{sec.name}",
        "academic_year": ay.name,
        "term": term,
        "school_name": school.name,
        "subjects": subjects,
        "overall": {
            "total_weighted_average": round(overall_pct, 1),
            "overall_grade": overall_grade,
            "overall_gpa": overall_gp,
            "rank": None,
            "class_strength": class_strength,
            "attendance_percentage": None,
            "total_working_days": None,
            "days_present": None,
        },
        "class_teacher_remarks": None,
        "principal_remarks": None,
        "generated_at": datetime.now(timezone.utc),
        "metadata": {},
    }


async def generate_report_cards(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    data: GenerateReportCardsRequest,
) -> dict:
    """Batch generate report cards for a class."""
    cs = await _get_class_section(db, school_id, data.class_name, data.section)
    ay = await _get_academic_year(db, school_id, data.academic_year)

    # Count students
    count = await _count_students_in_class(db, school_id, cs.id, ay.id)

    return {
        "generated": count,
        "class_section": f"{data.class_name}-{data.section}",
        "academic_year": data.academic_year,
        "term": data.term,
        "download_url": f"/api/v1/admin/examinations/report-card/download/?class_name={data.class_name}&section={data.section}&term={data.term or ''}&academic_year={data.academic_year}",
        "expires_at": None,
    }


async def get_exam_schedule(
    db: AsyncSession,
    school_id: uuid.UUID,
    class_name: str,
    section: str,
    academic_year: str | None = None,
    term: str | None = None,
) -> dict:
    """Get exam schedule for a class."""
    ay = await _get_academic_year(db, school_id, academic_year)
    cs = await _get_class_section(db, school_id, class_name, section)

    query = (
        select(Exam)
        .where(
            Exam.school_id == school_id,
            Exam.academic_year_id == ay.id,
            Exam.class_section_id == cs.id,
            Exam.is_active.is_(True),
            Exam.status.in_(["Scheduled", "In Progress", "Completed", "Published"]),
        )
        .order_by(Exam.date.asc())
    )
    if term:
        query = query.where(Exam.term == term)

    result = await db.execute(query)
    exams = list(result.scalars().all())

    exam_items = []
    for exam in exams:
        exam_items.append({
            "date": exam.date,
            "subject": exam.subject.name if exam.subject else "",
            "start_time": str(exam.start_time) if exam.start_time else None,
            "end_time": str(exam.end_time) if exam.end_time else None,
            "total_marks": float(exam.total_marks),
            "type": exam.exam_type,
        })

    return {
        "class_name": class_name,
        "section": section,
        "term": term,
        "academic_year": ay.name,
        "exams": exam_items,
    }
