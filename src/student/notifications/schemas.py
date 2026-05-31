from typing import Optional

import uuid
from datetime import datetime

from pydantic import BaseModel


# ────────────────────────────────────────────────────────────────────────────────
# Response schemas
# ────────────────────────────────────────────────────────────────────────────────


class StudentNotificationItem(BaseModel):
    id: uuid.UUID
    notification_id: uuid.UUID
    title: str
    message: str
    type: str | None = None
    is_read: bool
    read_at: datetime | None = None
    sent_at: datetime | None = None
    created_at: datetime | None = None


class StudentNotificationListResponse(BaseModel):
    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[StudentNotificationItem]
    unread_count: int


class StudentNotificationDetailResponse(BaseModel):
    id: uuid.UUID
    notification_id: uuid.UUID
    title: str
    message: str
    type: str | None = None
    send_via: str | None = None
    is_read: bool
    read_at: datetime | None = None
    sent_at: datetime | None = None
    created_at: datetime | None = None


class MarkReadResponse(BaseModel):
    id: uuid.UUID
    is_read: bool
    read_at: datetime | None = None
    message: str
