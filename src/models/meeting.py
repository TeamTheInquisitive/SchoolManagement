from __future__ import annotations

import uuid
from datetime import date, time

from sqlalchemy import Date, ForeignKey, Index, JSON, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base_model import BaseModel, UUIDType


class ParentMeeting(BaseModel):
    """Parent-teacher meetings for students."""

    __tablename__ = "parent_meetings"

    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("students.id"), nullable=False
    )
    meeting_date: Mapped[date] = mapped_column(Date, nullable=False)
    meeting_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    conducted_by: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("staff.id"), nullable=True
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("parents.id"), nullable=True
    )
    attendees: Mapped[dict] = mapped_column(JSON, default=list)
    agenda: Mapped[str | None] = mapped_column(Text, nullable=True)
    discussion_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_items: Mapped[dict] = mapped_column(JSON, default=list)
    next_meeting_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Scheduled"
    )
    meeting_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    follow_up_required: Mapped[bool] = mapped_column(nullable=False, default=False)
    parent_attended: Mapped[bool] = mapped_column(nullable=False, default=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("idx_parent_meetings_student", "student_id", "academic_year_id"),
        Index("idx_parent_meetings_date", "school_id", "meeting_date"),
        Index("idx_parent_meetings_conductor", "conducted_by", "meeting_date"),
        Index("idx_parent_meetings_status", "school_id", "academic_year_id", "status"),
    )
