from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import and_, case, func, select
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


async def list_leave_applications(
    db: AsyncSession,
    school_id: uuid.UUID,
    pagination: PaginationParams,
    status: str | None = None,
    teacher_id: uuid.UUID | None = None,
    leave_type: str | None = None,
    department: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> dict:
    """List all leave applications with filters and overall summary."""
    ay = await _get_current_academic_year(db, school_id)

    query = select(LeaveApplication).where(
        LeaveApplication.school_id == school_id,
        LeaveApplication.academic_year_id == ay.id,
        LeaveApplication.is_active.is_(True),
    )

    if status:
        query = query.where(LeaveApplication.status == status)
    if teacher_id:
        query = query.where(LeaveApplication.staff_id == teacher_id)
    if leave_type:
        query = query.where(LeaveApplication.leave_type == leave_type)
    if from_date:
        query = query.where(LeaveApplication.from_date >= from_date)
    if to_date:
        query = query.where(LeaveApplication.to_date <= to_date)
    if department:
        query = query.join(Staff, LeaveApplication.staff_id == Staff.id).where(
            Staff.department == department
        )

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.order_by(LeaveApplication.applied_on.desc())
    query = query.offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    applications = result.scalars().all()

    # Build results
    items = []
    for app in applications:
        staff = app.staff
        items.append(
            {
                "id": app.id,
                "teacher_id": app.staff_id,
                "employee_id": staff.employee_id if staff else "",
                "teacher_name": staff.full_name if staff else "",
                "department": staff.department if staff else None,
                "leave_type": app.leave_type,
                "from_date": app.from_date,
                "to_date": app.to_date,
                "days": app.days,
                "is_half_day": app.is_half_day,
                "reason": app.reason,
                "status": app.status,
                "applied_on": app.applied_on,
                "approved_by": app.approver.email if app.approver else None,
                "approved_on": app.approved_on,
                "rejected_by": app.rejector.email if app.rejector else None,
                "rejected_on": app.rejected_on,
                "remarks": app.remarks,
                "substitute_teacher": (
                    app.substitute_teacher.full_name if app.substitute_teacher else None
                ),
                "substitute_teacher_id": app.substitute_teacher_id,
            }
        )

    # Overall summary
    summary_query = select(
        func.count().label("total"),
        func.sum(case((LeaveApplication.status == "Approved", 1), else_=0)).label("approved"),
        func.sum(case((LeaveApplication.status == "Pending", 1), else_=0)).label("pending"),
        func.sum(case((LeaveApplication.status == "Rejected", 1), else_=0)).label("rejected"),
    ).where(
        LeaveApplication.school_id == school_id,
        LeaveApplication.academic_year_id == ay.id,
        LeaveApplication.is_active.is_(True),
    )
    summary_result = await db.execute(summary_query)
    summary_row = summary_result.one()

    # On leave today
    today = date.today()
    on_leave_query = select(func.count()).where(
        LeaveApplication.school_id == school_id,
        LeaveApplication.academic_year_id == ay.id,
        LeaveApplication.status == "Approved",
        LeaveApplication.from_date <= today,
        LeaveApplication.to_date >= today,
        LeaveApplication.is_active.is_(True),
    )
    on_leave_today = (await db.execute(on_leave_query)).scalar() or 0

    paginated = paginate(items, total, pagination)
    paginated["overall_summary"] = {
        "total_applications": summary_row.total or 0,
        "approved": summary_row.approved or 0,
        "pending": summary_row.pending or 0,
        "rejected": summary_row.rejected or 0,
        "on_leave_today": on_leave_today,
    }
    return paginated


async def get_teacher_leave_detail(
    db: AsyncSession,
    school_id: uuid.UUID,
    teacher_id: uuid.UUID,
) -> dict:
    """Get leave balance and history for a specific teacher."""
    ay = await _get_current_academic_year(db, school_id)

    # Get staff info
    staff_result = await db.execute(
        select(Staff).where(Staff.id == teacher_id, Staff.school_id == school_id)
    )
    staff = staff_result.scalar_one_or_none()
    if not staff:
        raise NotFound("Teacher", str(teacher_id))

    # Get balances
    balances_result = await db.execute(
        select(LeaveBalance).where(
            LeaveBalance.school_id == school_id,
            LeaveBalance.staff_id == teacher_id,
            LeaveBalance.academic_year_id == ay.id,
            LeaveBalance.is_active.is_(True),
        )
    )
    balances = balances_result.scalars().all()

    # Get display names from policies
    policies_result = await db.execute(
        select(LeavePolicy).where(
            LeavePolicy.school_id == school_id,
            LeavePolicy.academic_year_id == ay.id,
            LeavePolicy.is_active.is_(True),
        )
    )
    policy_display_map = {}
    for p in policies_result.scalars().all():
        policy_display_map[p.leave_type] = p.display_name or p.leave_type

    leave_balance: dict = {}
    total_allocated = 0
    total_availed = Decimal("0")
    total_pending = Decimal("0")
    total_remaining = Decimal("0")

    for bal in balances:
        available = Decimal(bal.total_allocated + bal.carried_forward) - bal.used - bal.pending
        display = policy_display_map.get(bal.leave_type, bal.leave_type)
        key = bal.leave_type.lower().replace(" leave", "").replace(" ", "_")
        leave_balance[key] = {
            "label": display,
            "total": bal.total_allocated + bal.carried_forward,
            "availed": bal.used,
            "pending": bal.pending,
            "remaining": available,
        }
        total_allocated += bal.total_allocated + bal.carried_forward
        total_availed += bal.used
        total_pending += bal.pending
        total_remaining += available

    # Get history
    history_result = await db.execute(
        select(LeaveApplication)
        .where(
            LeaveApplication.school_id == school_id,
            LeaveApplication.staff_id == teacher_id,
            LeaveApplication.academic_year_id == ay.id,
            LeaveApplication.is_active.is_(True),
        )
        .order_by(LeaveApplication.applied_on.desc())
    )
    applications = history_result.scalars().all()

    leave_history = [
        {
            "id": app.id,
            "leave_type": app.leave_type,
            "from_date": app.from_date,
            "to_date": app.to_date,
            "days": app.days,
            "is_half_day": app.is_half_day,
            "reason": app.reason,
            "status": app.status,
            "applied_on": app.applied_on,
        }
        for app in applications
    ]

    return {
        "teacher_id": staff.id,
        "employee_id": staff.employee_id,
        "teacher_name": staff.full_name,
        "department": staff.department,
        "academic_year": ay.name,
        "leave_balance": leave_balance,
        "total_summary": {
            "total_allocated": total_allocated,
            "total_availed": total_availed,
            "total_pending": total_pending,
            "total_remaining": total_remaining,
        },
        "leave_history": leave_history,
    }


async def get_all_balances(
    db: AsyncSession,
    school_id: uuid.UUID,
    department: str | None = None,
    search: str | None = None,
) -> dict:
    """Get leave balances for all teachers at a glance."""
    ay = await _get_current_academic_year(db, school_id)

    # Get all teaching staff
    staff_query = select(Staff).where(
        Staff.school_id == school_id,
        Staff.is_teacher.is_(True),
        Staff.is_active.is_(True),
    )
    if department:
        staff_query = staff_query.where(Staff.department == department)
    if search:
        staff_query = staff_query.where(Staff.full_name.ilike(f"%{search}%"))

    staff_result = await db.execute(staff_query)
    all_staff = staff_result.scalars().all()

    results = []
    for s in all_staff:
        balances_result = await db.execute(
            select(LeaveBalance).where(
                LeaveBalance.school_id == school_id,
                LeaveBalance.staff_id == s.id,
                LeaveBalance.academic_year_id == ay.id,
                LeaveBalance.is_active.is_(True),
            )
        )
        balances = balances_result.scalars().all()

        item: dict = {
            "teacher_id": s.id,
            "employee_id": s.employee_id,
            "teacher_name": s.full_name,
            "department": s.department,
            "total_availed": Decimal("0"),
            "total_remaining": Decimal("0"),
            "is_active": s.is_active,
        }

        for bal in balances:
            total = bal.total_allocated + bal.carried_forward
            remaining = Decimal(total) - bal.used - bal.pending
            balance_info = {
                "total": total,
                "availed": bal.used,
                "pending": bal.pending,
                "remaining": remaining,
            }
            key = bal.leave_type.lower().replace(" leave", "").replace(" ", "_")
            item[key] = balance_info
            item["total_availed"] += bal.used
            item["total_remaining"] += remaining

        results.append(item)

    return {
        "academic_year": ay.name,
        "results": results,
    }


async def get_leave_policy(
    db: AsyncSession,
    school_id: uuid.UUID,
) -> dict:
    """Get leave policy configuration for the current academic year."""
    ay = await _get_current_academic_year(db, school_id)

    result = await db.execute(
        select(LeavePolicy).where(
            LeavePolicy.school_id == school_id,
            LeavePolicy.academic_year_id == ay.id,
            LeavePolicy.is_active.is_(True),
        )
    )
    policies = result.scalars().all()

    leave_types = []
    for p in policies:
        applicable_to = p.applicable_to or "all"
        if applicable_to != "all" and "," in applicable_to:
            applicable_to = applicable_to.split(",")
        elif applicable_to != "all":
            applicable_to = [applicable_to]
        leave_types.append({
            "type": p.leave_type,
            "display_name": p.display_name,
            "code": p.code,
            "total_per_year": p.total_per_year,
            "carry_forward": p.carry_forward,
            "max_carry_forward": p.max_carry_forward,
            "max_consecutive_days": p.max_consecutive_days,
            "requires_approval": p.requires_approval,
            "half_day_allowed": p.half_day_allowed,
            "medical_certificate_required_after_days": p.medical_certificate_required_after_days,
            "advance_notice_days": p.advance_notice_days,
            "applicable_to": applicable_to,
            "members": p.members,
        })

    return {
        "academic_year": ay.name,
        "leave_types": leave_types,
    }


async def update_leave_policy(
    db: AsyncSession,
    school_id: uuid.UUID,
    data: dict,
) -> dict:
    """Update leave policy for the current academic year."""
    ay = await _get_current_academic_year(db, school_id)

    # Validate leave types
    leave_types = data.get("leave_types", [])
    for lt in leave_types:
        if not lt.get("type") or not str(lt["type"]).strip():
            raise AppException(
                status_code=400,
                error="Leave type name must not be empty",
                code="VALIDATION_ERROR",
            )
        if not lt.get("total_per_year") or lt["total_per_year"] <= 0:
            raise AppException(
                status_code=400,
                error="Leave total_per_year must be greater than 0",
                code="VALIDATION_ERROR",
            )

    # Delete existing policies for this academic year
    existing_result = await db.execute(
        select(LeavePolicy).where(
            LeavePolicy.school_id == school_id,
            LeavePolicy.academic_year_id == ay.id,
        )
    )
    for p in existing_result.scalars().all():
        await db.delete(p)
    await db.flush()
    new_policies = []
    for lt in leave_types:
        # Handle applicable_to - store as comma-separated string for list, or "all"
        applicable_to = lt.get("applicable_to", "all")
        if isinstance(applicable_to, list):
            applicable_to = ",".join(applicable_to)

        policy = LeavePolicy(
            school_id=school_id,
            academic_year_id=ay.id,
            leave_type=lt["type"],
            display_name=lt.get("display_name"),
            code=lt.get("code"),
            total_per_year=lt["total_per_year"],
            carry_forward=lt.get("carry_forward", False),
            max_carry_forward=lt.get("max_carry_forward"),
            max_consecutive_days=lt.get("max_consecutive_days"),
            requires_approval=lt.get("requires_approval", True),
            half_day_allowed=lt.get("half_day_allowed", False),
            medical_certificate_required_after_days=lt.get(
                "medical_certificate_required_after_days"
            ),
            advance_notice_days=lt.get("advance_notice_days"),
            applicable_to=applicable_to,
            members=lt.get("members"),
        )
        db.add(policy)
        new_policies.append(policy)

    await db.flush()

    # Build a set of valid (leave_type, staff_id) pairs from new policies
    valid_balance_keys: set[tuple[str, uuid.UUID]] = set()

    # Allocate leave balances to applicable staff
    for policy in new_policies:
        applicable_to = policy.applicable_to or "all"
        members = policy.members

        staff_query = select(Staff).where(
            Staff.school_id == school_id,
            Staff.is_active.is_(True),
        )

        if members and isinstance(members, list) and len(members) > 0:
            # Specific member IDs
            staff_ids = [uuid.UUID(m) if isinstance(m, str) else m for m in members]
            staff_query = staff_query.where(Staff.id.in_(staff_ids))
        elif applicable_to != "all":
            # Specific departments
            departments = [d.strip() for d in applicable_to.split(",") if d.strip()]
            if departments:
                staff_query = staff_query.where(Staff.department.in_(departments))

        staff_result = await db.execute(staff_query)
        staff_list = staff_result.scalars().all()

        for staff in staff_list:
            valid_balance_keys.add((policy.leave_type, staff.id))
            existing_bal = await db.execute(
                select(LeaveBalance).where(
                    LeaveBalance.school_id == school_id,
                    LeaveBalance.staff_id == staff.id,
                    LeaveBalance.academic_year_id == ay.id,
                    LeaveBalance.leave_type == policy.leave_type,
                )
            )
            balance = existing_bal.scalar_one_or_none()
            if balance:
                balance.total_allocated = policy.total_per_year
                balance.is_active = True
            else:
                balance = LeaveBalance(
                    school_id=school_id,
                    staff_id=staff.id,
                    academic_year_id=ay.id,
                    leave_type=policy.leave_type,
                    total_allocated=policy.total_per_year,
                    carried_forward=0,
                    used=Decimal("0"),
                    pending=Decimal("0"),
                )
                db.add(balance)

    await db.flush()

    # Deactivate leave balances that are no longer valid:
    # - Leave types that were removed
    # - Staff members who are no longer in the applicable departments/members
    all_balances_result = await db.execute(
        select(LeaveBalance).where(
            LeaveBalance.school_id == school_id,
            LeaveBalance.academic_year_id == ay.id,
            LeaveBalance.is_active.is_(True),
        )
    )
    for balance in all_balances_result.scalars().all():
        if (balance.leave_type, balance.staff_id) not in valid_balance_keys:
            balance.is_active = False

    await db.commit()

    return {
        "message": f"Leave policy updated for academic year {ay.name}",
        "academic_year": ay.name,
        "leave_types": [
            {
                "type": p.leave_type,
                "display_name": p.display_name,
                "code": p.code,
                "total_per_year": p.total_per_year,
                "carry_forward": p.carry_forward,
                "max_carry_forward": p.max_carry_forward,
                "max_consecutive_days": p.max_consecutive_days,
                "requires_approval": p.requires_approval,
                "half_day_allowed": p.half_day_allowed,
                "medical_certificate_required_after_days": p.medical_certificate_required_after_days,
                "advance_notice_days": p.advance_notice_days,
                "applicable_to": p.applicable_to.split(",") if p.applicable_to and p.applicable_to != "all" else p.applicable_to or "all",
                "members": p.members,
            }
            for p in new_policies
        ],
    }


async def approve_leave(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    leave_id: uuid.UUID,
    remarks: str | None = None,
    substitute_teacher_id: uuid.UUID | None = None,
) -> dict:
    """Approve a pending or rejected leave application."""
    result = await db.execute(
        select(LeaveApplication).where(
            LeaveApplication.id == leave_id,
            LeaveApplication.school_id == school_id,
            LeaveApplication.is_active.is_(True),
        )
    )
    application = result.scalar_one_or_none()
    if not application:
        raise NotFound("Leave application", str(leave_id))

    if application.status not in ("Pending", "Rejected"):
        raise ConflictError(
            f"Cannot approve a leave that is already {application.status}"
        )

    previous_status = application.status
    now = datetime.utcnow()
    application.status = "Approved"
    application.approved_by = user.id
    application.approved_on = now
    application.rejected_by = None
    application.rejected_on = None
    application.remarks = remarks
    if substitute_teacher_id:
        application.substitute_teacher_id = substitute_teacher_id

    # Update balance
    balance = await _get_or_create_balance(
        db, school_id, application.staff_id, application.academic_year_id, application.leave_type
    )
    if previous_status == "Pending":
        balance.pending -= application.days
    balance.used += application.days

    await db.commit()
    await db.refresh(application)

    # Build balance response
    total = Decimal(balance.total_allocated + balance.carried_forward)
    remaining = total - balance.used - balance.pending
    key = application.leave_type.lower().replace(" leave", "").replace(" ", "_")

    substitute_name = None
    if application.substitute_teacher:
        substitute_name = application.substitute_teacher.full_name

    return {
        "id": application.id,
        "status": "Approved",
        "approved_by": user.email,
        "approved_on": now,
        "substitute_teacher": substitute_name,
        "substitute_teacher_id": substitute_teacher_id,
        "leave_balance_after": {
            key: {
                "total": int(total),
                "availed": balance.used,
                "pending": balance.pending,
                "remaining": remaining,
            }
        },
    }


async def reject_leave(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    leave_id: uuid.UUID,
    remarks: str,
) -> dict:
    """Reject a pending or approved leave application."""
    result = await db.execute(
        select(LeaveApplication).where(
            LeaveApplication.id == leave_id,
            LeaveApplication.school_id == school_id,
            LeaveApplication.is_active.is_(True),
        )
    )
    application = result.scalar_one_or_none()
    if not application:
        raise NotFound("Leave application", str(leave_id))

    if application.status not in ("Pending", "Approved"):
        raise ConflictError(
            f"Cannot reject a leave that is already {application.status}"
        )

    previous_status = application.status
    now = datetime.utcnow()
    application.status = "Rejected"
    application.rejected_by = user.id
    application.rejected_on = now
    application.approved_by = None
    application.approved_on = None
    application.remarks = remarks

    # Restore balance
    balance = await _get_or_create_balance(
        db, school_id, application.staff_id, application.academic_year_id, application.leave_type
    )
    if previous_status == "Pending":
        balance.pending -= application.days
    elif previous_status == "Approved":
        balance.used -= application.days

    await db.commit()

    return {
        "id": application.id,
        "status": "Rejected",
        "rejected_by": user.email,
        "rejected_on": now,
        "remarks": remarks,
    }


async def cancel_leave(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    leave_id: uuid.UUID,
    reason: str | None = None,
) -> dict:
    """Cancel an approved or pending leave application (admin action)."""
    result = await db.execute(
        select(LeaveApplication).where(
            LeaveApplication.id == leave_id,
            LeaveApplication.school_id == school_id,
            LeaveApplication.is_active.is_(True),
        )
    )
    application = result.scalar_one_or_none()
    if not application:
        raise NotFound("Leave application", str(leave_id))

    if application.status not in ("Approved", "Pending"):
        raise ConflictError(
            f"Cannot cancel a leave that is already {application.status}"
        )

    previous_status = application.status
    now = datetime.utcnow()
    application.status = "Cancelled"
    application.cancelled_on = now
    if reason:
        application.remarks = reason

    # Restore balance
    balance = await _get_or_create_balance(
        db, school_id, application.staff_id, application.academic_year_id, application.leave_type
    )
    if previous_status == "Approved":
        balance.used -= application.days
    elif previous_status == "Pending":
        balance.pending -= application.days

    await db.commit()
    await db.refresh(balance)

    total = Decimal(balance.total_allocated + balance.carried_forward)
    remaining = total - balance.used - balance.pending
    key = application.leave_type.lower().replace(" leave", "").replace(" ", "_")

    return {
        "id": application.id,
        "status": "Cancelled",
        "cancelled_by": user.email,
        "cancelled_on": now,
        "days_restored": application.days,
        "leave_balance_after": {
            key: {
                "total": int(total),
                "availed": balance.used,
                "pending": balance.pending,
                "remaining": remaining,
            }
        },
    }


async def bulk_action(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    action: str,
    leave_ids: list[uuid.UUID],
    remarks: str | None = None,
) -> dict:
    """Bulk approve or reject leave applications."""
    # Validate action
    if action not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="action must be 'approve' or 'reject'")
    # Validate leave_ids not empty
    if not leave_ids:
        raise HTTPException(status_code=400, detail="leave_ids must not be empty")

    results = []
    for leave_id in leave_ids:
        try:
            if action == "approve":
                res = await approve_leave(db, school_id, user, leave_id, remarks)
            else:
                res = await reject_leave(
                    db, school_id, user, leave_id, remarks or "Rejected in bulk"
                )
            results.append({"id": leave_id, "status": res["status"]})
        except (NotFound, ConflictError):
            results.append({"id": leave_id, "status": "Failed"})

    return {
        "processed": len(results),
        "action": action,
        "results": results,
    }


async def get_calendar(
    db: AsyncSession,
    school_id: uuid.UUID,
    from_date: date,
    to_date: date,
    department: str | None = None,
) -> dict:
    """Get calendar view showing who is on leave for a date range."""
    query = select(LeaveApplication).where(
        LeaveApplication.school_id == school_id,
        LeaveApplication.status == "Approved",
        LeaveApplication.from_date <= to_date,
        LeaveApplication.to_date >= from_date,
        LeaveApplication.is_active.is_(True),
    )

    if department:
        query = query.join(Staff, LeaveApplication.staff_id == Staff.id).where(
            Staff.department == department
        )

    result = await db.execute(query)
    applications = result.scalars().all()

    leaves_by_date: dict[str, list[dict]] = {}
    total_leave_days = 0

    for app in applications:
        staff = app.staff
        current_date = max(app.from_date, from_date)
        end = min(app.to_date, to_date)
        while current_date <= end:
            date_key = current_date.isoformat()
            if date_key not in leaves_by_date:
                leaves_by_date[date_key] = []
            leaves_by_date[date_key].append(
                {
                    "teacher_id": app.staff_id,
                    "teacher_name": staff.full_name if staff else "",
                    "leave_type": app.leave_type,
                    "is_half_day": app.is_half_day,
                }
            )
            total_leave_days += 1
            current_date += timedelta(days=1)

    # Identify conflict dates (more than 1 person on leave)
    conflict_dates = [d for d, entries in leaves_by_date.items() if len(entries) > 1]

    return {
        "from_date": from_date,
        "to_date": to_date,
        "leaves_by_date": leaves_by_date,
        "conflict_dates": conflict_dates,
        "total_leave_days_this_month": total_leave_days,
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


async def allocate_leaves(
    db: AsyncSession,
    school_id: uuid.UUID,
    data: dict,
) -> dict:
    """Allocate leave balances to selected staff members."""
    ay = await _get_current_academic_year(db, school_id)
    staff_ids = data["staff_ids"]
    leave_types = data["leave_types"]  # {"Casual Leave": 12, "Sick Leave": 10}

    if not staff_ids:
        raise AppException(status_code=400, error="No staff members selected for allocation", code="NO_STAFF_SELECTED")
    if not leave_types:
        raise AppException(status_code=400, error="No leave types specified for allocation", code="NO_LEAVE_TYPES")

    # Validate all leave type values are > 0
    for leave_type_name, total in leave_types.items():
        if total is None or total <= 0:
            raise AppException(
                status_code=400,
                error=f"Leave allocation value for '{leave_type_name}' must be greater than 0",
                code="VALIDATION_ERROR",
            )

    count = 0
    for staff_id in staff_ids:
        # Validate staff exists
        staff_result = await db.execute(
            select(Staff).where(
                Staff.id == staff_id,
                Staff.school_id == school_id,
                Staff.is_active.is_(True),
            )
        )
        staff = staff_result.scalar_one_or_none()
        if not staff:
            continue  # Skip invalid/inactive staff

        for leave_type, total in leave_types.items():
            if total <= 0:
                continue
            # Query without is_active filter to avoid unique constraint violations
            result = await db.execute(
                select(LeaveBalance).where(
                    LeaveBalance.school_id == school_id,
                    LeaveBalance.staff_id == staff_id,
                    LeaveBalance.academic_year_id == ay.id,
                    LeaveBalance.leave_type == leave_type,
                )
            )
            balance = result.scalar_one_or_none()
            if balance:
                balance.total_allocated = total
                balance.is_active = True
            else:
                balance = LeaveBalance(
                    school_id=school_id,
                    staff_id=staff_id,
                    academic_year_id=ay.id,
                    leave_type=leave_type,
                    total_allocated=total,
                    carried_forward=0,
                    used=Decimal("0"),
                    pending=Decimal("0"),
                )
                db.add(balance)
            count += 1

    await db.commit()
    return {
        "allocated_count": count,
        "staff_count": len(staff_ids),
        "message": f"Successfully allocated leaves to {len(staff_ids)} employee(s)",
    }
