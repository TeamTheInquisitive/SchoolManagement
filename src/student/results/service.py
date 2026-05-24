from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFound, ValidationError
from src.core.pagination import PaginationParams, paginate
from src.models.academic import Class, ClassSection, Section, Subject
from src.models.core import AcademicYear, User
from src.models.examination import Exam, ExamResult, GradeScale, GradeSystem
from src.models.student import Student, StudentEnrollment


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
    """Compute grade from percentage."""
    for scale in sorted(scales, key=lambda s: s.min_percentage, reverse=True):
        if float(scale.min_percentage) <= percentage <= float(scale.max_percentage):
            return scale.grade
    return None


async def get_results_overview(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    academic_year: str | None = None,
) -> dict:
    """Get overall results summary with performance trend, subject comparison, and radar."""
    student = await _get_student_for_user(db, school_id, user)
    ay = await _get_academic_year(db, school_id, academic_year)

    # Get all published exam results for this student
    results_query = await db.execute(
        select(ExamResult)
        .join(Exam, ExamResult.exam_id == Exam.id)
        .where(
            ExamResult.student_id == student.id,
            ExamResult.school_id == school_id,
            ExamResult.is_active.is_(True),
            Exam.academic_year_id == ay.id,
            Exam.status == "Published",
            Exam.is_active.is_(True),
        )
        .order_by(Exam.date.asc())
    )
    exam_results = list(results_query.scalars().all())

    if not exam_results:
        return {
            "academic_year": ay.name,
            "summary": {"average_score": 0, "highest_score": 0, "lowest_score": 0, "avg_rank": 0},
            "filters": {},
            "performance_trend": [],
            "subject_wise_performance": [],
            "performance_radar": {"subjects": [], "student_scores": [], "max_marks": 100},
            "metadata": {},
        }

    # Group by exam for trends
    exam_groups: dict[uuid.UUID, list[ExamResult]] = {}
    for r in exam_results:
        if r.exam_id not in exam_groups:
            exam_groups[r.exam_id] = []
        exam_groups[r.exam_id].append(r)

    # Performance trend
    performance_trend = []
    percentages = []
    ranks = []
    for exam_id, results in exam_groups.items():
        exam = results[0].exam
        total_obtained = sum(float(r.marks_obtained) for r in results if r.marks_obtained is not None)
        total_possible = sum(float(r.exam.total_marks) for r in results if r.marks_obtained is not None)
        pct = total_obtained / total_possible * 100 if total_possible else 0
        percentages.append(pct)

        # Collect ranks
        for r in results:
            if r.rank:
                ranks.append(r.rank)

        subjects_dict = {}
        for r in results:
            if r.marks_obtained is not None and r.exam.subject:
                subj_pct = float(r.marks_obtained) / float(r.exam.total_marks) * 100
                subjects_dict[r.exam.subject.name] = round(subj_pct, 1)

        performance_trend.append({
            "exam_name": exam.name,
            "exam_type": exam.exam_type,
            "date": exam.date,
            "percentage": round(pct, 1),
            "subjects": subjects_dict,
        })

    # Subject-wise performance (average across all exams)
    subject_totals: dict[str, tuple[float, float]] = {}
    for r in exam_results:
        if r.marks_obtained is not None and r.exam.subject:
            subj_name = r.exam.subject.name
            obtained, possible = subject_totals.get(subj_name, (0.0, 0.0))
            subject_totals[subj_name] = (obtained + float(r.marks_obtained), possible + float(r.exam.total_marks))

    subject_wise_performance = []
    radar_subjects = []
    radar_scores = []
    for subj_name, (obtained, possible) in subject_totals.items():
        pct = obtained / possible * 100 if possible else 0
        subject_wise_performance.append({
            "subject": subj_name,
            "student_percentage": round(pct, 1),
            "max_marks": 100,
        })
        radar_subjects.append(subj_name)
        radar_scores.append(round(pct, 1))

    # Summary
    avg_score = sum(percentages) / len(percentages) if percentages else 0
    highest_score = max(percentages) if percentages else 0
    lowest_score = min(percentages) if percentages else 0
    avg_rank = sum(ranks) / len(ranks) if ranks else 0

    return {
        "academic_year": ay.name,
        "summary": {
            "average_score": round(avg_score, 1),
            "highest_score": round(highest_score, 1),
            "lowest_score": round(lowest_score, 1),
            "avg_rank": round(avg_rank, 1),
        },
        "filters": {},
        "performance_trend": performance_trend,
        "subject_wise_performance": subject_wise_performance,
        "performance_radar": {
            "subjects": radar_subjects,
            "student_scores": radar_scores,
            "max_marks": 100,
        },
        "metadata": {},
    }


async def get_exam_result_detail(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    exam_id: uuid.UUID,
) -> dict:
    """Get detailed result for a specific exam."""
    student = await _get_student_for_user(db, school_id, user)

    # The exam_id here is actually a "group exam" concept — find all exams for same
    # class-section, academic year, and exam_type/name that match this exam
    exam_result = await db.execute(
        select(Exam).where(
            Exam.id == exam_id,
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
            Exam.status == "Published",
        )
    )
    exam = exam_result.scalar_one_or_none()
    if not exam:
        raise NotFound("Exam", str(exam_id))

    ay = exam.academic_year

    # Get student's enrollment
    enrollment_result = await db.execute(
        select(StudentEnrollment).where(
            StudentEnrollment.student_id == student.id,
            StudentEnrollment.academic_year_id == ay.id,
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.is_active.is_(True),
        )
    )
    enrollment = enrollment_result.scalar_one_or_none()
    if not enrollment:
        raise NotFound("StudentEnrollment", str(student.id))

    cs = enrollment.class_section_id
    cs_result = await db.execute(select(ClassSection).where(ClassSection.id == cs))
    class_section = cs_result.scalar_one()
    cls_result = await db.execute(select(Class).where(Class.id == class_section.class_id))
    cls = cls_result.scalar_one()
    sec_result = await db.execute(select(Section).where(Section.id == class_section.section_id))
    sec = sec_result.scalar_one()

    # Get the student's result for this exam
    result_query = await db.execute(
        select(ExamResult).where(
            ExamResult.exam_id == exam_id,
            ExamResult.student_id == student.id,
            ExamResult.school_id == school_id,
            ExamResult.is_active.is_(True),
        )
    )
    student_result = result_query.scalar_one_or_none()
    if not student_result:
        raise NotFound("ExamResult", str(exam_id))

    total_marks = float(exam.total_marks)
    marks_obtained = float(student_result.marks_obtained) if student_result.marks_obtained is not None else 0
    pct = marks_obtained / total_marks * 100 if total_marks else 0
    passing_marks = float(exam.passing_marks) if exam.passing_marks else None

    # Get class stats for this exam
    all_results_query = await db.execute(
        select(ExamResult).where(
            ExamResult.exam_id == exam_id,
            ExamResult.school_id == school_id,
            ExamResult.is_active.is_(True),
            ExamResult.attendance == "Present",
            ExamResult.marks_obtained.isnot(None),
        )
    )
    all_results = list(all_results_query.scalars().all())
    all_marks = [float(r.marks_obtained) for r in all_results]
    class_avg = sum(all_marks) / len(all_marks) if all_marks else 0
    highest = max(all_marks) if all_marks else 0

    # Count total students
    total_students_result = await db.execute(
        select(func.count(StudentEnrollment.id)).where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.class_section_id == cs,
            StudentEnrollment.academic_year_id == ay.id,
            StudentEnrollment.is_active.is_(True),
        )
    )
    total_students = total_students_result.scalar() or 0

    subjects = [{
        "subject": exam.subject.name if exam.subject else "",
        "marks_obtained": marks_obtained,
        "max_marks": total_marks,
        "percentage": round(pct, 1),
        "grade": student_result.grade,
        "class_average": round(class_avg, 1),
        "highest_in_class": highest,
        "rank": student_result.rank,
        "status": "pass" if student_result.is_pass else "fail",
        "pass_marks": passing_marks,
    }]

    return {
        "exam_id": exam.id,
        "exam_name": exam.name,
        "exam_type": exam.exam_type,
        "date": exam.date,
        "class_section": f"{cls.name}-{sec.name}",
        "academic_year": ay.name,
        "total_marks_obtained": marks_obtained,
        "total_max_marks": total_marks,
        "overall_percentage": round(pct, 1),
        "overall_grade": student_result.grade,
        "class_rank": student_result.rank,
        "total_students": total_students,
        "subjects": subjects,
        "metadata": {},
    }


async def get_exams_with_results(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    pagination: PaginationParams,
    exam_type: str | None = None,
    academic_year: str | None = None,
) -> dict:
    """List all exams with results for the student."""
    student = await _get_student_for_user(db, school_id, user)
    ay = await _get_academic_year(db, school_id, academic_year)

    # Get student's results for published exams
    query = (
        select(ExamResult)
        .join(Exam, ExamResult.exam_id == Exam.id)
        .where(
            ExamResult.student_id == student.id,
            ExamResult.school_id == school_id,
            ExamResult.is_active.is_(True),
            Exam.academic_year_id == ay.id,
            Exam.status == "Published",
            Exam.is_active.is_(True),
        )
        .order_by(Exam.date.desc())
    )
    if exam_type:
        query = query.where(Exam.exam_type == exam_type)

    results_result = await db.execute(query)
    all_student_results = list(results_result.scalars().all())

    # Group by exam
    exam_map: dict[uuid.UUID, list[ExamResult]] = {}
    for r in all_student_results:
        if r.exam_id not in exam_map:
            exam_map[r.exam_id] = []
        exam_map[r.exam_id].append(r)

    items = []
    for exam_id, results in exam_map.items():
        exam = results[0].exam
        total_obtained = sum(float(r.marks_obtained) for r in results if r.marks_obtained is not None)
        total_possible = sum(float(r.exam.total_marks) for r in results if r.marks_obtained is not None)
        pct = total_obtained / total_possible * 100 if total_possible else 0

        # Grade system
        grade_system = await _get_active_grade_system(db, school_id)
        scales = grade_system.scales if grade_system else []
        overall_grade = _compute_grade(pct, scales) if scales else None

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

        # Subject details
        subjects = []
        for r in results:
            if r.marks_obtained is not None and r.exam.subject:
                subj_pct = float(r.marks_obtained) / float(r.exam.total_marks) * 100
                passing_marks = float(r.exam.passing_marks) if r.exam.passing_marks else None
                subjects.append({
                    "subject": r.exam.subject.name,
                    "marks_obtained": float(r.marks_obtained),
                    "max_marks": float(r.exam.total_marks),
                    "percentage": round(subj_pct, 1),
                    "grade": r.grade,
                    "rank": r.rank,
                    "status": "pass" if r.is_pass else "fail",
                    "pass_marks": passing_marks,
                    "leaderboard_url": f"/api/v1/student/results/exam/{r.exam_id}/leaderboard/?subject={r.exam.subject.name}",
                })

        # Use the rank from the first result (single exam) or None
        class_rank = results[0].rank if len(results) == 1 else None

        items.append({
            "id": exam_id,
            "exam_name": exam.name,
            "exam_type": exam.exam_type,
            "date": exam.date,
            "total_marks_obtained": total_obtained,
            "total_max_marks": total_possible,
            "percentage": round(pct, 1),
            "grade": overall_grade,
            "class_rank": class_rank,
            "total_students": total_students,
            "subjects_count": len(results),
            "subjects": subjects,
            "metadata": {},
        })

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
        "results": paginated_items,
        "metadata": {},
    }


async def get_exam_leaderboard(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    exam_id: uuid.UUID,
    subject: str | None = None,
) -> dict:
    """Get leaderboard for a specific exam."""
    student = await _get_student_for_user(db, school_id, user)

    exam_result = await db.execute(
        select(Exam).where(
            Exam.id == exam_id,
            Exam.school_id == school_id,
            Exam.is_active.is_(True),
            Exam.status == "Published",
        )
    )
    exam = exam_result.scalar_one_or_none()
    if not exam:
        raise NotFound("Exam", str(exam_id))

    ay = exam.academic_year
    total_marks = float(exam.total_marks)

    # Get all results for this exam, ordered by marks
    all_results_query = await db.execute(
        select(ExamResult).where(
            ExamResult.exam_id == exam_id,
            ExamResult.school_id == school_id,
            ExamResult.is_active.is_(True),
            ExamResult.attendance == "Present",
            ExamResult.marks_obtained.isnot(None),
        )
    )
    all_results = list(all_results_query.scalars().all())
    all_results.sort(key=lambda r: float(r.marks_obtained), reverse=True)  # type: ignore[arg-type]

    # Find student's position
    student_rank = None
    student_score = None
    for idx, r in enumerate(all_results, start=1):
        if r.student_id == student.id:
            student_rank = idx
            student_score = float(r.marks_obtained)
            break

    # Calculate percentile
    percentile = None
    if student_rank and len(all_results) > 0:
        percentile = round((len(all_results) - student_rank) / len(all_results) * 100, 1)

    # Build top performers
    top_performers = []
    for idx, r in enumerate(all_results[:10], start=1):
        marks = float(r.marks_obtained)
        top_performers.append({
            "rank": idx,
            "student_name": r.student.full_name,
            "marks_obtained": marks,
            "max_marks": total_marks,
            "percentage": round(marks / total_marks * 100, 1),
            "grade": r.grade,
            "is_current_student": r.student_id == student.id,
        })

    return {
        "exam_id": exam.id,
        "exam_name": exam.name,
        "subject": exam.subject.name if exam.subject else None,
        "academic_year": ay.name,
        "student_rank": student_rank,
        "student_score": student_score,
        "max_marks": total_marks,
        "percentile": percentile,
        "top_performers": top_performers,
        "metadata": {},
    }


async def get_download_report(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    academic_year: str | None = None,
    exam_id: uuid.UUID | None = None,
) -> dict:
    """Generate download report URL."""
    student = await _get_student_for_user(db, school_id, user)
    ay = await _get_academic_year(db, school_id, academic_year)

    scope = "single_exam" if exam_id else "all_exams"
    file_name = f"Results_Report_{student.full_name.replace(' ', '_')}_{ay.name}.pdf"

    return {
        "download_url": "/api/v1/student/results/download-report/file/",
        "file_name": file_name,
        "content_type": "application/pdf",
        "generated_at": datetime.now(timezone.utc),
        "report_scope": scope,
        "academic_year": ay.name,
        "metadata": {},
    }
