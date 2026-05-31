from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Query

from src.auth.dependencies import SchoolDep, TeacherUser
from src.core.dependencies import PaginationDep, SessionDep
from src.teacher.adhoc_classes import service
from src.teacher.adhoc_classes.schemas import (
    AdhocClassCreateRequest,
    AdhocClassDeleteResponse,
    AdhocClassListResponse,
    AdhocClassResponse,
    AdhocClassUpdateRequest,
)

router = APIRouter(prefix="/teacher/adhoc-classes", tags=["Teacher Adhoc Classes"])


@router.get("", response_model=AdhocClassListResponse)
async def list_adhoc_classes(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    pagination: PaginationDep,
    status: str | None = Query(default=None),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
) -> AdhocClassListResponse:
    """List adhoc classes for the authenticated teacher."""
    result = await service.list_adhoc_classes(
        db, school.id, user, pagination, status, from_date, to_date
    )
    return AdhocClassListResponse(**result)


@router.post("", response_model=AdhocClassResponse, status_code=201)
async def create_adhoc_class(
    data: AdhocClassCreateRequest,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> AdhocClassResponse:
    """Create/log an adhoc class."""
    result = await service.create_adhoc_class(db, school.id, user, data.model_dump())
    return AdhocClassResponse(**result)


@router.put("/{adhoc_id}", response_model=AdhocClassResponse)
async def update_adhoc_class(
    adhoc_id: uuid.UUID,
    data: AdhocClassUpdateRequest,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> AdhocClassResponse:
    """Update an adhoc class (mark done, add notes, student_count)."""
    result = await service.update_adhoc_class(
        db, school.id, user, adhoc_id, data.model_dump(exclude_unset=True)
    )
    return AdhocClassResponse(**result)


@router.delete("/{adhoc_id}", response_model=AdhocClassDeleteResponse)
async def delete_adhoc_class(
    adhoc_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> AdhocClassDeleteResponse:
    """Cancel (soft-delete) an adhoc class."""
    result = await service.delete_adhoc_class(db, school.id, user, adhoc_id)
    return AdhocClassDeleteResponse(**result)
