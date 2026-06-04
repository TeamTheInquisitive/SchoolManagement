from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, ForeignKey, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import (
    AuditMixin,
    Base,
    BaseModel,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDType,
)


class School(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """School / tenant table. Root table for multi-tenancy."""

    __tablename__ = "schools"

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    logo_url: Mapped[str | None] = mapped_column(Text, default=None)
    address_line1: Mapped[str | None] = mapped_column(String(255), default=None)
    address_line2: Mapped[str | None] = mapped_column(String(255), default=None)
    city: Mapped[str | None] = mapped_column(String(100), default=None)
    state: Mapped[str | None] = mapped_column(String(100), default=None)
    country: Mapped[str | None] = mapped_column(String(100), default="India")
    pincode: Mapped[str | None] = mapped_column(String(20), default=None)
    phone: Mapped[str | None] = mapped_column(String(20), default=None)
    email: Mapped[str | None] = mapped_column(String(255), default=None)
    website: Mapped[str | None] = mapped_column(String(255), default=None)
    board_affiliation: Mapped[str | None] = mapped_column(String(100), default=None)
    established_year: Mapped[int | None] = mapped_column(default=None)
    principal_name: Mapped[str | None] = mapped_column(String(255), default=None)

    # Subscription fields
    enrollment_date: Mapped[date | None] = mapped_column(default=None)
    subscription_status: Mapped[str] = mapped_column(String(20), default="trial", server_default="trial")  # trial, active, expired
    trial_start_date: Mapped[date | None] = mapped_column(default=None)
    trial_end_date: Mapped[date | None] = mapped_column(default=None)

    metadata_: Mapped[dict] = mapped_column(
        "metadata", JSON, default=dict
    )

    # Relationships
    users: Mapped[list[User]] = relationship("User", back_populates="school", lazy="selectin")
    subscriptions: Mapped[list] = relationship("Subscription", backref="school", lazy="selectin")


class User(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """User authentication and identity table."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("school_id", "email", name="uq_users_school_email"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, primary_key=True, default=uuid.uuid4
    )
    school_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("schools.id"), index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    password_changed: Mapped[bool] = mapped_column(default=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # admin, teacher, student, parent
    phone: Mapped[str | None] = mapped_column(String(20), default=None)
    avatar_url: Mapped[str | None] = mapped_column(Text, default=None)
    last_login_at: Mapped[datetime | None] = mapped_column(default=None)
    password_reset_token: Mapped[str | None] = mapped_column(String(255), default=None)
    password_reset_expires: Mapped[datetime | None] = mapped_column(default=None)
    is_locked: Mapped[bool] = mapped_column(default=False)
    failed_login_attempts: Mapped[int] = mapped_column(default=0)

    # Foreign keys to link user to staff/student/parent records
    staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("staff.id", use_alter=True), default=None
    )
    student_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("students.id", use_alter=True), default=None
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("parents.id", use_alter=True), default=None
    )

    metadata_: Mapped[dict] = mapped_column(
        "metadata", JSON, default=dict
    )

    # Relationships
    school: Mapped[School] = relationship("School", back_populates="users", lazy="selectin")


class AcademicYear(BaseModel):
    """Academic year scoping table."""

    __tablename__ = "academic_years"
    __table_args__ = (
        UniqueConstraint("school_id", "name", name="uq_academic_years_school_name"),
        CheckConstraint("end_date > start_date", name="chk_academic_years_dates"),
    )

    name: Mapped[str] = mapped_column(String(20), nullable=False)
    start_date: Mapped[date] = mapped_column(nullable=False)
    end_date: Mapped[date] = mapped_column(nullable=False)
    is_current: Mapped[bool] = mapped_column(default=False)


class Settings(BaseModel):
    """School-level settings (key-value per category)."""

    __tablename__ = "settings"
    __table_args__ = (
        UniqueConstraint(
            "school_id", "category", "key", name="uq_settings_school_category_key"
        ),
    )

    category: Mapped[str] = mapped_column(String(100), nullable=False)
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, default=None)


class EnumConfig(BaseModel):
    """Configurable enum values (fee types, leave types, etc.)."""

    __tablename__ = "enum_configs"
    __table_args__ = (
        UniqueConstraint(
            "school_id", "category", "value", name="uq_enum_configs_school_cat_val"
        ),
    )

    category: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(default=0)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
