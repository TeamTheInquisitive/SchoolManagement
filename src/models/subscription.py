from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import Base, TimestampMixin, UUIDType


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUIDType, primary_key=True, default=uuid.uuid4)
    school_id: Mapped[uuid.UUID] = mapped_column(UUIDType, ForeignKey("schools.id"), index=True)
    plan_type: Mapped[str] = mapped_column(String(20), nullable=False)  # monthly, yearly
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    start_date: Mapped[date] = mapped_column(nullable=False)
    end_date: Mapped[date] = mapped_column(nullable=False)
    auto_renew: Mapped[bool] = mapped_column(default=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    payments: Mapped[list[SubscriptionPayment]] = relationship(
        "SubscriptionPayment", back_populates="subscription", lazy="selectin"
    )


class SubscriptionPayment(Base, TimestampMixin):
    __tablename__ = "subscription_payments"

    id: Mapped[uuid.UUID] = mapped_column(UUIDType, primary_key=True, default=uuid.uuid4)
    subscription_id: Mapped[uuid.UUID] = mapped_column(UUIDType, ForeignKey("subscriptions.id"), index=True)
    school_id: Mapped[uuid.UUID] = mapped_column(UUIDType, ForeignKey("schools.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_date: Mapped[date] = mapped_column(nullable=False)
    period_start: Mapped[date] = mapped_column(nullable=False)
    period_end: Mapped[date] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="paid")  # paid, pending, overdue
    notes: Mapped[str | None] = mapped_column(Text, default=None)

    subscription: Mapped[Subscription] = relationship("Subscription", back_populates="payments")
