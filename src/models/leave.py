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


class LeavePolicy(BaseModel):
    """Leave policy configuration per academic year."""

    __tablename__ = "leave_policies"
    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "academic_year_id",
            "leave_type",
            name="uq_leave_policies_year_type",
        ),
        Index("idx_leave_policies_year", "school_id", "academic_year_id"),
    )

    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    leave_type: Mapped[str] = mapped_column(String(50), nullable=False)
    code: Mapped[str | None] = mapped_column(String(10), default=None)
    total_per_year: Mapped[int] = mapped_column(Integer, nullable=False)
    carry_forward: Mapped[bool] = mapped_column(Boolean, default=False)
    max_carry_forward: Mapped[int | None] = mapped_column(Integer, default=None)
    max_consecutive_days: Mapped[int | None] = mapped_column(Integer, default=None)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=True)
    half_day_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    medical_certificate_required_after_days: Mapped[int | None] = mapped_column(
        Integer, default=None
    )
    advance_notice_days: Mapped[int | None] = mapped_column(Integer, default=None)

    # Relationships
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", lazy="selectin")


class LeaveApplication(BaseModel):
    """Leave application submitted by staff."""

    __tablename__ = "leave_applications"
    __table_args__ = (
        Index("idx_leave_applications_staff", "staff_id", "academic_year_id"),
        Index(
            "idx_leave_applications_status",
            "school_id",
            "academic_year_id",
            "status",
        ),
        Index("idx_leave_applications_dates", "school_id", "from_date", "to_date"),
    )

    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    staff_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("staff.id"), nullable=False
    )
    leave_type: Mapped[str] = mapped_column(String(50), nullable=False)
    from_date: Mapped[date] = mapped_column(Date, nullable=False)
    to_date: Mapped[date] = mapped_column(Date, nullable=False)
    days: Mapped[Decimal] = mapped_column(Numeric(4, 1), nullable=False)
    is_half_day: Mapped[bool] = mapped_column(Boolean, default=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
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
    rejected_on: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    remarks: Mapped[str | None] = mapped_column(Text, default=None)
    substitute_teacher_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("staff.id"), default=None
    )
    cancelled_on: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )

    # Relationships
    staff: Mapped["Staff"] = relationship(
        "Staff", lazy="selectin", foreign_keys=[staff_id]
    )
    substitute_teacher: Mapped["Staff | None"] = relationship(
        "Staff", lazy="selectin", foreign_keys=[substitute_teacher_id]
    )
    approver: Mapped["User | None"] = relationship(
        "User", lazy="selectin", foreign_keys=[approved_by]
    )
    rejector: Mapped["User | None"] = relationship(
        "User", lazy="selectin", foreign_keys=[rejected_by]
    )
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", lazy="selectin")


class LeaveBalance(BaseModel):
    """Per-staff leave balance for each academic year and leave type."""

    __tablename__ = "leave_balances"
    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "staff_id",
            "academic_year_id",
            "leave_type",
            name="uq_leave_balances_staff_year_type",
        ),
        Index("idx_leave_balances_staff", "staff_id", "academic_year_id"),
    )

    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    staff_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("staff.id"), nullable=False
    )
    leave_type: Mapped[str] = mapped_column(String(50), nullable=False)
    total_allocated: Mapped[int] = mapped_column(Integer, nullable=False)
    carried_forward: Mapped[int] = mapped_column(Integer, default=0)
    used: Mapped[Decimal] = mapped_column(Numeric(5, 1), default=0)
    pending: Mapped[Decimal] = mapped_column(Numeric(5, 1), default=0)

    # Relationships
    staff: Mapped["Staff"] = relationship("Staff", lazy="selectin")
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", lazy="selectin")


# Type stubs for relationships (avoids circular imports at runtime)
from src.models.core import AcademicYear, User  # noqa: E402, F401
from src.models.staff import Staff  # noqa: E402, F401
