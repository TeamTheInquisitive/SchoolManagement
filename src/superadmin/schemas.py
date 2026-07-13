from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr


# --- Dashboard ---

class DashboardStatsResponse(BaseModel):
    total_schools: int
    total_students: int
    total_staff: int
    total_income: float
    active_subscriptions: int
    mrr: float
    expiring_in_7_days: int
    expiring_in_30_days: int


# --- Schools ---

class SchoolListItem(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    city: str | None
    student_count: int
    staff_count: int
    is_active: bool
    subscription_status: str
    enrollment_date: date | None = None
    trial_end_date: date | None = None
    created_at: datetime | None = None


class SchoolListResponse(BaseModel):
    schools: list[SchoolListItem]
    total: int


class SchoolCreate(BaseModel):
    name: str
    code: str | None = None
    city: str | None = None
    state: str | None = None
    address_line1: str | None = None
    phone: str | None = None
    email: str | None = None
    board_affiliation: str | None = None
    principal_name: str | None = None
    enrollment_date: date | None = None
    trial_start_date: date | None = None
    trial_end_date: date | None = None
    trial_duration_days: int | None = 14
    grace_period_days: int | None = 2


class SchoolUpdate(BaseModel):
    name: str | None = None
    city: str | None = None
    state: str | None = None
    address_line1: str | None = None
    phone: str | None = None
    email: str | None = None
    board_affiliation: str | None = None
    principal_name: str | None = None
    is_active: bool | None = None
    trial_duration_days: int | None = None
    grace_period_days: int | None = None


class SchoolDetailResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    logo_url: str | None = None
    city: str | None
    state: str | None
    address_line1: str | None
    phone: str | None
    email: str | None
    board_affiliation: str | None
    principal_name: str | None
    is_active: bool
    created_at: datetime | None
    enrollment_date: date | None
    subscription_status: str
    trial_start_date: date | None
    trial_end_date: date | None
    trial_duration_days: int | None = 14
    grace_period_days: int | None = 2
    student_count: int
    staff_count: int
    admin_users: list[UserItem]
    subscription: SubscriptionResponse | None = None


# --- Subscription Status ---

class SubscriptionStatusUpdate(BaseModel):
    subscription_status: str | None = None
    trial_start_date: date | None = None
    trial_end_date: date | None = None
    enrollment_date: date | None = None
    trial_duration_days: int | None = None
    grace_period_days: int | None = None


# --- Subscriptions ---

class SubscriptionCreate(BaseModel):
    plan_type: str  # monthly, yearly
    amount: Decimal
    start_date: date
    end_date: date
    auto_renew: bool = True


class SubscriptionUpdate(BaseModel):
    plan_type: str | None = None
    amount: Decimal | None = None
    start_date: date | None = None
    end_date: date | None = None
    auto_renew: bool | None = None


class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    plan_type: str
    amount: float
    start_date: date
    end_date: date
    auto_renew: bool
    is_active: bool
    created_at: datetime | None = None


class SubscriptionHistoryResponse(BaseModel):
    subscriptions: list[SubscriptionResponse]
    total: int


# --- Payments ---

class PaymentCreate(BaseModel):
    amount: Decimal
    payment_date: date
    period_start: date
    period_end: date
    status: str = "paid"
    notes: str | None = None


class PaymentResponse(BaseModel):
    id: uuid.UUID
    subscription_id: uuid.UUID
    amount: float
    payment_date: date
    period_start: date
    period_end: date
    status: str
    notes: str | None
    created_at: datetime | None = None


class PaymentListResponse(BaseModel):
    payments: list[PaymentResponse]
    total: int


# --- Admin / Users ---

class AdminCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    phone: str | None = None
    allowed_modules: list[str] | None = None


class AdminUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    allowed_modules: list[str] | None = None
    is_active: bool | None = None


class AdminPasswordReset(BaseModel):
    password: str


class UserItem(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    phone: str | None
    is_active: bool
    is_locked: bool = False
    failed_login_attempts: int = 0
    school_name: str | None = None
    last_login_at: datetime | None = None
    allowed_modules: list[str] | None = None
    roll_number: str | None = None


class UserListResponse(BaseModel):
    users: list[UserItem]
    total: int
    page: int = 1
    page_size: int = 20
    total_pages: int = 1


# --- Hard Delete ---

class HardDeleteResponse(BaseModel):
    school_id: uuid.UUID
    school_name: str
    deleted_tables: dict[str, int]
    total_records_deleted: int
