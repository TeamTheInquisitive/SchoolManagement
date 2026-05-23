from typing import Optional

import uuid
from datetime import date, datetime

from pydantic import BaseModel


class StudentDashboardStatsResponse(BaseModel):
    """KPI stats for student dashboard."""

    attendance_percentage: float = 0.0
    average_grade: str = ""
    pending_assignments: int = 0
    fee_status: str = "Clear"


class StudentTodayScheduleItem(BaseModel):
    period_number: int | None = None
    start_time: str | None = None
    end_time: str | None = None
    subject: str = ""
    teacher_name: str = ""
    slot_type: str = "Lecture"


class StudentTodayScheduleResponse(BaseModel):
    date: str
    day: str
    total_classes: int = 0
    schedule: list[StudentTodayScheduleItem] = []


class StudentPendingAssignmentItem(BaseModel):
    id: uuid.UUID
    title: str
    subject: str
    due_date: str
    total_marks: float | None = None
    status: str = "Pending"


class StudentPendingAssignmentsResponse(BaseModel):
    total: int = 0
    items: list[StudentPendingAssignmentItem] = []


class StudentUpcomingExamItem(BaseModel):
    id: uuid.UUID
    name: str
    subject: str
    date: str
    total_marks: float = 0
    start_time: str | None = None
    end_time: str | None = None


class StudentUpcomingExamsResponse(BaseModel):
    total: int = 0
    items: list[StudentUpcomingExamItem] = []


class SubjectAttendanceItem(BaseModel):
    subject: str
    total_classes: int = 0
    attended: int = 0
    percentage: float = 0.0


class SubjectAttendanceResponse(BaseModel):
    overall_percentage: float = 0.0
    subjects: list[SubjectAttendanceItem] = []


class RecentResultItem(BaseModel):
    exam_id: uuid.UUID
    exam_name: str
    subject: str
    marks_obtained: float | None = None
    total_marks: float = 0
    grade: str | None = None
    percentage: float | None = None


class RecentResultsResponse(BaseModel):
    items: list[RecentResultItem] = []


class AnnouncementItem(BaseModel):
    id: uuid.UUID
    title: str
    message: str
    date: str
    type: str = ""


class AnnouncementsResponse(BaseModel):
    items: list[AnnouncementItem] = []


class NotificationItem(BaseModel):
    id: uuid.UUID
    title: str
    message: str
    date: str
    is_read: bool = False


class NotificationsResponse(BaseModel):
    unread_count: int = 0
    items: list[NotificationItem] = []


class FeeStatusItem(BaseModel):
    fee_type: str
    amount: float = 0
    paid: float = 0
    pending: float = 0
    due_date: str = ""
    status: str = ""


class FeeStatusResponse(BaseModel):
    total_fees: float = 0
    total_paid: float = 0
    total_pending: float = 0
    items: list[FeeStatusItem] = []


class ParentMeetingItem(BaseModel):
    id: uuid.UUID
    meeting_type: str | None = None
    date: str
    conducted_by: str = ""
    status: str = ""
    notes: str | None = None


class ParentMeetingsResponse(BaseModel):
    total: int = 0
    items: list[ParentMeetingItem] = []
