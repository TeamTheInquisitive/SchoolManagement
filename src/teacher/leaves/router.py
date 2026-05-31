from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from src.auth.dependencies import SchoolDep, TeacherUser
from src.core.dependencies import PaginationDep, SessionDep
from src.teacher.leaves import service
from src.teacher.leaves.schemas import (
    ApplyLeaveRequest,
    ApplyLeaveResponse,
    CancelLeaveResponse,
    LeaveBalanceResponse,
    LeaveDetailResponse,
    LeaveHistoryResponse,
    UpcomingLeavesResponse,
)

router = APIRouter(prefix="/teacher/leaves", tags=["Teacher Leaves"])


@router.get("/balance", response_model=LeaveBalanceResponse)
async def get_leave_balance(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> LeaveBalanceResponse:
    """Get the authenticated teacher's leave balance."""
    result = await service.get_leave_balance(db, school.id, user)
    return LeaveBalanceResponse(**result)


@router.get("/upcoming", response_model=UpcomingLeavesResponse)
async def get_upcoming_leaves(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> UpcomingLeavesResponse:
    """Get upcoming/planned leaves (future dates)."""
    result = await service.get_upcoming_leaves(db, school.id, user)
    return UpcomingLeavesResponse(**result)


@router.get("", response_model=LeaveHistoryResponse)
async def get_leave_history(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    pagination: PaginationDep,
    status: str | None = Query(default=None),
    leave_type: str | None = Query(default=None),
) -> LeaveHistoryResponse:
    """Get leave history for the authenticated teacher."""
    result = await service.get_leave_history(
        db, school.id, user, pagination, status, leave_type
    )
    return LeaveHistoryResponse(**result)


@router.post("", response_model=ApplyLeaveResponse, status_code=201)
async def apply_leave(
    data: ApplyLeaveRequest,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> ApplyLeaveResponse:
    """Apply for leave."""
    result = await service.apply_leave(db, school.id, user, data.model_dump())
    return ApplyLeaveResponse(**result)


@router.get("/{leave_id}", response_model=LeaveDetailResponse)
async def get_leave_detail(
    leave_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> LeaveDetailResponse:
    """Get details of a specific leave application."""
    result = await service.get_leave_detail(db, school.id, user, leave_id)
    return LeaveDetailResponse(**result)


@router.delete("/{leave_id}", response_model=CancelLeaveResponse)
async def cancel_leave(
    leave_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> CancelLeaveResponse:
    """Cancel a pending leave application."""
    result = await service.cancel_leave(db, school.id, user, leave_id)
    return CancelLeaveResponse(**result)
