from typing import Optional

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


# --- Response Schemas ---


class AssignmentSummary(BaseModel):
    """Summary stats for student assignments."""

    total: int
    pending: int
    overdue: int
    submitted: int
    graded: int
    late: int


class StudentAssignmentListItem(BaseModel):
    """Single assignment item in student list."""

    id: uuid.UUID
    title: str
    subject: str
    teacher: str
    description: str | None = None
    assigned_date: date
    due_date: date
    max_marks: float | None = None
    marks_obtained: float | None = None
    status: str
    is_overdue: bool
    metadata: dict = Field(default_factory=dict)


class StudentAssignmentListResponse(BaseModel):
    """Paginated student assignment list with summary."""

    count: int
    page: int
    page_size: int
    total_pages: int
    summary: AssignmentSummary
    results: list[StudentAssignmentListItem]


class AssignmentAttachment(BaseModel):
    """Attachment info for assignment."""

    id: str
    filename: str
    url: str
    size_bytes: int | None = None
    type: str | None = None


class StudentAssignmentDetailResponse(BaseModel):
    """Detailed student assignment view."""

    id: uuid.UUID
    title: str
    subject: str
    teacher: str
    description: str | None = None
    assigned_date: date
    due_date: date
    max_marks: float | None = None
    marks_obtained: float | None = None
    status: str
    is_overdue: bool
    submission_status: str
    attachments: list[AssignmentAttachment] = Field(default_factory=list)
    class_section: str
    academic_year: str
    created_at: datetime
    updated_at: datetime
    metadata: dict = Field(default_factory=dict)


class SubmissionFile(BaseModel):
    """File in a submission."""

    id: str
    filename: str
    url: str
    size_bytes: int | None = None
    type: str | None = None
    uploaded_at: datetime | None = None


class SubmitAssignmentResponse(BaseModel):
    """Response after submitting an assignment."""

    id: uuid.UUID
    assignment_id: uuid.UUID
    status: str
    comments: str | None = None
    files: list[SubmissionFile] = Field(default_factory=list)
    submitted_at: datetime
    is_late: bool
    metadata: dict = Field(default_factory=dict)


class GradeInfo(BaseModel):
    """Grade details for a graded submission."""

    marks_obtained: float
    max_marks: float | None = None
    percentage: float | None = None
    grade: str | None = None
    graded_by: str | None = None
    graded_at: datetime | None = None
    feedback: str | None = None


class StudentSubmissionDetailResponse(BaseModel):
    """Student's own submission details with grade info."""

    id: uuid.UUID
    assignment_id: uuid.UUID
    assignment_title: str
    subject: str
    status: str
    comments: str | None = None
    files: list[SubmissionFile] = Field(default_factory=list)
    submitted_at: datetime | None = None
    is_late: bool
    grade: GradeInfo | None = None
    metadata: dict = Field(default_factory=dict)
