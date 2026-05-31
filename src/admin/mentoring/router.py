from __future__ import annotations

import uuid

from fastapi import APIRouter, Query
from pydantic import BaseModel

from src.admin.mentoring import service
from src.auth.dependencies import AdminUser, SchoolDep
from src.core.dependencies import SessionDep

router = APIRouter(prefix="/admin/mentoring", tags=["Admin Mentoring"])


class AssignRequest(BaseModel):
    staff_id: uuid.UUID
    student_ids: list[uuid.UUID]


@router.get("")
async def list_mentors(db: SessionDep, school: SchoolDep, user: AdminUser) -> dict:
    return await service.list_mentors(db, school.id)


@router.get("/teachers")
async def list_teachers(db: SessionDep, school: SchoolDep, user: AdminUser) -> dict:
    return await service.list_teachers(db, school.id)


@router.get("/students")
async def list_students(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    class_section_id: uuid.UUID | None = Query(default=None),
) -> dict:
    return await service.list_students(db, school.id, class_section_id)


@router.post("/assign", status_code=201)
async def assign_mentor(data: AssignRequest, db: SessionDep, school: SchoolDep, user: AdminUser) -> dict:
    return await service.assign_mentor(db, school.id, data.staff_id, data.student_ids, user.id)


@router.delete("/{assignment_id}")
async def remove_assignment(assignment_id: uuid.UUID, db: SessionDep, school: SchoolDep, user: AdminUser) -> dict:
    return await service.remove_assignment(db, school.id, assignment_id)
