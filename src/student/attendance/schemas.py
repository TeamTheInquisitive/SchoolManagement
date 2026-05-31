from typing import Optional

import uuid
from datetime import date as Date

from pydantic import BaseModel


# --- Nested Schemas ---


class OverallAttendance(BaseModel):
    percentage: float
    present_days: int
    absent_days: int
    late_days: int
    excused_days: int
    total_days: int
    threshold: int = 75
    status: str  # "above_threshold" or "below_threshold"


class AttendanceStats(BaseModel):
    present: int
    absent: int
    late: int
    excused: int


class AttendanceDistribution(BaseModel):
    present: int
    absent: int
    late: int
    excused: int


class AttendanceWarning(BaseModel):
    active: bool
    type: str
    message: str
    severity: str  # "critical", "warning", "info"


class SubjectAttendance(BaseModel):
    subject: str
    percentage: float
    present: int
    total: int
    color: str
    metadata: dict = {}


class RecentAttendanceRecord(BaseModel):
    date: Optional[Date] = None
    subject: str | None = None
    status: str
    period: int | None = None
    metadata: dict = {}


# --- Response Schemas ---


class StudentAttendanceOverviewResponse(BaseModel):
    academic_year: str
    overall: OverallAttendance
    stats: AttendanceStats
    distribution: AttendanceDistribution
    warning: AttendanceWarning | None = None
    subject_wise: list[SubjectAttendance]
    recent_records: list[RecentAttendanceRecord]
    metadata: dict = {}


class AttendanceHistoryItem(BaseModel):
    id: uuid.UUID
    date: Optional[Date] = None
    subject: str | None = None
    period: int | None = None
    status: str
    marked_by: str | None = None
    remarks: str | None = None
    metadata: dict = {}


class AttendanceHistoryFilters(BaseModel):
    subject: str | None = None
    month: str | None = None
    status: str | None = None


class StudentAttendanceHistoryResponse(BaseModel):
    count: int
    page: int
    page_size: int
    total_pages: int
    filters: AttendanceHistoryFilters
    results: list[AttendanceHistoryItem]
    metadata: dict = {}


class WarningItem(BaseModel):
    id: str
    type: str
    severity: str
    message: str
    issued_date: Date
    active: bool
    acknowledged: bool = False
    metadata: dict = {}


class SubjectAtRisk(BaseModel):
    subject: str
    percentage: float
    present: int
    total: int
    deficit: int
    message: str
    metadata: dict = {}


class StudentAttendanceWarningsResponse(BaseModel):
    academic_year: str
    threshold: int = 75
    current_percentage: float
    status: str
    warnings: list[WarningItem]
    subjects_at_risk: list[SubjectAtRisk]
    metadata: dict = {}
