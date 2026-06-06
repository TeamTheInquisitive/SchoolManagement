from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from src.admin.payroll import service
from src.admin.payroll.schemas import (
    CreateSalaryAdvanceRequest,
    CreateSalaryRevisionRequest,
    GeneratePayslipsRequest,
    GeneratePayslipsResponse,
    MarkAllPaidRequest,
    PayrollListResponse,
    RecordPaymentRequest,
    RejectAdvanceRequest,
    RunPayrollRequest,
    RunPayrollResponse,
    SalaryAdvanceActionResponse,
    SalaryAdvanceCreateResponse,
    SalaryAdvanceListResponse,
    SalaryRevisionCreateResponse,
    SalaryRevisionHistoryResponse,
    SalaryStructureResponse,
    UpdatePayslipRequest,
)
from src.auth.dependencies import AdminUser, SchoolDep
from src.core.dependencies import PaginationDep, SessionDep

router = APIRouter(prefix="/admin/staff", tags=["Admin Payroll"])


# --- Payroll endpoints ---


@router.get("/payroll", response_model=PayrollListResponse)
async def get_payroll(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    month: int | None = Query(default=None),
    year: int | None = Query(default=None),
    status: str | None = Query(default=None),
) -> PayrollListResponse:
    """Get payroll for a given month/year with summary."""
    result = await service.get_payroll(db, school.id, month, year, status)
    return PayrollListResponse(**result)


@router.post("/payroll/run", response_model=RunPayrollResponse)
async def run_payroll(
    data: RunPayrollRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> RunPayrollResponse:
    """Run payroll for a month (generate payslip entries for all active staff)."""
    result = await service.run_payroll(db, school.id, user, data.model_dump())
    return RunPayrollResponse(**result)


@router.post("/payroll/generate-payslips", response_model=GeneratePayslipsResponse)
async def generate_payslips(
    data: GeneratePayslipsRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> GeneratePayslipsResponse:
    """Generate downloadable payslips for all staff."""
    result = await service.generate_payslips(db, school.id, user, data.model_dump())
    return GeneratePayslipsResponse(**result)


@router.put("/payroll/{payslip_id}")
async def update_payslip(
    payslip_id: uuid.UUID,
    data: UpdatePayslipRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Update individual payslip salary components."""
    result = await service.update_payslip(db, school.id, payslip_id, data.model_dump(exclude_none=True))
    return result


@router.post("/payroll/{payslip_id}/pay")
async def record_payment(
    payslip_id: uuid.UUID,
    data: RecordPaymentRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Record partial or full payment on a payslip."""
    result = await service.record_payment(db, school.id, payslip_id, data.model_dump())
    return result


@router.post("/payroll/mark-all-paid")
async def mark_all_paid(
    data: MarkAllPaidRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Mark all unpaid payslips as paid for a given month/year."""
    result = await service.mark_all_paid(db, school.id, data.model_dump())
    return result


@router.post("/payroll/undo-all-paid")
async def undo_all_paid(
    data: MarkAllPaidRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Undo all paid payslips back to unpaid for a given month/year."""
    result = await service.undo_all_paid(db, school.id, data.model_dump())
    return result


@router.get("/payroll/salary-structure/{employee_id}", response_model=SalaryStructureResponse)
async def get_salary_structure(
    employee_id: str,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> SalaryStructureResponse:
    """Get salary breakdown for a staff member. Accepts staff UUID or employee_id string."""
    from sqlalchemy import select as sel
    from src.models.staff import Staff
    from src.core.exceptions import NotFound
    try:
        staff_uuid = uuid.UUID(employee_id)
    except ValueError:
        result = await db.execute(
            sel(Staff).where(Staff.school_id == school.id, Staff.employee_id == employee_id, Staff.is_active.is_(True))
        )
        staff = result.scalar_one_or_none()
        if not staff:
            raise NotFound("Staff", employee_id)
        staff_uuid = staff.id
    result = await service.get_salary_structure(db, school.id, staff_uuid)
    return SalaryStructureResponse(**result)


@router.put("/payroll/salary-structure/{staff_id}")
async def update_salary_structure(
    staff_id: uuid.UUID,
    data: dict,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Update a salary structure — used to activate draft records created on teacher onboarding."""
    result = await service.update_salary_structure(db, school.id, staff_id, data)
    return result


# --- Salary Advances endpoints ---


@router.get("/salary-advances", response_model=SalaryAdvanceListResponse)
async def list_salary_advances(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    pagination: PaginationDep,
    status: str | None = Query(default=None),
) -> SalaryAdvanceListResponse:
    """List salary advance requests with optional status filter."""
    result = await service.list_salary_advances(db, school.id, pagination, status)
    return SalaryAdvanceListResponse(**result)


@router.post("/salary-advances", status_code=201, response_model=SalaryAdvanceCreateResponse)
async def create_salary_advance(
    data: CreateSalaryAdvanceRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> SalaryAdvanceCreateResponse:
    """Create a new salary advance request."""
    result = await service.create_salary_advance(db, school.id, user, data.model_dump())
    return SalaryAdvanceCreateResponse(**result)


@router.post("/salary-advances/{advance_id}/approve", response_model=SalaryAdvanceActionResponse)
async def approve_salary_advance(
    advance_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> SalaryAdvanceActionResponse:
    """Approve a pending salary advance request."""
    result = await service.approve_salary_advance(db, school.id, user, advance_id)
    return SalaryAdvanceActionResponse(**result)


@router.post("/salary-advances/{advance_id}/reject", response_model=SalaryAdvanceActionResponse)
async def reject_salary_advance(
    advance_id: uuid.UUID,
    data: RejectAdvanceRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> SalaryAdvanceActionResponse:
    """Reject a pending salary advance request."""
    result = await service.reject_salary_advance(
        db, school.id, user, advance_id, data.model_dump()
    )
    return SalaryAdvanceActionResponse(**result)


@router.post("/salary-advances/{advance_id}/disburse", response_model=SalaryAdvanceActionResponse)
async def disburse_salary_advance(
    advance_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> SalaryAdvanceActionResponse:
    """Mark an approved advance as disbursed."""
    result = await service.disburse_salary_advance(db, school.id, user, advance_id)
    return SalaryAdvanceActionResponse(**result)


# --- Salary Revisions endpoints ---


@router.get("/payroll/salary-revisions/{staff_id}", response_model=SalaryRevisionHistoryResponse)
async def get_salary_revisions(
    staff_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> SalaryRevisionHistoryResponse:
    """Get salary revision history for a staff member."""
    result = await service.get_salary_revisions(db, school.id, staff_id)
    return SalaryRevisionHistoryResponse(**result)


@router.post("/payroll/salary-revisions", status_code=201, response_model=SalaryRevisionCreateResponse)
async def create_salary_revision(
    data: CreateSalaryRevisionRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> SalaryRevisionCreateResponse:
    """Create a salary revision/hike (updates salary structure)."""
    result = await service.create_salary_revision(db, school.id, user, data.model_dump())
    return SalaryRevisionCreateResponse(**result)
