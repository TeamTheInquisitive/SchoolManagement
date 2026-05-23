from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams:
    """Query parameters for pagination."""

    def __init__(self, page: int = 1, page_size: int = 20) -> None:
        self.page = max(1, page)
        self.page_size = min(100, max(1, page_size))

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema."""

    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[T]


def paginate(items: list, total: int, params: PaginationParams) -> dict:
    """Helper to build a paginated response dict."""
    return {
        "count": total,
        "page": params.page,
        "page_size": params.page_size,
        "total_pages": (total + params.page_size - 1) // params.page_size,
        "results": items,
    }
