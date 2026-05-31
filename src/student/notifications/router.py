from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from src.auth.dependencies import SchoolDep, StudentUser
from src.core.dependencies import PaginationDep, SessionDep
from src.student.notifications import service
from src.student.notifications.schemas import (
    MarkReadResponse,
    StudentNotificationDetailResponse,
    StudentNotificationListResponse,
)

router = APIRouter(prefix="/student/notifications", tags=["Student Notifications"])


# ────────────────────────────────────────────────────────────────────────────────
# List notifications
# ────────────────────────────────────────────────────────────────────────────────


@router.get("", response_model=StudentNotificationListResponse)
async def list_notifications(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
    pagination: PaginationDep,
    type: str | None = Query(default=None),
    is_read: bool | None = Query(default=None),
) -> StudentNotificationListResponse:
    """List own notifications (paginated, filterable by type/is_read)."""
    result = await service.list_notifications(
        db, school.id, user, pagination, type, is_read
    )
    return StudentNotificationListResponse(**result)


# ────────────────────────────────────────────────────────────────────────────────
# Get notification detail
# ────────────────────────────────────────────────────────────────────────────────


@router.get("/{notification_id}", response_model=StudentNotificationDetailResponse)
async def get_notification(
    notification_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
) -> StudentNotificationDetailResponse:
    """Get notification details."""
    result = await service.get_notification(db, school.id, user, notification_id)
    return StudentNotificationDetailResponse(**result)


# ────────────────────────────────────────────────────────────────────────────────
# Mark as read
# ────────────────────────────────────────────────────────────────────────────────


@router.put("/{notification_id}/read", response_model=MarkReadResponse)
async def mark_notification_read(
    notification_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
) -> MarkReadResponse:
    """Mark a notification as read."""
    result = await service.mark_as_read(db, school.id, user, notification_id)
    return MarkReadResponse(**result)
