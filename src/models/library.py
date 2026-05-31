from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base_model import BaseModel, UUIDType


class Book(BaseModel):
    """Library book catalog."""

    __tablename__ = "library_books"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    isbn: Mapped[str | None] = mapped_column(String(20), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)
    total_copies: Mapped[int] = mapped_column(default=1)
    available_copies: Mapped[int] = mapped_column(default=1)
    shelf_location: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="Available", server_default="Available")

    __table_args__ = (
        Index("idx_library_books_school_category", "school_id", "category"),
        Index("idx_library_books_school_title", "school_id", "title"),
    )


class BookIssue(BaseModel):
    """Book issue/borrow records."""

    __tablename__ = "library_issues"

    book_id: Mapped[uuid.UUID] = mapped_column(UUIDType, ForeignKey("library_books.id"), nullable=False)
    borrower_id: Mapped[uuid.UUID] = mapped_column(UUIDType, ForeignKey("users.id"), nullable=False)
    borrower_type: Mapped[str] = mapped_column(String(20), nullable=False, default="student")  # student/teacher/staff
    issue_date: Mapped[date] = mapped_column(nullable=False)
    due_date: Mapped[date] = mapped_column(nullable=False)
    return_date: Mapped[date | None] = mapped_column(nullable=True)
    fine_amount: Mapped[float] = mapped_column(default=0.0, server_default="0")
    status: Mapped[str] = mapped_column(String(20), default="Issued", server_default="Issued")  # Issued/Returned/Overdue

    __table_args__ = (
        Index("idx_library_issues_book", "book_id", "status"),
        Index("idx_library_issues_borrower", "borrower_id", "status"),
    )
