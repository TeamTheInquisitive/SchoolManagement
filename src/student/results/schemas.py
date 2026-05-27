from typing import Optional

import uuid
from datetime import date as Date, datetime

from pydantic import BaseModel, Field


# --- Response Schemas ---


class ResultSummary(BaseModel):
    """Overall results summary."""

    average_score: float = 0
    highest_score: float = 0
    lowest_score: float = 0
    avg_rank: float = 0


class PerformanceTrendItem(BaseModel):
    """Single data point in performance trend (line chart)."""

    exam_name: str
    exam_type: str
    date: Optional[Date] = None
    percentage: float
    subjects: dict[str, float] = Field(default_factory=dict)


class SubjectWisePerformance(BaseModel):
    """Subject-wise performance (bar chart)."""

    subject: str
    student_percentage: float
    max_marks: float


class PerformanceRadar(BaseModel):
    """Radar chart data."""

    subjects: list[str] = Field(default_factory=list)
    student_scores: list[float] = Field(default_factory=list)
    max_marks: float = 100


class ResultsOverviewResponse(BaseModel):
    """Response for overall results overview."""

    academic_year: str
    summary: ResultSummary
    filters: dict = Field(default_factory=dict)
    performance_trend: list[PerformanceTrendItem] = Field(default_factory=list)
    subject_wise_performance: list[SubjectWisePerformance] = Field(default_factory=list)
    performance_radar: PerformanceRadar = Field(default_factory=PerformanceRadar)
    metadata: dict = Field(default_factory=dict)


class ExamSubjectDetail(BaseModel):
    """Subject detail within an exam result."""

    subject: str
    marks_obtained: float
    max_marks: float
    percentage: float
    grade: str | None = None
    class_average: float | None = None
    highest_in_class: float | None = None
    rank: int | None = None
    status: str
    pass_marks: float | None = None


class ExamDetailResponse(BaseModel):
    """Detailed result for a specific exam."""

    exam_id: uuid.UUID
    exam_name: str
    exam_type: str
    date: Optional[Date] = None
    class_section: str
    academic_year: str
    total_marks_obtained: float
    total_max_marks: float
    overall_percentage: float
    overall_grade: str | None = None
    class_rank: int | None = None
    total_students: int
    subjects: list[ExamSubjectDetail] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class ExamSubjectBrief(BaseModel):
    """Brief subject detail in exam list."""

    subject: str
    marks_obtained: float
    max_marks: float
    percentage: float
    grade: str | None = None
    rank: int | None = None
    status: str
    pass_marks: float | None = None
    leaderboard_url: str | None = None


class ExamResultListItem(BaseModel):
    """Single exam result in list."""

    id: uuid.UUID
    exam_name: str
    exam_type: str
    date: Optional[Date] = None
    total_marks_obtained: float
    total_max_marks: float
    percentage: float
    grade: str | None = None
    class_rank: int | None = None
    total_students: int
    subjects_count: int
    subjects: list[ExamSubjectBrief] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class ExamResultsListResponse(BaseModel):
    """Paginated list of exam results."""

    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[ExamResultListItem]
    metadata: dict = Field(default_factory=dict)


class LeaderboardPerformer(BaseModel):
    """Single performer in leaderboard."""

    rank: int
    student_name: str
    marks_obtained: float
    max_marks: float
    percentage: float
    grade: str | None = None
    is_current_student: bool = False


class LeaderboardResponse(BaseModel):
    """Response for exam leaderboard."""

    exam_id: uuid.UUID
    exam_name: str
    subject: str | None = None
    academic_year: str
    student_rank: int | None = None
    student_score: float | None = None
    max_marks: float
    percentile: float | None = None
    top_performers: list[LeaderboardPerformer] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class DownloadReportResponse(BaseModel):
    """Response for download report."""

    download_url: str
    file_name: str
    content_type: str
    generated_at: datetime
    report_scope: str
    academic_year: str
    metadata: dict = Field(default_factory=dict)
