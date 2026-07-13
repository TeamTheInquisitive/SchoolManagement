from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import BaseModel, UUIDType


class Student(BaseModel):
    """Permanent student profile. Enrollment (class/section) is tracked separately per year."""

    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint("school_id", "admission_number", name="uq_students_school_admission"),
        Index("idx_students_name", "school_id", "full_name"),
        Index("idx_students_status", "school_id", "status"),
    )

    # Admission / roll number (unique per school)
    admission_number: Mapped[str] = mapped_column(String(50), nullable=False)

    # Personal info
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(100), default=None)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), default=None)
    phone: Mapped[str | None] = mapped_column(String(20), default=None)
    gender: Mapped[str | None] = mapped_column(String(10), default=None)
    date_of_birth: Mapped[date | None] = mapped_column(Date, default=None)
    photo_url: Mapped[str | None] = mapped_column(Text, default=None)

    # Medical
    blood_group: Mapped[str | None] = mapped_column(String(5), default=None)
    nationality: Mapped[str | None] = mapped_column(String(50), default=None)
    religion: Mapped[str | None] = mapped_column(String(50), default=None)
    caste: Mapped[str | None] = mapped_column(String(50), default=None)
    mother_tongue: Mapped[str | None] = mapped_column(String(50), default=None)
    medical_conditions: Mapped[str | None] = mapped_column(Text, default=None)
    allergies: Mapped[str | None] = mapped_column(Text, default=None)

    # Address
    address_line1: Mapped[str | None] = mapped_column(String(255), default=None)
    address_line2: Mapped[str | None] = mapped_column(String(255), default=None)
    city: Mapped[str | None] = mapped_column(String(100), default=None)
    state: Mapped[str | None] = mapped_column(String(100), default=None)
    pincode: Mapped[str | None] = mapped_column(String(20), default=None)

    # Admission info
    admission_date: Mapped[date | None] = mapped_column(Date, default=None)
    left_date: Mapped[date | None] = mapped_column(Date, default=None)
    left_reason: Mapped[str | None] = mapped_column(Text, default=None)
    previous_school: Mapped[str | None] = mapped_column(String(255), default=None)
    transfer_certificate_number: Mapped[str | None] = mapped_column(String(100), default=None)

    # Student type (day_scholar or hosteller)
    student_type: Mapped[str] = mapped_column(String(20), nullable=False, default="Day Scholar")

    # Status
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Active")

    # ID proof
    aadhar_number: Mapped[str | None] = mapped_column(String(20), default=None)

    # Relationships
    enrollments: Mapped[list[StudentEnrollment]] = relationship(
        "StudentEnrollment", back_populates="student", lazy="selectin"
    )
    student_parents: Mapped[list[StudentParent]] = relationship(
        "StudentParent", back_populates="student", lazy="selectin"
    )
    mentors: Mapped[list[StudentMentor]] = relationship(
        "StudentMentor", back_populates="student", lazy="selectin"
    )
class StudentEnrollment(BaseModel):
    """Tracks which class+section a student is in for each academic year."""

    __tablename__ = "student_enrollments"
    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "academic_year_id",
            "student_id",
            name="uq_student_enrollments_year",
        ),
        Index("idx_student_enrollments_class", "class_section_id", "academic_year_id"),
        Index("idx_student_enrollments_student", "student_id", "academic_year_id"),
    )

    # Foreign keys
    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("students.id"), nullable=False
    )
    class_section_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("class_sections.id"), nullable=False
    )

    # Enrollment details
    roll_number: Mapped[str | None] = mapped_column(String(20), default=None)
    enrollment_date: Mapped[date | None] = mapped_column(Date, default=None)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Active")

    # Relationships
    student: Mapped[Student] = relationship("Student", back_populates="enrollments")
    class_section: Mapped["ClassSection"] = relationship("ClassSection", lazy="selectin")  # noqa: F821
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", lazy="selectin")  # noqa: F821
class Parent(BaseModel):
    """Parent/guardian records linked to students."""

    __tablename__ = "parents"
    __table_args__ = (
        Index("idx_parents_email", "school_id", "email"),
        Index("idx_parents_phone", "school_id", "phone"),
    )

    # Personal info
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(100), default=None)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    relation: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), default=None)
    phone: Mapped[str | None] = mapped_column(String(20), default=None)
    alternate_phone: Mapped[str | None] = mapped_column(String(20), default=None)
    occupation: Mapped[str | None] = mapped_column(String(100), default=None)
    annual_income: Mapped[str | None] = mapped_column(String(50), default=None)

    # Address
    address_line1: Mapped[str | None] = mapped_column(String(255), default=None)
    address_line2: Mapped[str | None] = mapped_column(String(255), default=None)
    city: Mapped[str | None] = mapped_column(String(100), default=None)
    state: Mapped[str | None] = mapped_column(String(100), default=None)
    pincode: Mapped[str | None] = mapped_column(String(20), default=None)

    # ID proof
    aadhar_number: Mapped[str | None] = mapped_column(String(20), default=None)

    # Primary contact flag
    is_primary_contact: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    student_parents: Mapped[list[StudentParent]] = relationship(
        "StudentParent", back_populates="parent", lazy="selectin"
    )
class StudentParent(BaseModel):
    """Many-to-many: a student can have multiple parents/guardians."""

    __tablename__ = "student_parents"
    __table_args__ = (
        UniqueConstraint(
            "school_id", "student_id", "parent_id", name="uq_student_parents"
        ),
        Index("idx_student_parents_student", "student_id"),
        Index("idx_student_parents_parent", "parent_id"),
    )

    # Foreign keys
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("students.id"), nullable=False
    )
    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("parents.id"), nullable=False
    )

    # Relationships
    student: Mapped[Student] = relationship("Student", back_populates="student_parents")
    parent: Mapped[Parent] = relationship("Parent", back_populates="student_parents")
class StudentMentor(BaseModel):
    """Assigns a teacher/staff as mentor to a student for an academic year."""

    __tablename__ = "student_mentors"
    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "academic_year_id",
            "student_id",
            name="uq_student_mentors_year",
        ),
        Index("idx_student_mentors_staff", "staff_id", "academic_year_id"),
    )

    # Foreign keys
    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("students.id"), nullable=False
    )
    staff_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("staff.id"), nullable=False
    )

    # Details
    assigned_date: Mapped[date | None] = mapped_column(Date, default=None)
    notes: Mapped[str | None] = mapped_column(Text, default=None)

    # Relationships
    student: Mapped[Student] = relationship("Student", back_populates="mentors")
    staff: Mapped["Staff"] = relationship("Staff", lazy="selectin")  # noqa: F821
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", lazy="selectin")  # noqa: F821
