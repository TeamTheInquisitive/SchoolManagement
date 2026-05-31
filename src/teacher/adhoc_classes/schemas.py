from typing import Optional

import uuid
from datetime import date, time, datetime

from pydantic import BaseModel, Field


class AdhocClassCreateRequest(BaseModel):
    """Request schema for creating an adhoc class."""

    class_name: str
    section: str
    subject: str
    date: Optional[date] = None
    start_time: time | None = None
    end_time: time | None = None
    duration_minutes: int | None = None
    type: str = Field(..., description="Extra or Substitute")
    reason: str | None = None
    original_staff_id: uuid.UUID | None = None
    topic: str | None = None
    notes: str | None = None
    description: str | None = None
    student_count: int = 0


class AdhocClassUpdateRequest(BaseModel):
    """Request schema for updating an adhoc class."""

    status: str | None = None
    notes: str | None = None
    student_count: int | None = None
    topic: str | None = None
    duration_minutes: int | None = None


class AdhocClassResponse(BaseModel):
    """Response schema for an adhoc class."""

    id: uuid.UUID
    staff_id: uuid.UUID
    class_name: str
    section: str
    subject: str
    date: Optional[date] = None
    start_time: time | None = None
    end_time: time | None = None
    duration_minutes: int | None = None
    type: str
    reason: str | None = None
    original_staff_id: uuid.UUID | None = None
    topic: str | None = None
    notes: str | None = None
    description: str | None = None
    student_count: int = 0
    status: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class AdhocClassListResponse(BaseModel):
    """Paginated response for adhoc classes."""

    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[AdhocClassResponse]


class AdhocClassDeleteResponse(BaseModel):
    """Response schema for deleting/cancelling an adhoc class."""

    id: uuid.UUID
    status: str
    message: str
