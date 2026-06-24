from typing import Optional

import uuid
from datetime import date as date_type, datetime

from pydantic import BaseModel, Field


# --- Request Schemas ---


class GradeEntryItem(BaseModel):
    """Single grade entry for a student."""

    student_id: uuid.UUID
    marks: float


class SubmitGradesRequest(BaseModel):
    """Request to submit grades (bulk)."""

    class_id: uuid.UUID
    exam_id: uuid.UUID
    academic_year: str | None = None
    grades: list[GradeEntryItem]


class UpdateGradesRequest(BaseModel):
    """Request to update grades."""

    class_id: uuid.UUID
    exam_id: uuid.UUID
    grades: list[GradeEntryItem]


# --- Response Schemas ---


class GradeStats(BaseModel):
    """KPI stats for grades view."""

    class_average: float = 0
    highest_score: float = 0
    lowest_score: float = 0
    pass_rate: float = 0
    total_students: int = 0
    graded_count: int = 0


class GradeResultItem(BaseModel):
    """Single student grade in the list."""

    student_id: uuid.UUID
    roll_number: str
    full_name: str
    marks: float | None = None
    total_marks: float
    percentage: float | None = None
    grade: str | None = None
    status: str


class GradesListResponse(BaseModel):
    """Response for listing grades."""

    count: int
    page: int
    page_size: int
    total_pages: int
    class_section: str
    exam_name: str
    exam_type: str
    subject: str
    max_marks: float
    is_published: bool
    can_grade: bool = True
    stats: GradeStats
    results: list[GradeResultItem]


class GradeSummary(BaseModel):
    """Summary after submitting grades."""

    highest: float
    lowest: float
    average: float
    max_marks: float


class SubmitGradesResponse(BaseModel):
    """Response after submitting grades."""

    message: str
    class_section: str
    exam_name: str
    subject: str
    total_graded: int
    summary: GradeSummary
    saved_at: datetime


class UpdateGradesResponse(BaseModel):
    """Response after updating grades."""

    message: str
    class_section: str
    exam_name: str
    updated_count: int
    updated_at: datetime


class ExamForGradingItem(BaseModel):
    """Exam available for grading."""

    id: uuid.UUID
    name: str
    exam_type: str
    class_section: str
    class_section_id: uuid.UUID
    subject: str
    date: Optional[date_type] = None
    start_time: str | None = None
    end_time: str | None = None
    max_marks: float
    total_marks: float
    is_graded: bool
    graded_count: int
    total_students: int
    can_grade: bool = True
    is_published: bool = False
    # Why the teacher can see this exam: "subject_teacher" | "class_teacher" | "mentor"
    relationship: str = "subject_teacher"


class ExamTabCounts(BaseModel):
    """Counts for each tab."""

    upcoming: int = 0
    unpublished: int = 0
    completed: int = 0


class ExamsForGradingResponse(BaseModel):
    """Response listing exams available for grading."""

    count: int = 0
    page: int = 1
    page_size: int = 10
    total_pages: int = 1
    tab_counts: ExamTabCounts = ExamTabCounts()
    results: list[ExamForGradingItem]


class ExamDetailResponse(BaseModel):
    """Response for a single exam detail."""

    id: uuid.UUID
    name: str
    exam_type: str
    class_section: str
    class_section_id: uuid.UUID
    subject: str
    date: Optional[date_type] = None
    start_time: str | None = None
    end_time: str | None = None
    max_marks: float
    total_students: int
    graded_count: int
    can_grade: bool = True
    is_published: bool = False
    relationship: str = "subject_teacher"


class MarksDistributionItem(BaseModel):
    """Marks distribution range."""

    range: str
    count: int


class GradeDistributionItem(BaseModel):
    """Grade distribution entry."""

    grade: str
    count: int
    percentage: float


class GradeReportResponse(BaseModel):
    """Response for exam report."""

    exam_name: str
    class_section: str
    subject: str
    max_marks: float
    stats: GradeStats
    marks_distribution: list[MarksDistributionItem] = Field(default_factory=list)
    grade_distribution: list[GradeDistributionItem] = Field(default_factory=list)


class LeaderboardItem(BaseModel):
    """Single leaderboard entry."""

    rank: int
    roll_number: str
    student_name: str
    marks: float
    percentage: float
    grade: str


class LeaderboardResponse(BaseModel):
    """Response for leaderboard."""

    exam_name: str
    class_section: str
    subject: str
    max_marks: float
    leaderboard: list[LeaderboardItem]


class ImportGradesResponse(BaseModel):
    """Response after importing grades from CSV."""

    imported: int
    skipped: int
    errors: list[dict] = Field(default_factory=list)
    message: str


class PublishExamResponse(BaseModel):
    """Response after publishing exam results."""

    message: str
    exam_id: uuid.UUID
    exam_name: str
    published_at: datetime
