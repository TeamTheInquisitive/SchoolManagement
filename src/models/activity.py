from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base_model import BaseModel, UUIDType


class Activity(BaseModel):
    """Student extra-curricular activities and club memberships."""

    __tablename__ = "activities"

    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("students.id"), nullable=False
    )
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    achievement: Mapped[str | None] = mapped_column(Text, nullable=True)
    certificate_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("staff.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Active")

    __table_args__ = (
        Index("idx_activities_student", "student_id", "academic_year_id"),
        Index("idx_activities_type", "school_id", "academic_year_id", "activity_type"),
    )
class Award(BaseModel):
    """Student achievements and awards."""

    __tablename__ = "awards"

    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("students.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    awarded_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    awarded_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    certificate_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("staff.id"), nullable=True
    )

    __table_args__ = (
        Index("idx_awards_student", "student_id", "academic_year_id"),
        Index("idx_awards_category", "school_id", "academic_year_id", "category"),
    )
class DisciplinaryRecord(BaseModel):
    """Student disciplinary incidents."""

    __tablename__ = "disciplinary_records"

    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("students.id"), nullable=False
    )
    incident_date: Mapped[date] = mapped_column(Date, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    action_taken: Mapped[str | None] = mapped_column(Text, nullable=True)
    reported_by: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("staff.id"), nullable=True
    )
    parent_notified: Mapped[bool] = mapped_column(nullable=False, default=False)
    parent_notified_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    follow_up_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    follow_up_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Open")

    __table_args__ = (
        Index("idx_disciplinary_student", "student_id", "academic_year_id"),
        Index("idx_disciplinary_date", "school_id", "incident_date"),
        Index("idx_disciplinary_status", "school_id", "academic_year_id", "status"),
    )
