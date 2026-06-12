from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class SentNotificationItem(BaseModel):
    id: uuid.UUID
    title: str
    message: str
    type: str | None = None
    target_type: str | None = None
    target_class_name: str | None = None
    recipients_count: int = 0
    status: str | None = None
    sent_at: datetime | None = None
    is_read: bool = True


class SentNotificationListResponse(BaseModel):
    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[SentNotificationItem]
