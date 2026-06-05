from typing import Optional

import re
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Nested schemas
# ---------------------------------------------------------------------------


class TeacherUserInfo(BaseModel):
    full_name: str
    email: str
    phone: str | None = None


class ClassAssignmentResponse(BaseModel):
    id: UUID
    class_name: str
    section: str
    subject: str
    is_class_teacher: bool = False
    periods_per_week: int | None = None
    status: str = "Active"

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


def _clean_phone(v: str | None) -> str | None:
    """Strip spaces/dashes and validate Indian phone number format."""
    if v is None or v == "":
        return None
    cleaned = re.sub(r"[\s\-]+", "", v)
    if not re.match(r"^[6-9]\d{9}$", cleaned):
        raise ValueError("Phone must be 10 digits starting with 6-9")
    return cleaned


class CreateTeacherRequest(BaseModel):
    employee_id: str
    full_name: str
    email: str
    phone: str | None = None
    subjects: list[str] = Field(default_factory=list)
    primary_subject: str | None = None
    qualification: str | None = None
    joining_date: date | None = None
    max_workload_hours: int | None = None
    department: str | None = None
    designation: str | None = None
    gender: str | None = None
    employment_type: str | None = None
    date_of_birth: date | None = None
    address: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    emergency_contact_relationship: str | None = None
    # Salary fields
    basic_salary: float | None = None
    hra: float | None = None
    da: float | None = None
    ta: float | None = None
    other_allowances: float | None = None
    pf_deduction: float | None = None
    tax_deduction: float | None = None
    other_deductions: float | None = None
    bank_name: str | None = None
    account_number: str | None = None
    ifsc_code: str | None = None
    pan_number: str | None = None

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone(cls, v):
        return _clean_phone(v)

    @field_validator("emergency_contact_phone", mode="before")
    @classmethod
    def validate_emergency_phone(cls, v):
        return _clean_phone(v)


class UpdateTeacherRequest(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    subjects: list[str] | None = None
    primary_subject: str | None = None
    qualification: str | None = None
    max_workload_hours: int | None = None
    department: str | None = None
    designation: str | None = None
    gender: str | None = None
    employment_type: str | None = None
    date_of_birth: date | None = None
    address: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    emergency_contact_relationship: str | None = None
    # Salary fields
    basic_salary: float | None = None
    hra: float | None = None
    da: float | None = None
    ta: float | None = None
    other_allowances: float | None = None
    pf_deduction: float | None = None
    tax_deduction: float | None = None
    other_deductions: float | None = None
    bank_name: str | None = None
    account_number: str | None = None
    ifsc_code: str | None = None
    pan_number: str | None = None

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone(cls, v):
        return _clean_phone(v)

    @field_validator("emergency_contact_phone", mode="before")
    @classmethod
    def validate_emergency_phone(cls, v):
        return _clean_phone(v)


class DeleteTeacherRequest(BaseModel):
    reason: str | None = None
    left_date: date | None = None
    notes: str | None = None


class AssignClassRequest(BaseModel):
    class_name: str
    section: str
    subject: str = ""
    is_class_teacher: bool = False
    periods_per_week: int | None = None


class BulkAssignRequest(BaseModel):
    assignments: list[AssignClassRequest]


class RemoveAssignmentRequest(BaseModel):
    reason: str | None = None
    end_date: date | None = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class TeacherResponse(BaseModel):
    id: UUID
    employee_id: str
    user: TeacherUserInfo
    subjects: list[str] = Field(default_factory=list)
    primary_subject: str | None = None
    qualification: str | None = None
    department: str | None = None
    designation: str | None = None
    gender: str | None = None
    employment_type: str | None = None
    date_of_birth: date | None = None
    joining_date: date | None = None
    address: str | None = None
    address_line1: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    workload_hours: int = 0
    max_workload_hours: int | None = None
    class_assignments: list[ClassAssignmentResponse] = Field(default_factory=list)
    total_periods_per_week: int = 0
    classes_count: int = 0
    is_class_teacher_of: list[str] = Field(default_factory=list)
    status: str = "Active"
    is_active: bool = True
    left_date: date | None = None
    left_reason: str | None = None
    created_at: datetime | None = None
    password_changed: bool = False
    # Salary fields
    basic_salary: float | None = None
    hra: float | None = None
    da: float | None = None
    ta: float | None = None
    other_allowances: float | None = None
    pf_deduction: float | None = None
    tax_deduction: float | None = None
    other_deductions: float | None = None
    bank_name: str | None = None
    account_number: str | None = None
    ifsc_code: str | None = None
    pan_number: str | None = None

    model_config = {"from_attributes": True}


class TeacherDeleteResponse(BaseModel):
    id: UUID
    employee_id: str
    full_name: str
    status: str
    left_date: date | None = None
    reason: str | None = None
    notes: str | None = None
    message: str


class TeacherListResponse(BaseModel):
    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[TeacherResponse]


class AssignmentCreatedResponse(BaseModel):
    id: UUID
    class_name: str
    section: str
    subject: str
    is_class_teacher: bool = False
    periods_per_week: int | None = None


class BulkAssignResponse(BaseModel):
    assigned: int
    skipped: int = 0
    assignments: list[AssignmentCreatedResponse] = Field(default_factory=list)
    total_periods_per_week: int = 0
    workload_hours: int = 0


class TeacherAssignmentsResponse(BaseModel):
    teacher_id: UUID
    teacher_name: str
    total_assignments: int
    total_periods_per_week: int
    assignments: list[ClassAssignmentResponse]


class AssignmentDeleteResponse(BaseModel):
    id: UUID
    class_name: str
    section: str
    subject: str
    status: str
    end_date: date | None = None
    reason: str | None = None
    message: str


class TeachersByClassResponse(BaseModel):
    class_name: str
    section: str
    teachers: list[dict]


class TeacherHistoryResponse(BaseModel):
    teacher_id: UUID
    employee_id: str
    full_name: str
    status: str
    joining_date: date | None = None
    left_date: date | None = None
    reason: str | None = None
    subjects_taught: list[str] = Field(default_factory=list)
    assignment_history: list[dict] = Field(default_factory=list)


class BulkImportTeacherItem(BaseModel):
    employee_id: str
    full_name: str
    email: str
    phone: str | None = None
    gender: str | None = None
    date_of_birth: date | None = None
    department: str | None = None
    designation: str | None = None
    primary_subject: str | None = None
    subjects: list[str] | str = Field(default_factory=list)
    qualification: str | None = None
    employment_type: str | None = None
    joining_date: date | None = None
    max_workload_hours: int | None = None
    address: str | None = None
    basic_salary: float | None = None
    hra: float | None = None
    da: float | None = None
    bank_name: str | None = None
    account_number: str | None = None
    ifsc_code: str | None = None
    pan_number: str | None = None

    @field_validator("subjects", mode="before")
    @classmethod
    def parse_subjects(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone(cls, v):
        return _clean_phone(v)


class BulkImportTeacherRowResult(BaseModel):
    row: int
    employee_id: str | None = None
    success: bool
    error: str | None = None


class BulkImportTeacherRequest(BaseModel):
    teachers: list[BulkImportTeacherItem]


class BulkImportTeacherResponse(BaseModel):
    results: list[BulkImportTeacherRowResult]
    total: int
    passed: int
    failed: int
