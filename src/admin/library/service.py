from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFound, ConflictError
from src.models.library import Book, BookIssue
from src.models.core import User


async def list_books(
    db: AsyncSession, school_id: uuid.UUID, search: str | None = None, category: str | None = None, limit: int = 20
) -> dict:
    query = select(Book).where(Book.school_id == school_id, Book.is_active.is_(True))
    if search:
        query = query.where(Book.title.ilike(f"%{search}%"))
    if category:
        query = query.where(Book.category == category)
    query = query.order_by(Book.title).limit(limit)
    result = await db.execute(query)
    books = result.scalars().all()
    return {
        "count": len(books),
        "results": [
            {
                "id": b.id, "title": b.title, "author": b.author, "isbn": b.isbn,
                "category": b.category, "publisher": b.publisher,
                "total_copies": b.total_copies, "available_copies": b.available_copies,
                "shelf_location": b.shelf_location, "status": b.status,
                "is_active": b.is_active, "created_at": b.created_at,
            }
            for b in books
        ],
    }


async def create_book(
    db: AsyncSession, school_id: uuid.UUID, data: dict, user_id: uuid.UUID
) -> dict:
    book = Book(
        school_id=school_id,
        title=data["title"],
        author=data.get("author"),
        isbn=data.get("isbn"),
        category=data.get("category"),
        publisher=data.get("publisher"),
        total_copies=data.get("total_copies", 1),
        available_copies=data.get("total_copies", 1),
        shelf_location=data.get("shelf_location"),
        created_by=user_id,
    )
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return {
        "id": book.id, "title": book.title, "author": book.author, "isbn": book.isbn,
        "category": book.category, "publisher": book.publisher,
        "total_copies": book.total_copies, "available_copies": book.available_copies,
        "shelf_location": book.shelf_location, "status": book.status,
        "is_active": book.is_active, "created_at": book.created_at,
    }


async def issue_book(
    db: AsyncSession, school_id: uuid.UUID, data: dict, user_id: uuid.UUID
) -> dict:
    # Validate book
    book_result = await db.execute(
        select(Book).where(Book.id == data["book_id"], Book.school_id == school_id, Book.is_active.is_(True))
    )
    book = book_result.scalar_one_or_none()
    if not book:
        raise NotFound("Book")
    if book.available_copies <= 0:
        raise ConflictError("No copies available for this book")

    # Validate borrower (user)
    borrower_result = await db.execute(
        select(User).where(User.id == data["borrower_id"], User.school_id == school_id)
    )
    borrower = borrower_result.scalar_one_or_none()
    if not borrower:
        raise NotFound("User")

    issue = BookIssue(
        school_id=school_id,
        book_id=data["book_id"],
        borrower_id=data["borrower_id"],
        borrower_type=data.get("borrower_type", "student"),
        issue_date=date.today(),
        due_date=data["due_date"],
        status="Issued",
        created_by=user_id,
    )
    db.add(issue)
    book.available_copies -= 1
    await db.commit()
    await db.refresh(issue)

    return {
        "id": issue.id, "book_id": issue.book_id, "book_title": book.title,
        "borrower_id": issue.borrower_id, "borrower_name": borrower.full_name,
        "borrower_type": issue.borrower_type,
        "issue_date": issue.issue_date, "due_date": issue.due_date,
        "return_date": None, "fine_amount": 0, "status": "Issued",
    }


async def return_book(
    db: AsyncSession, school_id: uuid.UUID, issue_id: uuid.UUID, user_id: uuid.UUID
) -> dict:
    result = await db.execute(
        select(BookIssue).where(BookIssue.id == issue_id, BookIssue.school_id == school_id)
    )
    issue = result.scalar_one_or_none()
    if not issue:
        raise NotFound("Issue record")
    if issue.status == "Returned":
        raise ConflictError("Book already returned")

    today = date.today()
    fine = max(0.0, (today - issue.due_date).days * 2.0) if today > issue.due_date else 0.0

    issue.return_date = today
    issue.fine_amount = fine
    issue.status = "Returned"

    book_result = await db.execute(select(Book).where(Book.id == issue.book_id))
    book = book_result.scalar_one_or_none()
    if book:
        book.available_copies += 1

    await db.commit()
    await db.refresh(issue)

    borrower_result = await db.execute(select(User).where(User.id == issue.borrower_id))
    borrower = borrower_result.scalar_one_or_none()

    return {
        "id": issue.id, "book_id": issue.book_id, "book_title": book.title if book else "",
        "borrower_id": issue.borrower_id, "borrower_name": borrower.full_name if borrower else "",
        "borrower_type": issue.borrower_type,
        "issue_date": issue.issue_date, "due_date": issue.due_date,
        "return_date": issue.return_date, "fine_amount": issue.fine_amount, "status": issue.status,
    }


async def list_issued(
    db: AsyncSession, school_id: uuid.UUID, search: str | None = None
) -> dict:
    query = (
        select(BookIssue, Book.title, User.full_name)
        .join(Book, BookIssue.book_id == Book.id)
        .join(User, BookIssue.borrower_id == User.id)
        .where(BookIssue.school_id == school_id, BookIssue.status == "Issued", BookIssue.is_active.is_(True))
    )
    if search:
        query = query.where(
            (Book.title.ilike(f"%{search}%")) | (User.full_name.ilike(f"%{search}%"))
        )
    query = query.order_by(BookIssue.issue_date.desc())
    result = await db.execute(query)
    rows = result.all()
    return {
        "count": len(rows),
        "results": [
            {
                "id": issue.id, "book_id": issue.book_id, "book_title": title,
                "borrower_id": issue.borrower_id, "borrower_name": name,
                "borrower_type": issue.borrower_type,
                "issue_date": issue.issue_date, "due_date": issue.due_date,
                "return_date": issue.return_date, "fine_amount": issue.fine_amount,
                "status": issue.status,
            }
            for issue, title, name in rows
        ],
    }


async def list_overdue(db: AsyncSession, school_id: uuid.UUID) -> dict:
    today = date.today()
    query = (
        select(BookIssue, Book.title, User.full_name)
        .join(Book, BookIssue.book_id == Book.id)
        .join(User, BookIssue.borrower_id == User.id)
        .where(
            BookIssue.school_id == school_id,
            BookIssue.status == "Issued",
            BookIssue.due_date < today,
            BookIssue.is_active.is_(True),
        )
    )
    query = query.order_by(BookIssue.due_date)
    result = await db.execute(query)
    rows = result.all()
    total_fines = sum((today - issue.due_date).days * 2.0 for issue, _, _ in rows)
    return {
        "count": len(rows),
        "total_fines": total_fines,
        "results": [
            {
                "id": issue.id, "book_id": issue.book_id, "book_title": title,
                "borrower_id": issue.borrower_id, "borrower_name": name,
                "borrower_type": issue.borrower_type,
                "issue_date": issue.issue_date, "due_date": issue.due_date,
                "return_date": None, "fine_amount": (today - issue.due_date).days * 2.0,
                "status": "Overdue",
            }
            for issue, title, name in rows
        ],
    }
