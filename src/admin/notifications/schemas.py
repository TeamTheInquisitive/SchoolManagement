
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ────────────────────────────────────────────────────────────────────────────────
# Request schemas
# ────────────────────────────────────────────────────────────────────────────────


class NotificationCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    type: str | None = Field(default=None, max_length=50)
    target_type: Literal[
        "all",
        "students",
        "teaching_staff",
        "non_teaching_staff",
        "parents",
        "specific_class",
    ]
    target_class_name: str | None = Field(default=None, max_length=100)
    target_section: str | None = Field(default=None, max_length=10)
    send_via: str = Field(default="in_app", max_length=20)
    schedule_for_later: bool = False
    scheduled_at: datetime | None = None


class NotificationUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    message: str | None = Field(default=None, min_length=1)
    type: str | None = Field(default=None, max_length=50)
    target_type: Literal[
        "all",
        "students",
        "teaching_staff",
        "non_teaching_staff",
        "parents",
        "specific_class",
    ] | None = None
    target_class_name: str | None = None
    target_section: str | None = None
    send_via: str | None = None
    scheduled_at: datetime | None = None


# ────────────────────────────────────────────────────────────────────────────────
# Response schemas
# ────────────────────────────────────────────────────────────────────────────────


class NotificationItem(BaseModel):
    id: uuid.UUID
    title: str
    message: str
    target: str
    type: str | None = None
    send_via: str
    date: str | None = None
    status: str
    read_rate: str | None = None
    recipients_count: int
    scheduled_at: datetime | None = None


class NotificationSummary(BaseModel):
    total_sent: int
    this_month: int
    scheduled: int
    average_read_rate: int


class NotificationListResponse(BaseModel):
    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[NotificationItem]
    summary: NotificationSummary


class NotificationDetailResponse(BaseModel):
    id: uuid.UUID
    title: str
    message: str
    type: str | None = None
    target: str
    target_type: str
    target_class_name: str | None = None
    target_section: str | None = None
    send_via: str
    date: str | None = None
    status: str
    read_rate: str | None = None
    recipients_count: int
    read_count: int
    scheduled_at: datetime | None = None
    created_by: str | None = None
    created_at: datetime | None = None


class NotificationCreateResponse(BaseModel):
    id: uuid.UUID
    title: str
    message: str
    type: str | None = None
    target_type: str
    target: str
    send_via: str
    status: str
    scheduled_at: datetime | None = None
    recipients_count: int
    created_at: datetime | None = None


class NotificationArchiveResponse(BaseModel):
    id: uuid.UUID
    title: str
    status: str
    archived_on: str | None = None
    message: str
