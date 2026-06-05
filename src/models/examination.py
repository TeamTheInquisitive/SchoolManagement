from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import BaseModel, UUIDType


class Exam(BaseModel):
    """Exam definition for a class-section and subject."""

    __tablename__ = "exams"
    __table_args__ = (
        Index("idx_exams_class_year", "class_section_id", "academic_year_id"),
        Index("idx_exams_subject", "subject_id", "academic_year_id"),
        Index("idx_exams_date", "school_id", "date"),
        Index("idx_exams_status", "school_id", "academic_year_id", "status"),
        Index("idx_exams_type", "school_id", "academic_year_id", "exam_type"),
    )

    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    exam_type: Mapped[str] = mapped_column(String(50), nullable=False)
    class_section_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("class_sections.id"), nullable=False
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("subjects.id"), nullable=False
    )
    date: Mapped[date | None] = mapped_column(Date, default=None)
    start_time: Mapped[str | None] = mapped_column(Time, default=None)
    end_time: Mapped[str | None] = mapped_column(Time, default=None)
    total_marks: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    passing_marks: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), default=None)
    status: Mapped[str] = mapped_column(
        String(20), default="Draft", nullable=False
    )
    examiner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("staff.id"), default=None
    )
    term: Mapped[str | None] = mapped_column(String(20), default=None)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )

    # Relationships
    results: Mapped[list[ExamResult]] = relationship(
        "ExamResult", back_populates="exam", lazy="selectin"
    )
    class_section: Mapped["ClassSection"] = relationship("ClassSection", lazy="selectin")
    subject: Mapped["Subject"] = relationship("Subject", lazy="selectin")
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", lazy="selectin")
    examiner: Mapped["Staff | None"] = relationship(
        "Staff", lazy="selectin", foreign_keys=[examiner_id]
    )


class ExamResult(BaseModel):
    """Individual student result for an exam."""

    __tablename__ = "exam_results"
    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "exam_id",
            "student_id",
            name="uq_exam_results_school_exam_student",
        ),
        Index("idx_exam_results_student", "student_id"),
        Index("idx_exam_results_exam", "exam_id", "rank"),
        Index("idx_exam_results_grade", "exam_id", "grade"),
    )

    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=False,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("students.id"), nullable=False
    )
    marks_obtained: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2), default=None
    )
    grade: Mapped[str | None] = mapped_column(String(10), default=None)
    rank: Mapped[int | None] = mapped_column(Integer, default=None)
    attendance: Mapped[str] = mapped_column(
        String(10), default="Present", nullable=False
    )
    remarks: Mapped[str | None] = mapped_column(Text, default=None)
    is_pass: Mapped[bool | None] = mapped_column(Boolean, default=None)

    # Relationships
    exam: Mapped[Exam] = relationship("Exam", back_populates="results")
    student: Mapped["Student"] = relationship("Student", lazy="selectin")


class GradeSystem(BaseModel):
    """Configurable grade system for a school."""

    __tablename__ = "grade_systems"
    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "name",
            name="uq_grade_systems_school_name",
        ),
    )

    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    scales: Mapped[list[GradeScale]] = relationship(
        "GradeScale", back_populates="grade_system", lazy="selectin"
    )
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", lazy="selectin")


class GradeScale(BaseModel):
    """Individual grade definition within a grade system."""

    __tablename__ = "grade_scales"
    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "grade_system_id",
            "grade",
            name="uq_grade_scales_system_grade",
        ),
        Index("idx_grade_scales_system", "grade_system_id", "sort_order"),
    )

    grade_system_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("grade_systems.id", ondelete="CASCADE"),
        nullable=False,
    )
    grade: Mapped[str] = mapped_column(String(10), nullable=False)
    min_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    max_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    grade_point: Mapped[Decimal | None] = mapped_column(Numeric(3, 1), default=None)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    grade_system: Mapped[GradeSystem] = relationship(
        "GradeSystem", back_populates="scales"
    )


# Type stubs for relationships (avoids circular imports at runtime)
from src.models.academic import ClassSection  # noqa: E402, F401
from src.models.academic import Subject  # noqa: E402, F401
from src.models.core import AcademicYear  # noqa: E402, F401
from src.models.staff import Staff  # noqa: E402, F401
from src.models.student import Student  # noqa: E402, F401
