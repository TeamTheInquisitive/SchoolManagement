from typing import Optional

import uuid
from datetime import date, time, datetime

from pydantic import BaseModel


class TeacherDashboardStatsResponse(BaseModel):
    """KPI stats for teacher dashboard."""

    total_students: int = 0
    pending_reviews: int = 0
    upcoming_exams: int = 0
    classes_today: int = 0


class TodayScheduleItem(BaseModel):
    period_number: int | None = None
    start_time: str | None = None
    end_time: str | None = None
    subject: str = ""
    class_name: str = ""
    section: str = ""
    slot_type: str = "Lecture"


class TodayScheduleResponse(BaseModel):
    date: str
    day: str
    total_classes: int = 0
    schedule: list[TodayScheduleItem] = []


class PendingReviewItem(BaseModel):
    id: uuid.UUID
    title: str
    class_section: str
    subject: str
    due_date: str
    submissions_pending: int = 0


class PendingReviewsResponse(BaseModel):
    total: int = 0
    items: list[PendingReviewItem] = []


class UpcomingExamItem(BaseModel):
    id: uuid.UUID
    name: str
    class_section: str
    subject: str
    date: str
    total_marks: float = 0


class UpcomingExamsResponse(BaseModel):
    total: int = 0
    items: list[UpcomingExamItem] = []


class ClassSummaryItem(BaseModel):
    class_section_id: str
    class_name: str
    section: str
    class_section: str = ""
    subject: str | None = None
    student_count: int = 0
    is_class_teacher: bool = False


class ClassesSummaryResponse(BaseModel):
    total_classes: int = 0
    classes: list[ClassSummaryItem] = []


class LeaveUpdateItem(BaseModel):
    id: uuid.UUID
    leave_type: str
    from_date: str
    to_date: str
    days: float = 0
    status: str


class LeaveUpdatesResponse(BaseModel):
    items: list[LeaveUpdateItem] = []


class MenteeItem(BaseModel):
    student_id: uuid.UUID
    name: str
    class_section: str
    attendance_percentage: float = 0


class MenteesSummaryResponse(BaseModel):
    total: int = 0
    mentees: list[MenteeItem] = []


class AdhocClassSummaryItem(BaseModel):
    id: uuid.UUID
    class_name: str
    section: str
    subject: str
    date: str
    type: str
    status: str


class AdhocClassesDashboardResponse(BaseModel):
    total: int = 0
    items: list[AdhocClassSummaryItem] = []
