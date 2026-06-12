from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFound
from src.core.pagination import PaginationParams, paginate
from src.models.core import User
from src.models.staff import Staff
from src.models.notification import Notification, NotificationRecipient
from src.models.student import Student, StudentEnrollment
from src.models.academic import ClassSection, Class, Section


# ────────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────────


def _format_target(notification: Notification) -> str:
    """Format target_type into a human-readable string."""
    mapping = {
        "all": "All",
        "students": "All Students",
        "teaching_staff": "Teaching Staff",
        "non_teaching_staff": "Non-Teaching Staff",
        "parents": "All Parents",
    }
    if notification.target_type == "specific_class":
        parts = []
        if notification.target_class_name:
            parts.append(f"Class {notification.target_class_name}")
        if notification.target_section:
            parts.append(f"Section {notification.target_section}")
        return " - ".join(parts) if parts else "Specific Class"
    return mapping.get(notification.target_type, notification.target_type)


def _format_read_rate(recipients_count: int, read_count: int) -> str:
    """Format read rate as percentage string."""
    if recipients_count == 0:
        return "0%"
    rate = round((read_count / recipients_count) * 100)
    return f"{rate}%"


async def _resolve_recipients(
    db: AsyncSession,
    school_id: uuid.UUID,
    target_type: str,
    target_class_name: str | None,
    target_section: str | None,
) -> list[uuid.UUID]:
    """Resolve target audience to a list of user IDs."""
    if target_type == "all":
        result = await db.execute(
            select(User.id).where(
                User.school_id == school_id,
                User.is_active.is_(True),
            )
        )
        return list(result.scalars().all())

    elif target_type == "students":
        result = await db.execute(
            select(User.id).where(
                User.school_id == school_id,
                User.role == "student",
                User.is_active.is_(True),
            )
        )
        return list(result.scalars().all())

    elif target_type == "teaching_staff":
        result = await db.execute(
            select(User.id).where(
                User.school_id == school_id,
                User.role == "teacher",
                User.is_active.is_(True),
            )
        )
        return list(result.scalars().all())

    elif target_type == "non_teaching_staff":
        # Non-teaching staff: users with role admin who are staff but not teachers
        # or staff role users who are not teachers
        result = await db.execute(
            select(User.id)
            .join(Staff, Staff.id == User.staff_id)
            .where(
                User.school_id == school_id,
                User.is_active.is_(True),
                Staff.is_teacher.is_(False),
                Staff.is_active.is_(True),
            )
        )
        return list(result.scalars().all())

    elif target_type == "parents":
        result = await db.execute(
            select(User.id).where(
                User.school_id == school_id,
                User.role == "parent",
                User.is_active.is_(True),
            )
        )
        return list(result.scalars().all())

    elif target_type == "specific_class":
        # Find students enrolled in the specific class/section
        query = (
            select(User.id)
            .join(Student, Student.id == User.student_id)
            .join(StudentEnrollment, StudentEnrollment.student_id == Student.id)
            .join(ClassSection, ClassSection.id == StudentEnrollment.class_section_id)
            .join(Class, Class.id == ClassSection.class_id)
        )

        conditions = [
            User.school_id == school_id,
            User.is_active.is_(True),
            User.role == "student",
            StudentEnrollment.is_active.is_(True),
            Class.is_active.is_(True),
        ]

        if target_class_name:
            conditions.append(Class.name == target_class_name)

        if target_section:
            query = query.join(Section, Section.id == ClassSection.section_id)
            conditions.append(Section.name == target_section)

        result = await db.execute(query.where(and_(*conditions)))
        return list(result.scalars().all())

    return []


# ────────────────────────────────────────────────────────────────────────────────
# List notifications
# ────────────────────────────────────────────────────────────────────────────────


async def list_notifications(
    db: AsyncSession,
    school_id: uuid.UUID,
    pagination: PaginationParams,
    search: str | None = None,
    type: str | None = None,
    status: str | None = None,
    target_type: str | None = None,
) -> dict:
    """List notifications with filters and summary KPIs."""
    base_query = select(Notification).where(
        Notification.school_id == school_id,
        Notification.is_active.is_(True),
    )

    count_query = select(func.count(Notification.id)).where(
        Notification.school_id == school_id,
        Notification.is_active.is_(True),
    )

    # Apply filters
    if search:
        search_filter = or_(
            Notification.title.ilike(f"%{search}%"),
            Notification.message.ilike(f"%{search}%"),
        )
        base_query = base_query.where(search_filter)
        count_query = count_query.where(search_filter)

    if type:
        base_query = base_query.where(Notification.type == type)
        count_query = count_query.where(Notification.type == type)

    if status:
        base_query = base_query.where(Notification.status == status)
        count_query = count_query.where(Notification.status == status)

    if target_type:
        base_query = base_query.where(Notification.target_type == target_type)
        count_query = count_query.where(Notification.target_type == target_type)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    result = await db.execute(
        base_query.order_by(Notification.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    )
    notifications = list(result.scalars().all())

    # Build summary KPIs
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    sent_count_result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.school_id == school_id,
            Notification.is_active.is_(True),
            Notification.status == "Sent",
        )
    )
    total_sent = sent_count_result.scalar() or 0

    this_month_result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.school_id == school_id,
            Notification.is_active.is_(True),
            Notification.status == "Sent",
            Notification.sent_at >= month_start,
        )
    )
    this_month = this_month_result.scalar() or 0

    scheduled_result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.school_id == school_id,
            Notification.is_active.is_(True),
            Notification.status == "Scheduled",
        )
    )
    scheduled = scheduled_result.scalar() or 0

    # Average read rate
    avg_result = await db.execute(
        select(
            func.coalesce(func.sum(Notification.read_count), 0),
            func.coalesce(func.sum(Notification.recipients_count), 0),
        ).where(
            Notification.school_id == school_id,
            Notification.is_active.is_(True),
            Notification.status == "Sent",
            Notification.recipients_count > 0,
        )
    )
    avg_row = avg_result.one()
    total_read = int(avg_row[0])
    total_recipients = int(avg_row[1])
    average_read_rate = (
        round((total_read / total_recipients) * 100) if total_recipients > 0 else 0
    )

    # Format results
    items = []
    for n in notifications:
        items.append(
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "target": _format_target(n),
                "type": n.type,
                "send_via": n.send_via,
                "date": n.sent_at.strftime("%Y-%m-%d") if n.sent_at else (
                    n.created_at.strftime("%Y-%m-%d") if n.created_at else None
                ),
                "status": n.status,
                "read_rate": _format_read_rate(n.recipients_count, n.read_count),
                "recipients_count": n.recipients_count,
                "scheduled_at": n.scheduled_at,
            }
        )

    paginated = paginate(items, total, pagination)
    paginated["summary"] = {
        "total_sent": total_sent,
        "this_month": this_month,
        "scheduled": scheduled,
        "average_read_rate": average_read_rate,
    }
    return paginated


# ────────────────────────────────────────────────────────────────────────────────
# Create notification
# ────────────────────────────────────────────────────────────────────────────────


async def create_notification(
    db: AsyncSession,
    school_id: uuid.UUID,
    data: dict,
    user_id: uuid.UUID,
) -> dict:
    """Create and send (or schedule) a notification."""
    from fastapi import HTTPException

    # Validate required fields
    if not data.get("title") or not str(data["title"]).strip():
        raise HTTPException(status_code=400, detail="Notification title must not be empty")
    if not data.get("message") or not str(data["message"]).strip():
        raise HTTPException(status_code=400, detail="Notification message must not be empty")

    schedule_for_later = data.pop("schedule_for_later", False)
    scheduled_at = data.get("scheduled_at")

    now = datetime.now(timezone.utc)

    # Determine status
    if schedule_for_later and scheduled_at:
        status = "Scheduled"
        sent_at = None
    else:
        status = "Sent"
        sent_at = now

    notification = Notification(
        school_id=school_id,
        title=data["title"],
        message=data["message"],
        type=data.get("type"),
        target_type=data["target_type"],
        target_class_name=data.get("target_class_name"),
        target_section=data.get("target_section"),
        send_via=data.get("send_via", "in_app"),
        status=status,
        scheduled_at=scheduled_at if schedule_for_later else None,
        sent_at=sent_at,
        recipients_count=0,
        read_count=0,
        created_by=user_id,
        created_by_user_id=user_id,
    )
    db.add(notification)
    await db.flush()

    # Resolve recipients and create records
    if status == "Sent":
        user_ids = await _resolve_recipients(
            db,
            school_id,
            data["target_type"],
            data.get("target_class_name"),
            data.get("target_section"),
        )

        for uid in user_ids:
            recipient = NotificationRecipient(
                school_id=school_id,
                notification_id=notification.id,
                user_id=uid,
                is_read=False,
                created_by=user_id,
            )
            db.add(recipient)

        notification.recipients_count = len(user_ids)

    await db.commit()
    await db.refresh(notification)

    return {
        "id": notification.id,
        "title": notification.title,
        "message": notification.message,
        "type": notification.type,
        "target_type": notification.target_type,
        "target": _format_target(notification),
        "send_via": notification.send_via,
        "status": notification.status,
        "scheduled_at": notification.scheduled_at,
        "recipients_count": notification.recipients_count,
        "created_at": notification.created_at,
    }


# ────────────────────────────────────────────────────────────────────────────────
# Get notification detail
# ────────────────────────────────────────────────────────────────────────────────


async def get_notification(
    db: AsyncSession,
    school_id: uuid.UUID,
    notification_id: uuid.UUID,
) -> dict:
    """Get notification details with delivery stats."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.school_id == school_id,
            Notification.is_active.is_(True),
        )
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise NotFound("Notification", str(notification_id))

    # Get creator name
    created_by_name = None
    if notification.created_by_user_id:
        user_result = await db.execute(
            select(User).where(User.id == notification.created_by_user_id)
        )
        creator = user_result.scalar_one_or_none()
        if creator:
            # Try to get staff name
            if creator.staff_id:
                staff_result = await db.execute(
                    select(Staff).where(Staff.id == creator.staff_id)
                )
                staff = staff_result.scalar_one_or_none()
                if staff:
                    created_by_name = staff.full_name
            if not created_by_name:
                created_by_name = creator.email

    return {
        "id": notification.id,
        "title": notification.title,
        "message": notification.message,
        "type": notification.type,
        "target": _format_target(notification),
        "target_type": notification.target_type,
        "target_class_name": notification.target_class_name,
        "target_section": notification.target_section,
        "send_via": notification.send_via,
        "date": notification.sent_at.strftime("%Y-%m-%d") if notification.sent_at else (
            notification.created_at.strftime("%Y-%m-%d") if notification.created_at else None
        ),
        "status": notification.status,
        "read_rate": _format_read_rate(
            notification.recipients_count, notification.read_count
        ),
        "recipients_count": notification.recipients_count,
        "read_count": notification.read_count,
        "scheduled_at": notification.scheduled_at,
        "created_by": created_by_name,
        "created_at": notification.created_at,
    }


# ────────────────────────────────────────────────────────────────────────────────
# Update notification
# ────────────────────────────────────────────────────────────────────────────────


async def update_notification(
    db: AsyncSession,
    school_id: uuid.UUID,
    notification_id: uuid.UUID,
    data: dict,
    user_id: uuid.UUID,
) -> dict:
    """Update a notification's title, message, and other editable fields."""
    from fastapi import HTTPException

    # Validate title and message if provided
    if "title" in data and (not data["title"] or not str(data["title"]).strip()):
        raise HTTPException(status_code=400, detail="Notification title must not be empty")
    if "message" in data and (not data["message"] or not str(data["message"]).strip()):
        raise HTTPException(status_code=400, detail="Notification message must not be empty")

    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.school_id == school_id,
            Notification.is_active.is_(True),
        )
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise NotFound("Notification", str(notification_id))

    # Update fields
    for key, value in data.items():
        if value is not None and hasattr(notification, key):
            setattr(notification, key, value)

    notification.updated_by = user_id
    await db.commit()
    await db.refresh(notification)

    return {
        "id": notification.id,
        "title": notification.title,
        "message": notification.message,
        "type": notification.type,
        "target": _format_target(notification),
        "target_type": notification.target_type,
        "target_class_name": notification.target_class_name,
        "target_section": notification.target_section,
        "send_via": notification.send_via,
        "date": notification.sent_at.strftime("%Y-%m-%d") if notification.sent_at else (
            notification.created_at.strftime("%Y-%m-%d") if notification.created_at else None
        ),
        "status": notification.status,
        "read_rate": _format_read_rate(
            notification.recipients_count, notification.read_count
        ),
        "recipients_count": notification.recipients_count,
        "read_count": notification.read_count,
        "scheduled_at": notification.scheduled_at,
        "created_by": None,
        "created_at": notification.created_at,
    }


# ────────────────────────────────────────────────────────────────────────────────
# Archive (soft-delete) notification
# ────────────────────────────────────────────────────────────────────────────────


async def archive_notification(
    db: AsyncSession,
    school_id: uuid.UUID,
    notification_id: uuid.UUID,
    user_id: uuid.UUID,
) -> dict:
    """Archive a notification (soft-delete). Sets status to Archived."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.school_id == school_id,
            Notification.is_active.is_(True),
        )
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise NotFound("Notification", str(notification_id))

    now = datetime.now(timezone.utc)
    notification.status = "Archived"
    notification.archived_at = now
    notification.updated_by = user_id

    await db.commit()
    await db.refresh(notification)

    return {
        "id": notification.id,
        "title": notification.title,
        "status": "Archived",
        "archived_on": now.strftime("%Y-%m-%d"),
        "message": "Notification archived. Delivery records preserved.",
    }
