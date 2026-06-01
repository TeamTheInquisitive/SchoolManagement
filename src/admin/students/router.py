from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, File, Query, UploadFile
from fastapi.responses import StreamingResponse

from src.admin.students import service
from src.admin.students.schemas import (
    ActivitiesResponse,
    BulkImportResponse,
    DeleteStudentRequest,
    DisciplinaryRecordsResponse,
    ExamResultsResponse,
    FeeHistoryResponse,
    ParentMeetingsResponse,
    StudentDeleteResponse,
    StudentListResponse,
    StudentResponse,
    CreateStudentRequest,
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
    """Admin sets a temporary password for a student."""
    from sqlalchemy import select as sel
    from src.models.core import User
    from src.core.security import hash_password
    from src.core.exceptions import NotFound

    temp_password = data.get("password", "changeme123") if data else "changeme123"

    result = await db.execute(
        sel(User).where(User.school_id == school.id, User.student_id == student_id, User.is_active.is_(True))
    )
    user_obj = result.scalar_one_or_none()
    if not user_obj:
        raise NotFound("User account for this student")

    user_obj.password_hash = hash_password(temp_password)
    await db.commit()

    return {"message": "Password reset successfully", "temporary_password": temp_password}


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
