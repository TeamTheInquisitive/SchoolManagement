from __future__ import annotations

import os
import uuid
from datetime import date, datetime, timezone

import aiofiles
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.config import settings
from src.core.exceptions import ConflictError, NotFound, ValidationError
from src.core.pagination import PaginationParams, paginate
from src.models.academic import Class, ClassSection, Section, Subject
from src.models.assignment import Assignment, AssignmentSubmission
from src.models.core import AcademicYear, User
from src.models.staff import Staff
from src.models.student import Student, StudentEnrollment


ALLOWED_FILE_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/zip",
    "application/x-zip-compressed",
}
MAX_FILES = 5
MAX_FILE_SIZE_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024


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
) -> StudentEnrollment:
    """Get the student's active enrollment."""
    result = await db.execute(
        select(StudentEnrollment).where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.student_id == student_id,
            StudentEnrollment.academic_year_id == academic_year_id,
            StudentEnrollment.is_active.is_(True),
            StudentEnrollment.status == "Active",
        )
    )
    enrollment = result.scalar_one_or_none()
    if not enrollment:
        raise NotFound("StudentEnrollment")
    return enrollment


def _compute_student_status(submission: AssignmentSubmission, due_date: date) -> str:
    """Compute the student-facing status."""
    if submission.status == "Graded":
        return "graded"
    if submission.status == "Late":
        return "late"
    if submission.status in ("Submitted",):
        return "submitted"
    # Pending
    if due_date < date.today():
        return "overdue"
    return "pending"


def _is_overdue(submission: AssignmentSubmission, due_date: date) -> bool:
    """Check if submission is overdue."""
    if submission.status == "Pending" and due_date < date.today():
        return True
    return False


async def list_assignments(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    pagination: PaginationParams,
    status_filter: str | None = None,
    subject_filter: str | None = None,
    academic_year: str | None = None,
) -> dict:
    """List student's assignments with summary and filtering."""
    student = await _get_student_for_user(db, school_id, user)
    ay = await _get_current_academic_year(db, school_id, academic_year)
    enrollment = await _get_student_enrollment(db, school_id, student.id, ay.id)

    # Get all submissions for this student in this academic year
    base_filter = and_(
        AssignmentSubmission.school_id == school_id,
        AssignmentSubmission.student_id == student.id,
        AssignmentSubmission.is_active.is_(True),
        Assignment.academic_year_id == ay.id,
        Assignment.is_active.is_(True),
    )

    # Get submissions with assignment join for filtering
    query = (
        select(AssignmentSubmission)
        .join(Assignment, AssignmentSubmission.assignment_id == Assignment.id)
        .where(base_filter)
    )

    if subject_filter:
        query = query.join(Subject, Assignment.subject_id == Subject.id).where(
            Subject.name.ilike(f"%{subject_filter}%")
        )

    # Get all for summary calculation
    all_result = await db.execute(
        select(AssignmentSubmission)
        .join(Assignment, AssignmentSubmission.assignment_id == Assignment.id)
        .where(base_filter)
        .options(
            selectinload(AssignmentSubmission.assignment)
            .selectinload(Assignment.subject),
            selectinload(AssignmentSubmission.assignment)
            .selectinload(Assignment.staff),
        )
    )
    all_submissions = list(all_result.scalars().all())

    # Calculate summary
    total = len(all_submissions)
    pending = 0
    overdue = 0
    submitted = 0
    graded = 0
    late = 0

    for sub in all_submissions:
        assignment = sub.assignment
        status = _compute_student_status(sub, assignment.due_date)
        if status == "pending":
            pending += 1
        elif status == "overdue":
            overdue += 1
        elif status == "submitted":
            submitted += 1
        elif status == "graded":
            graded += 1
        elif status == "late":
            late += 1

    # Apply status filter
    if status_filter:
        filtered_submissions = []
        for sub in all_submissions:
            assignment = sub.assignment
            status = _compute_student_status(sub, assignment.due_date)
            if status == status_filter.lower():
                filtered_submissions.append(sub)
            # Handle "pending" also matching "overdue" if user filters by "pending"
        all_submissions = filtered_submissions
        total_filtered = len(all_submissions)
    else:
        total_filtered = total

    # Pagination
    start = pagination.offset
    end = start + pagination.page_size
    page_submissions = all_submissions[start:end]

    items = []
    for sub in page_submissions:
        assignment = sub.assignment
        subject_name = assignment.subject.name if assignment.subject else ""
        staff = assignment.staff
        teacher_name = staff.full_name if staff else ""

        status = _compute_student_status(sub, assignment.due_date)
        is_overdue_flag = _is_overdue(sub, assignment.due_date)

        items.append({
            "id": assignment.id,
            "title": assignment.title,
            "subject": subject_name,
            "teacher": teacher_name,
            "description": assignment.description,
            "assigned_date": assignment.assigned_date,
            "due_date": assignment.due_date,
            "max_marks": float(assignment.max_marks) if assignment.max_marks else None,
            "marks_obtained": float(sub.marks) if sub.marks is not None else None,
            "status": status,
            "is_overdue": is_overdue_flag,
            "metadata": assignment.metadata_ or {},
        })

    paginated = paginate(items, total_filtered, pagination)
    paginated["summary"] = {
        "total": total,
        "pending": pending,
        "overdue": overdue,
        "submitted": submitted,
        "graded": graded,
        "late": late,
    }
    return paginated


async def get_assignment_detail(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    assignment_id: uuid.UUID,
) -> dict:
    """Get detailed assignment information for a student."""
    student = await _get_student_for_user(db, school_id, user)

    # Get the assignment
    a_result = await db.execute(
        select(Assignment).where(
            Assignment.id == assignment_id,
            Assignment.school_id == school_id,
            Assignment.is_active.is_(True),
        ).options(
            selectinload(Assignment.subject),
            selectinload(Assignment.staff),
            selectinload(Assignment.class_section),
        )
    )
    assignment = a_result.scalar_one_or_none()
    if not assignment:
        raise NotFound("Assignment", str(assignment_id))

    # Get the student's submission
    sub_result = await db.execute(
        select(AssignmentSubmission).where(
            AssignmentSubmission.assignment_id == assignment_id,
            AssignmentSubmission.student_id == student.id,
            AssignmentSubmission.is_active.is_(True),
        )
    )
    submission = sub_result.scalar_one_or_none()
    if not submission:
        raise NotFound("Assignment", str(assignment_id))

    # Get class/section info
    cs = assignment.class_section
    cs_result = await db.execute(select(Class).where(Class.id == cs.class_id))
    class_obj = cs_result.scalar_one_or_none()
    sec_result = await db.execute(select(Section).where(Section.id == cs.section_id))
    section_obj = sec_result.scalar_one_or_none()
    class_section_str = f"{class_obj.name}-{section_obj.name}" if class_obj and section_obj else ""

    subject_name = assignment.subject.name if assignment.subject else ""
    staff = assignment.staff
    teacher_name = staff.full_name if staff else ""
    ay = assignment.academic_year

    status = _compute_student_status(submission, assignment.due_date)
    is_overdue_flag = _is_overdue(submission, assignment.due_date)

    # Determine submission status
    if submission.status == "Pending":
        submission_status = "not_submitted"
    elif submission.status in ("Submitted", "Late"):
        submission_status = "submitted"
    elif submission.status == "Graded":
        submission_status = "graded"
    else:
        submission_status = submission.status.lower()

    return {
        "id": assignment.id,
        "title": assignment.title,
        "subject": subject_name,
        "teacher": teacher_name,
        "description": assignment.description,
        "assigned_date": assignment.assigned_date,
        "due_date": assignment.due_date,
        "max_marks": float(assignment.max_marks) if assignment.max_marks else None,
        "marks_obtained": float(submission.marks) if submission.marks is not None else None,
        "status": status,
        "is_overdue": is_overdue_flag,
        "submission_status": submission_status,
        "attachments": [],
        "class_section": class_section_str,
        "academic_year": ay.name if ay else "",
        "created_at": assignment.created_at,
        "updated_at": assignment.updated_at,
        "metadata": assignment.metadata_ or {},
    }


async def submit_assignment(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    assignment_id: uuid.UUID,
    comments: str | None = None,
    files: list | None = None,
) -> dict:
    """Submit an assignment with optional files."""
    student = await _get_student_for_user(db, school_id, user)

    # Get assignment
    a_result = await db.execute(
        select(Assignment).where(
            Assignment.id == assignment_id,
            Assignment.school_id == school_id,
            Assignment.is_active.is_(True),
        )
    )
    assignment = a_result.scalar_one_or_none()
    if not assignment:
        raise NotFound("Assignment", str(assignment_id))

    # Get the student's submission record
    sub_result = await db.execute(
        select(AssignmentSubmission).where(
            AssignmentSubmission.assignment_id == assignment_id,
            AssignmentSubmission.student_id == student.id,
            AssignmentSubmission.is_active.is_(True),
        )
    )
    submission = sub_result.scalar_one_or_none()
    if not submission:
        raise NotFound("Assignment", str(assignment_id))

    # Check if already submitted
    if submission.status in ("Submitted", "Graded", "Late"):
        raise ConflictError(
            "Assignment already submitted. Use resubmit endpoint if allowed.",
            details={"submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None},
        )

    # Validate files
    file_urls = []
    if files:
        if len(files) > MAX_FILES:
            raise ValidationError(
                f"Maximum {MAX_FILES} files allowed per submission",
                details={"max_files": MAX_FILES, "uploaded_count": len(files)},
            )

        upload_dir = os.path.join(
            settings.UPLOAD_DIR,
            "assignments",
            str(assignment_id),
            str(student.id),
        )
        os.makedirs(upload_dir, exist_ok=True)

        for file in files:
            # Check file size
            content = await file.read()
            if len(content) > MAX_FILE_SIZE_BYTES:
                raise ValidationError(
                    f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE_MB}MB",
                    details={
                        "max_size_bytes": MAX_FILE_SIZE_BYTES,
                        "uploaded_size_bytes": len(content),
                        "filename": file.filename,
                    },
                )

            # Check file type
            if file.content_type not in ALLOWED_FILE_TYPES:
                raise ValidationError(
                    "File type not allowed. Accepted: PDF, JPEG, PNG, DOC, DOCX, PPT, PPTX, ZIP",
                    details={
                        "filename": file.filename,
                        "type": file.content_type,
                    },
                )

            # Save file
            file_id = str(uuid.uuid4())
            file_path = os.path.join(upload_dir, f"{file_id}_{file.filename}")
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(content)

            file_urls.append({
                "id": file_id,
                "filename": file.filename,
                "url": f"/api/v1/student/assignments/{assignment_id}/submission/files/{file_id}/",
                "size_bytes": len(content),
                "type": file.content_type,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
            })

    now = datetime.now(timezone.utc)
    is_late = assignment.due_date < date.today()

    submission.status = "Late" if is_late else "Submitted"
    submission.submitted_at = now
    submission.comments = comments
    submission.file_urls = file_urls if file_urls else submission.file_urls
    submission.is_late = is_late
    submission.updated_by = user.id

    await db.commit()
    await db.refresh(submission)

    return {
        "id": submission.id,
        "assignment_id": assignment_id,
        "status": submission.status.lower(),
        "comments": submission.comments,
        "files": file_urls,
        "submitted_at": submission.submitted_at,
        "is_late": submission.is_late,
        "metadata": submission.metadata_ or {},
    }


async def get_submission_detail(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    assignment_id: uuid.UUID,
) -> dict:
    """Get the student's own submission details with grade info."""
    student = await _get_student_for_user(db, school_id, user)

    # Get assignment
    a_result = await db.execute(
        select(Assignment).where(
            Assignment.id == assignment_id,
            Assignment.school_id == school_id,
            Assignment.is_active.is_(True),
        ).options(
            selectinload(Assignment.subject),
            selectinload(Assignment.staff),
        )
    )
    assignment = a_result.scalar_one_or_none()
    if not assignment:
        raise NotFound("Assignment", str(assignment_id))

    # Get submission
    sub_result = await db.execute(
        select(AssignmentSubmission).where(
            AssignmentSubmission.assignment_id == assignment_id,
            AssignmentSubmission.student_id == student.id,
            AssignmentSubmission.is_active.is_(True),
        ).options(
            selectinload(AssignmentSubmission.grader),
        )
    )
    submission = sub_result.scalar_one_or_none()
    if not submission:
        raise NotFound("Submission")

    subject_name = assignment.subject.name if assignment.subject else ""

    # Build grade info if graded
    grade_info = None
    if submission.status == "Graded" and submission.marks is not None:
        max_marks = float(assignment.max_marks) if assignment.max_marks else None
        percentage = None
        if max_marks and max_marks > 0:
            percentage = round(float(submission.marks) / max_marks * 100, 1)

        grader_name = None
        if submission.grader:
            grader_name = submission.grader.full_name

        grade_info = {
            "marks_obtained": float(submission.marks),
            "max_marks": max_marks,
            "percentage": percentage,
            "grade": None,
            "graded_by": grader_name,
            "graded_at": submission.graded_at,
            "feedback": submission.feedback,
        }

    # Build file list
    files = []
    if submission.file_urls:
        for f in submission.file_urls:
            files.append({
                "id": f.get("id", ""),
                "filename": f.get("filename", ""),
                "url": f.get("url", ""),
                "size_bytes": f.get("size_bytes"),
                "type": f.get("type"),
                "uploaded_at": f.get("uploaded_at"),
            })

    return {
        "id": submission.id,
        "assignment_id": assignment_id,
        "assignment_title": assignment.title,
        "subject": subject_name,
        "status": submission.status.lower(),
        "comments": submission.comments,
        "files": files,
        "submitted_at": submission.submitted_at,
        "is_late": submission.is_late,
        "grade": grade_info,
        "metadata": submission.metadata_ or {},
    }
