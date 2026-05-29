
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


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
    address: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    parent_name: str | None = None
    parent_phone: str | None = None
    parent_email: str | None = None
    parent_relationship: str | None = "Parent/Guardian"


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
    address: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    status: str | None = None
    class_name: str | None = None
    section: str | None = None


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
    medical: MedicalInfo | None = None
    mentor: MentorInfo | None = None
    stats: StudentStats | None = None
    behavior: BehaviorInfo | None = None
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


class ParentMeetingsResponse(BaseModel):
    total_meetings: int = 0
    attended: int = 0
    meetings: list[MeetingItem] = []


class ActivityItem(BaseModel):
    id: UUID | None = None
    name: str
    since: str | None = None
    role: str | None = None
    status: str | None = None


class AwardItem(BaseModel):
    id: UUID | None = None
    name: str
    category: str | None = None
    year: str | None = None
    description: str | None = None


class ActivitiesResponse(BaseModel):
    extra_curricular: list[ActivityItem] = []
    awards: list[AwardItem] = []


class FeeStructureItem(BaseModel):
    component: str
    amount: float
    frequency: str | None = None


class FeePaymentItem(BaseModel):
    id: UUID | None = None
    date: Optional[date] = None
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
