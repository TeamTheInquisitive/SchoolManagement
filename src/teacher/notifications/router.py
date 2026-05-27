from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from src.auth.dependencies import SchoolDep, TeacherUser
from src.core.dependencies import PaginationDep, SessionDep
from src.teacher.notifications import service
from src.student.notifications.schemas import (
    MarkReadResponse,
    StudentNotificationDetailResponse as NotificationDetailResponse,
    StudentNotificationListResponse as NotificationListResponse,
)

router = APIRouter(prefix="/teacher/notifications", tags=["Teacher Notifications"])


@router.get("/", response_model=NotificationListResponse)
async def list_notifications(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    pagination: PaginationDep,
    type: str | None = Query(default=None),
    is_read: bool | None = Query(default=None),
) -> NotificationListResponse:
    result = await service.list_notifications(db, school.id, user, pagination, type, is_read)
    return NotificationListResponse(**result)


@router.get("/{notification_id}/", response_model=NotificationDetailResponse)
async def get_notification(
    notification_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> NotificationDetailResponse:
    result = await service.get_notification(db, school.id, user, notification_id)
    return NotificationDetailResponse(**result)


@router.put("/{notification_id}/read/", response_model=MarkReadResponse)
async def mark_notification_read(
    notification_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> MarkReadResponse:
    result = await service.mark_as_read(db, school.id, user, notification_id)
    return MarkReadResponse(**result)
