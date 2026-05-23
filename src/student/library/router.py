from __future__ import annotations

from fastapi import APIRouter, Query

from src.auth.dependencies import SchoolDep, StudentUser
from src.core.dependencies import PaginationDep, SessionDep
from src.student.library import service
from src.student.library.schemas import (
    BorrowingHistoryResponse,
    CatalogResponse,
    FinesResponse,
    MyBooksResponse,
)

router = APIRouter(prefix="/student/library", tags=["Student Library"])


@router.get("/", response_model=MyBooksResponse)
async def get_my_books(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
) -> MyBooksResponse:
    """Get my books + summary (borrowed, overdue, fines)."""
    result = await service.get_my_books(db, school.id, user)
    return MyBooksResponse(**result)


@router.get("/catalog/", response_model=CatalogResponse)
async def get_catalog(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
    pagination: PaginationDep,
    search: str | None = Query(default=None),
    category: str | None = Query(default=None),
) -> CatalogResponse:
    """Browse catalog (search, filter)."""
    result = await service.get_catalog(db, school.id, user, pagination, search, category)
    return CatalogResponse(**result)


@router.get("/history/", response_model=BorrowingHistoryResponse)
async def get_borrowing_history(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
    pagination: PaginationDep,
) -> BorrowingHistoryResponse:
    """Get borrowing history."""
    result = await service.get_borrowing_history(db, school.id, user, pagination)
    return BorrowingHistoryResponse(**result)


@router.get("/fines/", response_model=FinesResponse)
async def get_fines(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
) -> FinesResponse:
    """Get fine details."""
    result = await service.get_fines(db, school.id, user)
    return FinesResponse(**result)
