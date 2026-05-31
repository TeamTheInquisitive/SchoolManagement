from typing import Optional

from datetime import date
from uuid import UUID

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class TeacherStudentListItem(BaseModel):
    """Student item in teacher's list response."""

    id: UUID
    roll_number: str
    full_name: str
    email: str | None = None
    class_name: str | None = None
    section: str | None = None
    class_section: str | None = None
    avatar_url: str | None = None
    status: str


class TeacherMenteeItem(BaseModel):
    """Mentee item in teacher's mentees response."""

    id: UUID
    roll_number: str
    full_name: str
    email: str | None = None
    phone: str | None = None
    class_name: str | None = None
    section: str | None = None
    class_section: str | None = None
    avatar_url: str | None = None
    assigned_date: date | None = None


class TeacherMenteesResponse(BaseModel):
    """Mentees list response for teacher."""

    total: int = 0
    mentees: list[TeacherMenteeItem] = []


class TeacherStudentListResponse(BaseModel):
    """Paginated student list response for teacher."""

    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[TeacherStudentListItem]


class QuickStats(BaseModel):
    attendance_percentage: float | None = None
    average_grade: str | None = None
    assignments_submitted: int | None = None
    fee_due: float | None = None


class PersonalInfo(BaseModel):
    date_of_birth: date | None = None
    admission_date: date | None = None
    address: str | None = None
    nationality: str | None = None


class ParentInfo(BaseModel):
    father_name: str | None = None
    father_phone: str | None = None
    father_email: str | None = None
    mother_name: str | None = None
    mother_phone: str | None = None
    mother_email: str | None = None
    emergency_contact: str | None = None
    relationship: str | None = None


class MedicalInfo(BaseModel):
    blood_group: str | None = None
    gender: str | None = None
    religion: str | None = None
    medical_conditions: str | None = None
    allergies: str | None = None


class TransportInfo(BaseModel):
    transport_service: str | None = None
    route: str | None = None
    bus_number: str | None = None
    pickup_point: str | None = None


class MentorInfo(BaseModel):
    id: UUID | None = None
    full_name: str | None = None
    subject: str | None = None
    qualification: str | None = None
    email: str | None = None
    phone: str | None = None


class AcademicSummary(BaseModel):
    overall_attendance: float | None = None
    overall_grade: float | None = None
    assignments_submitted: int | None = None
    assignments_total: int | None = None
    class_rank: int | None = None
    class_strength: int | None = None


class BehaviorConduct(BaseModel):
    overall_rating: str | None = None
    discipline_percentage: float | None = None
    punctuality_percentage: float | None = None


class TeacherStudentDetailResponse(BaseModel):
    """Full student profile as viewed by teacher."""

    id: UUID
    roll_number: str
    full_name: str
    email: str | None = None
    phone: str | None = None
    class_name: str | None = None
    section: str | None = None
    class_section: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    admission_date: date | None = None
    student_type: str | None = None
    blood_group: str | None = None
    religion: str | None = None
    address: str | None = None
    avatar_url: str | None = None
    status: str
    is_active: bool = True
    quick_stats: QuickStats | None = None
    personal_info: PersonalInfo | None = None
    parent_info: ParentInfo | None = None
    medical_info: MedicalInfo | None = None
    transport_info: TransportInfo | None = None
    assigned_mentor: MentorInfo | None = None
    academic_summary: AcademicSummary | None = None
    behavior_conduct: BehaviorConduct | None = None
    metadata: dict = {}


class ExamSubjectResult(BaseModel):
    subject: str
    marks: float | None = None
    max_marks: float | None = None
    grade: str | None = None
    percentage: float | None = None


class ExamItem(BaseModel):
    id: UUID | None = None
    exam_name: str
    exam_type: str | None = None
    date: Optional[date] = None
    results: list[ExamSubjectResult] = []
    total_marks: float | None = None
    total_max_marks: float | None = None
    overall_percentage: float | None = None
    overall_grade: str | None = None


class PerformanceAnalysis(BaseModel):
    subject_wise_marks: list[dict] = []
    subject_strengths_radar: list[dict] = []
    performance_trend_over_time: list[dict] = []


class TeacherStudentExamResultsResponse(BaseModel):
    student_id: UUID
    student_name: str
    academic_year: str | None = None
    exams: list[ExamItem] = []
    performance_analysis: PerformanceAnalysis | None = None


class MeetingItem(BaseModel):
    id: UUID | None = None
    meeting_type: str | None = None
    date: Optional[date] = None
    conducted_by: str | None = None
    attendee: str | None = None
    notes: str | None = None
    attendance_status: str | None = None
    follow_up_required: bool = False
    metadata: dict = {}


class TeacherStudentMeetingsResponse(BaseModel):
    count: int = 0
    page: int = 1
    page_size: int = 10
    total_pages: int = 0
    results: list[MeetingItem] = []


class ActivityItem(BaseModel):
    id: UUID | None = None
    activity_name: str
    year_joined: int | None = None
    role: str | None = None
    is_active: bool = True
    metadata: dict = {}


class AwardItem(BaseModel):
    id: UUID | None = None
    award_name: str
    category: str | None = None
    year: int | None = None
    description: str | None = None
    metadata: dict = {}


class TeacherStudentActivitiesResponse(BaseModel):
    activities: list[ActivityItem] = []
    awards: list[AwardItem] = []


class FeePayment(BaseModel):
    date: Optional[date] = None
    amount: float
    method: str | None = None
    status: str | None = None
    reference: str | None = None


class FeeStructureItem(BaseModel):
    component: str
    amount: float
    frequency: str | None = None


class TeacherStudentFeeSummaryResponse(BaseModel):
    student_id: UUID
    student_name: str
    academic_year: str | None = None
    summary: dict = {}
    fee_structure: list[FeeStructureItem] = []
    recent_payments: list[FeePayment] = []


class ConductNote(BaseModel):
    id: UUID | None = None
    note: str
    subject: str | None = None
    noted_by: str | None = None
    date: Optional[date] = None
    type: str | None = None


class BehaviorSummary(BaseModel):
    overall_rating: str | None = None
    discipline_percentage: float | None = None
    punctuality_percentage: float | None = None


class TeacherStudentBehaviorResponse(BaseModel):
    student_id: UUID | None = None
    student_name: str | None = None
    behavior_summary: BehaviorSummary | None = None
    recent_conduct_notes: list[ConductNote] = []
    disciplinary_records: list[dict] = []
    has_clean_record: bool = True
    metadata: dict = {}


class AttendanceRecord(BaseModel):
    date: Optional[date] = None
    subject: str | None = None
    status: str


class TeacherStudentAttendanceResponse(BaseModel):
    student_id: UUID | None = None
    student_name: str | None = None
    records: list[AttendanceRecord] = []


class TeacherStudentAssignmentsResponse(BaseModel):
    student_id: UUID | None = None
    student_name: str | None = None
    count: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0
    results: list[dict] = []
