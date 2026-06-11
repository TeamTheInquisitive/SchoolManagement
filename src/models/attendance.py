from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import BaseModel, UUIDType


class AttendanceSession(BaseModel):
    """One record per attendance-taking event (class + date + who submitted)."""

    __tablename__ = "attendance_sessions"
    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "class_section_id",
            "date",
            "academic_year_id",
            "subject_id",
            "period_number",
            name="uq_attendance_sessions_school_class_date_year_subject_period",
        ),
        Index("idx_attendance_sessions_class_date", "class_section_id", "date"),
        Index("idx_attendance_sessions_date", "school_id", "date"),
        Index("idx_attendance_sessions_submitted_by", "submitted_by", "date"),
        Index("idx_attendance_sessions_subject", "class_section_id", "date", "subject_id"),
    )

    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    class_section_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("class_sections.id"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    subject_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("subjects.id"), nullable=True, default=None
    )
    period_number: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    submitted_by: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("staff.id"), nullable=True, default=None
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default="Submitted", nullable=False
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    cancelled_by: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, default=None
    )

    # Cached counts
    total_present: Mapped[int | None] = mapped_column(Integer, default=None)
    total_absent: Mapped[int | None] = mapped_column(Integer, default=None)
    total_late: Mapped[int | None] = mapped_column(Integer, default=None)

    # Relationships
    records: Mapped[list[AttendanceRecord]] = relationship(
        "AttendanceRecord",
        back_populates="session",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    class_section: Mapped["ClassSection"] = relationship("ClassSection", lazy="selectin")
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", lazy="selectin")
    subject: Mapped["Subject | None"] = relationship("Subject", lazy="selectin")
    staff: Mapped["Staff"] = relationship("Staff", lazy="selectin", foreign_keys=[submitted_by])


class AttendanceRecord(BaseModel):
    """Individual student attendance within a session."""

    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "attendance_session_id",
            "student_id",
            name="uq_attendance_records_session_student",
        ),
        Index("idx_attendance_records_student", "student_id"),
        Index("idx_attendance_records_status", "attendance_session_id", "status"),
    )

    attendance_session_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("attendance_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("students.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(10), nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text, default=None)

    # Relationships
    session: Mapped[AttendanceSession] = relationship(
        "AttendanceSession", back_populates="records"
    )
    student: Mapped["Student"] = relationship("Student", lazy="selectin")


# Type stubs for relationships (avoids circular imports at runtime)
from src.models.academic import ClassSection, Subject  # noqa: E402, F401
from src.models.core import AcademicYear  # noqa: E402, F401
from src.models.staff import Staff  # noqa: E402, F401
from src.models.student import Student  # noqa: E402, F401
