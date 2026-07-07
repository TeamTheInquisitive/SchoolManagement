from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Query

from src.admin.leaves import service
from src.admin.leaves.schemas import (
    AllBalancesResponse,
    AllocateLeaveRequest,
    AllocateLeaveResponse,
    ApproveLeaveRequest,
    ApproveLeaveResponse,
    BulkActionRequest,
    BulkActionResponse,
    CalendarResponse,
    CancelLeaveRequest,
    CancelLeaveResponse,
    LeaveApplicationListResponse,
    LeavePolicyResponse,
    RejectLeaveRequest,
    RejectLeaveResponse,
    TeacherLeaveDetailResponse,
    UpdateLeavePolicyRequest,
    UpdateLeavePolicyResponse,
)
from src.auth.dependencies import AdminUser, SchoolDep
from src.core.dependencies import PaginationDep, SessionDep

router = APIRouter(prefix="/admin/leaves", tags=["Admin Leaves"])


@router.get("", response_model=LeaveApplicationListResponse)
async def list_leave_applications(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    pagination: PaginationDep,
    status: str | None = Query(default=None),
    teacher_id: uuid.UUID | None = Query(default=None),
    type: str | None = Query(default=None),
    department: str | None = Query(default=None),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
) -> LeaveApplicationListResponse:
    """List all leave applications with filters."""
    result = await service.list_leave_applications(
        db, school.id, pagination, status, teacher_id, type, department, from_date, to_date
    )
    return LeaveApplicationListResponse(**result)


@router.get("/teacher/{teacher_id}", response_model=TeacherLeaveDetailResponse)
async def get_teacher_leave_detail(
    teacher_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> TeacherLeaveDetailResponse:
    """Get leave balance and history for a specific teacher."""
    result = await service.get_teacher_leave_detail(db, school.id, teacher_id)
    return TeacherLeaveDetailResponse(**result)


@router.get("/balances", response_model=AllBalancesResponse)
async def get_all_balances(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    department: str | None = Query(default=None),
    search: str | None = Query(default=None),
) -> AllBalancesResponse:
    """Get leave balances for all teachers at a glance."""
    result = await service.get_all_balances(db, school.id, department, search)
    return AllBalancesResponse(**result)


@router.get("/policy", response_model=LeavePolicyResponse)
async def get_leave_policy(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> LeavePolicyResponse:
    """Get the leave policy configuration for the current academic year."""
    result = await service.get_leave_policy(db, school.id)
    return LeavePolicyResponse(**result)


@router.put("/policy", response_model=UpdateLeavePolicyResponse)
async def update_leave_policy(
    data: UpdateLeavePolicyRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> UpdateLeavePolicyResponse:
    """Update leave policy for the current academic year."""
    result = await service.update_leave_policy(db, school.id, data.model_dump())
    return UpdateLeavePolicyResponse(**result)


@router.post("/{leave_id}/approve", response_model=ApproveLeaveResponse)
async def approve_leave(
    leave_id: uuid.UUID,
    data: ApproveLeaveRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> ApproveLeaveResponse:
    """Approve a pending leave application."""
    result = await service.approve_leave(
        db, school.id, user, leave_id, data.remarks, data.substitute_teacher_id
    )
    return ApproveLeaveResponse(**result)


@router.post("/{leave_id}/reject", response_model=RejectLeaveResponse)
async def reject_leave(
    leave_id: uuid.UUID,
    data: RejectLeaveRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> RejectLeaveResponse:
    """Reject a pending leave application."""
    result = await service.reject_leave(db, school.id, user, leave_id, data.remarks)
    return RejectLeaveResponse(**result)


@router.post("/{leave_id}/cancel", response_model=CancelLeaveResponse)
async def cancel_leave(
    leave_id: uuid.UUID,
    data: CancelLeaveRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> CancelLeaveResponse:
    """Cancel an approved leave (restores balance)."""
    result = await service.cancel_leave(db, school.id, user, leave_id, data.reason)
    return CancelLeaveResponse(**result)


@router.post("/bulk-action", response_model=BulkActionResponse)
async def bulk_action(
    data: BulkActionRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> BulkActionResponse:
    """Bulk approve or reject leave applications."""
    result = await service.bulk_action(
        db, school.id, user, data.action, data.leave_ids, data.remarks
    )
    return BulkActionResponse(**result)


@router.get("/calendar", response_model=CalendarResponse)
async def get_calendar(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    from_date: date = Query(...),
    to_date: date = Query(...),
    department: str | None = Query(default=None),
) -> CalendarResponse:
    """Get calendar view showing who is on leave for a date range."""
    result = await service.get_calendar(db, school.id, from_date, to_date, department)
    return CalendarResponse(**result)


@router.post("/allocate", response_model=AllocateLeaveResponse)
async def allocate_leaves(
    data: AllocateLeaveRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> AllocateLeaveResponse:
    """Allocate leave balances to selected teachers."""
    result = await service.allocate_leaves(db, school.id, data.model_dump())
    return AllocateLeaveResponse(**result)
