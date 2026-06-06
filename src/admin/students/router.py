from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, File, Query, UploadFile
from fastapi.responses import StreamingResponse

from src.admin.students import service
from src.admin.students.schemas import (
    ActivitiesResponse,
    BulkImportJsonRequest,
    BulkImportJsonResponse,
    BulkImportResponse,
    CreateActivityRequest,
    CreateAwardRequest,
    CreateDisciplinaryRequest,
    CreateParentMeetingRequest,
    DeleteStudentRequest,
    DisciplinaryRecordsResponse,
    ExamResultsResponse,
    FeeHistoryResponse,
    ParentMeetingsResponse,
    StudentDeleteResponse,
    StudentListResponse,
    StudentResponse,
    CreateStudentRequest,
    UpdateActivityRequest,
    UpdateAwardRequest,
    UpdateDisciplinaryRequest,
    UpdateParentMeetingRequest,
    UpdateStudentRequest,
)
from src.auth.dependencies import AdminUser, SchoolDep
from src.core.dependencies import PaginationDep, SessionDep

router = APIRouter(prefix="/admin/students", tags=["Admin Students"])


# ---------------------------------------------------------------------------
# List & CRUD
# ---------------------------------------------------------------------------


@router.get("", response_model=StudentListResponse)
async def list_students(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    pagination: PaginationDep,
    search: str | None = Query(default=None),
    class_name: str | None = Query(default=None),
    section: str | None = Query(default=None),
    status: str | None = Query(default=None),
    gender: str | None = Query(default=None),
) -> StudentListResponse:
    """List students with filters and pagination."""
    result = await service.list_students(
        db, school.id, pagination, search, class_name, section, status, gender
    )
    return StudentListResponse(**result)


@router.post("", response_model=StudentResponse, status_code=201)
async def create_student(
    data: CreateStudentRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> StudentResponse:
    """Create a new student (+ optional user account + enrollment)."""
    result = await service.create_student(db, school.id, data.model_dump(exclude_none=True), user.id)
    return StudentResponse(**result)


@router.get("/export")
async def export_students(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    class_name: str | None = Query(default=None),
    section: str | None = Query(default=None),
    status: str | None = Query(default=None),
) -> StreamingResponse:
    """Export students as CSV."""
    csv_content = await service.export_students_csv(db, school.id, class_name, section, status)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=students_export.csv"},
    )


@router.post("/bulk-import", response_model=BulkImportResponse)
async def bulk_import_students(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    file: UploadFile = File(...),
) -> BulkImportResponse:
    """Bulk import students via CSV file."""
    content = await file.read()
    csv_content = content.decode("utf-8")
    result = await service.bulk_import_students(db, school.id, csv_content, user.id)
    return BulkImportResponse(**result)


@router.post("/bulk-import-json", response_model=BulkImportJsonResponse)
async def bulk_import_students_json(
    data: BulkImportJsonRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> BulkImportJsonResponse:
    """Bulk import students via JSON payload."""
    results = []
    passed = 0
    failed = 0
    for idx, student in enumerate(data.students, start=1):
        try:
            await service.create_student(db, school.id, student.model_dump(exclude_none=True), user.id)
            await db.commit()
            passed += 1
            results.append({"row": idx, "roll_number": student.roll_number, "success": True})
        except Exception as e:
            await db.rollback()
            failed += 1
            results.append({"row": idx, "roll_number": student.roll_number, "success": False, "error": str(e)})
    return BulkImportJsonResponse(results=results, total=len(data.students), passed=passed, failed=failed)


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> StudentResponse:
    """Get a single student's full details."""
    result = await service.get_student(db, school.id, student_id)
    return StudentResponse(**result)


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: UUID,
    data: UpdateStudentRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> StudentResponse:
    """Update student details."""
    result = await service.update_student(
        db, school.id, student_id, data.model_dump(exclude_none=True), user.id
    )
    return StudentResponse(**result)


@router.delete("/{student_id}", response_model=StudentDeleteResponse)
async def delete_student(
    student_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    data: DeleteStudentRequest | None = None,
) -> StudentDeleteResponse:
    """Soft-delete student (set status to Inactive/Alumni)."""
    status_val = data.status if data else "Inactive"
    reason = data.reason if data else None
    student = await service.delete_student(db, school.id, student_id, user.id, status_val, reason)
    return StudentDeleteResponse(
        id=student.id,
        roll_number=student.admission_number,
        full_name=student.full_name,
        status=student.status,
        reason=student.left_reason,
        deactivated_on=student.left_date,
        message="Student deactivated. All records preserved.",
    )


# ---------------------------------------------------------------------------
# Reset Password
# ---------------------------------------------------------------------------


@router.post("/{student_id}/reset-password")
async def reset_student_password(
    student_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    data: dict | None = None,
):
    """Admin sets a temporary password for a student. Creates user account if none exists."""
    from sqlalchemy import select as sel
    from src.models.core import User
    from src.models.student import Student
    from src.core.security import hash_password
    from src.core.exceptions import NotFound

    temp_password = data.get("password", "changeme123") if data else "changeme123"
    temp_email = data.get("email") if data else None

    result = await db.execute(
        sel(User).where(User.school_id == school.id, User.student_id == student_id, User.is_active.is_(True))
    )
    user_obj = result.scalar_one_or_none()

    if not user_obj:
        # Create user account for this student
        student_result = await db.execute(sel(Student).where(Student.id == student_id, Student.school_id == school.id))
        student_obj = student_result.scalar_one_or_none()
        if not student_obj:
            raise NotFound("Student")
        email = temp_email or student_obj.email or f"{student_obj.admission_number}@{school.code}.com"
        user_obj = User(
            school_id=school.id,
            email=email,
            password_hash=hash_password(temp_password),
            full_name=student_obj.full_name,
            role="student",
            student_id=student_id,
        )
        db.add(user_obj)
    else:
        user_obj.password_hash = hash_password(temp_password)
        user_obj.password_changed = False

    await db.commit()

    return {"message": "Password reset successfully", "temporary_password": temp_password, "email": user_obj.email}


# ---------------------------------------------------------------------------
# Sub-resource endpoints
# ---------------------------------------------------------------------------


@router.get("/{student_id}/exam-results", response_model=ExamResultsResponse)
async def get_exam_results(
    student_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    academic_year: str | None = Query(default=None),
) -> ExamResultsResponse:
    """Get student exam results."""
    result = await service.get_exam_results(db, school.id, student_id, academic_year)
    return ExamResultsResponse(**result)


@router.get("/{student_id}/parent-meetings", response_model=ParentMeetingsResponse)
async def get_parent_meetings(
    student_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> ParentMeetingsResponse:
    """Get parent meeting history."""
    result = await service.get_parent_meetings(db, school.id, student_id)
    return ParentMeetingsResponse(**result)


@router.post("/{student_id}/parent-meetings", status_code=201)
async def create_parent_meeting(
    student_id: UUID,
    data: CreateParentMeetingRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Create a parent meeting."""
    return await service.create_parent_meeting(db, school.id, student_id, data.model_dump(exclude_none=True), user.id)


@router.put("/{student_id}/parent-meetings/{meeting_id}")
async def update_parent_meeting(
    student_id: UUID,
    meeting_id: UUID,
    data: UpdateParentMeetingRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Update a parent meeting."""
    return await service.update_parent_meeting(db, school.id, student_id, meeting_id, data.model_dump(exclude_none=True))


@router.delete("/{student_id}/parent-meetings/{meeting_id}", status_code=204)
async def delete_parent_meeting(
    student_id: UUID,
    meeting_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Delete a parent meeting."""
    await service.delete_parent_meeting(db, school.id, student_id, meeting_id)


@router.get("/{student_id}/activities", response_model=ActivitiesResponse)
async def get_activities(
    student_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> ActivitiesResponse:
    """Get extra-curricular activities and awards."""
    result = await service.get_activities(db, school.id, student_id)
    return ActivitiesResponse(**result)


@router.post("/{student_id}/activities", status_code=201)
async def create_activity(
    student_id: UUID,
    data: CreateActivityRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Create an activity for a student."""
    return await service.create_activity(db, school.id, student_id, data.model_dump(exclude_none=True), user.id)


@router.put("/{student_id}/activities/{activity_id}")
async def update_activity(
    student_id: UUID,
    activity_id: UUID,
    data: UpdateActivityRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Update an activity."""
    return await service.update_activity(db, school.id, student_id, activity_id, data.model_dump(exclude_none=True))


@router.delete("/{student_id}/activities/{activity_id}", status_code=204)
async def delete_activity(
    student_id: UUID,
    activity_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Delete an activity."""
    await service.delete_activity(db, school.id, student_id, activity_id)


@router.post("/{student_id}/awards", status_code=201)
async def create_award(
    student_id: UUID,
    data: CreateAwardRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Create an award for a student."""
    return await service.create_award(db, school.id, student_id, data.model_dump(exclude_none=True), user.id)


@router.put("/{student_id}/awards/{award_id}")
async def update_award(
    student_id: UUID,
    award_id: UUID,
    data: UpdateAwardRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Update an award."""
    return await service.update_award(db, school.id, student_id, award_id, data.model_dump(exclude_none=True))


@router.delete("/{student_id}/awards/{award_id}", status_code=204)
async def delete_award(
    student_id: UUID,
    award_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Delete an award."""
    await service.delete_award(db, school.id, student_id, award_id)


@router.get("/{student_id}/fee-history", response_model=FeeHistoryResponse)
async def get_fee_history(
    student_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> FeeHistoryResponse:
    """Get fee structure and payments."""
    result = await service.get_fee_history(db, school.id, student_id)
    return FeeHistoryResponse(**result)


@router.get("/{student_id}/disciplinary-records", response_model=DisciplinaryRecordsResponse)
async def get_disciplinary_records(
    student_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> DisciplinaryRecordsResponse:
    """Get disciplinary records."""
    result = await service.get_disciplinary_records(db, school.id, student_id)
    return DisciplinaryRecordsResponse(**result)


@router.post("/{student_id}/disciplinary-records", status_code=201)
async def create_disciplinary_record(
    student_id: UUID,
    data: CreateDisciplinaryRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Create a disciplinary record."""
    return await service.create_disciplinary_record(db, school.id, student_id, data.model_dump(exclude_none=True), user.id)


@router.put("/{student_id}/disciplinary-records/{record_id}")
async def update_disciplinary_record(
    student_id: UUID,
    record_id: UUID,
    data: UpdateDisciplinaryRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Update a disciplinary record."""
    return await service.update_disciplinary_record(db, school.id, student_id, record_id, data.model_dump(exclude_none=True))


@router.delete("/{student_id}/disciplinary-records/{record_id}", status_code=204)
async def delete_disciplinary_record(
    student_id: UUID,
    record_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Delete a disciplinary record."""
    await service.delete_disciplinary_record(db, school.id, student_id, record_id)


# ---------------------------------------------------------------------------
# Attendance Calendar
# ---------------------------------------------------------------------------


@router.get("/{student_id}/attendance")
async def get_student_attendance(
    student_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    month: int = Query(default=None),
    year: int = Query(default=None),
):
    """Get attendance records for a student for a given month."""
    from datetime import date as _date
    today = _date.today()
    m = month or today.month
    y = year or today.year
    return await service.get_student_attendance(db, school.id, student_id, m, y)
