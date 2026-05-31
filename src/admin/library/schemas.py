from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel


class BookCreateRequest(BaseModel):
    title: str
    author: str | None = None
    isbn: str | None = None
    category: str | None = None
    publisher: str | None = None
    total_copies: int = 1
    shelf_location: str | None = None


class BookResponse(BaseModel):
    id: uuid.UUID
    title: str
    author: str | None = None
    isbn: str | None = None
    category: str | None = None
    publisher: str | None = None
    total_copies: int
    available_copies: int
    shelf_location: str | None = None
    status: str
    is_active: bool
    created_at: datetime | None = None


class BookListResponse(BaseModel):
    count: int
    results: list[BookResponse]


class IssueBookRequest(BaseModel):
    book_id: uuid.UUID
    borrower_id: uuid.UUID
    borrower_type: str = "student"  # student/teacher/staff
    due_date: date


class ReturnBookRequest(BaseModel):
    issue_id: uuid.UUID


class BookIssueResponse(BaseModel):
    id: uuid.UUID
    book_id: uuid.UUID
    book_title: str
    borrower_id: uuid.UUID
    borrower_name: str
    borrower_type: str
    issue_date: date
    due_date: date
    return_date: date | None = None
    fine_amount: float = 0
    status: str


class IssuedListResponse(BaseModel):
    count: int
    results: list[BookIssueResponse]


class OverdueListResponse(BaseModel):
    count: int
    total_fines: float
    results: list[BookIssueResponse]
