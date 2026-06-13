from typing import Optional

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


# --- Request schemas ---


class RunPayrollRequest(BaseModel):
    month: int
    year: int


class GeneratePayslipsRequest(BaseModel):
    month: int
    year: int


class UpdatePayslipRequest(BaseModel):
    basic_salary: Decimal | None = None
    hra: Decimal | None = None
    da: Decimal | None = None
    transport_allowance: Decimal | None = None
    total_allowances: Decimal | None = None
    total_deductions: Decimal | None = None
    net_salary: Decimal | None = None


class RecordPaymentRequest(BaseModel):
    amount: Decimal
    payment_method: str


class MarkAllPaidRequest(BaseModel):
    month: int
    year: int


class CreateSalaryAdvanceRequest(BaseModel):
    staff_id: uuid.UUID
    amount: Decimal
    reason: str | None = None
    recovery_months: int | None = None


class RejectAdvanceRequest(BaseModel):
    remarks: str | None = None


class CreateSalaryRevisionRequest(BaseModel):
    staff_id: uuid.UUID
    new_basic: Decimal
    revision_type: str  # "Annual Hike" | "Promotion" | "Adjustment"
    percentage: Decimal | None = None
    effective_date: date
    remarks: str | None = None


# --- Response schemas ---


class PayslipListItem(BaseModel):
    id: uuid.UUID
    employee_id: str
    employee_name: str
    basic_salary: Decimal
    hra: Decimal = Decimal("0")
    da: Decimal = Decimal("0")
    transport_allowance: Decimal = Decimal("0")
    allowances: Decimal
    deductions: Decimal
    net_salary: Decimal
    paid_amount: Decimal = Decimal("0")
    status: str
    paid_on: date | None = None


class PayrollSummary(BaseModel):
    total_staff: int
    total_disbursed: Decimal = Decimal("0")
    pending_amount: Decimal = Decimal("0")
    pending_count: int


class PayrollListResponse(BaseModel):
    month: str
    year: int
    results: list[PayslipListItem]
    summary: PayrollSummary


class RunPayrollResponse(BaseModel):
    generated: int
    total_amount: Decimal
    message: str


class GeneratePayslipsResponse(BaseModel):
    generated: int
    download_url: str


class SalaryStructureResponse(BaseModel):
    employee_id: str
    employee_name: str
    basic: Decimal
    hra: Decimal
    da: Decimal
    allowances: dict
    deductions: dict
    net_salary: Decimal


class SalaryAdvanceListItem(BaseModel):
    id: uuid.UUID
    employee_id: str
    employee_name: str
    amount: Decimal
    reason: str | None = None
    recovery_months: int | None = None
    per_month_deduction: Decimal | None = None
    status: str
    applied_on: datetime


class SalaryAdvanceListResponse(BaseModel):
    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[SalaryAdvanceListItem]


class SalaryAdvanceCreateResponse(BaseModel):
    id: uuid.UUID
    staff_id: uuid.UUID
    employee_id: str
    employee_name: str
    amount: Decimal
    reason: str | None = None
    recovery_months: int | None = None
    per_month_deduction: Decimal | None = None
    status: str
    applied_on: datetime


class SalaryAdvanceActionResponse(BaseModel):
    id: uuid.UUID
    status: str
    approved_by: str | None = None
    approved_on: datetime | None = None
    remarks: str | None = None
    disbursed_on: datetime | None = None


class SalaryRevisionItem(BaseModel):
    id: uuid.UUID
    previous_basic: Decimal
    new_basic: Decimal
    revision_type: str
    percentage: Decimal | None = None
    increment_amount: Decimal | None = None
    effective_date: date
    remarks: str | None = None
    created_at: datetime


class SalaryRevisionHistoryResponse(BaseModel):
    staff_id: uuid.UUID
    employee_name: str
    current_basic: Decimal
    revisions: list[SalaryRevisionItem]


class SalaryRevisionCreateResponse(BaseModel):
    id: uuid.UUID
    staff_id: uuid.UUID
    previous_basic: Decimal
    new_basic: Decimal
    revision_type: str
    percentage: Decimal | None = None
    increment_amount: Decimal
    effective_date: date
