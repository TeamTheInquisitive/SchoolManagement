from typing import Optional

import uuid
from datetime import date as date_type, datetime

from pydantic import BaseModel, Field


# --- Request Schemas ---


class CreateExamRequest(BaseModel):
    """Request to create a new exam."""

    name: str = Field(..., min_length=1, max_length=255)
    exam_type: str = Field(..., min_length=1, max_length=50)
    class_name: str = Field(..., min_length=1)
    section: str = Field(..., min_length=1)
    subject: str = Field(..., min_length=1)
    date: Optional[date_type] = None
    start_time: str | None = None
    end_time: str | None = None
    total_marks: float = Field(..., gt=0)
    passing_marks: float | None = None
    academic_year: str | None = None
    term: str | None = None
    examiner_id: uuid.UUID | None = None
    status: str = "Draft"
    metadata: dict = Field(default_factory=dict)


class UpdateExamRequest(BaseModel):
    """Request to update an exam."""

    name: str | None = Field(default=None, max_length=255)
    exam_type: str | None = None
    date: Optional[date_type] = None
    start_time: str | None = None
    end_time: str | None = None
    total_marks: float | None = None
    passing_marks: float | None = None
    status: str | None = None
    term: str | None = None
    examiner_id: uuid.UUID | None = None
    metadata: dict | None = None


class ResultEntryItem(BaseModel):
    """Single student result entry."""

    student_id: uuid.UUID
    marks_obtained: float | None = None
    attendance: str = "Present"
    remarks: str | None = None


class EnterResultsRequest(BaseModel):
    """Request to enter results for multiple students."""

    results: list[ResultEntryItem]


class UpdateResultRequest(BaseModel):
    """Request to update a single result."""

    marks_obtained: float | None = None
    attendance: str | None = None
    remarks: str | None = None


class PublishResultsRequest(BaseModel):
    """Request to publish exam results."""

    notify_students: bool = True
    notify_parents: bool = True
    notification_message: str | None = None


class GradeScaleItem(BaseModel):
    """A single grade scale entry."""

    grade: str
    min_percentage: float
    max_percentage: float
    grade_point: float | None = None
    description: str | None = None


class UpdateGradeSystemRequest(BaseModel):
    """Request to update the grade system."""

    name: str | None = None
    grades: list[GradeScaleItem]


class GenerateReportCardsRequest(BaseModel):
    """Request to batch generate report cards."""

    class_name: str
    section: str
    academic_year: str
    term: str | None = None
    include_attendance: bool = True
    include_remarks: bool = True


# --- Response Schemas ---


class ExamListItem(BaseModel):
    """Single exam in the list response."""

    id: uuid.UUID
    name: str
    type: str
    class_name: str
    section: str
    subject: str
    date: Optional[date_type] = None
    start_time: str | None = None
    end_time: str | None = None
    total_marks: float
    passing_marks: float | None = None
    total_students: int = 0
    present: int = 0
    absent: int = 0
    pass_count: int = 0
    fail_count: int = 0
    pass_rate: float = 0
    class_average: float = 0
    highest_marks: float = 0
    lowest_marks: float = 0
    status: str
    academic_year: str
    term: str | None = None
    examiner_id: uuid.UUID | None = None
    examiner_name: str | None = None
    created_at: datetime
    published_at: datetime | None = None
    metadata: dict = Field(default_factory=dict)


class ExamListSummary(BaseModel):
    """Summary stats for exam list."""

    total_exams: int
    published: int
    upcoming: int
    draft: int
    average_pass_rate: float


class ExamListResponse(BaseModel):
    """Paginated exam list response."""

    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[ExamListItem]
    summary: ExamListSummary


class GradeDistributionItem(BaseModel):
    """Grade distribution entry."""

    grade: str
    count: int
    percentage: float


class TopperItem(BaseModel):
    """Topper entry for exam detail."""

    student_id: uuid.UUID
    student_name: str
    roll_number: str
    marks: float
    grade: str
    rank: int


class ExamDetailResponse(BaseModel):
    """Detailed exam response with result summary."""

    id: uuid.UUID
    name: str
    type: str
    class_name: str
    section: str
    subject: str
    date: Optional[date_type] = None
    start_time: str | None = None
    end_time: str | None = None
    total_marks: float
    passing_marks: float | None = None
    total_students: int = 0
    present: int = 0
    absent: int = 0
    pass_count: int = 0
    fail_count: int = 0
    pass_rate: float = 0
    class_average: float = 0
    highest_marks: float = 0
    lowest_marks: float = 0
    status: str
    academic_year: str
    term: str | None = None
    examiner_id: uuid.UUID | None = None
    examiner_name: str | None = None
    created_at: datetime
    published_at: datetime | None = None
    grade_distribution: list[GradeDistributionItem] = Field(default_factory=list)
    toppers: list[TopperItem] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class ExamCreateResponse(BaseModel):
    """Response after creating an exam."""

    id: uuid.UUID
    name: str
    type: str
    class_name: str
    section: str
    subject: str
    date: Optional[date_type] = None
    start_time: str | None = None
    end_time: str | None = None
    total_marks: float
    passing_marks: float | None = None
    total_students: int = 0
    status: str
    academic_year: str
    term: str | None = None
    examiner_id: uuid.UUID | None = None
    examiner_name: str | None = None
    created_at: datetime
    metadata: dict = Field(default_factory=dict)


class ExamCancelResponse(BaseModel):
    """Response after cancelling an exam."""

    id: uuid.UUID
    name: str
    status: str
    cancelled_on: date_type
    message: str


class ResultItem(BaseModel):
    """Single result in the results list."""

    id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    roll_number: str
    marks_obtained: float | None = None
    percentage: float | None = None
    grade: str | None = None
    rank: int | None = None
    status: str
    attendance: str
    remarks: str | None = None


class ResultsSummary(BaseModel):
    """Summary stats for exam results."""

    total_students: int
    present: int
    absent: int
    pass_count: int = Field(alias="pass", default=0)
    fail_count: int = Field(alias="fail", default=0)
    class_average: float
    highest: float
    lowest: float

    class Config:
        populate_by_name = True


class ExamResultsResponse(BaseModel):
    """Response for getting all results of an exam."""

    exam_id: uuid.UUID
    exam_name: str
    subject: str
    class_section: str
    total_marks: float
    passing_marks: float | None = None
    results: list[ResultItem]
    summary: ResultsSummary


class EnteredResultItem(BaseModel):
    """Single result entry response."""

    student_id: uuid.UUID
    marks_obtained: float | None = None
    grade: str | None = None
    rank: int | None = None
    status: str


class EnterResultsResponse(BaseModel):
    """Response after entering results."""

    exam_id: uuid.UUID
    entered: int
    results: list[EnteredResultItem]
    message: str


class BulkUploadResponse(BaseModel):
    """Response after CSV bulk upload."""

    exam_id: uuid.UUID
    imported: int
    skipped: int
    errors: list[dict] = Field(default_factory=list)
    message: str


class UpdateResultResponse(BaseModel):
    """Response after updating a result."""

    id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    marks_obtained: float | None = None
    previous_marks: float | None = None
    grade: str | None = None
    previous_grade: str | None = None
    rank: int | None = None
    status: str
    updated_at: datetime
    updated_by: str | None = None
    update_reason: str | None = None


class PublishResultsResponse(BaseModel):
    """Response after publishing results."""

    exam_id: uuid.UUID
    status: str
    published_at: datetime
    published_by: str | None = None
    notifications_sent: dict = Field(default_factory=dict)
    message: str


class GradeScaleResponse(BaseModel):
    """Single grade scale in response."""

    grade: str
    min_percentage: float
    max_percentage: float
    grade_point: float | None = None
    description: str | None = None


class GradeSystemResponse(BaseModel):
    """Response for the grade system."""

    id: uuid.UUID
    name: str
    academic_year: str
    is_active: bool
    grades: list[GradeScaleResponse]
    metadata: dict = Field(default_factory=dict)


class GradeSystemUpdateResponse(BaseModel):
    """Response after updating grade system."""

    message: str
    id: uuid.UUID
    grades: list[GradeScaleResponse]


class SubjectTrendItem(BaseModel):
    """A single exam trend point."""

    exam_name: str
    date: Optional[date_type] = None
    average: float
    pass_rate: float


class SubjectPerformance(BaseModel):
    """Performance for a single subject."""

    subject: str
    exams_conducted: int
    average_pass_rate: float
    class_average: float
    highest_average: float
    lowest_average: float
    trend: list[SubjectTrendItem] = Field(default_factory=list)


class TermComparison(BaseModel):
    """Term comparison entry."""

    term: str
    class_average: float
    pass_rate: float
    toppers_count: int


class StudentRanking(BaseModel):
    """Student ranking entry."""

    rank: int
    student_id: uuid.UUID
    student_name: str
    weighted_average: float
    grade: str


class AtRiskStudent(BaseModel):
    """At-risk student entry."""

    student_id: uuid.UUID
    student_name: str
    weighted_average: float
    grade: str
    trend: str


class AnalyticsResponse(BaseModel):
    """Analytics response for class/subject performance."""

    class_name: str
    section: str
    academic_year: str
    subject_performance: list[SubjectPerformance] = Field(default_factory=list)
    term_comparison: list[TermComparison] = Field(default_factory=list)
    student_rankings: list[StudentRanking] = Field(default_factory=list)
    grade_distribution: list[GradeDistributionItem] = Field(default_factory=list)
    at_risk_students: list[AtRiskStudent] = Field(default_factory=list)


class ReportCardSubjectExam(BaseModel):
    """Marks entry for an exam in report card."""

    marks: float
    total: float


class ReportCardSubject(BaseModel):
    """Subject entry in the report card."""

    subject: str
    weighted_total: float | None = None
    grade: str | None = None
    grade_point: float | None = None
    remarks: str | None = None


class ReportCardOverall(BaseModel):
    """Overall summary in report card."""

    total_weighted_average: float
    overall_grade: str | None = None
    overall_gpa: float | None = None
    rank: int | None = None
    class_strength: int
    attendance_percentage: float | None = None
    total_working_days: int | None = None
    days_present: int | None = None


class ReportCardResponse(BaseModel):
    """Report card response."""

    student_id: uuid.UUID
    student_name: str
    roll_number: str
    class_section: str
    academic_year: str
    term: str | None = None
    school_name: str
    subjects: list[ReportCardSubject] = Field(default_factory=list)
    overall: ReportCardOverall
    class_teacher_remarks: str | None = None
    principal_remarks: str | None = None
    generated_at: datetime
    metadata: dict = Field(default_factory=dict)


class GenerateReportCardsResponse(BaseModel):
    """Response after batch generating report cards."""

    generated: int
    class_section: str
    academic_year: str
    term: str | None = None
    download_url: str | None = None
    expires_at: datetime | None = None


class ScheduleExamItem(BaseModel):
    """Exam entry in the schedule."""

    date: Optional[date_type] = None
    subject: str
    start_time: str | None = None
    end_time: str | None = None
    total_marks: float
    type: str


class ExamScheduleResponse(BaseModel):
    """Exam schedule response."""

    class_name: str
    section: str
    term: str | None = None
    academic_year: str
    exams: list[ScheduleExamItem] = Field(default_factory=list)
