from typing import Optional

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class CreateStaffRequest(BaseModel):
    employee_id: str
    first_name: str
    last_name: str | None = None
    full_name: str
    email: str
    phone: str | None = None
    department: str | None = None
    designation: str | None = None
    employment_type: str | None = None  # Full-time / Part-time / Contract
    joining_date: date | None = None
    salary: Decimal | None = None
    is_teacher: bool = False
    gender: str | None = None
    qualification: str | None = None
    experience_years: Decimal | None = None
    address_line1: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    blood_group: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None


class UpdateStaffRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    department: str | None = None
    designation: str | None = None
    employment_type: str | None = None
    joining_date: date | None = None
    salary: Decimal | None = None
    is_teacher: bool | None = None
    gender: str | None = None
    qualification: str | None = None
    experience_years: Decimal | None = None
    address_line1: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    blood_group: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    status: str | None = None


class DeleteStaffRequest(BaseModel):
    reason: str | None = None
    left_date: date | None = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class StaffResponse(BaseModel):
    id: UUID
    employee_id: str
    full_name: str
    email: str
    phone: str | None = None
    department: str | None = None
    designation: str | None = None
    employment_type: str | None = None
    joining_date: date | None = None
    salary: Decimal | None = None
    is_teacher: bool = False
    status: str
    gender: str | None = None
    qualification: str | None = None
    experience_years: Decimal | None = None
    left_date: date | None = None
    left_reason: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class StaffDeleteResponse(BaseModel):
    id: UUID
    employee_id: str
    full_name: str
    status: str
    left_date: date | None = None
    reason: str | None = None
    message: str


class StaffListResponse(BaseModel):
    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[StaffResponse]
