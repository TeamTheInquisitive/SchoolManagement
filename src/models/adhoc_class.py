from __future__ import annotations

import uuid
from datetime import date, time

from sqlalchemy import Date, ForeignKey, Index, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base_model import BaseModel, UUIDType


class AdhocClass(BaseModel):
    """Substitute/extra classes logged by teachers."""

    __tablename__ = "adhoc_classes"

    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    staff_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("staff.id"), nullable=False
    )
    class_section_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("class_sections.id"), nullable=False
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("subjects.id"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(nullable=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("staff.id"), nullable=True
    )
    topic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    student_count: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Scheduled"
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("idx_adhoc_classes_staff", "staff_id", "date"),
        Index("idx_adhoc_classes_class", "class_section_id", "date"),
        Index("idx_adhoc_classes_date", "school_id", "date"),
        Index("idx_adhoc_classes_status", "school_id", "academic_year_id", "status"),
    )
