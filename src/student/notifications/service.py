from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFound
from src.core.pagination import PaginationParams, paginate
from src.models.core import User
from src.models.notification import Notification, NotificationRecipient


# ────────────────────────────────────────────────────────────────────────────────
# List student notifications
# ────────────────────────────────────────────────────────────────────────────────


async def list_notifications(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    pagination: PaginationParams,
    type: str | None = None,
    is_read: bool | None = None,
) -> dict:
    """List notifications for the authenticated student."""
    base_query = (
        select(NotificationRecipient, Notification)
        .join(Notification, Notification.id == NotificationRecipient.notification_id)
        .where(
            NotificationRecipient.school_id == school_id,
            NotificationRecipient.user_id == user.id,
            NotificationRecipient.is_active.is_(True),
            Notification.is_active.is_(True),
            Notification.status != "Archived",
        )
    )

    count_query = (
        select(func.count(NotificationRecipient.id))
        .join(Notification, Notification.id == NotificationRecipient.notification_id)
        .where(
            NotificationRecipient.school_id == school_id,
            NotificationRecipient.user_id == user.id,
            NotificationRecipient.is_active.is_(True),
            Notification.is_active.is_(True),
            Notification.status != "Archived",
        )
    )

    # Apply filters
    if type:
        base_query = base_query.where(Notification.type == type)
        count_query = count_query.where(Notification.type == type)

    if is_read is not None:
        base_query = base_query.where(NotificationRecipient.is_read == is_read)
        count_query = count_query.where(NotificationRecipient.is_read == is_read)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    result = await db.execute(
        base_query.order_by(Notification.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    )
    rows = result.all()

    # Get unread count
    unread_result = await db.execute(
        select(func.count(NotificationRecipient.id))
        .join(Notification, Notification.id == NotificationRecipient.notification_id)
        .where(
            NotificationRecipient.school_id == school_id,
            NotificationRecipient.user_id == user.id,
            NotificationRecipient.is_active.is_(True),
            NotificationRecipient.is_read.is_(False),
            Notification.is_active.is_(True),
            Notification.status != "Archived",
        )
    )
    unread_count = unread_result.scalar() or 0

    # Format results
    items = []
    for recipient, notification in rows:
        items.append(
            {
                "id": recipient.id,
                "notification_id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.type,
                "is_read": recipient.is_read,
                "read_at": recipient.read_at,
                "sent_at": notification.sent_at,
                "created_at": notification.created_at,
            }
        )

    paginated = paginate(items, total, pagination)
    paginated["unread_count"] = unread_count
    return paginated


# ────────────────────────────────────────────────────────────────────────────────
# Get notification detail
# ────────────────────────────────────────────────────────────────────────────────


async def get_notification(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    recipient_id: uuid.UUID,
) -> dict:
    """Get a specific notification detail for the student."""
    result = await db.execute(
        select(NotificationRecipient, Notification)
        .join(Notification, Notification.id == NotificationRecipient.notification_id)
        .where(
            NotificationRecipient.id == recipient_id,
            NotificationRecipient.school_id == school_id,
            NotificationRecipient.user_id == user.id,
            NotificationRecipient.is_active.is_(True),
            Notification.is_active.is_(True),
        )
    )
    row = result.one_or_none()
    if not row:
        raise NotFound("Notification", str(recipient_id))

    recipient, notification = row

    return {
        "id": recipient.id,
        "notification_id": notification.id,
        "title": notification.title,
        "message": notification.message,
        "type": notification.type,
        "send_via": notification.send_via,
        "is_read": recipient.is_read,
        "read_at": recipient.read_at,
        "sent_at": notification.sent_at,
        "created_at": notification.created_at,
    }


# ────────────────────────────────────────────────────────────────────────────────
# Mark as read
# ────────────────────────────────────────────────────────────────────────────────


async def mark_as_read(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    recipient_id: uuid.UUID,
) -> dict:
    """Mark a notification as read. Updates read_at and increments Notification.read_count."""
    result = await db.execute(
        select(NotificationRecipient).where(
            NotificationRecipient.id == recipient_id,
            NotificationRecipient.school_id == school_id,
            NotificationRecipient.user_id == user.id,
            NotificationRecipient.is_active.is_(True),
        )
    )
    recipient = result.scalar_one_or_none()
    if not recipient:
        raise NotFound("Notification", str(recipient_id))

    now = datetime.now(timezone.utc)

    # Only update if not already read
    if not recipient.is_read:
        recipient.is_read = True
        recipient.read_at = now

        # Increment Notification.read_count
        notif_result = await db.execute(
            select(Notification).where(Notification.id == recipient.notification_id)
        )
        notification = notif_result.scalar_one_or_none()
        if notification:
            notification.read_count = (notification.read_count or 0) + 1

        await db.commit()
        await db.refresh(recipient)

    return {
        "id": recipient.id,
        "is_read": recipient.is_read,
        "read_at": recipient.read_at,
        "message": "Notification marked as read.",
    }
