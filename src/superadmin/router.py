from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query

from src.auth.dependencies import SuperAdminUser
from src.core.dependencies import SessionDep
from src.superadmin import service
from src.superadmin.schemas import (
    AdminCreate,
    DashboardStatsResponse,
    SchoolCreate,
    SchoolDetailResponse,
    SchoolListResponse,
    SchoolUpdate,
    UserListResponse,
)

router = APIRouter(prefix="/superadmin", tags=["Super Admin"])


@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(db: SessionDep, user: SuperAdminUser):
    return await service.get_dashboard_stats(db)


@router.get("/schools", response_model=SchoolListResponse)
async def list_schools(db: SessionDep, user: SuperAdminUser):
    return await service.get_schools(db)


@router.post("/schools", response_model=SchoolDetailResponse, status_code=201)
async def create_school(db: SessionDep, user: SuperAdminUser, data: SchoolCreate):
    school = await service.create_school(db, data.model_dump(exclude_none=True))
    detail = await service.get_school_detail(db, school.id)
    return detail


@router.get("/schools/{school_id}", response_model=SchoolDetailResponse)
async def get_school_detail(db: SessionDep, user: SuperAdminUser, school_id: uuid.UUID):
    detail = await service.get_school_detail(db, school_id)
    if not detail:
        raise HTTPException(status_code=404, detail="School not found")
    return detail


@router.put("/schools/{school_id}", response_model=SchoolDetailResponse)
async def update_school(db: SessionDep, user: SuperAdminUser, school_id: uuid.UUID, data: SchoolUpdate):
    school = await service.update_school(db, school_id, data.model_dump(exclude_none=True))
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    detail = await service.get_school_detail(db, school.id)
    return detail


@router.post("/schools/{school_id}/admin", status_code=201)
async def create_school_admin(db: SessionDep, user: SuperAdminUser, school_id: uuid.UUID, data: AdminCreate):
    admin = await service.create_admin_for_school(db, school_id, data.model_dump())
    return {"id": admin.id, "email": admin.email, "full_name": admin.full_name, "role": admin.role}


@router.get("/users", response_model=UserListResponse)
async def list_users(
    db: SessionDep,
    user: SuperAdminUser,
    role: str | None = Query(default=None),
    school_id: uuid.UUID | None = Query(default=None),
):
    return await service.get_users(db, role=role, school_id=school_id)
