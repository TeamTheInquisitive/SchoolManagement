from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import BaseModel, UUIDType


class Staff(BaseModel):
    """Staff member (all employees). Teacher is Staff with is_teacher=True."""

    __tablename__ = "staff"
    __table_args__ = (
        UniqueConstraint("school_id", "employee_id", name="uq_staff_school_employee_id"),
        UniqueConstraint("school_id", "email", name="uq_staff_school_email"),
        Index("idx_staff_is_teacher", "school_id", "is_teacher"),
        Index("idx_staff_department", "school_id", "department"),
        Index("idx_staff_name", "school_id", "full_name"),
        Index("idx_staff_status", "school_id", "status"),
    )

    # Human-readable ID (e.g. EMP001)
    employee_id: Mapped[str] = mapped_column(String(50), nullable=False)

    # Personal info
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(100), default=None)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), default=None)
    alternate_phone: Mapped[str | None] = mapped_column(String(20), default=None)
    gender: Mapped[str | None] = mapped_column(String(10), default=None)
    date_of_birth: Mapped[date | None] = mapped_column(Date, default=None)
    photo_url: Mapped[str | None] = mapped_column(Text, default=None)

    # Employment info
    department: Mapped[str | None] = mapped_column(String(100), default=None)
    designation: Mapped[str | None] = mapped_column(String(100), default=None)
    employment_type: Mapped[str | None] = mapped_column(String(50), default=None)
    joining_date: Mapped[date | None] = mapped_column(Date, default=None)
    left_date: Mapped[date | None] = mapped_column(Date, default=None)
    left_reason: Mapped[str | None] = mapped_column(Text, default=None)

    # Qualifications & experience
    qualification: Mapped[str | None] = mapped_column(String(255), default=None)
    experience_years: Mapped[Decimal | None] = mapped_column(Numeric(4, 1), default=None)

    # Address
    address_line1: Mapped[str | None] = mapped_column(String(255), default=None)
    address_line2: Mapped[str | None] = mapped_column(String(255), default=None)
    city: Mapped[str | None] = mapped_column(String(100), default=None)
    state: Mapped[str | None] = mapped_column(String(100), default=None)
    pincode: Mapped[str | None] = mapped_column(String(20), default=None)

    # Medical / emergency
    blood_group: Mapped[str | None] = mapped_column(String(5), default=None)
    emergency_contact_name: Mapped[str | None] = mapped_column(String(255), default=None)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(20), default=None)

    # Banking
    bank_name: Mapped[str | None] = mapped_column(String(100), default=None)
    bank_account_number: Mapped[str | None] = mapped_column(String(50), default=None)
    bank_ifsc: Mapped[str | None] = mapped_column(String(20), default=None)
    pan_number: Mapped[str | None] = mapped_column(String(20), default=None)
    aadhar_number: Mapped[str | None] = mapped_column(String(20), default=None)

    # Teacher-specific
    is_teacher: Mapped[bool] = mapped_column(Boolean, default=False)
    primary_subject_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, default=None
    )
    max_workload_hours: Mapped[int | None] = mapped_column(default=None)

    # Salary (base info stored here; detailed structure in payroll)
    salary: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), default=None)

    # Status
    status: Mapped[str] = mapped_column(String(20), default="Active", nullable=False)

    # FK to users (nullable -- user account may not be created yet)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("users.id", use_alter=True), default=None
    )

    # Relationships
    subjects: Mapped[list[StaffSubject]] = relationship(
        "StaffSubject", back_populates="staff", lazy="selectin", cascade="all, delete-orphan"
    )
    class_assignments: Mapped[list[ClassAssignment]] = relationship(
        "ClassAssignment", back_populates="staff", lazy="selectin"
    )


class StaffSubject(BaseModel):
    """Many-to-many: staff qualified to teach subjects."""

    __tablename__ = "staff_subjects"
    __table_args__ = (
        UniqueConstraint(
            "school_id", "staff_id", "subject_id", name="uq_staff_subjects_staff_subject"
        ),
        Index("idx_staff_subjects_staff", "staff_id"),
    )

    staff_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("staff.id", ondelete="CASCADE"), nullable=False
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("subjects.id"), nullable=False
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    staff: Mapped[Staff] = relationship("Staff", back_populates="subjects")
    subject: Mapped["Subject"] = relationship("Subject", lazy="selectin")


class ClassAssignment(BaseModel):
    """Maps a teacher to a class-section-subject for an academic year."""

    __tablename__ = "class_assignments"
    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "staff_id",
            "class_section_id",
            "subject_id",
            "academic_year_id",
            name="uq_class_assignments_unique",
        ),
        Index("idx_class_assignments_staff", "staff_id", "academic_year_id"),
        Index("idx_class_assignments_class_section", "class_section_id", "academic_year_id"),
    )

    staff_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("staff.id"), nullable=False
    )
    class_section_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("class_sections.id"), nullable=False
    )
    subject_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("subjects.id"), nullable=True, default=None
    )
    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )

    is_class_teacher: Mapped[bool] = mapped_column(Boolean, default=False)
    periods_per_week: Mapped[int | None] = mapped_column(default=None)
    status: Mapped[str] = mapped_column(String(20), default="Active", nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, default=None)
    end_reason: Mapped[str | None] = mapped_column(Text, default=None)

    # Relationships
    staff: Mapped[Staff] = relationship("Staff", back_populates="class_assignments")
    class_section: Mapped["ClassSection"] = relationship("ClassSection", lazy="selectin")
    subject: Mapped["Subject"] = relationship("Subject", lazy="selectin")
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", lazy="selectin")


# Type stubs for relationships (avoids circular imports at runtime)
from src.models.academic import ClassSection, Subject  # noqa: E402, F401
from src.models.core import AcademicYear  # noqa: E402, F401
