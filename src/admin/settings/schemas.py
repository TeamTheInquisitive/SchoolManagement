from typing import Optional

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


# --- Settings (generic) ---


class SettingsResponse(BaseModel):
    """Response for GET /settings/ — all settings grouped by category."""

    school_profile: dict = Field(default_factory=dict)
    academic_year: dict = Field(default_factory=dict)
    classes: list[str] = Field(default_factory=list)
    sections: list[str] = Field(default_factory=list)
    working_days: list[str] = Field(default_factory=list)
    fine_rules: dict = Field(default_factory=dict)
    notification_channels: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class SettingsUpdateRequest(BaseModel):
    """Request for PUT /settings/ — partial update."""

    fine_rules: dict | None = None
    working_days: list[str] | None = None
    notification_channels: list[str] | None = None


class SettingsUpdateResponse(BaseModel):
    message: str
    updated_fields: list[str]
    metadata: dict = Field(default_factory=dict)


# --- School Profile ---


class SchoolProfileResponse(BaseModel):
    school_name: str
    school_code: str
    logo_url: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    pin_code: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    principal_name: str | None = None
    established_year: int | None = None
    board: str | None = None
    metadata: dict = Field(default_factory=dict)


class SchoolProfileUpdateRequest(BaseModel):
    school_name: str | None = None
    logo_url: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    pin_code: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    principal_name: str | None = None
    established_year: int | None = None
    board: str | None = None


class SchoolProfileUpdateResponse(BaseModel):
    message: str
    school_name: str
    updated_fields: list[str]
    metadata: dict = Field(default_factory=dict)


# --- Academic Year ---


class TermSchema(BaseModel):
    id: UUID | None = None
    name: str
    start_date: date
    end_date: date


class AcademicYearResponse(BaseModel):
    current: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    terms: list[TermSchema] = Field(default_factory=list)
    previous_years: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class AcademicYearUpdateRequest(BaseModel):
    current: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    terms: list[TermSchema] | None = None


class AcademicYearUpdateResponse(BaseModel):
    message: str
    current: str | None = None
    terms_count: int = 0
    metadata: dict = Field(default_factory=dict)


# --- Enums ---


class EnumValueSchema(BaseModel):
    id: UUID | None = None
    code: str
    label: str
    is_active: bool = True


class EnumCategoryResponse(BaseModel):
    category: str
    values: list[EnumValueSchema] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class EnumCategoryUpdateRequest(BaseModel):
    values: list[EnumValueSchema]


class EnumCategoryUpdateResponse(BaseModel):
    category: str
    added: int = 0
    updated: int = 0
    message: str
    metadata: dict = Field(default_factory=dict)


# --- Classes Bulk ---


class ClassesBulkRequest(BaseModel):
    classes: list[str]


class ClassesBulkResponse(BaseModel):
    created: int
    message: str
    metadata: dict = Field(default_factory=dict)


# --- Sections Bulk ---


class SectionsBulkRequest(BaseModel):
    sections: list[str]
    class_id: str | None = None


class SectionsBulkResponse(BaseModel):
    created: int
    message: str
    metadata: dict = Field(default_factory=dict)


# --- Subjects Bulk ---


class SubjectItem(BaseModel):
    name: str
    code: str | None = None


class SubjectsBulkRequest(BaseModel):
    subjects: list[SubjectItem]


class SubjectsBulkResponse(BaseModel):
    created: int
    message: str
    metadata: dict = Field(default_factory=dict)
