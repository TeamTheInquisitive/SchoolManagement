from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import BaseModel, UUIDType


class Assignment(BaseModel):
    """Assignment created by a teacher for a class-section."""

    __tablename__ = "assignments"
    __table_args__ = (
        Index("idx_assignments_class", "class_section_id", "academic_year_id"),
        Index("idx_assignments_teacher", "staff_id", "academic_year_id"),
        Index("idx_assignments_due", "school_id", "due_date"),
        Index("idx_assignments_status", "school_id", "academic_year_id", "status"),
    )

    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    class_section_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("class_sections.id"), nullable=False
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("subjects.id"), nullable=False
    )
    staff_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("staff.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    max_marks: Mapped[float | None] = mapped_column(Numeric(6, 2), default=None)
    status: Mapped[str] = mapped_column(
        String(20), default="Active", nullable=False
    )
    assigned_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    submissions: Mapped[list[AssignmentSubmission]] = relationship(
        "AssignmentSubmission",
        back_populates="assignment",
        lazy="selectin",
    )
    class_section: Mapped["ClassSection"] = relationship("ClassSection", lazy="selectin")
    subject: Mapped["Subject"] = relationship("Subject", lazy="selectin")
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", lazy="selectin")
    staff: Mapped["Staff"] = relationship("Staff", lazy="selectin")


class AssignmentSubmission(BaseModel):
    """Individual student submission for an assignment."""

    __tablename__ = "assignment_submissions"
    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "assignment_id",
            "student_id",
            name="uq_assignment_submissions_school_assignment_student",
        ),
        Index("idx_assignment_submissions_assignment", "assignment_id", "status"),
        Index("idx_assignment_submissions_student", "student_id"),
    )

    assignment_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("assignments.id", ondelete="CASCADE"),
        nullable=False,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("students.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default="Pending", nullable=False
    )
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    comments: Mapped[str | None] = mapped_column(Text, default=None)
    file_urls: Mapped[list | None] = mapped_column(JSON, default=list)
    marks: Mapped[float | None] = mapped_column(Numeric(6, 2), default=None)
    feedback: Mapped[str | None] = mapped_column(Text, default=None)
    graded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    graded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("staff.id"), default=None
    )
    is_late: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    assignment: Mapped[Assignment] = relationship(
        "Assignment", back_populates="submissions", lazy="selectin"
    )
    student: Mapped["Student"] = relationship("Student", lazy="selectin")
    grader: Mapped["Staff | None"] = relationship(
        "Staff", lazy="selectin", foreign_keys=[graded_by]
    )


# Type stubs for relationships (avoids circular imports at runtime)
from src.models.academic import ClassSection  # noqa: E402, F401
from src.models.core import AcademicYear  # noqa: E402, F401
from src.models.staff import Staff  # noqa: E402, F401
from src.models.student import Student  # noqa: E402, F401
from src.models.academic import Subject  # noqa: E402, F401
