from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from src.admin.notifications import service
from src.admin.notifications.schemas import (
    NotificationArchiveResponse,
    NotificationCreateRequest,
    NotificationCreateResponse,
    NotificationDetailResponse,
    NotificationListResponse,
    NotificationUpdateRequest,
)
from src.auth.dependencies import AdminUser, SchoolDep
from src.core.dependencies import PaginationDep, SessionDep

router = APIRouter(prefix="/admin/notifications", tags=["Admin Notifications"])


# ────────────────────────────────────────────────────────────────────────────────
# List notifications
# ────────────────────────────────────────────────────────────────────────────────


@router.get("/", response_model=NotificationListResponse)
async def list_notifications(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    pagination: PaginationDep,
    search: str | None = Query(default=None),
    type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    target_type: str | None = Query(default=None),
) -> NotificationListResponse:
    """List notifications with filters and summary KPIs."""
    result = await service.list_notifications(
        db, school.id, pagination, search, type, status, target_type
    )
    return NotificationListResponse(**result)


# ────────────────────────────────────────────────────────────────────────────────
# Create notification
# ────────────────────────────────────────────────────────────────────────────────


@router.post("/", status_code=201, response_model=NotificationCreateResponse)
async def create_notification(
    data: NotificationCreateRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> NotificationCreateResponse:
    """Create and send (or schedule) a notification."""
    result = await service.create_notification(
        db, school.id, data.model_dump(), user.id
    )
    return NotificationCreateResponse(**result)


# ────────────────────────────────────────────────────────────────────────────────
# Get notification detail
# ────────────────────────────────────────────────────────────────────────────────


@router.get("/{notification_id}/", response_model=NotificationDetailResponse)
async def get_notification(
    notification_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> NotificationDetailResponse:
    """Get notification details with delivery stats."""
    result = await service.get_notification(db, school.id, notification_id)
    return NotificationDetailResponse(**result)


# ────────────────────────────────────────────────────────────────────────────────
# Update notification
# ────────────────────────────────────────────────────────────────────────────────


@router.put("/{notification_id}/", response_model=NotificationDetailResponse)
async def update_notification(
    notification_id: uuid.UUID,
    data: NotificationUpdateRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> NotificationDetailResponse:
    """Update a notification (only if Scheduled or Draft)."""
    result = await service.update_notification(
        db, school.id, notification_id, data.model_dump(exclude_unset=True), user.id
    )
    return NotificationDetailResponse(**result)


# ────────────────────────────────────────────────────────────────────────────────
# Archive (delete) notification
# ────────────────────────────────────────────────────────────────────────────────


@router.delete("/{notification_id}/", response_model=NotificationArchiveResponse)
async def delete_notification(
    notification_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> NotificationArchiveResponse:
    """Archive a notification (soft-delete)."""
    result = await service.archive_notification(
        db, school.id, notification_id, user.id
    )
    return NotificationArchiveResponse(**result)
