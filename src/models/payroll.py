from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import BaseModel, UUIDType


class SalaryStructure(BaseModel):
    """Defines salary components for a staff member per academic year."""

    __tablename__ = "salary_structures"
    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "staff_id",
            name="uq_salary_structures_active",
        ),
        Index("idx_salary_structures_staff", "staff_id", "academic_year_id"),
    )

    staff_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("staff.id"), nullable=False
    )
    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    basic_salary: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    hra: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    da: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    transport_allowance: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0")
    )
    medical_allowance: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0")
    )
    other_allowances: Mapped[dict] = mapped_column(JSON, default=dict)
    pf_deduction: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    professional_tax: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0")
    )
    tds: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    other_deductions: Mapped[dict] = mapped_column(JSON, default=dict)
    net_salary: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    staff: Mapped["Staff"] = relationship("Staff", lazy="selectin")
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", lazy="selectin")


class Payslip(BaseModel):
    """Monthly payslip record for a staff member."""

    __tablename__ = "payslips"
    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "staff_id",
            "month",
            "year",
            name="uq_payslips_month",
        ),
        Index("idx_payslips_staff", "staff_id", "year", "month"),
        Index("idx_payslips_period", "school_id", "year", "month"),
        Index("idx_payslips_status", "school_id", "year", "month", "status"),
    )

    staff_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("staff.id"), nullable=False
    )
    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    basic_salary: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    hra: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    da: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    transport_allowance: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    total_allowances: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_deductions: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    net_salary: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    status: Mapped[str] = mapped_column(
        String(20), default="Generated", nullable=False
    )
    paid_on: Mapped[date | None] = mapped_column(Date, default=None)
    payment_method: Mapped[str | None] = mapped_column(String(50), default=None)
    reference: Mapped[str | None] = mapped_column(String(100), default=None)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    generated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("users.id"), default=None
    )

    # Relationships
    staff: Mapped["Staff"] = relationship("Staff", lazy="selectin")
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", lazy="selectin")
    generator: Mapped["User | None"] = relationship("User", lazy="selectin")


class SalaryAdvance(BaseModel):
    """Salary advance request by a staff member."""

    __tablename__ = "salary_advances"
    __table_args__ = (
        Index("idx_salary_advances_staff", "staff_id"),
        Index("idx_salary_advances_status", "school_id", "status"),
    )

    staff_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("staff.id"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, default=None)
    recovery_months: Mapped[int | None] = mapped_column(Integer, default=None)
    per_month_deduction: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), default=None
    )
    status: Mapped[str] = mapped_column(String(20), default="Pending", nullable=False)
    applied_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("users.id"), default=None
    )
    approved_on: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    rejected_by: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("users.id"), default=None
    )
    remarks: Mapped[str | None] = mapped_column(Text, default=None)
    disbursed_on: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )

    # Relationships
    staff: Mapped["Staff"] = relationship("Staff", lazy="selectin")
    approver: Mapped["User | None"] = relationship(
        "User", lazy="selectin", foreign_keys=[approved_by]
    )
    rejector: Mapped["User | None"] = relationship(
        "User", lazy="selectin", foreign_keys=[rejected_by]
    )


class SalaryRevision(BaseModel):
    """Tracks salary hikes and revisions over time for staff members."""

    __tablename__ = "salary_revisions"
    __table_args__ = (
        Index("idx_salary_revisions_staff", "staff_id", "effective_date"),
        Index("idx_salary_revisions_date", "school_id", "effective_date"),
        Index("idx_salary_revisions_year", "school_id", "academic_year_id"),
    )

    staff_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("staff.id"), nullable=False
    )
    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    previous_basic: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    new_basic: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    revision_type: Mapped[str] = mapped_column(String(50), nullable=False)
    percentage: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), default=None)
    increment_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), default=None
    )
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("users.id"), default=None
    )
    approved_on: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    remarks: Mapped[str | None] = mapped_column(Text, default=None)

    # Relationships
    staff: Mapped["Staff"] = relationship("Staff", lazy="selectin")
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", lazy="selectin")
    approver: Mapped["User | None"] = relationship("User", lazy="selectin")


# Type stubs for relationships (avoids circular imports at runtime)
from src.models.core import AcademicYear, User  # noqa: E402, F401
from src.models.staff import Staff  # noqa: E402, F401
