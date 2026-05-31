from typing import Optional

import uuid
from datetime import date

from pydantic import BaseModel


class LibrarySummary(BaseModel):
    total_borrowed: int = 0
    currently_holding: int = 0
    overdue: int = 0
    total_fines: float = 0


class BorrowedBookItem(BaseModel):
    id: uuid.UUID | str
    title: str
    author: str = ""
    isbn: str = ""
    issue_date: str = ""
    due_date: str = ""
    status: str = "Active"
    is_overdue: bool = False
    fine: float = 0


class MyBooksResponse(BaseModel):
    summary: LibrarySummary
    books: list[BorrowedBookItem] = []


class CatalogBookItem(BaseModel):
    id: uuid.UUID | str
    title: str
    author: str = ""
    isbn: str = ""
    category: str = ""
    publisher: str = ""
    available_copies: int = 0
    total_copies: int = 0


class CatalogResponse(BaseModel):
    count: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0
    results: list[CatalogBookItem] = []


class BorrowingHistoryItem(BaseModel):
    id: uuid.UUID | str
    title: str
    author: str = ""
    issue_date: str = ""
    due_date: str = ""
    return_date: str | None = None
    status: str = ""
    fine_paid: float = 0


class BorrowingHistoryResponse(BaseModel):
    count: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0
    results: list[BorrowingHistoryItem] = []


class FineItem(BaseModel):
    id: uuid.UUID | str
    book_title: str = ""
    fine_amount: float = 0
    reason: str = ""
    date: str = ""
    status: str = "Pending"


class FinesResponse(BaseModel):
    total_fines: float = 0
    total_paid: float = 0
    total_pending: float = 0
    items: list[FineItem] = []
