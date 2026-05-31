from typing import Optional

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


# --- Policy Schemas ---


class LeavePolicyTypeSchema(BaseModel):
    type: str
    code: str | None = None
    total_per_year: int
    carry_forward: bool = False
    max_carry_forward: int | None = None
    max_consecutive_days: int | None = None
    requires_approval: bool = True
    half_day_allowed: bool = False
    medical_certificate_required_after_days: int | None = None
    advance_notice_days: int | None = None


class LeavePolicyResponse(BaseModel):
    academic_year: str
    leave_types: list[LeavePolicyTypeSchema]


class UpdateLeavePolicyRequest(BaseModel):
    academic_year: str | None = None
    leave_types: list[LeavePolicyTypeSchema]


class UpdateLeavePolicyResponse(BaseModel):
    message: str
    academic_year: str
    leave_types: list[LeavePolicyTypeSchema]


# --- Leave Application Schemas ---


class LeaveApplicationListItem(BaseModel):
    id: uuid.UUID
    teacher_id: uuid.UUID
    employee_id: str
    teacher_name: str
    department: str | None = None
    leave_type: str
    from_date: date
    to_date: date
    days: Decimal
    is_half_day: bool
    reason: str
    status: str
    applied_on: datetime
    approved_by: str | None = None
    approved_on: datetime | None = None
    substitute_teacher: str | None = None
    substitute_teacher_id: uuid.UUID | None = None


class OverallSummary(BaseModel):
    total_applications: int
    approved: int
    pending: int
    rejected: int
    on_leave_today: int


class LeaveApplicationListResponse(BaseModel):
    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[LeaveApplicationListItem]
    overall_summary: OverallSummary


# --- Teacher Balance Schemas ---


class LeaveTypeBalance(BaseModel):
    total: int
    availed: Decimal
    pending: Decimal
    remaining: Decimal


class TotalSummary(BaseModel):
    total_allocated: int
    total_availed: Decimal
    total_pending: Decimal
    total_remaining: Decimal


class TeacherLeaveHistoryItem(BaseModel):
    id: uuid.UUID
    leave_type: str
    from_date: date
    to_date: date
    days: Decimal
    is_half_day: bool
    reason: str
    status: str
    applied_on: datetime


class TeacherLeaveDetailResponse(BaseModel):
    teacher_id: uuid.UUID
    employee_id: str
    teacher_name: str
    department: str | None = None
    academic_year: str
    leave_balance: dict[str, LeaveTypeBalance]
    total_summary: TotalSummary
    leave_history: list[TeacherLeaveHistoryItem]


# --- All Balances Overview ---


class TeacherBalanceOverviewItem(BaseModel):
    teacher_id: uuid.UUID
    employee_id: str
    teacher_name: str
    department: str | None = None
    casual: LeaveTypeBalance | None = None
    sick: LeaveTypeBalance | None = None
    annual: LeaveTypeBalance | None = None
    total_availed: Decimal
    total_remaining: Decimal
    is_active: bool = True


class AllBalancesResponse(BaseModel):
    academic_year: str
    results: list[TeacherBalanceOverviewItem]


# --- Approve/Reject/Cancel Schemas ---


class ApproveLeaveRequest(BaseModel):
    remarks: str | None = None
    substitute_teacher_id: uuid.UUID | None = None


class ApproveLeaveResponse(BaseModel):
    id: uuid.UUID
    status: str
    approved_by: str
    approved_on: datetime
    substitute_teacher: str | None = None
    substitute_teacher_id: uuid.UUID | None = None
    leave_balance_after: dict[str, LeaveTypeBalance]


class RejectLeaveRequest(BaseModel):
    remarks: str


class RejectLeaveResponse(BaseModel):
    id: uuid.UUID
    status: str
    rejected_by: str
    rejected_on: datetime
    remarks: str


class CancelLeaveRequest(BaseModel):
    reason: str | None = None


class CancelLeaveResponse(BaseModel):
    id: uuid.UUID
    status: str
    cancelled_by: str
    cancelled_on: datetime
    days_restored: Decimal
    leave_balance_after: dict[str, LeaveTypeBalance]


# --- Bulk Action Schemas ---


class BulkActionRequest(BaseModel):
    action: str  # "approve" or "reject"
    leave_ids: list[uuid.UUID]
    remarks: str | None = None


class BulkActionResult(BaseModel):
    id: uuid.UUID
    status: str


class BulkActionResponse(BaseModel):
    processed: int
    action: str
    results: list[BulkActionResult]


class AllocateLeaveRequest(BaseModel):
    staff_ids: list[uuid.UUID]
    leave_types: dict[str, int]  # e.g. {"Casual Leave": 12, "Sick Leave": 10, "Annual Leave": 15}


class AllocateLeaveResponse(BaseModel):
    allocated_count: int
    message: str


# --- Calendar Schemas ---


class CalendarLeaveEntry(BaseModel):
    teacher_id: uuid.UUID
    teacher_name: str
    leave_type: str
    is_half_day: bool


class CalendarResponse(BaseModel):
    from_date: date
    to_date: date
    leaves_by_date: dict[str, list[CalendarLeaveEntry]]
    conflict_dates: list[str]
    total_leave_days_this_month: int
