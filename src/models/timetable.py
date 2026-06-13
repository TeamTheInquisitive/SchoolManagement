from __future__ import annotations

import uuid
from datetime import time

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import BaseModel, UUIDType


class PeriodConfig(BaseModel):
    """Defines the period structure (time slots) for a school's timetable.

    Periods are school-wide: the same time grid applies to all days.
    Day-specific assignments live in TimetableSlot.
    """

    __tablename__ = "period_configs"
    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "academic_year_id",
            "start_time",
            name="uq_period_configs_unique",
        ),
        Index("idx_period_configs_year", "school_id", "academic_year_id"),
        CheckConstraint("end_time > start_time", name="chk_period_configs_time"),
    )

    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    name: Mapped[str | None] = mapped_column(String(50), default=None)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, default=None)
    is_break: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", lazy="selectin")
    timetable_slots: Mapped[list["TimetableSlot"]] = relationship(
        "TimetableSlot", back_populates="period_config", lazy="selectin"
    )
class TimetableSlot(BaseModel):
    """Actual timetable assignment: day + period + class-section = subject + teacher."""

    __tablename__ = "timetable_slots"
    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "academic_year_id",
            "class_section_id",
            "period_config_id",
            "day_of_week",
            name="uq_timetable_slots_class",
        ),
        Index("idx_timetable_slots_teacher", "staff_id", "academic_year_id", "day_of_week"),
        Index("idx_timetable_slots_class_day", "class_section_id", "academic_year_id", "day_of_week"),
    )

    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    class_section_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("class_sections.id"), nullable=False
    )
    period_config_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("period_configs.id"), nullable=False
    )
    day_of_week: Mapped[str] = mapped_column(String(10), nullable=False)
    subject_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("subjects.id"), default=None
    )
    staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("staff.id"), default=None
    )
    slot_type: Mapped[str] = mapped_column(String(50), default="Subject", nullable=False)

    # Relationships
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", lazy="selectin")
    class_section: Mapped["ClassSection"] = relationship("ClassSection", lazy="selectin")
    period_config: Mapped["PeriodConfig"] = relationship(
        "PeriodConfig", back_populates="timetable_slots", lazy="selectin"
    )
    subject: Mapped["Subject | None"] = relationship("Subject", lazy="selectin")
    staff: Mapped["Staff | None"] = relationship("Staff", lazy="selectin")
# Type stubs for relationships (avoids circular imports at runtime)
from src.models.academic import ClassSection, Subject  # noqa: E402, F401
from src.models.core import AcademicYear  # noqa: E402, F401
from src.models.staff import Staff  # noqa: E402, F401
