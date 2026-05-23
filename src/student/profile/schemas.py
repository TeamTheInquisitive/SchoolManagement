from typing import Optional

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class AddressSchema(BaseModel):
    """Address for profile update."""

    street: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    country: str | None = None


class UpdateProfileRequest(BaseModel):
    """Student can only update phone, address, and emergency contact."""

    phone: str | None = None
    alternate_phone: str | None = None
    address: AddressSchema | None = None
    emergency_contact: str | None = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class QuickStats(BaseModel):
    attendance_percentage: float | None = None
    avg_grade: float | None = None
    pending_assignments: int | None = None
    fee_due: float | None = None


class PersonalSection(BaseModel):
    date_of_birth: date | None = None
    gender: str | None = None
    admission_date: date | None = None
    blood_group: str | None = None
    religion: str | None = None
    nationality: str | None = None
    student_type: str | None = None
    address: AddressSchema | None = None
    phone: str | None = None
    alternate_phone: str | None = None


class ParentSection(BaseModel):
    parent_name: str | None = None
    relationship: str | None = None
    phone: str | None = None
    email: str | None = None
    occupation: str | None = None
    emergency_contact: str | None = None
    address: AddressSchema | None = None


class MedicalSection(BaseModel):
    blood_group: str | None = None
    gender: str | None = None
    religion: str | None = None
    conditions: str | None = None
    allergies: str | None = None
    medications: str | None = None
    doctor_name: str | None = None
    doctor_phone: str | None = None
    insurance_id: str | None = None


class TransportSection(BaseModel):
    enrolled: bool = False
    route_name: str | None = None
    bus_number: str | None = None
    pickup_point: str | None = None
    pickup_time: str | None = None
    drop_time: str | None = None
    driver_name: str | None = None
    driver_phone: str | None = None


class MentorSection(BaseModel):
    teacher_id: UUID | None = None
    name: str | None = None
    subject: str | None = None
    qualification: str | None = None
    email: str | None = None
    phone: str | None = None


class AttendanceRecord(BaseModel):
    id: str | None = None
    subject: str | None = None
    date: Optional[date] = None
    status: str | None = None
    metadata: dict = {}


class StudentProfileResponse(BaseModel):
    """Full student profile response."""

    id: UUID
    roll_number: str
    full_name: str
    email: str | None = None
    phone: str | None = None
    class_name: str | None = None
    section: str | None = None
    class_section: str | None = None
    academic_year: str | None = None
    student_type: str | None = None
    avatar_url: str | None = None
    avatar_initials: str | None = None
    quick_stats: QuickStats | None = None
    personal: PersonalSection | None = None
    parent: ParentSection | None = None
    medical: MedicalSection | None = None
    transport: TransportSection | None = None
    mentor: MentorSection | None = None
    recent_attendance: list[AttendanceRecord] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None
    metadata: dict = {}


class UpdateProfileResponse(BaseModel):
    """Response after profile update."""

    message: str
    updated_fields: list[str] = []
    updated_at: datetime | None = None
    metadata: dict = {}


class MentorDetailResponse(BaseModel):
    """Mentor detail response."""

    teacher_id: UUID | None = None
    name: str | None = None
    subject: str | None = None
    qualification: str | None = None
    email: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    avatar_initials: str | None = None
    designation: str | None = None
    experience_years: float | None = None
    assigned_since: date | None = None
    total_mentees: int | None = None
    available_hours: str | None = None
    metadata: dict = {}
