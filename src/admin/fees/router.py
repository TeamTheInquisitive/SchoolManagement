from __future__ import annotations

import csv
import io
import uuid
from datetime import date

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from src.admin.fees import service
from src.admin.fees.schemas import (
    ApplyLateFeeRequest,
    ApplyLateFeeResponse,
    BulkApplyLateFeesRequest,
    BulkApplyLateFeesResponse,
    BulkRecordPaymentRequest,
    BulkRecordPaymentResponse,
    ConsolidatedReceiptResponse,
    CreateFeeRecordRequest,
    FeeReceiptResponse,
    FeeRecordCreateResponse,
    FeeRecordDetailResponse,
    FeeRecordListResponse,
    GenerateDueRequest,
    GenerateDueResponse,
    RecordPaymentRequest,
    RecordPaymentResponse,
    SendReminderRequest,
    SendReminderResponse,
    StudentFeeListResponse,
    StudentFeeDetailResponse,
    StudentFeeRecordsResponse,
    UpdateFeeRecordRequest,
)
from src.auth.dependencies import AdminUser, SchoolDep
from src.core.dependencies import PaginationDep, SessionDep

router = APIRouter(prefix="/admin/fees", tags=["Admin Fees"])


@router.get("/daily-collection")
async def get_daily_collection(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    payment_date: date = Query(default=None),
    from_date: date = Query(default=None),
    to_date: date = Query(default=None),
) -> dict:
    """Get all fee payments for a specific date or date range."""
    start = from_date or payment_date or date.today()
    end = to_date or payment_date or date.today()
    result = await service.get_daily_collection(db, school.id, start, end)
    return result


@router.get("", response_model=StudentFeeListResponse)
async def list_fee_records(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    pagination: PaginationDep,
    search: str | None = Query(default=None),
    class_name: str | None = Query(default=None),
    section: str | None = Query(default=None),
    status: str | None = Query(default=None),
    fee_type: str | None = Query(default=None),
    fee_category: str | None = Query(default=None),
    due_from: date | None = Query(default=None),
    due_to: date | None = Query(default=None),
) -> FeeRecordListResponse:
    """List fee records with filters, pagination, and summary KPIs."""
    result = await service.list_fee_records(
        db,
        school.id,
        pagination,
        search,
        class_name,
        section,
        status,
        fee_type,
        fee_category,
        due_from,
        due_to,
    )
    return StudentFeeListResponse(**result)


@router.get("/export")
async def export_fee_records(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    class_name: str | None = Query(default=None),
    status: str | None = Query(default=None),
) -> StreamingResponse:
    """Export fee records as CSV."""
    rows = await service.export_fee_records(db, school.id, class_name, status)

    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    else:
        writer = csv.writer(output)
        writer.writerow(["student_name", "class", "section", "fee_type", "fee_category", "total_amount", "paid", "pending", "late_fine", "due_date", "status"])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=fee_records.csv"},
    )


@router.get("/student/{student_id}", response_model=StudentFeeRecordsResponse)
async def get_student_fee_records(
    student_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    academic_year: str | None = Query(default=None),
    status: str | None = Query(default=None),
) -> StudentFeeRecordsResponse:
    """Get all fee records for a specific student with summary."""
    result = await service.get_student_fee_records(
        db, school.id, student_id, academic_year, status
    )
    return StudentFeeRecordsResponse(**result)


@router.get("/student/{student_id}/receipt", response_model=ConsolidatedReceiptResponse)
async def get_student_consolidated_receipt(
    student_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    academic_year: str | None = Query(default=None),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
) -> ConsolidatedReceiptResponse:
    """Generate a consolidated payment receipt for a student."""
    result = await service.get_student_consolidated_receipt(
        db, school.id, student_id, academic_year, from_date, to_date
    )
    return ConsolidatedReceiptResponse(**result)


@router.get("/{fee_id}", response_model=FeeRecordDetailResponse)
async def get_fee_record_detail(
    fee_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> FeeRecordDetailResponse:
    """Get a single fee record with full payment and fine history."""
    result = await service.get_fee_record_detail(db, school.id, fee_id)
    return FeeRecordDetailResponse(**result)


@router.get("/{fee_id}/receipt", response_model=FeeReceiptResponse)
async def get_fee_receipt(
    fee_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> FeeReceiptResponse:
    """Generate a payment receipt for a specific fee record."""
    result = await service.get_fee_receipt(db, school.id, fee_id)
    return FeeReceiptResponse(**result)


@router.put("/{fee_id}")
async def update_fee_record(
    fee_id: uuid.UUID,
    data: UpdateFeeRecordRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Update a fee record (used to activate draft records created on student admission)."""
    result = await service.update_fee_record(db, school.id, fee_id, data.model_dump(exclude_none=True))
    return result


@router.delete("/{fee_id}")
async def delete_fee_record(
    fee_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Soft-delete a fee record. Only allowed if no payment has been made."""
    result = await service.delete_fee_record(db, school.id, fee_id, user.id)
    return result


@router.post("", status_code=201, response_model=FeeRecordCreateResponse)
async def create_fee_record(
    data: CreateFeeRecordRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> FeeRecordCreateResponse:
    """Create a fee record (assign fee to a student)."""
    result = await service.create_fee_record(db, school.id, user, data.model_dump())
    return FeeRecordCreateResponse(**result)


@router.post("/generate-due", status_code=201, response_model=GenerateDueResponse)
async def generate_due_fees(
    data: GenerateDueRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> GenerateDueResponse:
    """Bulk generate due fee records for students in a class."""
    result = await service.generate_due_fees(db, school.id, user, data.model_dump())
    return GenerateDueResponse(**result)


@router.post("/{fee_id}/record-payment", response_model=RecordPaymentResponse)
async def record_payment(
    fee_id: uuid.UUID,
    data: RecordPaymentRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> RecordPaymentResponse:
    """Record a payment (partial or full) against a fee record."""
    result = await service.record_payment(db, school.id, user, fee_id, data.model_dump())
    return RecordPaymentResponse(**result)


@router.post("/student/{student_id}/bulk-record-payment", response_model=BulkRecordPaymentResponse)
async def bulk_record_payment(
    student_id: uuid.UUID,
    data: BulkRecordPaymentRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> BulkRecordPaymentResponse:
    """Record a bulk payment that distributes across multiple pending fee components for a student."""
    result = await service.bulk_record_payment(db, school.id, user, student_id, data.model_dump())
    return BulkRecordPaymentResponse(**result)


@router.post("/{fee_id}/apply-late-fee", response_model=ApplyLateFeeResponse)
async def apply_late_fee(
    fee_id: uuid.UUID,
    data: ApplyLateFeeRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> ApplyLateFeeResponse:
    """Apply a late fee/penalty to a fee record."""
    result = await service.apply_late_fee(db, school.id, user, fee_id, data.model_dump())
    return ApplyLateFeeResponse(**result)


@router.post("/bulk-apply-late-fees", response_model=BulkApplyLateFeesResponse)
async def bulk_apply_late_fees(
    data: BulkApplyLateFeesRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> BulkApplyLateFeesResponse:
    """Bulk apply late fees to all overdue records."""
    result = await service.bulk_apply_late_fees(db, school.id, user, data.model_dump())
    return BulkApplyLateFeesResponse(**result)


@router.post("/send-reminder", response_model=SendReminderResponse)
async def send_reminder(
    data: SendReminderRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> SendReminderResponse:
    """Send fee payment reminders to students/parents."""
    result = await service.send_reminder(db, school.id, user, data.model_dump())
    return SendReminderResponse(**result)
