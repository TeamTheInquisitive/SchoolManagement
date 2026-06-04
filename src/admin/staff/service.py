from __future__ import annotations

import csv
import io
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ConflictError, NotFound
from src.core.pagination import PaginationParams, paginate
from src.models.core import AcademicYear
from src.models.payroll import SalaryStructure
from src.models.staff import Staff

SALARY_FIELDS = {"basic_salary", "hra", "da", "ta", "other_allowances", "pf_deduction", "tax_deduction", "other_deductions"}


def _split_salary_data(data: dict) -> tuple[dict, dict]:
    """Split salary structure fields from staff fields."""
    salary_data = {}
    staff_data = {}
    for k, v in data.items():
        if k in SALARY_FIELDS:
            salary_data[k] = v
        else:
            staff_data[k] = v
    return staff_data, salary_data


async def _get_current_academic_year(db: AsyncSession, school_id: uuid.UUID):
    result = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
            AcademicYear.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


async def _upsert_salary_structure(
    db: AsyncSession, school_id: uuid.UUID, staff_id: uuid.UUID,
    salary_data: dict, created_by: uuid.UUID, joining_date=None,
):
    """Create or update salary structure for a staff member."""
    if not any(v for v in salary_data.values()):
        return
    ay = await _get_current_academic_year(db, school_id)
    if not ay:
        return

    result = await db.execute(
        select(SalaryStructure).where(
            SalaryStructure.school_id == school_id,
            SalaryStructure.staff_id == staff_id,
        )
    )
    ss = result.scalar_one_or_none()

    basic = Decimal(str(salary_data.get("basic_salary") or 0))
    hra = Decimal(str(salary_data.get("hra") or 0))
    da = Decimal(str(salary_data.get("da") or 0))
    ta = Decimal(str(salary_data.get("ta") or 0))
    other_allow = Decimal(str(salary_data.get("other_allowances") or 0))
    pf = Decimal(str(salary_data.get("pf_deduction") or 0))
    tax = Decimal(str(salary_data.get("tax_deduction") or 0))
    other_ded = Decimal(str(salary_data.get("other_deductions") or 0))
    net = basic + hra + da + ta + other_allow - pf - tax - other_ded

    if ss:
        ss.basic_salary = basic
        ss.hra = hra
        ss.da = da
        ss.transport_allowance = ta
        ss.other_allowances = {"other_allowances": float(other_allow)}
        ss.pf_deduction = pf
        ss.tds = tax
        ss.other_deductions = {"other_deductions": float(other_ded)}
        ss.net_salary = net
        ss.is_active = True
        ss.academic_year_id = ay.id
        ss.updated_by = created_by
    else:
        ss = SalaryStructure(
            school_id=school_id,
            staff_id=staff_id,
            academic_year_id=ay.id,
            basic_salary=basic,
            hra=hra,
            da=da,
            transport_allowance=ta,
            other_allowances={"other_allowances": float(other_allow)},
            pf_deduction=pf,
            tds=tax,
            other_deductions={"other_deductions": float(other_ded)},
            net_salary=net,
            effective_from=joining_date or date.today(),
            is_active=True,
            created_by=created_by,
        )
        db.add(ss)


async def _get_salary_for_staff(db: AsyncSession, school_id: uuid.UUID, staff_id: uuid.UUID) -> dict:
    """Get salary structure fields for a staff member."""
    result = await db.execute(
        select(SalaryStructure).where(
            SalaryStructure.school_id == school_id,
            SalaryStructure.staff_id == staff_id,
        )
    )
    ss = result.scalar_one_or_none()
    if not ss:
        return {}
    other_allow = ss.other_allowances.get("other_allowances", 0) if isinstance(ss.other_allowances, dict) else 0
    other_ded = ss.other_deductions.get("other_deductions", 0) if isinstance(ss.other_deductions, dict) else 0
    return {
        "basic_salary": ss.basic_salary,
        "hra": ss.hra,
        "da": ss.da,
        "ta": ss.transport_allowance,
        "other_allowances": Decimal(str(other_allow)),
        "pf_deduction": ss.pf_deduction,
        "tax_deduction": ss.tds,
        "other_deductions": Decimal(str(other_ded)),
    }


def _staff_to_dict(staff: Staff, salary: dict | None = None) -> dict:
    """Convert staff ORM to dict including salary fields."""
    d = {
        "id": staff.id,
        "employee_id": staff.employee_id,
        "full_name": staff.full_name,
        "email": staff.email,
        "phone": staff.phone,
        "department": staff.department,
        "designation": staff.designation,
        "employment_type": staff.employment_type,
        "joining_date": staff.joining_date,
        "salary": staff.salary,
        "is_teacher": staff.is_teacher,
        "status": staff.status,
        "gender": staff.gender,
        "qualification": staff.qualification,
        "experience_years": staff.experience_years,
        "left_date": staff.left_date,
        "left_reason": staff.left_reason,
        "created_at": staff.created_at,
        "bank_name": staff.bank_name,
        "bank_account_number": staff.bank_account_number,
        "bank_ifsc": staff.bank_ifsc,
        "pan_number": staff.pan_number,
        "basic_salary": None,
        "hra": None,
        "da": None,
        "ta": None,
        "other_allowances": None,
        "pf_deduction": None,
        "tax_deduction": None,
        "other_deductions": None,
    }
    if salary:
        d.update(salary)
    return d


async def list_staff(
    db: AsyncSession,
    school_id: uuid.UUID,
    pagination: PaginationParams,
    search: str | None = None,
    department: str | None = None,
    status: str | None = None,
    employment_type: str | None = None,
) -> dict:
    """List staff with filtering and pagination."""
    query = select(Staff).where(
        Staff.school_id == school_id,
        Staff.is_active.is_(True),
    )

    if search:
        search_filter = f"%{search}%"
        query = query.where(
            or_(
                Staff.full_name.ilike(search_filter),
                Staff.email.ilike(search_filter),
                Staff.employee_id.ilike(search_filter),
            )
        )

    if department:
        query = query.where(Staff.department == department)

    if status:
        query = query.where(Staff.status == status)
    else:
        query = query.where(Staff.status == "Active")

    if employment_type:
        query = query.where(Staff.employment_type == employment_type)

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Fetch page
    query = query.order_by(Staff.full_name).offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    staff_list = result.scalars().all()

    # Fetch salary structures for all staff in one query
    staff_ids = [s.id for s in staff_list]
    salary_map = {}
    if staff_ids:
        sal_result = await db.execute(
            select(SalaryStructure).where(
                SalaryStructure.school_id == school_id,
                SalaryStructure.staff_id.in_(staff_ids),
            )
        )
        for ss in sal_result.scalars().all():
            other_allow = ss.other_allowances.get("other_allowances", 0) if isinstance(ss.other_allowances, dict) else 0
            other_ded = ss.other_deductions.get("other_deductions", 0) if isinstance(ss.other_deductions, dict) else 0
            salary_map[ss.staff_id] = {
                "basic_salary": ss.basic_salary,
                "hra": ss.hra,
                "da": ss.da,
                "ta": ss.transport_allowance,
                "other_allowances": Decimal(str(other_allow)),
                "pf_deduction": ss.pf_deduction,
                "tax_deduction": ss.tds,
                "other_deductions": Decimal(str(other_ded)),
            }

    results = [_staff_to_dict(s, salary_map.get(s.id)) for s in staff_list]
    return paginate(results, total, pagination)


async def create_staff(
    db: AsyncSession,
    school_id: uuid.UUID,
    data: dict,
    created_by: uuid.UUID,
) -> dict:
    """Create a new staff member."""
    staff_data, salary_data = _split_salary_data(data)

    # Check duplicate employee_id
    existing = await db.execute(
        select(Staff).where(
            Staff.school_id == school_id,
            Staff.employee_id == staff_data["employee_id"],
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError(
            f"Staff with employee ID {staff_data['employee_id']} already exists",
            {"employee_id": staff_data["employee_id"]},
        )

    # Check duplicate email
    existing_email = await db.execute(
        select(Staff).where(
            Staff.school_id == school_id,
            Staff.email == staff_data["email"],
            Staff.is_active.is_(True),
        )
    )
    if existing_email.scalar_one_or_none():
        raise ConflictError(
            f"Staff with email {staff_data['email']} already exists",
            {"email": staff_data["email"]},
        )

    staff = Staff(
        school_id=school_id,
        created_by=created_by,
        **staff_data,
    )
    db.add(staff)
    await db.flush()

    # Create salary structure if salary fields provided
    if salary_data:
        await _upsert_salary_structure(
            db, school_id, staff.id, salary_data, created_by,
            joining_date=staff_data.get("joining_date"),
        )

    await db.commit()
    await db.refresh(staff)

    salary = await _get_salary_for_staff(db, school_id, staff.id)
    return _staff_to_dict(staff, salary)


async def update_staff(
    db: AsyncSession,
    school_id: uuid.UUID,
    staff_id: uuid.UUID,
    data: dict,
    updated_by: uuid.UUID,
) -> dict:
    """Update a staff member."""
    staff_data, salary_data = _split_salary_data(data)

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

    # Check email uniqueness if changing
    if "email" in staff_data and staff_data["email"] != staff.email:
        existing_email = await db.execute(
            select(Staff).where(
                Staff.school_id == school_id,
                Staff.email == staff_data["email"],
                Staff.is_active.is_(True),
                Staff.id != staff_id,
            )
        )
        if existing_email.scalar_one_or_none():
            raise ConflictError(
                f"Staff with email {staff_data['email']} already exists",
                {"email": staff_data["email"]},
            )

    for key, value in staff_data.items():
        setattr(staff, key, value)

    staff.updated_by = updated_by

    # Update salary structure if salary fields provided
    if salary_data:
        await _upsert_salary_structure(
            db, school_id, staff.id, salary_data, updated_by,
            joining_date=staff.joining_date,
        )

    await db.commit()
    await db.refresh(staff)

    salary = await _get_salary_for_staff(db, school_id, staff.id)
    return _staff_to_dict(staff, salary)


async def delete_staff(
    db: AsyncSession,
    school_id: uuid.UUID,
    staff_id: uuid.UUID,
    deleted_by: uuid.UUID,
    reason: str | None = None,
    left_date_val: date | None = None,
) -> Staff:
    """Soft-delete a staff member (set Inactive)."""
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

    staff.status = "Inactive"
    staff.left_date = left_date_val or date.today()
    staff.left_reason = reason
    staff.updated_by = deleted_by
    await db.commit()
    await db.refresh(staff)
    return staff


async def export_staff_csv(
    db: AsyncSession,
    school_id: uuid.UUID,
    department: str | None = None,
    status: str | None = None,
) -> str:
    """Export staff data as CSV string."""
    query = select(Staff).where(
        Staff.school_id == school_id,
        Staff.is_active.is_(True),
    )

    if department:
        query = query.where(Staff.department == department)

    if status:
        query = query.where(Staff.status == status)

    query = query.order_by(Staff.full_name)
    result = await db.execute(query)
    staff_list = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Employee ID",
        "Full Name",
        "Email",
        "Phone",
        "Department",
        "Designation",
        "Employment Type",
        "Joining Date",
        "Status",
        "Is Teacher",
    ])

    for s in staff_list:
        writer.writerow([
            s.employee_id,
            s.full_name,
            s.email,
            s.phone or "",
            s.department or "",
            s.designation or "",
            s.employment_type or "",
            str(s.joining_date) if s.joining_date else "",
            s.status,
            "Yes" if s.is_teacher else "No",
        ])

    return output.getvalue()
