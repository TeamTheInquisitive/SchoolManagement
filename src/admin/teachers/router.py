from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from src.admin.teachers import service
from src.admin.teachers.schemas import (
    AssignClassRequest,
    AssignmentCreatedResponse,
    AssignmentDeleteResponse,
    BulkAssignRequest,
    BulkAssignResponse,
    BulkImportTeacherRequest,
    BulkImportTeacherResponse,
    CreateTeacherRequest,
    DeleteTeacherRequest,
    RemoveAssignmentRequest,
    TeacherAssignmentsResponse,
    TeacherDeleteResponse,
    TeacherHistoryResponse,
    TeacherListResponse,
    TeacherResponse,
    TeachersByClassResponse,
    UpdateTeacherRequest,
)
from src.auth.dependencies import AdminUser, SchoolDep
from src.core.dependencies import PaginationDep, SessionDep

router = APIRouter(prefix="/admin/teachers", tags=["Admin Teachers"])


# ---------------------------------------------------------------------------
# List & CRUD
# ---------------------------------------------------------------------------


@router.get("", response_model=TeacherListResponse)
async def list_teachers(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    pagination: PaginationDep,
    search: str | None = Query(default=None),
    subject: str | None = Query(default=None),
    class_name: str | None = Query(default=None, alias="class"),
    section: str | None = Query(default=None),
    status: str | None = Query(default=None),
    include_inactive: bool = Query(default=False),
) -> TeacherListResponse:
    """List teachers with filters and pagination."""
    result = await service.list_teachers(
        db, school.id, pagination, search, subject, class_name, section, status, include_inactive
    )
    return TeacherListResponse(**result)


@router.post("", response_model=TeacherResponse, status_code=201)
async def create_teacher(
    data: CreateTeacherRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> TeacherResponse:
    """Create a new teacher (staff + user account + subjects)."""
    result = await service.create_teacher(
        db, school.id, data.model_dump(exclude_none=True), user.id
    )
    return TeacherResponse(**result)


@router.get("/export")
async def export_teachers(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> StreamingResponse:
    """Export teachers as CSV."""
    csv_content = await service.export_teachers_csv(db, school.id)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=teachers_export.csv"},
    )


@router.post("/bulk-import", response_model=BulkImportTeacherResponse)
async def bulk_import_teachers(
    data: BulkImportTeacherRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> BulkImportTeacherResponse:
    """Bulk import teachers via JSON payload."""
    results = []
    passed = 0
    failed = 0
    for idx, teacher in enumerate(data.teachers, start=1):
        try:
            teacher_data = teacher.model_dump(exclude_none=True)
            await service.create_teacher(db, school.id, teacher_data, user.id)
            await db.commit()
            passed += 1
            results.append({"row": idx, "employee_id": teacher.employee_id, "success": True})
        except Exception as e:
            await db.rollback()
            failed += 1
            results.append({"row": idx, "employee_id": teacher.employee_id, "success": False, "error": str(e)})
    return BulkImportTeacherResponse(results=results, total=len(data.teachers), passed=passed, failed=failed)


@router.get("/by-class", response_model=TeachersByClassResponse)
async def get_teachers_by_class(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    class_name: str = Query(alias="class_name"),
    section: str = Query(),
) -> TeachersByClassResponse:
    """Get all teachers assigned to a specific class/section."""
    result = await service.get_teachers_by_class(db, school.id, class_name, section)
    return TeachersByClassResponse(**result)


@router.get("/{teacher_id}", response_model=TeacherResponse)
async def get_teacher(
    teacher_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> TeacherResponse:
    """Get a single teacher's full profile."""
    result = await service.get_teacher(db, school.id, teacher_id)
    return TeacherResponse(**result)


@router.put("/{teacher_id}", response_model=TeacherResponse)
async def update_teacher(
    teacher_id: UUID,
    data: UpdateTeacherRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> TeacherResponse:
    """Update teacher details."""
    result = await service.update_teacher(
        db, school.id, teacher_id, data.model_dump(exclude_none=True), user.id
    )
    return TeacherResponse(**result)


@router.delete("/{teacher_id}", response_model=TeacherDeleteResponse)
async def delete_teacher(
    teacher_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    data: DeleteTeacherRequest | None = None,
) -> TeacherDeleteResponse:
    """Soft-delete a teacher (set Inactive, preserve history)."""
    reason = data.reason if data else None
    left_date_val = data.left_date if data else None
    notes = data.notes if data else None
    staff = await service.delete_teacher(db, school.id, teacher_id, user.id, reason, left_date_val)
    return TeacherDeleteResponse(
        id=staff.id,
        employee_id=staff.employee_id,
        full_name=staff.full_name,
        status=staff.status,
        left_date=staff.left_date,
        reason=staff.left_reason,
        notes=notes,
        message="Teacher deactivated. Historical records preserved.",
    )


# ---------------------------------------------------------------------------
# Reset Password
# ---------------------------------------------------------------------------


@router.post("/{teacher_id}/reset-password")
async def reset_teacher_password(
    teacher_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    data: dict | None = None,
):
    """Admin sets a temporary password for a teacher."""
    from sqlalchemy import select as sel
    from src.models.core import User
    from src.models.staff import Staff
    from src.core.security import hash_password
    from src.core.exceptions import NotFound

    temp_password = data.get("password", "Welcome@123") if data else "Welcome@123"

    # Find user account linked to this staff/teacher
    result = await db.execute(
        sel(User).where(User.school_id == school.id, User.staff_id == teacher_id, User.is_active.is_(True))
    )
    user_obj = result.scalar_one_or_none()
    if not user_obj:
        # Try via email match
        staff_result = await db.execute(sel(Staff).where(Staff.id == teacher_id, Staff.school_id == school.id))
        staff = staff_result.scalar_one_or_none()
        if staff:
            result2 = await db.execute(sel(User).where(User.school_id == school.id, User.email == staff.email, User.is_active.is_(True)))
            user_obj = result2.scalar_one_or_none()
    if not user_obj:
        raise NotFound("User account for this teacher")

    user_obj.password_hash = hash_password(temp_password)
    user_obj.password_changed = False
    await db.commit()

    return {"message": "Password reset successfully", "temporary_password": temp_password}


# ---------------------------------------------------------------------------
# Assignments
# ---------------------------------------------------------------------------


@router.post("/{teacher_id}/assign-class", response_model=AssignmentCreatedResponse, status_code=201)
async def assign_class(
    teacher_id: UUID,
    data: AssignClassRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> AssignmentCreatedResponse:
    """Assign a class-section-subject combination to a teacher."""
    assignment = await service.assign_class(
        db, school.id, teacher_id, data.model_dump(), user.id
    )
    class_name = ""
    section = ""
    if assignment.class_section:
        if assignment.class_section.class_:
            class_name = assignment.class_section.class_.name
        if assignment.class_section.section:
            section = assignment.class_section.section.name

    return AssignmentCreatedResponse(
        id=assignment.id,
        class_name=class_name,
        section=section,
        subject=assignment.subject.name if assignment.subject else "",
        is_class_teacher=assignment.is_class_teacher,
        periods_per_week=assignment.periods_per_week,
    )


@router.post("/{teacher_id}/bulk-assign", response_model=BulkAssignResponse, status_code=201)
async def bulk_assign(
    teacher_id: UUID,
    data: BulkAssignRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> BulkAssignResponse:
    """Assign multiple class-section-subject combinations at once."""
    assignments_data = [a.model_dump() for a in data.assignments]
    result = await service.bulk_assign(db, school.id, teacher_id, assignments_data, user.id)
    return BulkAssignResponse(**result)


@router.get("/{teacher_id}/assignments", response_model=TeacherAssignmentsResponse)
async def get_assignments(
    teacher_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    subject: str | None = Query(default=None),
    class_name: str | None = Query(default=None),
) -> TeacherAssignmentsResponse:
    """List all assignments for a teacher."""
    result = await service.get_assignments(db, school.id, teacher_id, subject, class_name)
    return TeacherAssignmentsResponse(**result)


@router.delete(
    "/{teacher_id}/class-assignment/{assignment_id}/",
    response_model=AssignmentDeleteResponse,
)
async def remove_assignment(
    teacher_id: UUID,
    assignment_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    data: RemoveAssignmentRequest | None = None,
) -> AssignmentDeleteResponse:
    """Soft-remove a class assignment."""
    reason = data.reason if data else None
    end_date_val = data.end_date if data else None
    result = await service.remove_assignment(
        db, school.id, teacher_id, assignment_id, user.id, reason, end_date_val
    )
    return AssignmentDeleteResponse(**result)


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------


@router.get("/{teacher_id}/history", response_model=TeacherHistoryResponse)
async def get_teacher_history(
    teacher_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    academic_year: str | None = Query(default=None),
) -> TeacherHistoryResponse:
    """Get historical records for a teacher."""
    result = await service.get_teacher_history(db, school.id, teacher_id, academic_year)
    return TeacherHistoryResponse(**result)
