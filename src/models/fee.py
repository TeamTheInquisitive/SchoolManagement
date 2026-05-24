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
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import BaseModel, UUIDType


class FeeStructure(BaseModel):
    """Fee structure definition per class per academic year."""

    __tablename__ = "fee_structures"
    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "academic_year_id",
            "class_section_id",
            "fee_type",
            name="uq_fee_structures_year_class_type",
        ),
        Index("idx_fee_structures_class", "class_section_id", "academic_year_id"),
        Index("idx_fee_structures_year", "school_id", "academic_year_id"),
    )

    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    class_section_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("class_sections.id"), default=None
    )
    fee_type: Mapped[str] = mapped_column(String(50), nullable=False)
    fee_category: Mapped[str] = mapped_column(
        String(20), nullable=False, default="academic"
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    frequency: Mapped[str] = mapped_column(String(30), nullable=False)

    # Relationships
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", lazy="selectin")
    class_section: Mapped["ClassSection | None"] = relationship(
        "ClassSection", lazy="selectin"
    )


class FeeRecord(BaseModel):
    """Individual fee charge assigned to a student."""

    __tablename__ = "fee_records"
    __table_args__ = (
        Index("idx_fee_records_student", "student_id", "academic_year_id"),
        Index("idx_fee_records_status", "school_id", "academic_year_id", "status"),
        Index("idx_fee_records_due_date", "school_id", "due_date"),
        Index("idx_fee_records_fee_type", "school_id", "academic_year_id", "fee_type"),
    )

    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("students.id"), nullable=False
    )
    fee_structure_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("fee_structures.id"), default=None
    )
    fee_type: Mapped[str] = mapped_column(String(50), nullable=False)
    fee_category: Mapped[str] = mapped_column(
        String(20), nullable=False, default="academic"
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    paid: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    pending: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_late_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=0, nullable=False
    )
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="Pending", nullable=False
    )
    description: Mapped[str | None] = mapped_column(String(255), default=None)

    # Relationships
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", lazy="selectin")
    student: Mapped["Student"] = relationship("Student", lazy="selectin")
    fee_structure: Mapped["FeeStructure | None"] = relationship(
        "FeeStructure", lazy="selectin"
    )
    payments: Mapped[list["FeePayment"]] = relationship(
        "FeePayment", back_populates="fee_record", lazy="selectin"
    )
    penalties: Mapped[list["FeePenalty"]] = relationship(
        "FeePenalty", back_populates="fee_record", lazy="selectin"
    )


class FeePayment(BaseModel):
    """Payment made against a fee record."""

    __tablename__ = "fee_payments"
    __table_args__ = (
        Index("idx_fee_payments_record", "fee_record_id"),
        Index("idx_fee_payments_student", "school_id", "fee_record_id"),
        Index("idx_fee_payments_date", "school_id", "payment_date"),
    )

    fee_record_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("fee_records.id"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
    reference: Mapped[str | None] = mapped_column(String(100), default=None)
    recorded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("users.id"), default=None
    )

    # Relationships
    fee_record: Mapped["FeeRecord"] = relationship(
        "FeeRecord", back_populates="payments", lazy="selectin"
    )
    recorder: Mapped["User | None"] = relationship("User", lazy="selectin")


class FeeReminder(BaseModel):
    """Fee reminders sent to students/parents."""

    __tablename__ = "fee_reminders"
    __table_args__ = (
        Index("idx_fee_reminders_sent", "school_id", "sent_at"),
        Index("idx_fee_reminders_year", "school_id", "academic_year_id"),
    )

    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    target_group: Mapped[str] = mapped_column(String(20), nullable=False)
    class_name: Mapped[str | None] = mapped_column(String(50), default=None)
    section: Mapped[str | None] = mapped_column(String(10), default=None)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    send_via: Mapped[str] = mapped_column(String(20), nullable=False)
    sent_to_count: Mapped[int] = mapped_column(Integer, default=0)
    sent_by: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("users.id"), nullable=False
    )
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Relationships
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", lazy="selectin")
    sender: Mapped["User"] = relationship("User", lazy="selectin")


class FeePenalty(BaseModel):
    """Late fee / penalty applied to a fee record."""

    __tablename__ = "fee_penalties"
    __table_args__ = (
        Index("idx_fee_penalties_record", "fee_record_id"),
        Index("idx_fee_penalties_date", "school_id", "applied_on"),
    )

    fee_record_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("fee_records.id"), nullable=False
    )
    penalty_type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    percentage: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), default=None)
    applied_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    applied_by: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("users.id"), nullable=False
    )

    # Relationships
    fee_record: Mapped["FeeRecord"] = relationship(
        "FeeRecord", back_populates="penalties", lazy="selectin"
    )
    applier: Mapped["User"] = relationship("User", lazy="selectin")


# Type stubs for relationships (avoids circular imports at runtime)
from src.models.core import AcademicYear, User  # noqa: E402, F401
from src.models.academic import ClassSection  # noqa: E402, F401
from src.models.student import Student  # noqa: E402, F401
