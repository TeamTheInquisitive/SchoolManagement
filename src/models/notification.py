from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Index, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base_model import BaseModel, UUIDType


class Notification(BaseModel):
    """Notification sent by admin/staff to targeted audience."""

    __tablename__ = "notifications"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    target_type: Mapped[str] = mapped_column(String(30), nullable=False)
    target_class_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    target_section: Mapped[str | None] = mapped_column(String(10), nullable=True)
    send_via: Mapped[str] = mapped_column(
        String(20), nullable=False, default="in_app"
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Sent")
    scheduled_at: Mapped[datetime | None] = mapped_column(nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(nullable=True)
    recipients_count: Mapped[int] = mapped_column(nullable=False, default=0)
    read_count: Mapped[int] = mapped_column(nullable=False, default=0)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        "created_by_user_id", UUIDType, ForeignKey("users.id"), nullable=True
    )

    __table_args__ = (
        Index(
            "idx_notifications_school_status",
            "school_id",
            "status",
            "sent_at",
        ),
        Index(
            "idx_notifications_target",
            "school_id",
            "target_type",
        ),
    )


class NotificationRecipient(BaseModel):
    """Individual recipient record for a notification."""

    __tablename__ = "notification_recipients"

    notification_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("notifications.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("users.id"), nullable=False
    )
    is_read: Mapped[bool] = mapped_column(nullable=False, default=False)
    read_at: Mapped[datetime | None] = mapped_column(nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "notification_id",
            "user_id",
            name="uq_notification_recipients_school_notif_user",
        ),
        Index(
            "idx_notification_recipients_user",
            "user_id",
            "is_read",
        ),
        Index(
            "idx_notification_recipients_notification",
            "notification_id",
        ),
    )
