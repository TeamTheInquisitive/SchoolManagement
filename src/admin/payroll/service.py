from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AppException, NotFound
from src.core.pagination import PaginationParams, paginate
from src.models.core import AcademicYear, User
from src.models.payroll import Payslip, SalaryAdvance, SalaryRevision, SalaryStructure
from src.models.staff import Staff


MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


async def _get_current_academic_year(
    db: AsyncSession, school_id: uuid.UUID
) -> AcademicYear:
    """Get the current academic year for the school."""
    result = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
            AcademicYear.is_active.is_(True),
        )
    )
    ay = result.scalar_one_or_none()
    if not ay:
        raise NotFound("Current academic year")
    return ay


async def _get_staff_by_id(
    db: AsyncSession, school_id: uuid.UUID, staff_id: uuid.UUID
) -> Staff:
    """Get a staff member by ID."""
    result = await db.execute(
        select(Staff).where(
            Staff.id == staff_id,
            Staff.school_id == school_id,
            Staff.is_active.is_(True),
        )
    )
    staff = result.scalar_one_or_none()
    if not staff:
        raise NotFound("Staff", str(staff_id))
    return staff


def _compute_net_salary(structure: SalaryStructure) -> Decimal:
    """Compute net salary from salary structure components."""
    total_allowances = (
        structure.hra
        + structure.da
        + structure.transport_allowance
        + structure.medical_allowance
    )
    # Add other allowances (JSONB values)
    if structure.other_allowances:
        for value in structure.other_allowances.values():
            total_allowances += Decimal(str(value))

    total_deductions = (
        structure.pf_deduction + structure.professional_tax + structure.tds
    )
    # Add other deductions (JSONB values)
    if structure.other_deductions:
        for value in structure.other_deductions.values():
            total_deductions += Decimal(str(value))

    return structure.basic_salary + total_allowances - total_deductions


async def get_payroll(
    db: AsyncSession,
    school_id: uuid.UUID,
    month: int | None = None,
    year: int | None = None,
    status: str | None = None,
) -> dict:
    """Get payroll for a given month/year with summary."""
    ay = await _get_current_academic_year(db, school_id)

    now = datetime.now(timezone.utc)
    if not month:
        month = now.month
    if not year:
        year = now.year

    query = select(Payslip).where(
        Payslip.school_id == school_id,
        Payslip.month == month,
        Payslip.year == year,
        Payslip.is_active.is_(True),
    )

    if status:
        query = query.where(Payslip.status == status)

    result = await db.execute(query)
    payslips = result.scalars().all()

    items = []
    total_disbursed = Decimal("0")
    pending_amount = Decimal("0")
    pending_count = 0

    for payslip in payslips:
        staff = payslip.staff
        remaining = payslip.net_salary - (payslip.paid_amount or Decimal("0"))
        items.append({
            "id": payslip.id,
            "employee_id": staff.employee_id if staff else "",
            "employee_name": staff.full_name if staff else "",
            "basic_salary": payslip.basic_salary,
            "hra": payslip.hra or Decimal("0"),
            "da": payslip.da or Decimal("0"),
            "transport_allowance": payslip.transport_allowance or Decimal("0"),
            "allowances": payslip.total_allowances,
            "deductions": payslip.total_deductions,
            "net_salary": payslip.net_salary,
            "paid_amount": payslip.paid_amount or Decimal("0"),
            "status": payslip.status,
            "paid_on": payslip.paid_on,
        })

        total_disbursed += payslip.paid_amount or Decimal("0")
        if payslip.status != "Paid":
            pending_amount += remaining
            pending_count += 1

    return {
        "month": MONTH_NAMES[month],
        "year": year,
        "results": items,
        "summary": {
            "total_staff": len(payslips),
            "total_disbursed": total_disbursed,
            "pending_amount": pending_amount,
            "pending_count": pending_count,
        },
    }


async def run_payroll(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    data: dict,
) -> dict:
    """Run payroll for a month: generate payslip entries for all active staff."""
    ay = await _get_current_academic_year(db, school_id)

    month = data["month"]
    year = data["year"]
    now = datetime.now(timezone.utc)

    # Check if payroll already run for this month
    existing = await db.execute(
        select(func.count()).select_from(Payslip).where(
            Payslip.school_id == school_id,
            Payslip.month == month,
            Payslip.year == year,
            Payslip.is_active.is_(True),
        )
    )
    if (existing.scalar() or 0) > 0:
        raise AppException(
            status_code=409,
            error=f"Payroll already generated for {MONTH_NAMES[month]} {year}",
            code="PAYROLL_ALREADY_GENERATED",
        )

    # Get all active staff with salary structures
    structures_result = await db.execute(
        select(SalaryStructure).where(
            SalaryStructure.school_id == school_id,
            SalaryStructure.is_active.is_(True),
        )
    )
    structures = structures_result.scalars().all()

    if not structures:
        raise AppException(
            status_code=400,
            error="No active salary structures found. Configure salary structures first.",
            code="NO_SALARY_STRUCTURES",
        )

    generated = 0
    total_amount = Decimal("0")

    for structure in structures:
        # Compute allowances and deductions
        total_allowances = (
            structure.hra
            + structure.da
            + structure.transport_allowance
            + structure.medical_allowance
        )
        if structure.other_allowances:
            for value in structure.other_allowances.values():
                total_allowances += Decimal(str(value))

        total_deductions = (
            structure.pf_deduction + structure.professional_tax + structure.tds
        )
        if structure.other_deductions:
            for value in structure.other_deductions.values():
                total_deductions += Decimal(str(value))

        net = structure.basic_salary + total_allowances - total_deductions

        payslip = Payslip(
            school_id=school_id,
            staff_id=structure.staff_id,
            academic_year_id=ay.id,
            month=month,
            year=year,
            basic_salary=structure.basic_salary,
            hra=structure.hra,
            da=structure.da,
            transport_allowance=structure.transport_allowance,
            total_allowances=total_allowances,
            total_deductions=total_deductions,
            net_salary=net,
            paid_amount=Decimal("0"),
            status="Unpaid",
            generated_at=now,
            generated_by=user.id,
            created_by=user.id,
        )
        db.add(payslip)
        generated += 1
        total_amount += net

    await db.commit()

    return {
        "generated": generated,
        "total_amount": total_amount,
        "message": f"Payroll generated for {generated} staff members",
    }


async def generate_payslips(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    data: dict,
) -> dict:
    """Generate downloadable payslips for a given month/year."""
    month = data["month"]
    year = data["year"]

    result = await db.execute(
        select(func.count()).select_from(Payslip).where(
            Payslip.school_id == school_id,
            Payslip.month == month,
            Payslip.year == year,
            Payslip.is_active.is_(True),
        )
    )
    count = result.scalar() or 0

    if count == 0:
        raise NotFound("Payslips", f"{MONTH_NAMES[month]} {year}")

    download_url = f"/api/v1/admin/payroll/payslips/download/?month={month}&year={year}"

    return {
        "generated": count,
        "download_url": download_url,
    }


async def update_payslip(
    db: AsyncSession,
    school_id: uuid.UUID,
    payslip_id: uuid.UUID,
    data: dict,
) -> dict:
    """Update a payslip's salary components."""
    result = await db.execute(
        select(Payslip).where(
            Payslip.id == payslip_id,
            Payslip.school_id == school_id,
            Payslip.is_active.is_(True),
        )
    )
    payslip = result.scalar_one_or_none()
    if not payslip:
        raise NotFound("Payslip", str(payslip_id))

    for field in ["basic_salary", "hra", "da", "transport_allowance", "total_allowances", "total_deductions", "net_salary"]:
        if field in data and data[field] is not None:
            setattr(payslip, field, Decimal(str(data[field])))

    await db.commit()
    await db.refresh(payslip)
    staff = payslip.staff
    return {
        "id": payslip.id,
        "employee_name": staff.full_name if staff else "",
        "basic_salary": payslip.basic_salary,
        "hra": payslip.hra,
        "da": payslip.da,
        "transport_allowance": payslip.transport_allowance,
        "allowances": payslip.total_allowances,
        "deductions": payslip.total_deductions,
        "net_salary": payslip.net_salary,
        "paid_amount": payslip.paid_amount,
        "status": payslip.status,
    }


async def record_payment(
    db: AsyncSession,
    school_id: uuid.UUID,
    payslip_id: uuid.UUID,
    data: dict,
) -> dict:
    """Record a partial or full payment on a payslip."""
    result = await db.execute(
        select(Payslip).where(
            Payslip.id == payslip_id,
            Payslip.school_id == school_id,
            Payslip.is_active.is_(True),
        )
    )
    payslip = result.scalar_one_or_none()
    if not payslip:
        raise NotFound("Payslip", str(payslip_id))

    amount = Decimal(str(data["amount"]))
    payslip.paid_amount = (payslip.paid_amount or Decimal("0")) + amount
    payslip.payment_method = data.get("payment_method")
    payslip.paid_on = date.today()

    if payslip.paid_amount >= payslip.net_salary:
        payslip.status = "Paid"
    elif payslip.paid_amount > Decimal("0"):
        payslip.status = "Partially Paid"

    await db.commit()
    await db.refresh(payslip)
    return {
        "id": payslip.id,
        "paid_amount": payslip.paid_amount,
        "status": payslip.status,
    }


async def mark_all_paid(
    db: AsyncSession,
    school_id: uuid.UUID,
    data: dict,
) -> dict:
    """Mark all unpaid/partially paid payslips as fully paid for a month."""
    month = data["month"]
    year = data["year"]

    result = await db.execute(
        select(Payslip).where(
            Payslip.school_id == school_id,
            Payslip.month == month,
            Payslip.year == year,
            Payslip.status.in_(["Unpaid", "Partially Paid", "Generated"]),
            Payslip.is_active.is_(True),
        )
    )
    payslips = result.scalars().all()
    today = date.today()
    count = 0
    for p in payslips:
        p.paid_amount = p.net_salary
        p.status = "Paid"
        p.paid_on = today
        p.payment_method = "Bulk"
        count += 1

    await db.commit()
    return {"updated": count, "message": f"Marked {count} payslips as paid"}


async def get_salary_structure(
    db: AsyncSession,
    school_id: uuid.UUID,
    employee_id: uuid.UUID,
) -> dict:
    """Get salary breakdown for a staff member."""
    staff = await _get_staff_by_id(db, school_id, employee_id)

    result = await db.execute(
        select(SalaryStructure).where(
            SalaryStructure.school_id == school_id,
            SalaryStructure.staff_id == staff.id,
            SalaryStructure.is_active.is_(True),
        )
    )
    structure = result.scalar_one_or_none()
    if not structure:
        raise NotFound("Salary structure", str(employee_id))

    allowances = {
        "transport": structure.transport_allowance,
        "medical": structure.medical_allowance,
    }
    if structure.other_allowances:
        allowances.update(structure.other_allowances)

    deductions = {
        "pf": structure.pf_deduction,
        "professional_tax": structure.professional_tax,
        "tds": structure.tds,
    }
    if structure.other_deductions:
        deductions.update(structure.other_deductions)

    return {
        "employee_id": staff.employee_id,
        "employee_name": staff.full_name,
        "basic": structure.basic_salary,
        "hra": structure.hra,
        "da": structure.da,
        "allowances": allowances,
        "deductions": deductions,
        "net_salary": structure.net_salary,
    }


async def update_salary_structure(
    db: AsyncSession,
    school_id: uuid.UUID,
    staff_id: uuid.UUID,
    data: dict,
) -> dict:
    """Update a salary structure — activate draft records created on teacher onboarding."""
    from decimal import Decimal

    result = await db.execute(
        select(SalaryStructure).where(
            SalaryStructure.school_id == school_id,
            SalaryStructure.staff_id == staff_id,
        ).order_by(SalaryStructure.created_at.desc())
    )
    structure = result.scalars().first()
    if not structure:
        raise NotFound("Salary structure", str(staff_id))

    for k, v in data.items():
        if k == "is_active" and v is True:
            structure.is_active = True
        elif hasattr(structure, k) and v is not None:
            setattr(structure, k, v)

    # Recalculate net salary if basic changed
    if "basic_salary" in data or "is_active" in data:
        total_allowances = (
            (structure.hra or Decimal("0")) +
            (structure.da or Decimal("0")) +
            (structure.transport_allowance or Decimal("0")) +
            (structure.medical_allowance or Decimal("0"))
        )
        total_deductions = (
            (structure.pf_deduction or Decimal("0")) +
            (structure.professional_tax or Decimal("0")) +
            (structure.tds or Decimal("0"))
        )
        structure.net_salary = structure.basic_salary + total_allowances - total_deductions

    await db.commit()
    await db.refresh(structure)

    staff = await _get_staff_by_id(db, school_id, staff_id)

    return {
        "id": str(structure.id),
        "staff_id": str(staff_id),
        "employee_name": staff.full_name,
        "basic_salary": float(structure.basic_salary),
        "hra": float(structure.hra),
        "da": float(structure.da),
        "net_salary": float(structure.net_salary),
        "is_active": structure.is_active,
        "effective_from": str(structure.effective_from),
    }


async def list_salary_advances(
    db: AsyncSession,
    school_id: uuid.UUID,
    pagination: PaginationParams,
    status: str | None = None,
) -> dict:
    """List salary advance requests with optional status filter."""
    query = select(SalaryAdvance).where(
        SalaryAdvance.school_id == school_id,
        SalaryAdvance.is_active.is_(True),
    )

    if status:
        query = query.where(SalaryAdvance.status == status)

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.order_by(SalaryAdvance.applied_on.desc())
    query = query.offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    advances = result.scalars().all()

    items = []
    for advance in advances:
        staff = advance.staff
        items.append({
            "id": advance.id,
            "employee_id": staff.employee_id if staff else "",
            "employee_name": staff.full_name if staff else "",
            "amount": advance.amount,
            "reason": advance.reason,
            "recovery_months": advance.recovery_months,
            "per_month_deduction": advance.per_month_deduction,
            "status": advance.status,
            "applied_on": advance.applied_on,
        })

    return paginate(items, total, pagination)


async def create_salary_advance(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    data: dict,
) -> dict:
    """Create a new salary advance request."""
    staff_id = data["staff_id"]
    staff = await _get_staff_by_id(db, school_id, staff_id)

    amount = Decimal(str(data["amount"]))
    recovery_months = data.get("recovery_months")
    per_month_deduction = None
    if recovery_months and recovery_months > 0:
        per_month_deduction = amount / Decimal(str(recovery_months))

    now = datetime.now(timezone.utc)

    advance = SalaryAdvance(
        school_id=school_id,
        staff_id=staff.id,
        amount=amount,
        reason=data.get("reason"),
        recovery_months=recovery_months,
        per_month_deduction=per_month_deduction,
        status="Pending",
        applied_on=now,
        created_by=user.id,
    )
    db.add(advance)
    await db.commit()
    await db.refresh(advance)

    return {
        "id": advance.id,
        "staff_id": staff.id,
        "employee_id": staff.employee_id,
        "employee_name": staff.full_name,
        "amount": advance.amount,
        "reason": advance.reason,
        "recovery_months": advance.recovery_months,
        "per_month_deduction": advance.per_month_deduction,
        "status": advance.status,
        "applied_on": advance.applied_on,
    }


async def approve_salary_advance(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    advance_id: uuid.UUID,
) -> dict:
    """Approve a pending salary advance request."""
    result = await db.execute(
        select(SalaryAdvance).where(
            SalaryAdvance.id == advance_id,
            SalaryAdvance.school_id == school_id,
            SalaryAdvance.is_active.is_(True),
        )
    )
    advance = result.scalar_one_or_none()
    if not advance:
        raise NotFound("Salary advance", str(advance_id))

    if advance.status != "Pending":
        raise AppException(
            status_code=400,
            error=f"Cannot approve advance with status '{advance.status}'. Only Pending advances can be approved.",
            code="INVALID_STATUS_TRANSITION",
        )

    now = datetime.now(timezone.utc)
    advance.status = "Approved"
    advance.approved_by = user.id
    advance.approved_on = now
    advance.updated_by = user.id

    await db.commit()
    await db.refresh(advance)

    # Get approver name
    approver_result = await db.execute(select(User).where(User.id == user.id))
    approver = approver_result.scalar_one_or_none()

    return {
        "id": advance.id,
        "status": advance.status,
        "approved_by": approver.email if approver else None,
        "approved_on": advance.approved_on,
    }


async def reject_salary_advance(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    advance_id: uuid.UUID,
    data: dict,
) -> dict:
    """Reject a pending salary advance request."""
    result = await db.execute(
        select(SalaryAdvance).where(
            SalaryAdvance.id == advance_id,
            SalaryAdvance.school_id == school_id,
            SalaryAdvance.is_active.is_(True),
        )
    )
    advance = result.scalar_one_or_none()
    if not advance:
        raise NotFound("Salary advance", str(advance_id))

    if advance.status != "Pending":
        raise AppException(
            status_code=400,
            error=f"Cannot reject advance with status '{advance.status}'. Only Pending advances can be rejected.",
            code="INVALID_STATUS_TRANSITION",
        )

    advance.status = "Rejected"
    advance.rejected_by = user.id
    advance.remarks = data.get("remarks")
    advance.updated_by = user.id

    await db.commit()
    await db.refresh(advance)

    return {
        "id": advance.id,
        "status": advance.status,
        "remarks": advance.remarks,
    }


async def disburse_salary_advance(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    advance_id: uuid.UUID,
) -> dict:
    """Mark an approved advance as disbursed."""
    result = await db.execute(
        select(SalaryAdvance).where(
            SalaryAdvance.id == advance_id,
            SalaryAdvance.school_id == school_id,
            SalaryAdvance.is_active.is_(True),
        )
    )
    advance = result.scalar_one_or_none()
    if not advance:
        raise NotFound("Salary advance", str(advance_id))

    if advance.status != "Approved":
        raise AppException(
            status_code=400,
            error=f"Cannot disburse advance with status '{advance.status}'. Only Approved advances can be disbursed.",
            code="INVALID_STATUS_TRANSITION",
        )

    now = datetime.now(timezone.utc)
    advance.status = "Disbursed"
    advance.disbursed_on = now
    advance.updated_by = user.id

    await db.commit()
    await db.refresh(advance)

    return {
        "id": advance.id,
        "status": advance.status,
        "disbursed_on": advance.disbursed_on,
    }


async def get_salary_revisions(
    db: AsyncSession,
    school_id: uuid.UUID,
    staff_id: uuid.UUID,
) -> dict:
    """Get salary revision history for a staff member."""
    staff = await _get_staff_by_id(db, school_id, staff_id)

    result = await db.execute(
        select(SalaryRevision).where(
            SalaryRevision.school_id == school_id,
            SalaryRevision.staff_id == staff.id,
            SalaryRevision.is_active.is_(True),
        ).order_by(SalaryRevision.effective_date.desc())
    )
    revisions = result.scalars().all()

    # Get current basic from salary structure
    structure_result = await db.execute(
        select(SalaryStructure).where(
            SalaryStructure.school_id == school_id,
            SalaryStructure.staff_id == staff.id,
            SalaryStructure.is_active.is_(True),
        )
    )
    structure = structure_result.scalar_one_or_none()
    current_basic = structure.basic_salary if structure else Decimal("0")

    items = []
    for revision in revisions:
        items.append({
            "id": revision.id,
            "previous_basic": revision.previous_basic,
            "new_basic": revision.new_basic,
            "revision_type": revision.revision_type,
            "percentage": revision.percentage,
            "increment_amount": revision.increment_amount,
            "effective_date": revision.effective_date,
            "remarks": revision.remarks,
            "created_at": revision.created_at,
        })

    return {
        "staff_id": staff.id,
        "employee_name": staff.full_name,
        "current_basic": current_basic,
        "revisions": items,
    }


async def create_salary_revision(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    data: dict,
) -> dict:
    """Create a salary revision/hike and update the salary structure."""
    ay = await _get_current_academic_year(db, school_id)

    staff_id = data["staff_id"]
    staff = await _get_staff_by_id(db, school_id, staff_id)

    # Get current salary structure
    structure_result = await db.execute(
        select(SalaryStructure).where(
            SalaryStructure.school_id == school_id,
            SalaryStructure.staff_id == staff.id,
            SalaryStructure.is_active.is_(True),
        )
    )
    structure = structure_result.scalar_one_or_none()
    if not structure:
        raise NotFound("Salary structure", str(staff_id))

    previous_basic = structure.basic_salary
    new_basic = Decimal(str(data["new_basic"]))
    increment_amount = new_basic - previous_basic
    percentage = data.get("percentage")
    if percentage is not None:
        percentage = Decimal(str(percentage))

    now = datetime.now(timezone.utc)

    # Create revision record
    revision = SalaryRevision(
        school_id=school_id,
        staff_id=staff.id,
        academic_year_id=ay.id,
        effective_date=data["effective_date"],
        previous_basic=previous_basic,
        new_basic=new_basic,
        revision_type=data["revision_type"],
        percentage=percentage,
        increment_amount=increment_amount,
        approved_by=user.id,
        approved_on=now,
        remarks=data.get("remarks"),
        created_by=user.id,
    )
    db.add(revision)

    # Update salary structure with new basic and recompute net
    structure.basic_salary = new_basic
    structure.net_salary = _compute_net_salary(structure)
    structure.updated_by = user.id

    await db.commit()
    await db.refresh(revision)

    return {
        "id": revision.id,
        "staff_id": staff.id,
        "previous_basic": previous_basic,
        "new_basic": new_basic,
        "revision_type": revision.revision_type,
        "percentage": revision.percentage,
        "increment_amount": increment_amount,
        "effective_date": revision.effective_date,
    }
