from typing import Optional

import uuid
from datetime import date

from pydantic import BaseModel


class DashboardStatsResponse(BaseModel):
    """KPI stats for admin dashboard."""

    total_students: int = 0
    total_teachers: int = 0
    active_classes: int = 0
    fee_collection_percentage: float = 0.0
    students_change: str = "+0%"
    teachers_change: str = "+0%"
    classes_change: str = "+0"
    fee_change: str = "+0%"


class AttendanceTrendItem(BaseModel):
    month: str
    value: float


class AttendanceTrendsResponse(BaseModel):
    data: list[AttendanceTrendItem]


class FeeCollectionItem(BaseModel):
    name: str
    value: float
    color: str


class FeeCollectionStatusResponse(BaseModel):
    data: list[FeeCollectionItem]


class StudentDistributionItem(BaseModel):
    class_name: str
    male: int = 0
    female: int = 0


class StudentDistributionResponse(BaseModel):
    data: list[StudentDistributionItem]


class RecentActivityItem(BaseModel):
    id: uuid.UUID | str
    title: str
    description: str
    date: str
    tag: str = ""
    category: str = ""


class RecentActivitiesResponse(BaseModel):
    data: list[RecentActivityItem]


class PendingApprovalItem(BaseModel):
    id: uuid.UUID
    employee_name: str
    leave_type: str
    duration_days: float
    from_date: str
    to_date: str


class LeaveOverviewResponse(BaseModel):
    pending_requests: int = 0
    approved: int = 0
    on_leave_today: int = 0
    upcoming_leaves: int = 0
    pending_approvals: list[PendingApprovalItem] = []


class LowAttendanceItem(BaseModel):
    student_id: uuid.UUID
    name: str
    class_section: str
    attendance_percentage: float


class LowAttendanceResponse(BaseModel):
    data: list[LowAttendanceItem]
