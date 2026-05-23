from __future__ import annotations

import csv
import io
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AccessDenied, NotFound, ValidationError
from src.core.pagination import PaginationParams, paginate
from src.models.academic import Class, ClassSection, Section, Subject
from src.models.assignment import Assignment, AssignmentSubmission
from src.models.core import AcademicYear, User
from src.models.staff import ClassAssignment, Staff
from src.models.student import Student, StudentEnrollment
from src.teacher.assignments.schemas import (
    CreateAssignmentRequest,
    GradeSubmissionRequest,
    UpdateAssignmentRequest,
)


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


async def _verify_teacher_class_assignment(
    db: AsyncSession,
    school_id: uuid.UUID,
    staff_id: uuid.UUID,
    class_section_id: uuid.UUID,
    academic_year_id: uuid.UUID,
) -> ClassAssignment:
    """Verify teacher is assigned to the class and return the assignment (for subject)."""
    result = await db.execute(
        select(ClassAssignment).where(
            ClassAssignment.school_id == school_id,
            ClassAssignment.staff_id == staff_id,
            ClassAssignment.class_section_id == class_section_id,
            ClassAssignment.academic_year_id == academic_year_id,
            ClassAssignment.is_active.is_(True),
        )
    )
    ca = result.scalar_one_or_none()
    if not ca:
        raise AccessDenied("You are not assigned to this class")
    return ca


async def _get_enrolled_students(
    db: AsyncSession,
    school_id: uuid.UUID,
    class_section_id: uuid.UUID,
    academic_year_id: uuid.UUID,
) -> list[StudentEnrollment]:
    """Get all active enrolled students for a class-section in an academic year."""
    result = await db.execute(
        select(StudentEnrollment).where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.class_section_id == class_section_id,
            StudentEnrollment.academic_year_id == academic_year_id,
            StudentEnrollment.is_active.is_(True),
            StudentEnrollment.status == "Active",
        )
    )
    return list(result.scalars().all())


def _compute_assignment_status(assignment: Assignment) -> str:
    """Compute the display status of an assignment."""
    if assignment.status == "Closed":
        return "Completed"
    if assignment.due_date < date.today():
        return "Past Due"
    return "Active"


async def list_assignments(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    pagination: PaginationParams,
    class_id: uuid.UUID | None = None,
    status_filter: str | None = None,
    search: str | None = None,
    academic_year: str | None = None,
) -> dict:
    """List assignments for this teacher with KPI summary."""
    staff = await _get_staff_for_user(db, school_id, user)
    ay = await _get_current_academic_year(db, school_id, academic_year)

    # Base query: assignments created by this teacher
    base_filter = and_(
        Assignment.school_id == school_id,
        Assignment.staff_id == staff.id,
        Assignment.academic_year_id == ay.id,
        Assignment.is_active.is_(True),
    )

    # Count total for summary
    total_result = await db.execute(
        select(func.count(Assignment.id)).where(base_filter)
    )
    total_assignments = total_result.scalar() or 0

    # Active assignments (due_date >= today and status Active)
    active_result = await db.execute(
        select(func.count(Assignment.id)).where(
            base_filter,
            Assignment.due_date >= date.today(),
            Assignment.status == "Active",
        )
    )
    active_count = active_result.scalar() or 0

    # Graded submissions count (across all this teacher's assignments)
    graded_result = await db.execute(
        select(func.count(AssignmentSubmission.id))
        .join(Assignment, AssignmentSubmission.assignment_id == Assignment.id)
        .where(
            Assignment.school_id == school_id,
            Assignment.staff_id == staff.id,
            Assignment.academic_year_id == ay.id,
            Assignment.is_active.is_(True),
            AssignmentSubmission.status == "Graded",
            AssignmentSubmission.is_active.is_(True),
        )
    )
    graded_count = graded_result.scalar() or 0

    # To review: submitted but not yet graded
    to_review_result = await db.execute(
        select(func.count(AssignmentSubmission.id))
        .join(Assignment, AssignmentSubmission.assignment_id == Assignment.id)
        .where(
            Assignment.school_id == school_id,
            Assignment.staff_id == staff.id,
            Assignment.academic_year_id == ay.id,
            Assignment.is_active.is_(True),
            AssignmentSubmission.status == "Submitted",
            AssignmentSubmission.is_active.is_(True),
        )
    )
    to_review_count = to_review_result.scalar() or 0

    # Build list query with filters
    query = select(Assignment).where(base_filter)

    if class_id:
        query = query.where(Assignment.class_section_id == class_id)

    if search:
        query = query.where(Assignment.title.ilike(f"%{search}%"))

    # Count for pagination
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Apply pagination
    query = query.order_by(Assignment.created_at.desc())
    query = query.offset(pagination.offset).limit(pagination.page_size)

    result = await db.execute(query)
    assignments = list(result.scalars().all())

    # Build results
    items = []
    for a in assignments:
        # Get class/section names
        cs = a.class_section
        class_obj = cs.class_ if hasattr(cs, "class_") else None
        section_obj = cs.section if hasattr(cs, "section") else None

        # Try to get class/section from relationship
        cs_result = await db.execute(
            select(Class).where(Class.id == cs.class_id)
        )
        class_obj = cs_result.scalar_one_or_none()
        sec_result = await db.execute(
            select(Section).where(Section.id == cs.section_id)
        )
        section_obj = sec_result.scalar_one_or_none()

        class_name = class_obj.name if class_obj else ""
        section_name = section_obj.name if section_obj else ""
        subject_name = a.subject.name if a.subject else ""

        # Submission counts
        total_students_result = await db.execute(
            select(func.count(AssignmentSubmission.id)).where(
                AssignmentSubmission.assignment_id == a.id,
                AssignmentSubmission.is_active.is_(True),
            )
        )
        total_students = total_students_result.scalar() or 0

        submissions_count_result = await db.execute(
            select(func.count(AssignmentSubmission.id)).where(
                AssignmentSubmission.assignment_id == a.id,
                AssignmentSubmission.is_active.is_(True),
                AssignmentSubmission.status.in_(["Submitted", "Graded", "Late"]),
            )
        )
        submissions_count = submissions_count_result.scalar() or 0

        graded_count_result = await db.execute(
            select(func.count(AssignmentSubmission.id)).where(
                AssignmentSubmission.assignment_id == a.id,
                AssignmentSubmission.is_active.is_(True),
                AssignmentSubmission.status == "Graded",
            )
        )
        assignment_graded = graded_count_result.scalar() or 0

        computed_status = _compute_assignment_status(a)

        # Apply status filter after computing
        if status_filter and computed_status.lower() != status_filter.lower():
            continue

        items.append({
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "class_name": class_name,
            "section": section_name,
            "class_section": f"{class_name}-{section_name}",
            "subject": subject_name,
            "due_date": a.due_date,
            "max_marks": float(a.max_marks) if a.max_marks else None,
            "total_students": total_students,
            "submissions_count": submissions_count,
            "graded_count": assignment_graded,
            "status": computed_status,
            "created_at": a.created_at,
            "is_active": a.is_active,
            "metadata": a.metadata_ or {},
        })

    paginated = paginate(items, total, pagination)
    paginated["summary"] = {
        "total_assignments": total_assignments,
        "active": active_count,
        "graded": graded_count,
        "to_review": to_review_count,
    }
    return paginated


async def create_assignment(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    data: CreateAssignmentRequest,
) -> dict:
    """Create a new assignment and auto-generate submissions for enrolled students."""
    staff = await _get_staff_for_user(db, school_id, user)
    ay = await _get_current_academic_year(db, school_id, data.academic_year)
    cs = await _get_class_section(db, school_id, data.class_name, data.section)

    # Verify teacher is assigned to this class
    class_assignment = await _verify_teacher_class_assignment(
        db, school_id, staff.id, cs.id, ay.id
    )

    # Get subject from teacher's class assignment
    subject_result = await db.execute(
        select(Subject).where(Subject.id == class_assignment.subject_id)
    )
    subject = subject_result.scalar_one_or_none()
    if not subject:
        raise NotFound("Subject")

    # Create assignment
    assignment = Assignment(
        school_id=school_id,
        academic_year_id=ay.id,
        class_section_id=cs.id,
        subject_id=subject.id,
        staff_id=staff.id,
        title=data.title,
        description=data.description,
        due_date=data.due_date,
        max_marks=data.max_marks,
        status="Active",
        assigned_date=date.today(),
        created_by=user.id,
    )
    db.add(assignment)
    await db.flush()

    # Auto-generate submission records for all enrolled students
    enrollments = await _get_enrolled_students(db, school_id, cs.id, ay.id)
    for enrollment in enrollments:
        submission = AssignmentSubmission(
            school_id=school_id,
            assignment_id=assignment.id,
            student_id=enrollment.student_id,
            status="Pending",
            created_by=user.id,
        )
        db.add(submission)

    await db.commit()
    await db.refresh(assignment)

    return {
        "id": assignment.id,
        "title": assignment.title,
        "description": assignment.description,
        "class_name": data.class_name,
        "section": data.section,
        "class_section": f"{data.class_name}-{data.section}",
        "subject": subject.name,
        "due_date": assignment.due_date,
        "max_marks": float(assignment.max_marks) if assignment.max_marks else None,
        "total_students": len(enrollments),
        "submissions_count": 0,
        "graded_count": 0,
        "status": "Active",
        "created_at": assignment.created_at,
        "is_active": assignment.is_active,
        "academic_year": ay.name,
        "metadata": assignment.metadata_ or {},
    }


async def get_assignment_detail(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    assignment_id: uuid.UUID,
) -> dict:
    """Get assignment details with submission statistics."""
    staff = await _get_staff_for_user(db, school_id, user)

    result = await db.execute(
        select(Assignment).where(
            Assignment.id == assignment_id,
            Assignment.school_id == school_id,
            Assignment.staff_id == staff.id,
            Assignment.is_active.is_(True),
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise NotFound("Assignment", str(assignment_id))

    # Get class/section info
    cs = assignment.class_section
    cs_result = await db.execute(select(Class).where(Class.id == cs.class_id))
    class_obj = cs_result.scalar_one_or_none()
    sec_result = await db.execute(select(Section).where(Section.id == cs.section_id))
    section_obj = sec_result.scalar_one_or_none()
    class_section_str = f"{class_obj.name}-{section_obj.name}" if class_obj and section_obj else ""

    # Submission stats
    total_result = await db.execute(
        select(func.count(AssignmentSubmission.id)).where(
            AssignmentSubmission.assignment_id == assignment.id,
            AssignmentSubmission.is_active.is_(True),
        )
    )
    total_students = total_result.scalar() or 0

    submitted_result = await db.execute(
        select(func.count(AssignmentSubmission.id)).where(
            AssignmentSubmission.assignment_id == assignment.id,
            AssignmentSubmission.is_active.is_(True),
            AssignmentSubmission.status.in_(["Submitted", "Graded", "Late"]),
        )
    )
    submitted = submitted_result.scalar() or 0

    graded_result = await db.execute(
        select(func.count(AssignmentSubmission.id)).where(
            AssignmentSubmission.assignment_id == assignment.id,
            AssignmentSubmission.is_active.is_(True),
            AssignmentSubmission.status == "Graded",
        )
    )
    graded = graded_result.scalar() or 0

    # Average marks for graded submissions
    avg_result = await db.execute(
        select(func.avg(AssignmentSubmission.marks)).where(
            AssignmentSubmission.assignment_id == assignment.id,
            AssignmentSubmission.is_active.is_(True),
            AssignmentSubmission.status == "Graded",
        )
    )
    avg_marks = avg_result.scalar()

    # Academic year
    ay = assignment.academic_year

    return {
        "id": assignment.id,
        "title": assignment.title,
        "description": assignment.description,
        "class_id": assignment.class_section_id,
        "class_section": class_section_str,
        "subject": assignment.subject.name if assignment.subject else "",
        "due_date": assignment.due_date,
        "max_marks": float(assignment.max_marks) if assignment.max_marks else None,
        "status": _compute_assignment_status(assignment),
        "created_at": assignment.created_at,
        "updated_at": assignment.updated_at,
        "is_active": assignment.is_active,
        "academic_year": ay.name if ay else "",
        "submission_stats": {
            "total_students": total_students,
            "submitted": submitted,
            "not_submitted": total_students - submitted,
            "graded": graded,
            "average_marks": round(float(avg_marks), 2) if avg_marks else None,
        },
        "metadata": assignment.metadata_ or {},
    }


async def update_assignment(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    assignment_id: uuid.UUID,
    data: UpdateAssignmentRequest,
) -> dict:
    """Update an existing assignment."""
    staff = await _get_staff_for_user(db, school_id, user)

    result = await db.execute(
        select(Assignment).where(
            Assignment.id == assignment_id,
            Assignment.school_id == school_id,
            Assignment.staff_id == staff.id,
            Assignment.is_active.is_(True),
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise NotFound("Assignment", str(assignment_id))

    # Update fields
    if data.title is not None:
        assignment.title = data.title
    if data.description is not None:
        assignment.description = data.description
    if data.due_date is not None:
        assignment.due_date = data.due_date
    if data.max_marks is not None:
        assignment.max_marks = data.max_marks

    assignment.updated_by = user.id
    await db.commit()
    await db.refresh(assignment)

    # Get class/section info
    cs = assignment.class_section
    cs_result = await db.execute(select(Class).where(Class.id == cs.class_id))
    class_obj = cs_result.scalar_one_or_none()
    sec_result = await db.execute(select(Section).where(Section.id == cs.section_id))
    section_obj = sec_result.scalar_one_or_none()
    class_section_str = f"{class_obj.name}-{section_obj.name}" if class_obj and section_obj else ""

    ay = assignment.academic_year

    return {
        "id": assignment.id,
        "title": assignment.title,
        "description": assignment.description,
        "class_id": assignment.class_section_id,
        "class_section": class_section_str,
        "subject": assignment.subject.name if assignment.subject else "",
        "due_date": assignment.due_date,
        "max_marks": float(assignment.max_marks) if assignment.max_marks else None,
        "status": _compute_assignment_status(assignment),
        "created_at": assignment.created_at,
        "updated_at": assignment.updated_at,
        "is_active": assignment.is_active,
        "academic_year": ay.name if ay else "",
        "metadata": assignment.metadata_ or {},
    }


async def delete_assignment(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    assignment_id: uuid.UUID,
) -> dict:
    """Soft-delete an assignment."""
    staff = await _get_staff_for_user(db, school_id, user)

    result = await db.execute(
        select(Assignment).where(
            Assignment.id == assignment_id,
            Assignment.school_id == school_id,
            Assignment.staff_id == staff.id,
            Assignment.is_active.is_(True),
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise NotFound("Assignment", str(assignment_id))

    now = datetime.now(timezone.utc)
    assignment.is_active = False
    assignment.deleted_at = now
    assignment.deleted_by = user.id
    await db.commit()

    return {
        "message": "Assignment deleted successfully",
        "id": assignment.id,
        "deactivated_on": now,
    }


async def list_submissions(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    assignment_id: uuid.UUID,
    pagination: PaginationParams,
    status_filter: str | None = None,
) -> dict:
    """List student submissions for a specific assignment."""
    staff = await _get_staff_for_user(db, school_id, user)

    # Verify assignment belongs to this teacher
    a_result = await db.execute(
        select(Assignment).where(
            Assignment.id == assignment_id,
            Assignment.school_id == school_id,
            Assignment.staff_id == staff.id,
            Assignment.is_active.is_(True),
        )
    )
    assignment = a_result.scalar_one_or_none()
    if not assignment:
        raise NotFound("Assignment", str(assignment_id))

    # Get class/section info
    cs = assignment.class_section
    cs_result = await db.execute(select(Class).where(Class.id == cs.class_id))
    class_obj = cs_result.scalar_one_or_none()
    sec_result = await db.execute(select(Section).where(Section.id == cs.section_id))
    section_obj = sec_result.scalar_one_or_none()
    class_section_str = f"{class_obj.name}-{section_obj.name}" if class_obj and section_obj else ""

    # Base query for submissions
    base_filter = and_(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.is_active.is_(True),
    )

    # Apply status filter
    if status_filter:
        if status_filter == "pending_review":
            base_filter = and_(base_filter, AssignmentSubmission.status == "Submitted")
        elif status_filter == "graded":
            base_filter = and_(base_filter, AssignmentSubmission.status == "Graded")
        elif status_filter == "not_submitted":
            base_filter = and_(base_filter, AssignmentSubmission.status == "Pending")
        elif status_filter == "submitted":
            base_filter = and_(
                base_filter,
                AssignmentSubmission.status.in_(["Submitted", "Late"]),
            )

    # Count
    count_result = await db.execute(
        select(func.count(AssignmentSubmission.id)).where(base_filter)
    )
    total = count_result.scalar() or 0

    # Total students (all submissions regardless of filter)
    total_students_result = await db.execute(
        select(func.count(AssignmentSubmission.id)).where(
            AssignmentSubmission.assignment_id == assignment_id,
            AssignmentSubmission.is_active.is_(True),
        )
    )
    total_students = total_students_result.scalar() or 0

    # Submissions count (submitted + graded + late)
    submitted_count_result = await db.execute(
        select(func.count(AssignmentSubmission.id)).where(
            AssignmentSubmission.assignment_id == assignment_id,
            AssignmentSubmission.is_active.is_(True),
            AssignmentSubmission.status.in_(["Submitted", "Graded", "Late"]),
        )
    )
    submissions_count = submitted_count_result.scalar() or 0

    # Fetch submissions with student info
    query = (
        select(AssignmentSubmission)
        .where(base_filter)
        .order_by(AssignmentSubmission.submitted_at.desc().nullslast())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    )
    result = await db.execute(query)
    submissions = list(result.scalars().all())

    items = []
    for sub in submissions:
        student = sub.student
        # Get enrollment for roll number
        enrollment_result = await db.execute(
            select(StudentEnrollment).where(
                StudentEnrollment.student_id == sub.student_id,
                StudentEnrollment.class_section_id == assignment.class_section_id,
                StudentEnrollment.academic_year_id == assignment.academic_year_id,
                StudentEnrollment.is_active.is_(True),
            )
        )
        enrollment = enrollment_result.scalar_one_or_none()

        # Map internal status to display status
        display_status = sub.status
        if sub.status == "Submitted":
            display_status = "Pending Review"

        items.append({
            "id": sub.id,
            "student_id": sub.student_id,
            "student_name": student.full_name if student else "",
            "roll_number": enrollment.roll_number if enrollment else (student.admission_number if student else None),
            "submitted_at": sub.submitted_at,
            "status": display_status,
            "marks": float(sub.marks) if sub.marks is not None else None,
            "max_marks": float(assignment.max_marks) if assignment.max_marks else None,
            "graded_at": sub.graded_at,
        })

    paginated = paginate(items, total, pagination)
    paginated["assignment_id"] = assignment.id
    paginated["assignment_title"] = assignment.title
    paginated["class_section"] = class_section_str
    paginated["total_students"] = total_students
    paginated["submissions_count"] = submissions_count
    return paginated


async def grade_submission(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    assignment_id: uuid.UUID,
    submission_id: uuid.UUID,
    data: GradeSubmissionRequest,
) -> dict:
    """Grade a student submission."""
    staff = await _get_staff_for_user(db, school_id, user)

    # Verify assignment belongs to this teacher
    a_result = await db.execute(
        select(Assignment).where(
            Assignment.id == assignment_id,
            Assignment.school_id == school_id,
            Assignment.staff_id == staff.id,
            Assignment.is_active.is_(True),
        )
    )
    assignment = a_result.scalar_one_or_none()
    if not assignment:
        raise NotFound("Assignment", str(assignment_id))

    # Validate marks
    if assignment.max_marks is not None and data.marks > float(assignment.max_marks):
        raise ValidationError(
            f"Marks ({data.marks}) cannot exceed max marks ({assignment.max_marks})",
            details={"marks": data.marks, "max_marks": float(assignment.max_marks)},
        )

    # Get submission
    sub_result = await db.execute(
        select(AssignmentSubmission).where(
            AssignmentSubmission.id == submission_id,
            AssignmentSubmission.assignment_id == assignment_id,
            AssignmentSubmission.is_active.is_(True),
        )
    )
    submission = sub_result.scalar_one_or_none()
    if not submission:
        raise NotFound("Submission", str(submission_id))

    now = datetime.now(timezone.utc)
    submission.marks = data.marks
    submission.feedback = data.feedback
    submission.graded_at = now
    submission.graded_by = staff.id
    submission.status = "Graded"
    submission.updated_by = user.id

    await db.commit()
    await db.refresh(submission)

    student = submission.student

    return {
        "id": submission.id,
        "student_name": student.full_name if student else "",
        "marks": float(submission.marks),
        "max_marks": float(assignment.max_marks) if assignment.max_marks else None,
        "feedback": submission.feedback,
        "status": "Graded",
        "graded_at": submission.graded_at,
        "message": "Submission graded successfully.",
    }


async def export_submissions_csv(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    assignment_id: uuid.UUID,
) -> str:
    """Export all submissions for an assignment as CSV content."""
    staff = await _get_staff_for_user(db, school_id, user)

    # Verify assignment belongs to this teacher
    a_result = await db.execute(
        select(Assignment).where(
            Assignment.id == assignment_id,
            Assignment.school_id == school_id,
            Assignment.staff_id == staff.id,
            Assignment.is_active.is_(True),
        )
    )
    assignment = a_result.scalar_one_or_none()
    if not assignment:
        raise NotFound("Assignment", str(assignment_id))

    # Fetch all submissions
    result = await db.execute(
        select(AssignmentSubmission)
        .where(
            AssignmentSubmission.assignment_id == assignment_id,
            AssignmentSubmission.is_active.is_(True),
        )
        .order_by(AssignmentSubmission.student_id)
    )
    submissions = list(result.scalars().all())

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Roll Number",
        "Student Name",
        "Submitted At",
        "Status",
        "Marks",
        "Max Marks",
        "Feedback",
    ])

    for sub in submissions:
        student = sub.student
        # Get enrollment for roll number
        enrollment_result = await db.execute(
            select(StudentEnrollment).where(
                StudentEnrollment.student_id == sub.student_id,
                StudentEnrollment.class_section_id == assignment.class_section_id,
                StudentEnrollment.academic_year_id == assignment.academic_year_id,
                StudentEnrollment.is_active.is_(True),
            )
        )
        enrollment = enrollment_result.scalar_one_or_none()
        roll_number = enrollment.roll_number if enrollment else (student.admission_number if student else "")

        writer.writerow([
            roll_number,
            student.full_name if student else "",
            sub.submitted_at.isoformat() if sub.submitted_at else "",
            sub.status,
            float(sub.marks) if sub.marks is not None else "",
            float(assignment.max_marks) if assignment.max_marks else "",
            sub.feedback or "",
        ])

    return output.getvalue()
