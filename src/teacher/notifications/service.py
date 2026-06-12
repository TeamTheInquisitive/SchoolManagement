from src.student.notifications.service import list_notifications, get_notification, mark_as_read  # noqa: F401

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.pagination import PaginationParams, paginate
from src.models.core import User
from src.models.notification import Notification


async def list_sent_notifications(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    pagination: PaginationParams,
) -> dict:
    """Get notifications sent by this teacher."""
    query = select(Notification).where(
        Notification.school_id == school_id,
        Notification.created_by_user_id == user.id,
        Notification.is_active.is_(True),
    )

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(Notification.sent_at.desc().nulls_last(), Notification.created_at.desc())
    query = query.offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    notifications = result.scalars().all()

    items = [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "type": n.type,
            "target_type": n.target_type,
            "target_class_name": n.target_class_name,
            "recipients_count": n.recipients_count,
            "status": n.status,
            "sent_at": n.sent_at,
            "is_read": True,
        }
        for n in notifications
    ]

    return paginate(items, total, pagination)
