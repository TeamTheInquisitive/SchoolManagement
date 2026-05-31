from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr


class DashboardStatsResponse(BaseModel):
    total_schools: int
    total_students: int
    total_staff: int
    total_revenue: float


class SchoolListItem(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    city: str | None
    student_count: int
    staff_count: int
    is_active: bool
    created_at: datetime | None = None


class SchoolListResponse(BaseModel):
    schools: list[SchoolListItem]
    total: int


class SchoolCreate(BaseModel):
    name: str
    code: str
    city: str | None = None
    state: str | None = None
    address_line1: str | None = None
    phone: str | None = None
    email: str | None = None
    board_affiliation: str | None = None
    principal_name: str | None = None


class SchoolUpdate(BaseModel):
    name: str | None = None
    city: str | None = None
    state: str | None = None
    address_line1: str | None = None
    phone: str | None = None
    email: str | None = None
    board_affiliation: str | None = None
    principal_name: str | None = None
    is_active: bool | None = None


class SchoolDetailResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    city: str | None
    state: str | None
    address_line1: str | None
    phone: str | None
    email: str | None
    board_affiliation: str | None
    principal_name: str | None
    is_active: bool
    created_at: datetime | None
    student_count: int
    staff_count: int
    admin_users: list[UserItem]


class AdminCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    phone: str | None = None


class UserItem(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    phone: str | None
    is_active: bool
    school_name: str | None = None
    last_login_at: datetime | None = None


class UserListResponse(BaseModel):
    users: list[UserItem]
    total: int
