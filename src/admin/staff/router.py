from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from src.admin.staff import service
from src.admin.staff.schemas import (
    BulkImportStaffRequest,
    BulkImportStaffResponse,
    CreateStaffRequest,
    DeleteStaffRequest,
    StaffDeleteResponse,
    StaffListResponse,
    StaffResponse,
    UpdateStaffRequest,
)
from src.auth.dependencies import AdminUser, SchoolDep
from src.core.dependencies import PaginationDep, SessionDep

router = APIRouter(prefix="/admin/staff", tags=["Admin Staff"])


@router.get("", response_model=StaffListResponse)
async def list_staff(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    pagination: PaginationDep,
    search: str | None = Query(default=None),
    department: str | None = Query(default=None),
    status: str | None = Query(default=None),
    type: str | None = Query(default=None, alias="type"),
) -> StaffListResponse:
    """List staff members with filters and pagination."""
    result = await service.list_staff(
        db, school.id, pagination, search, department, status, type
    )
    return StaffListResponse(**result)


@router.get("/export")
async def export_staff(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    department: str | None = Query(default=None),
    status: str | None = Query(default=None),
) -> StreamingResponse:
    """Export staff data as CSV."""
    csv_content = await service.export_staff_csv(db, school.id, department, status)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=staff_export.csv"},
    )


@router.post("/bulk-import", response_model=BulkImportStaffResponse)
async def bulk_import_staff(
    data: BulkImportStaffRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> BulkImportStaffResponse:
    """Bulk import staff members via JSON payload."""
    results = []
    passed = 0
    failed = 0
    for idx, staff_item in enumerate(data.staff, start=1):
        try:
            staff_data = staff_item.model_dump(exclude_none=True)
            await service.create_staff(db, school.id, staff_data, user.id)
            await db.commit()
            passed += 1
            results.append({"row": idx, "employee_id": staff_item.employee_id, "success": True})
        except Exception as e:
            await db.rollback()
            failed += 1
            results.append({"row": idx, "employee_id": staff_item.employee_id, "success": False, "error": str(e)})
    return BulkImportStaffResponse(results=results, total=len(data.staff), passed=passed, failed=failed)


@router.post("", response_model=StaffResponse, status_code=201)
async def create_staff(
    data: CreateStaffRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> StaffResponse:
    """Create a new staff member."""
    result = await service.create_staff(
        db, school.id, data.model_dump(exclude_none=True), user.id
    )
    return StaffResponse.model_validate(result)


@router.put("/{staff_id}", response_model=StaffResponse)
async def update_staff(
    staff_id: UUID,
    data: UpdateStaffRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> StaffResponse:
    """Update a staff member."""
    result = await service.update_staff(
        db, school.id, staff_id, data.model_dump(exclude_none=True), user.id
    )
    return StaffResponse.model_validate(result)


@router.delete("/{staff_id}", response_model=StaffDeleteResponse)
async def delete_staff(
    staff_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    data: DeleteStaffRequest | None = None,
) -> StaffDeleteResponse:
    """Soft-delete a staff member (set Inactive)."""
    reason = data.reason if data else None
    left_date_val = data.left_date if data else None
    staff = await service.delete_staff(db, school.id, staff_id, user.id, reason, left_date_val)
    return StaffDeleteResponse(
        id=staff.id,
        employee_id=staff.employee_id,
        full_name=staff.full_name,
        status=staff.status,
        left_date=staff.left_date,
        reason=staff.left_reason,
        message="Staff member deactivated. All records preserved.",
    )
