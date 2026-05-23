from typing import Optional

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


# --- Request Schemas ---


class CreateAssignmentRequest(BaseModel):
    """Request to create a new assignment."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    class_name: str = Field(..., min_length=1)
    section: str = Field(..., min_length=1)
    due_date: date
    max_marks: float | None = None
    academic_year: str | None = None


class UpdateAssignmentRequest(BaseModel):
    """Request to update an existing assignment."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    due_date: date | None = None
    max_marks: float | None = None


class GradeSubmissionRequest(BaseModel):
    """Request to grade a student submission."""

    marks: float = Field(..., ge=0)
    feedback: str | None = None


# --- Response Schemas ---


class AssignmentSummary(BaseModel):
    """KPI summary for assignments list."""

    total_assignments: int
    active: int
    graded: int
    to_review: int


class AssignmentListItem(BaseModel):
    """Single assignment in the list response."""

    id: uuid.UUID
    title: str
    description: str | None = None
    class_name: str
    section: str
    class_section: str
    subject: str
    due_date: date
    max_marks: float | None = None
    total_students: int
    submissions_count: int
    graded_count: int
    status: str
    created_at: datetime
    is_active: bool
    metadata: dict = Field(default_factory=dict)


class AssignmentListResponse(BaseModel):
    """Paginated assignment list response with summary."""

    count: int
    page: int
    page_size: int
    total_pages: int
    summary: AssignmentSummary
    results: list[AssignmentListItem]


class AssignmentCreateResponse(BaseModel):
    """Response after creating an assignment."""

    id: uuid.UUID
    title: str
    description: str | None = None
    class_name: str
    section: str
    class_section: str
    subject: str
    due_date: date
    max_marks: float | None = None
    total_students: int
    submissions_count: int
    graded_count: int
    status: str
    created_at: datetime
    is_active: bool
    academic_year: str
    metadata: dict = Field(default_factory=dict)


class SubmissionStats(BaseModel):
    """Submission statistics for an assignment detail view."""

    total_students: int
    submitted: int
    not_submitted: int
    graded: int
    average_marks: float | None = None


class AssignmentDetailResponse(BaseModel):
    """Detailed assignment response."""

    id: uuid.UUID
    title: str
    description: str | None = None
    class_id: uuid.UUID
    class_section: str
    subject: str
    due_date: date
    max_marks: float | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    academic_year: str
    submission_stats: SubmissionStats
    metadata: dict = Field(default_factory=dict)


class AssignmentUpdateResponse(BaseModel):
    """Response after updating an assignment."""

    id: uuid.UUID
    title: str
    description: str | None = None
    class_id: uuid.UUID
    class_section: str
    subject: str
    due_date: date
    max_marks: float | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    academic_year: str
    metadata: dict = Field(default_factory=dict)


class AssignmentDeleteResponse(BaseModel):
    """Response after deleting an assignment."""

    message: str
    id: uuid.UUID
    deactivated_on: datetime


class SubmissionListItem(BaseModel):
    """Single submission in the list."""

    id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    roll_number: str | None = None
    submitted_at: datetime | None = None
    status: str
    marks: float | None = None
    max_marks: float | None = None
    graded_at: datetime | None = None


class SubmissionListResponse(BaseModel):
    """Paginated list of submissions for an assignment."""

    count: int
    page: int
    page_size: int
    total_pages: int
    assignment_id: uuid.UUID
    assignment_title: str
    class_section: str
    total_students: int
    submissions_count: int
    results: list[SubmissionListItem]


class GradeSubmissionResponse(BaseModel):
    """Response after grading a submission."""

    id: uuid.UUID
    student_name: str
    marks: float
    max_marks: float | None = None
    feedback: str | None = None
    status: str
    graded_at: datetime
    message: str
