from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from src.auth.dependencies import SchoolDep, StudentUser
from src.core.dependencies import PaginationDep, SessionDep
from src.student.fees import service
from src.student.fees.schemas import (
    FeeDuesResponse,
    FeeReceiptResponse,
    FeeStructureResponse,
    FeeSummaryResponse,
    PaymentHistoryResponse,
    RemindersResponse,
)

router = APIRouter(prefix="/student/fees", tags=["Student Fees"])


@router.get("/", response_model=FeeSummaryResponse)
async def get_fee_summary(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
    academic_year: str | None = Query(default=None),
) -> FeeSummaryResponse:
    """Get fee summary with current dues and recent payment history."""
    result = await service.get_fee_summary(db, school.id, user, academic_year)
    return FeeSummaryResponse(**result)


@router.get("/structure/", response_model=FeeStructureResponse)
async def get_fee_structure(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
    academic_year: str | None = Query(default=None),
) -> FeeStructureResponse:
    """Get fee structure breakdown with components and frequency."""
    result = await service.get_fee_structure(db, school.id, user, academic_year)
    return FeeStructureResponse(**result)


@router.get("/dues/", response_model=FeeDuesResponse)
async def get_fee_dues(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
    pagination: PaginationDep,
    academic_year: str | None = Query(default=None),
) -> FeeDuesResponse:
    """Get list of current fee dues."""
    result = await service.get_fee_dues(db, school.id, user, pagination, academic_year)
    return FeeDuesResponse(**result)


@router.get("/history/", response_model=PaymentHistoryResponse)
async def get_payment_history(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
    pagination: PaginationDep,
    academic_year: str | None = Query(default=None),
) -> PaymentHistoryResponse:
    """Get payment history."""
    result = await service.get_payment_history(
        db, school.id, user, pagination, academic_year
    )
    return PaymentHistoryResponse(**result)


@router.get("/receipt/{payment_id}/", response_model=FeeReceiptResponse)
async def get_receipt(
    payment_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
) -> FeeReceiptResponse:
    """Get payment receipt details with download URL."""
    result = await service.get_receipt(db, school.id, user, payment_id)
    return FeeReceiptResponse(**result)


@router.get("/reminders/", response_model=RemindersResponse)
async def get_reminders(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
) -> RemindersResponse:
    """Get fee reminders sent by admin."""
    result = await service.get_reminders(db, school.id, user)
    return RemindersResponse(**result)
