from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, MetaData, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Explicit naming conventions for constraints/indexes
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now(), onupdate=func.now()
    )


class SoftDeleteMixin:
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)
    deleted_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), default=None)


class AuditMixin:
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), default=None)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), default=None)


class SchoolMixin:
    school_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("schools.id"), index=True
    )


class BaseModel(Base, TimestampMixin, SoftDeleteMixin, AuditMixin, SchoolMixin):
    """Abstract base model combining all mixins with UUID PK and metadata JSONB."""

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    metadata_: Mapped[dict] = mapped_column(
        "metadata", JSONB, default=dict, server_default="{}"
    )
