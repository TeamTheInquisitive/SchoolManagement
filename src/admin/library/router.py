from __future__ import annotations

from fastapi import APIRouter, Query

from src.admin.library import service
from src.admin.library.schemas import (
    BookCreateRequest,
    BookListResponse,
    BookResponse,
    IssuedListResponse,
    IssueBookRequest,
    BookIssueResponse,
    OverdueListResponse,
    ReturnBookRequest,
)
from src.auth.dependencies import AdminUser, SchoolDep
from src.core.dependencies import SessionDep

router = APIRouter(prefix="/admin/library", tags=["Admin Library"])


@router.get("/books", response_model=BookListResponse)
async def list_books(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    search: str | None = Query(default=None),
    category: str | None = Query(default=None),
    limit: int = Query(default=20, le=100),
) -> BookListResponse:
    result = await service.list_books(db, school.id, search, category, limit)
    return BookListResponse(**result)


@router.post("/books", status_code=201, response_model=BookResponse)
async def create_book(
    data: BookCreateRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> BookResponse:
    result = await service.create_book(db, school.id, data.model_dump(), user.id)
    return BookResponse(**result)


@router.post("/issue", status_code=201, response_model=BookIssueResponse)
async def issue_book(
    data: IssueBookRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> BookIssueResponse:
    result = await service.issue_book(db, school.id, data.model_dump(), user.id)
    return BookIssueResponse(**result)


@router.post("/return", response_model=BookIssueResponse)
async def return_book(
    data: ReturnBookRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> BookIssueResponse:
    result = await service.return_book(db, school.id, data.issue_id, user.id)
    return BookIssueResponse(**result)


@router.get("/issued", response_model=IssuedListResponse)
async def list_issued(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    search: str | None = Query(default=None),
) -> IssuedListResponse:
    result = await service.list_issued(db, school.id, search)
    return IssuedListResponse(**result)


@router.get("/overdue", response_model=OverdueListResponse)
async def list_overdue(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> OverdueListResponse:
    result = await service.list_overdue(db, school.id)
    return OverdueListResponse(**result)
