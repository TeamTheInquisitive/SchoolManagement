from typing import Optional

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


# --- Request schemas ---


class CreateFeeRecordRequest(BaseModel):
    student_id: uuid.UUID
    fee_type: str
    fee_category: str = "academic"
    total_amount: Decimal
    due_date: date
    description: str | None = None


class GenerateDueRequest(BaseModel):
    fee_type: str
    fee_category: str = "academic"
    amount: Decimal
    due_date: date
    student_ids: list[str] | None = None
    class_name: str | None = None
    section: str | None = None
    academic_year: str | None = None
    term: str | None = None


class RecordPaymentRequest(BaseModel):
    amount: Decimal
    payment_method: str
    reference: str | None = None


class ApplyLateFeeRequest(BaseModel):
    penalty_type: str  # "fixed" or "percentage"
    amount: Decimal | None = None
    percentage: Decimal | None = None


class BulkApplyLateFeesRequest(BaseModel):
    penalty_type: str  # "fixed" or "percentage"
    amount: Decimal | None = None
    percentage: Decimal | None = None
    apply_to: str = "all_overdue"
    class_name: str | None = None
    section: str | None = None


class UpdateFeeRecordRequest(BaseModel):
    fee_type: str | None = None
    fee_category: str | None = None
    total_amount: Decimal | None = None
    due_date: date | None = None
    description: str | None = None
    is_active: bool | None = None
    status: str | None = None


class SendReminderRequest(BaseModel):
    target_group: str  # "All", "Class", "Section", "Overdue", "Selected"
    class_name: str | None = None
    section: str | None = None
    student_ids: list[uuid.UUID] | None = None
    message: str
    send_via: str  # "email", "in_app"


# --- Response schemas ---


class FeeRecordSummary(BaseModel):
    total_fees: Decimal
    collected: Decimal
    pending: Decimal
    overdue_count: int
    late_fines_total: Decimal
    collection_rate: float


class FeeRecordListItem(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    class_name: str
    section: str
    fee_type: str
    fee_category: str
    total_amount: Decimal
    paid: Decimal
    pending: Decimal
    late_fine: Decimal
    due_date: date
    status: str
    overdue_days: int
    is_active: bool
    metadata: dict = {}


class FeeRecordListResponse(BaseModel):
    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[FeeRecordListItem]
    summary: FeeRecordSummary


class PaymentHistoryItem(BaseModel):
    id: uuid.UUID
    amount: Decimal
    payment_date: date
    method: str
    reference: str | None = None
    recorded_by: str | None = None


class FineHistoryItem(BaseModel):
    id: uuid.UUID
    penalty_type: str
    amount: Decimal
    applied_on: datetime
    applied_by: str | None = None


class FeeRecordDetailResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    class_name: str
    section: str
    fee_type: str
    fee_category: str
    total_amount: Decimal
    paid: Decimal
    pending: Decimal
    late_fine: Decimal
    due_date: date
    status: str
    overdue_days: int
    payment_history: list[PaymentHistoryItem]
    fine_history: list[FineHistoryItem]
    is_active: bool
    metadata: dict = {}


class FeeRecordCreateResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    class_name: str
    section: str
    fee_type: str
    fee_category: str
    total_amount: Decimal
    paid: Decimal
    pending: Decimal
    late_fine: Decimal
    due_date: date
    status: str
    created_at: datetime
    metadata: dict = {}


class GeneratedFeeRecord(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    fee_type: str
    total_amount: Decimal
    due_date: date
    status: str


class GenerateDueResponse(BaseModel):
    generated: int
    fee_type: str
    amount: Decimal
    due_date: date
    class_section: str
    skipped: int
    message: str
    records: list[GeneratedFeeRecord] = []


class RecordPaymentResponse(BaseModel):
    id: uuid.UUID
    fee_id: uuid.UUID
    student_name: str
    fee_type: str
    total_amount: Decimal
    previously_paid: Decimal
    payment_recorded: Decimal
    total_paid_now: Decimal
    pending_now: Decimal
    status: str
    payment_date: date
    payment_method: str
    reference: str | None = None
    recorded_by: str | None = None
    message: str


class ApplyLateFeeResponse(BaseModel):
    id: uuid.UUID
    fee_id: uuid.UUID
    student_name: str
    pending_amount: Decimal
    overdue_days: int
    penalty_type: str
    penalty_applied: Decimal
    total_late_fine_now: Decimal
    new_pending_with_fine: Decimal
    applied_on: date
    applied_by: str
    message: str


class BulkLateFeeRecordItem(BaseModel):
    fee_id: uuid.UUID
    student_name: str
    fine_applied: Decimal


class BulkApplyLateFeesResponse(BaseModel):
    applied_to: int
    total_fines_applied: Decimal
    records: list[BulkLateFeeRecordItem]
    message: str


class SendReminderResponse(BaseModel):
    sent_to: int
    target_group: str
    send_via: str
    message: str


class StudentFeeRecordItem(BaseModel):
    id: uuid.UUID
    fee_type: str
    fee_category: str
    total_amount: Decimal
    paid: Decimal
    pending: Decimal
    late_fine: Decimal
    due_date: date
    status: str


class StudentFeeSummary(BaseModel):
    total_fees: Decimal
    total_paid: Decimal
    total_pending: Decimal
    total_fines: Decimal


class StudentFeeRecordsResponse(BaseModel):
    student_id: uuid.UUID
    student_name: str
    class_section: str
    academic_year: str
    summary: StudentFeeSummary
    records: list[StudentFeeRecordItem]


class ReceiptPaymentItem(BaseModel):
    amount: Decimal
    payment_date: date
    method: str
    reference: str | None = None


class FeeReceiptResponse(BaseModel):
    receipt_number: str
    generated_on: date
    school_name: str
    school_address: str
    student_name: str
    student_id: uuid.UUID
    roll_number: str | None = None
    class_section: str
    fee_type: str
    academic_year: str
    total_amount: Decimal
    total_paid: Decimal
    pending: Decimal
    late_fine: Decimal
    status: str
    payments: list[ReceiptPaymentItem]
    download_url: str
    metadata: dict = {}


class ConsolidatedReceiptPaymentItem(BaseModel):
    fee_type: str
    amount: Decimal
    payment_date: date
    method: str
    reference: str | None = None


class ConsolidatedReceiptSummary(BaseModel):
    total_fees_assigned: Decimal
    total_paid: Decimal
    total_pending: Decimal
    total_fines: Decimal


class ConsolidatedReceiptResponse(BaseModel):
    receipt_number: str
    generated_on: date
    school_name: str
    school_address: str
    student_name: str
    student_id: uuid.UUID
    roll_number: str | None = None
    class_section: str
    academic_year: str
    period: str
    fee_summary: ConsolidatedReceiptSummary
    payments: list[ConsolidatedReceiptPaymentItem]
    total_payments_count: int
    total_amount_paid: Decimal
    download_url: str
    metadata: dict = {}
