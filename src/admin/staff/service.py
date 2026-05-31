from __future__ import annotations

import csv
import io
import uuid
from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ConflictError, NotFound
from src.core.pagination import PaginationParams, paginate
from src.models.staff import Staff


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

    return paginate(staff_list, total, pagination)


async def create_staff(
    db: AsyncSession,
    school_id: uuid.UUID,
    data: dict,
    created_by: uuid.UUID,
) -> Staff:
    """Create a new staff member."""
    # Check duplicate employee_id
    existing = await db.execute(
        select(Staff).where(
            Staff.school_id == school_id,
            Staff.employee_id == data["employee_id"],
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError(
            f"Staff with employee ID {data['employee_id']} already exists",
            {"employee_id": data["employee_id"]},
        )

    # Check duplicate email
    existing_email = await db.execute(
        select(Staff).where(
            Staff.school_id == school_id,
            Staff.email == data["email"],
            Staff.is_active.is_(True),
        )
    )
    if existing_email.scalar_one_or_none():
        raise ConflictError(
            f"Staff with email {data['email']} already exists",
            {"email": data["email"]},
        )

    staff = Staff(
        school_id=school_id,
        created_by=created_by,
        **data,
    )
    db.add(staff)
    await db.commit()
    await db.refresh(staff)
    return staff


async def update_staff(
    db: AsyncSession,
    school_id: uuid.UUID,
    staff_id: uuid.UUID,
    data: dict,
    updated_by: uuid.UUID,
) -> Staff:
    """Update a staff member."""
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
    if "email" in data and data["email"] != staff.email:
        existing_email = await db.execute(
            select(Staff).where(
                Staff.school_id == school_id,
                Staff.email == data["email"],
                Staff.is_active.is_(True),
                Staff.id != staff_id,
            )
        )
        if existing_email.scalar_one_or_none():
            raise ConflictError(
                f"Staff with email {data['email']} already exists",
                {"email": data["email"]},
            )

    for key, value in data.items():
        setattr(staff, key, value)

    staff.updated_by = updated_by
    await db.commit()
    await db.refresh(staff)
    return staff


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
