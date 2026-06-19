
from datetime import date, datetime
import re
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


def _clean_phone(v: str | None) -> str | None:
    if not v:
        return None
    cleaned = re.sub(r'^(\+91[-\s]?|91[-\s]?|0)', '', v.strip())
    cleaned = re.sub(r'[-\s]', '', cleaned)
    if not re.match(r'^[6-9]\d{9}$', cleaned):
        return v.strip()  # Return as-is if doesn't match expected format
    return cleaned


class CreateStudentRequest(BaseModel):
    """Request to create a student."""

    roll_number: str
    full_name: str
    email: str | None = None
    phone: str | None = None
    class_name: str
    section: str
    date_of_birth: date | None = None
    admission_date: date | None = None
    gender: str | None = None
    student_type: str | None = None
    blood_group: str | None = None
    religion: str | None = None
    medical_conditions: str | None = None
    allergies: str | None = None
    address: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    parent_name: str | None = None
    parent_phone: str | None = None
    parent_email: str | None = None
    parent_relationship: str | None = "Parent/Guardian"
    concessions: dict[str, float] | None = None
    custom_fees: list[dict] | None = None
    excluded_fee_ids: list[str] | None = None
    previous_school: str | None = None
    token_advance: float | None = None
    token_payment_method: str | None = None
    parent_occupation: str | None = None
    status: str | None = None

    @field_validator('phone', 'parent_phone', mode='before')
    @classmethod
    def validate_phone(cls, v):
        return _clean_phone(v)


    @field_validator('date_of_birth', 'admission_date', mode='before')
    @classmethod
    def validate_dates(cls, v):
        if v is None or v == "":
            return None
        return v

    @field_validator('token_advance', mode='before')
    @classmethod
    def validate_numerics(cls, v):
        if v is None or v == "":
            return None
        return v

class UpdateStudentRequest(BaseModel):
    """Request to update a student."""

    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    student_type: str | None = None
    blood_group: str | None = None
    religion: str | None = None
    medical_conditions: str | None = None
    allergies: str | None = None
    address: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    status: str | None = None
    class_name: str | None = None
    section: str | None = None
    parent_name: str | None = None
    parent_phone: str | None = None
    parent_email: str | None = None
    parent_relationship: str | None = None
    parent_occupation: str | None = None
    admission_date: date | None = None

    @field_validator('phone', 'parent_phone', mode='before')
    @classmethod
    def validate_phone(cls, v):
        return _clean_phone(v)

    @field_validator('date_of_birth', 'admission_date', mode='before')
    @classmethod
    def clean_date(cls, v):
        if v == '' or v is None:
            return None
        return v


class DeleteStudentRequest(BaseModel):
    """Request for student soft-delete."""

    status: str = "Inactive"
    reason: str | None = None
    notes: str | None = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class StudentListItem(BaseModel):
    """Student item in list response."""

    id: UUID
    roll_number: str
    full_name: str
    email: str | None = None
    phone: str | None = None
    class_name: str | None = None
    section: str | None = None
    status: str
    gender: str | None = None
    date_of_birth: date | None = None
    admission_date: date | None = None
    blood_group: str | None = None
    religion: str | None = None
    address: str | None = None
    student_type: str | None = None
    previous_school: str | None = None
    token_advance: float | None = None
    token_payment_method: str | None = None
    password_changed: bool = False
    parent_name: str | None = None
    parent_phone: str | None = None
    parent_email: str | None = None
    parent_relationship: str | None = None


class StudentListSummary(BaseModel):
    """Summary stats for student list."""

    total: int
    active: int
    inactive: int


class StudentListResponse(BaseModel):
    """Paginated student list response."""

    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[StudentListItem]
    summary: StudentListSummary


class ParentInfo(BaseModel):
    """Parent info in student detail."""

    name: str | None = None
    phone: str | None = None
    email: str | None = None
    emergency_contact: str | None = None
    relationship: str | None = None


class MedicalInfo(BaseModel):
    """Medical info in student detail."""

    blood_group: str | None = None
    religion: str | None = None
    conditions: str | None = None
    allergies: list[str] | None = None


class MentorInfo(BaseModel):
    """Mentor info in student detail."""

    id: UUID | None = None
    name: str | None = None
    subject: str | None = None
    qualification: str | None = None
    email: str | None = None
    phone: str | None = None


class StudentStats(BaseModel):
    """Quick stats for student detail."""

    attendance_percentage: float | None = None
    average_grade: float | None = None
    assignments_submitted: int | None = None
    assignments_total: int | None = None
    fee_due: float | None = None
    class_rank: int | None = None
    class_strength: int | None = None


class BehaviorInfo(BaseModel):
    """Behavior info in student detail."""

    overall_rating: str | None = None
    discipline_score: float | None = None
    punctuality_score: float | None = None


class TransportInfo(BaseModel):
    """Transport info in student detail."""

    enrolled: bool = False
    route_name: str | None = None
    route_code: str | None = None
    bus_number: str | None = None
    pickup_point: str | None = None
    drop_point: str | None = None


class ClassTeacherInfo(BaseModel):
    """Class teacher info in student detail."""

    name: str | None = None
    email: str | None = None
    phone: str | None = None


class StudentResponse(BaseModel):
    """Full student detail response."""

    id: UUID
    roll_number: str
    full_name: str
    email: str | None = None
    phone: str | None = None
    class_name: str | None = None
    section: str | None = None
    status: str
    type: str | None = None
    gender: str | None = None
    date_of_birth: date | None = None
    admission_date: date | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    parent: ParentInfo | None = None
    parent_name: str | None = None
    parent_phone: str | None = None
    parent_email: str | None = None
    parent_relationship: str | None = None
    parent_occupation: str | None = None
    previous_school: str | None = None
    token_advance: Any | None = None
    medical: MedicalInfo | None = None
    mentor: MentorInfo | None = None
    class_teacher: ClassTeacherInfo | None = None
    stats: StudentStats | None = None
    behavior: BehaviorInfo | None = None
    transport: TransportInfo | None = None
    created_at: datetime | None = None


class StudentDeleteResponse(BaseModel):
    """Response for student delete (soft-delete)."""

    id: UUID
    roll_number: str
    full_name: str
    status: str
    reason: str | None = None
    deactivated_on: date | None = None
    message: str


# ---------------------------------------------------------------------------
# Sub-resource response schemas
# ---------------------------------------------------------------------------


class ExamSubjectResult(BaseModel):
    name: str
    marks: float | None = None
    total: float | None = None
    grade: str | None = None


class ExamResult(BaseModel):
    id: UUID | None = None
    name: str
    total_marks: float | None = None
    marks_obtained: float | None = None
    percentage: float | None = None
    subjects: list[ExamSubjectResult] = []


class ExamResultsResponse(BaseModel):
    exams: list[ExamResult] = []
    trend: list[dict] = []


class MeetingItem(BaseModel):
    id: UUID | None = None
    type: str | None = None
    date: Optional[date] = None
    attendee: str | None = None
    conductor: str | None = None
    notes: str | None = None
    status: str | None = None
    agenda: str | None = None
    remarks: str | None = None
    follow_up_required: bool | None = None
    next_meeting_date: Optional[date] = None
    parent_attended: bool | None = None


class ParentMeetingsResponse(BaseModel):
    total_meetings: int = 0
    attended: int = 0
    meetings: list[MeetingItem] = []


class ActivityItem(BaseModel):
    id: UUID | None = None
    name: str
    activity_type: str | None = None
    description: str | None = None
    role: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    achievement: str | None = None
    since: str | None = None
    status: str | None = None


class AwardItem(BaseModel):
    id: UUID | None = None
    name: str
    title: str | None = None
    category: str | None = None
    year: str | None = None
    description: str | None = None
    awarded_date: date | None = None
    awarded_by: str | None = None
    level: str | None = None


class ActivitiesResponse(BaseModel):
    extra_curricular: list[ActivityItem] = []
    awards: list[AwardItem] = []


class FeeStructureItem(BaseModel):
    component: str
    amount: float
    frequency: str | None = None


class FeePaymentItem(BaseModel):
    id: UUID | None = None
    payment_date: date | None = None
    amount: float
    method: str | None = None
    status: str | None = None
    reference: str | None = None


class FeeSummary(BaseModel):
    total_fees: float = 0
    total_paid: float = 0
    total_due: float = 0


class FeeHistoryResponse(BaseModel):
    summary: FeeSummary
    fee_structure: list[FeeStructureItem] = []
    payments: list[FeePaymentItem] = []


class DisciplinaryRecordItem(BaseModel):
    id: UUID | None = None
    incident_date: date | None = None
    category: str | None = None
    severity: str | None = None
    description: str | None = None
    action_taken: str | None = None
    status: str | None = None


class DisciplinaryRecordsResponse(BaseModel):
    records: list[DisciplinaryRecordItem] = []
    status: str = "Clean"


class BulkImportResponse(BaseModel):
    """Response for bulk import."""

    imported: int = 0
    skipped: int = 0
    errors: list[dict] = []


class BulkImportRowResult(BaseModel):
    row: int
    roll_number: str | None = None
    success: bool
    error: str | None = None


class CreateAwardRequest(BaseModel):
    """Request to create a student award."""
    title: str
    category: str | None = None
    description: str | None = None
    awarded_date: date | None = None
    awarded_by: str | None = None
    level: str | None = None
    certificate_url: str | None = None


class UpdateAwardRequest(BaseModel):
    """Request to update a student award."""
    title: str | None = None
    category: str | None = None
    description: str | None = None
    awarded_date: date | None = None
    awarded_by: str | None = None
    level: str | None = None
    certificate_url: str | None = None


class CreateActivityRequest(BaseModel):
    """Request to create a student activity."""
    name: str
    activity_type: str
    description: str | None = None
    role: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    achievement: str | None = None


class UpdateActivityRequest(BaseModel):
    """Request to update a student activity."""
    name: str | None = None
    activity_type: str | None = None
    description: str | None = None
    role: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    achievement: str | None = None


class CreateParentMeetingRequest(BaseModel):
    """Request to create a parent meeting."""
    meeting_date: date
    meeting_type: str | None = None
    agenda: str | None = None
    discussion_notes: str | None = None
    remarks: str | None = None
    follow_up_required: bool = False
    next_meeting_date: date | None = None
    status: str | None = "Scheduled"
    parent_attended: bool = True


class UpdateParentMeetingRequest(BaseModel):
    """Request to update a parent meeting."""
    meeting_date: date | None = None
    meeting_type: str | None = None
    agenda: str | None = None
    discussion_notes: str | None = None
    remarks: str | None = None
    follow_up_required: bool | None = None
    next_meeting_date: date | None = None
    status: str | None = None
    parent_attended: bool | None = None


class CreateDisciplinaryRequest(BaseModel):
    """Request to create a disciplinary record."""
    incident_date: date
    category: str
    severity: str
    description: str
    action_taken: str | None = None
    parent_notified: bool = False
    status: str = "Open"


class UpdateDisciplinaryRequest(BaseModel):
    """Request to update a disciplinary record."""
    incident_date: date | None = None
    category: str | None = None
    severity: str | None = None
    description: str | None = None
    action_taken: str | None = None
    parent_notified: bool | None = None
    status: str | None = None


class BulkImportJsonRequest(BaseModel):
    students: list[CreateStudentRequest]


class BulkImportJsonResponse(BaseModel):
    results: list[BulkImportRowResult]
    total: int
    passed: int
    failed: int
