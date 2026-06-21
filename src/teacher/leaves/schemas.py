from typing import Optional

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


# --- Balance Schemas ---


class LeaveBalanceItem(BaseModel):
    leave_type: str
    display_name: str | None = None
    total_allocated: int
    available: Decimal = Decimal("0")
    used: Decimal = Decimal("0")
    pending: Decimal = Decimal("0")


class LeaveBalanceSummary(BaseModel):
    total_leaves: int
    available: Decimal
    used: Decimal
    pending: Decimal


class LeaveBalanceResponse(BaseModel):
    academic_year: str
    balances: list[LeaveBalanceItem]
    summary: LeaveBalanceSummary


# --- Leave History Schemas ---


class LeaveHistoryItem(BaseModel):
    id: uuid.UUID
    leave_type: str
    from_date: date
    to_date: date
    duration_days: Decimal
    is_half_day: bool = False
    reason: str
    status: str
    applied_on: datetime
    approved_by: str | None = None
    approved_on: datetime | None = None
    remarks: str | None = None
    metadata: dict = {}


class LeaveHistoryResponse(BaseModel):
    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[LeaveHistoryItem]


# --- Upcoming Leaves ---


class UpcomingLeaveItem(BaseModel):
    id: uuid.UUID
    leave_type: str
    from_date: date
    to_date: date
    duration_days: Decimal
    reason: str
    status: str
    applied_on: datetime
    approved_by: str | None = None
    can_cancel: bool


class UpcomingLeavesResponse(BaseModel):
    results: list[UpcomingLeaveItem]


# --- Apply Leave ---


class ApplyLeaveRequest(BaseModel):
    leave_type: str
    from_date: date
    to_date: date
    reason: str
    is_half_day: bool = False
    academic_year: str | None = None
    metadata: dict = {}


class ApplyLeaveResponse(BaseModel):
    id: uuid.UUID
    leave_type: str
    from_date: date
    to_date: date
    duration_days: Decimal
    reason: str
    status: str
    applied_on: datetime
    approved_by: str | None = None
    approved_on: datetime | None = None
    remarks: str | None = None
    academic_year: str
    metadata: dict = {}


# --- Leave Detail ---


class LeaveDetailResponse(BaseModel):
    id: uuid.UUID
    leave_type: str
    from_date: date
    to_date: date
    duration_days: Decimal
    reason: str
    status: str
    applied_on: datetime
    approved_by: str | None = None
    approved_on: datetime | None = None
    remarks: str | None = None
    substitute_teacher: str | None = None
    academic_year: str
    metadata: dict = {}


# --- Cancel Leave ---


class CancelLeaveResponse(BaseModel):
    message: str
    id: uuid.UUID
    status: str
    cancelled_on: datetime
