from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AppException, ConflictError, NotFound
from src.core.pagination import PaginationParams, paginate
from src.models.core import AcademicYear, User
from src.models.leave import LeaveApplication, LeaveBalance, LeavePolicy
from src.models.staff import Staff


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


async def _get_staff_for_user(
    db: AsyncSession, school_id: uuid.UUID, user: User
) -> Staff:
    """Get the staff record linked to the current user."""
    if not user.staff_id:
        raise NotFound("Staff record for current user")
    result = await db.execute(
        select(Staff).where(
            Staff.id == user.staff_id,
            Staff.school_id == school_id,
            Staff.is_active.is_(True),
        )
    )
    staff = result.scalar_one_or_none()
    if not staff:
        raise NotFound("Staff record", str(user.staff_id))
    return staff


async def get_leave_balance(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
) -> dict:
    """Get the authenticated teacher's leave balance."""
    staff = await _get_staff_for_user(db, school_id, user)
    ay = await _get_current_academic_year(db, school_id)

    result = await db.execute(
        select(LeaveBalance, LeavePolicy.display_name)
        .outerjoin(LeavePolicy, and_(
            LeavePolicy.school_id == LeaveBalance.school_id,
            LeavePolicy.academic_year_id == LeaveBalance.academic_year_id,
            LeavePolicy.leave_type == LeaveBalance.leave_type,
            LeavePolicy.is_active.is_(True),
        ))
        .where(
            LeaveBalance.school_id == school_id,
            LeaveBalance.staff_id == staff.id,
            LeaveBalance.academic_year_id == ay.id,
            LeaveBalance.is_active.is_(True),
        )
    )
    rows = result.all()

    balance_items = []
    total_leaves = 0
    total_available = Decimal("0")
    total_used = Decimal("0")
    total_pending = Decimal("0")

    for bal, display_name in rows:
        total = bal.total_allocated + bal.carried_forward
        available = Decimal(total) - bal.used - bal.pending
        balance_items.append(
            {
                "leave_type": bal.leave_type,
                "display_name": display_name or bal.leave_type,
                "total_allocated": total,
                "available": available,
                "used": bal.used,
                "pending": bal.pending,
            }
        )
        total_leaves += total
        total_available += available
        total_used += bal.used
        total_pending += bal.pending

    return {
        "academic_year": ay.name,
        "balances": balance_items,
        "summary": {
            "total_leaves": total_leaves,
            "available": total_available,
            "used": total_used,
            "pending": total_pending,
        },
    }


async def get_leave_history(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    pagination: PaginationParams,
    status: str | None = None,
    leave_type: str | None = None,
) -> dict:
    """Get leave history for the authenticated teacher."""
    staff = await _get_staff_for_user(db, school_id, user)
    ay = await _get_current_academic_year(db, school_id)

    query = select(LeaveApplication).where(
        LeaveApplication.school_id == school_id,
        LeaveApplication.staff_id == staff.id,
        LeaveApplication.academic_year_id == ay.id,
        LeaveApplication.is_active.is_(True),
    )

    if status:
        query = query.where(LeaveApplication.status == status)
    if leave_type:
        query = query.where(LeaveApplication.leave_type == leave_type)

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.order_by(LeaveApplication.applied_on.desc())
    query = query.offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    applications = result.scalars().all()

    items = []
    for app in applications:
        approver_name = None
        if app.approver:
            # Try to get name from related staff
            approver_name = app.approver.email
        items.append(
            {
                "id": app.id,
                "leave_type": app.leave_type,
                "from_date": app.from_date,
                "to_date": app.to_date,
                "duration_days": app.days,
                "is_half_day": app.is_half_day,
                "reason": app.reason,
                "status": app.status,
                "applied_on": app.applied_on,
                "approved_by": approver_name,
                "approved_on": app.approved_on,
                "remarks": app.remarks,
                "metadata": app.metadata_ or {},
            }
        )

    return paginate(items, total, pagination)


async def get_upcoming_leaves(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
) -> dict:
    """Get upcoming/planned leaves (future dates)."""
    staff = await _get_staff_for_user(db, school_id, user)
    today = date.today()

    result = await db.execute(
        select(LeaveApplication)
        .where(
            LeaveApplication.school_id == school_id,
            LeaveApplication.staff_id == staff.id,
            LeaveApplication.to_date >= today,
            LeaveApplication.status.in_(["Approved", "Pending"]),
            LeaveApplication.is_active.is_(True),
        )
        .order_by(LeaveApplication.from_date.asc())
    )
    applications = result.scalars().all()

    items = []
    for app in applications:
        approver_name = None
        if app.approver:
            approver_name = app.approver.email
        # Can cancel only if Pending
        can_cancel = app.status == "Pending"
        items.append(
            {
                "id": app.id,
                "leave_type": app.leave_type,
                "from_date": app.from_date,
                "to_date": app.to_date,
                "duration_days": app.days,
                "reason": app.reason,
                "status": app.status,
                "applied_on": app.applied_on,
                "approved_by": approver_name,
                "can_cancel": can_cancel,
            }
        )

    return {"results": items}


async def apply_leave(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    data: dict,
) -> dict:
    """Apply for leave."""
    staff = await _get_staff_for_user(db, school_id, user)
    ay = await _get_current_academic_year(db, school_id)

    leave_type = data["leave_type"]
    from_date = data["from_date"]
    to_date = data["to_date"]
    reason = data["reason"]
    is_half_day = data.get("is_half_day", False)
    metadata = data.get("metadata", {})

    # Fetch holidays for the school
    from src.models.core import Settings
    from datetime import timedelta

    holiday_dates = set()
    ay_key = f"holidays_{ay.id}" if ay else "holidays"
    hol_result = await db.execute(
        select(Settings).where(
            Settings.school_id == school_id,
            Settings.category == "school",
            Settings.key == ay_key,
            Settings.is_active.is_(True),
        )
    )
    hol_row = hol_result.scalar_one_or_none()
    if hol_row and hol_row.value:
        for h in hol_row.value:
            if isinstance(h, dict) and h.get("date"):
                holiday_dates.add(h["date"])

    # Fetch working days from settings (default: Mon-Sat)
    wd_result = await db.execute(
        select(Settings.value).where(
            Settings.school_id == school_id,
            Settings.category == "general",
            Settings.key == "working_days",
            Settings.is_active.is_(True),
        )
    )
    working_days_list = wd_result.scalar_one_or_none()
    if not isinstance(working_days_list, list) or not working_days_list:
        working_days_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Calculate days (excluding holidays and non-working days)
    if is_half_day:
        date_str = from_date.isoformat()
        day_name = day_names[from_date.weekday()]
        if date_str in holiday_dates:
            raise AppException(
                status_code=400,
                error="Cannot apply half-day leave on a holiday",
                code="HOLIDAY_CONFLICT",
            )
        if day_name not in working_days_list:
            raise AppException(
                status_code=400,
                error=f"Cannot apply leave on {day_name} — it's a non-working day",
                code="NON_WORKING_DAY",
            )
        days = Decimal("0.5")
    else:
        count = 0
        current = from_date
        while current <= to_date:
            date_str = current.isoformat()
            day_name = day_names[current.weekday()]
            if date_str not in holiday_dates and day_name in working_days_list:
                count += 1
            current += timedelta(days=1)
        days = Decimal(str(count))

    if days <= 0:
        raise AppException(
            status_code=400,
            error="Selected dates fall entirely on holidays/non-working days. No working days to apply leave for.",
            code="NO_WORKING_DAYS",
        )

    # Check for date overlap
    overlap_query = select(LeaveApplication).where(
        LeaveApplication.school_id == school_id,
        LeaveApplication.staff_id == staff.id,
        LeaveApplication.status.in_(["Pending", "Approved"]),
        LeaveApplication.from_date <= to_date,
        LeaveApplication.to_date >= from_date,
        LeaveApplication.is_active.is_(True),
    )
    overlap_result = await db.execute(overlap_query)
    if overlap_result.scalar_one_or_none():
        raise ConflictError(
            "You already have a leave application for overlapping dates"
        )

    # Check balance sufficient
    balance = await _get_or_create_balance(
        db, school_id, staff.id, ay.id, leave_type
    )
    total_available = (
        Decimal(balance.total_allocated + balance.carried_forward)
        - balance.used
        - balance.pending
    )
    if days > total_available:
        raise AppException(
            status_code=400,
            error="Insufficient leave balance",
            code="INSUFFICIENT_BALANCE",
            details={
                "leave_type": leave_type,
                "remaining": float(total_available),
                "requested": float(days),
            },
        )

    # Create application
    now = datetime.utcnow()
    application = LeaveApplication(
        school_id=school_id,
        academic_year_id=ay.id,
        staff_id=staff.id,
        leave_type=leave_type,
        from_date=from_date,
        to_date=to_date,
        days=days,
        is_half_day=is_half_day,
        reason=reason,
        status="Pending",
        applied_on=now,
        created_by=user.id,
        metadata_=metadata,
    )
    db.add(application)

    # Increment pending balance
    balance.pending += days

    await db.commit()
    await db.refresh(application)

    return {
        "id": application.id,
        "leave_type": application.leave_type,
        "from_date": application.from_date,
        "to_date": application.to_date,
        "duration_days": application.days,
        "reason": application.reason,
        "status": application.status,
        "applied_on": application.applied_on,
        "approved_by": None,
        "approved_on": None,
        "remarks": None,
        "academic_year": ay.name,
        "metadata": application.metadata_ or {},
    }


async def get_leave_detail(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    leave_id: uuid.UUID,
) -> dict:
    """Get details of a specific leave application."""
    staff = await _get_staff_for_user(db, school_id, user)

    result = await db.execute(
        select(LeaveApplication).where(
            LeaveApplication.id == leave_id,
            LeaveApplication.school_id == school_id,
            LeaveApplication.staff_id == staff.id,
            LeaveApplication.is_active.is_(True),
        )
    )
    application = result.scalar_one_or_none()
    if not application:
        raise NotFound("Leave application", str(leave_id))

    approver_name = None
    if application.approver:
        approver_name = application.approver.email

    substitute_name = None
    if application.substitute_teacher:
        substitute_name = application.substitute_teacher.full_name

    # Get academic year name
    ay_name = ""
    if application.academic_year:
        ay_name = application.academic_year.name

    return {
        "id": application.id,
        "leave_type": application.leave_type,
        "from_date": application.from_date,
        "to_date": application.to_date,
        "duration_days": application.days,
        "reason": application.reason,
        "status": application.status,
        "applied_on": application.applied_on,
        "approved_by": approver_name,
        "approved_on": application.approved_on,
        "remarks": application.remarks,
        "substitute_teacher": substitute_name,
        "academic_year": ay_name,
        "metadata": application.metadata_ or {},
    }


async def cancel_leave(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    leave_id: uuid.UUID,
) -> dict:
    """Cancel a pending leave application (teacher action)."""
    staff = await _get_staff_for_user(db, school_id, user)

    result = await db.execute(
        select(LeaveApplication).where(
            LeaveApplication.id == leave_id,
            LeaveApplication.school_id == school_id,
            LeaveApplication.staff_id == staff.id,
            LeaveApplication.is_active.is_(True),
        )
    )
    application = result.scalar_one_or_none()
    if not application:
        raise NotFound("Leave application", str(leave_id))

    if application.status != "Pending":
        raise AppException(
            status_code=400,
            error="Cannot cancel a leave that has already been approved or rejected",
            code="LEAVE_NOT_CANCELLABLE",
        )

    now = datetime.utcnow()
    application.status = "Cancelled"
    application.cancelled_on = now

    # Restore pending balance
    balance_result = await db.execute(
        select(LeaveBalance).where(
            LeaveBalance.school_id == school_id,
            LeaveBalance.staff_id == staff.id,
            LeaveBalance.academic_year_id == application.academic_year_id,
            LeaveBalance.leave_type == application.leave_type,
            LeaveBalance.is_active.is_(True),
        )
    )
    balance = balance_result.scalar_one_or_none()
    if balance:
        balance.pending -= application.days

    await db.commit()

    return {
        "message": "Leave application cancelled successfully",
        "id": application.id,
        "status": "Cancelled",
        "cancelled_on": now,
    }


async def _get_or_create_balance(
    db: AsyncSession,
    school_id: uuid.UUID,
    staff_id: uuid.UUID,
    academic_year_id: uuid.UUID,
    leave_type: str,
) -> LeaveBalance:
    """Get existing leave balance or create one with defaults."""
    result = await db.execute(
        select(LeaveBalance).where(
            LeaveBalance.school_id == school_id,
            LeaveBalance.staff_id == staff_id,
            LeaveBalance.academic_year_id == academic_year_id,
            LeaveBalance.leave_type == leave_type,
            LeaveBalance.is_active.is_(True),
        )
    )
    balance = result.scalar_one_or_none()
    if not balance:
        # Look up policy for default allocation
        policy_result = await db.execute(
            select(LeavePolicy).where(
                LeavePolicy.school_id == school_id,
                LeavePolicy.academic_year_id == academic_year_id,
                LeavePolicy.leave_type == leave_type,
                LeavePolicy.is_active.is_(True),
            )
        )
        policy = policy_result.scalar_one_or_none()
        total_allocated = policy.total_per_year if policy else 0

        balance = LeaveBalance(
            school_id=school_id,
            staff_id=staff_id,
            academic_year_id=academic_year_id,
            leave_type=leave_type,
            total_allocated=total_allocated,
            carried_forward=0,
            used=Decimal("0"),
            pending=Decimal("0"),
        )
        db.add(balance)
        await db.flush()

    return balance


async def get_holidays(
    db: AsyncSession,
    school_id: uuid.UUID,
) -> dict:
    """Get holidays and working days for leave day calculation."""
    from src.models.core import Settings

    ay = await _get_current_academic_year(db, school_id)
    ay_key = f"holidays_{ay.id}" if ay else "holidays"

    result = await db.execute(
        select(Settings).where(
            Settings.school_id == school_id,
            Settings.category == "school",
            Settings.key == ay_key,
            Settings.is_active.is_(True),
        )
    )
    row = result.scalar_one_or_none()
    holidays = row.value if row and row.value else []

    # Fetch working days
    wd_result = await db.execute(
        select(Settings.value).where(
            Settings.school_id == school_id,
            Settings.category == "general",
            Settings.key == "working_days",
            Settings.is_active.is_(True),
        )
    )
    working_days = wd_result.scalar_one_or_none()
    if not isinstance(working_days, list) or not working_days:
        working_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    return {"holidays": holidays, "working_days": working_days, "academic_year": ay.name if ay else None}
