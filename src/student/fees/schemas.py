from typing import Optional

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


# --- Fee Summary ---


class FeeSummaryData(BaseModel):
    total_fees: Decimal
    paid: Decimal
    due: Decimal
    overdue: Decimal
    late_fines: Decimal
    currency: str = "INR"


class RecentPaymentItem(BaseModel):
    id: uuid.UUID
    fee_type: str
    fee_category: str
    amount: Decimal
    currency: str = "INR"
    paid_date: date
    method: str
    receipt_id: str | None = None
    status: str


class CurrentDueItem(BaseModel):
    id: uuid.UUID
    fee_type: str
    fee_category: str
    amount: Decimal
    due_date: date
    status: str


class FeeSummaryResponse(BaseModel):
    academic_year: str
    summary: FeeSummaryData
    current_dues: list[CurrentDueItem]
    recent_payments: list[RecentPaymentItem]
    metadata: dict = {}


# --- Fee Structure ---


class FeeComponentItem(BaseModel):
    id: uuid.UUID
    fee_component: str
    fee_category: str
    amount: Decimal
    currency: str = "INR"
    frequency: str
    metadata: dict = {}


class FeeStructureResponse(BaseModel):
    academic_year: str
    components: list[FeeComponentItem]
    total_annual_fee: Decimal
    currency: str = "INR"
    metadata: dict = {}


# --- Fee Dues ---


class FeeDueItem(BaseModel):
    id: uuid.UUID
    fee_type: str
    fee_category: str
    description: str | None = None
    amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    balance: Decimal
    currency: str = "INR"
    due_date: date
    status: str
    is_overdue: bool
    days_until_due: int | None = None
    days_overdue: int | None = None
    pay_now_url: str | None = None
    receipt_url: str | None = None
    metadata: dict = {}


class FeeDuesResponse(BaseModel):
    count: int
    page: int
    page_size: int
    total_pages: int
    total_due: Decimal
    currency: str = "INR"
    results: list[FeeDueItem]


# --- Payment History ---


class PaymentHistoryItem(BaseModel):
    id: uuid.UUID
    fee_type: str
    fee_category: str
    description: str | None = None
    amount: Decimal
    currency: str = "INR"
    paid_date: date
    method: str
    transaction_id: str | None = None
    receipt_id: str | None = None
    receipt_url: str | None = None
    status: str
    metadata: dict = {}


class PaymentHistoryResponse(BaseModel):
    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[PaymentHistoryItem]
    metadata: dict = {}


# --- Receipt ---


class FeeReceiptResponse(BaseModel):
    payment_id: uuid.UUID
    receipt_id: str
    student_name: str
    roll_number: str | None = None
    class_section: str
    fee_type: str
    description: str | None = None
    amount: Decimal
    currency: str = "INR"
    paid_date: date
    method: str
    transaction_id: str | None = None
    school_name: str
    school_address: str
    download_url: str
    content_type: str = "application/pdf"
    generated_at: datetime | None = None
    metadata: dict = {}


# --- Reminders ---


class ReminderItem(BaseModel):
    id: uuid.UUID
    message: str
    sent_at: datetime
    send_via: str
    target_group: str


class RemindersResponse(BaseModel):
    count: int
    results: list[ReminderItem]
