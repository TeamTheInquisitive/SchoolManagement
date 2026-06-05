from typing import Optional

import uuid
from datetime import date as date_type, datetime
from enum import Enum

from pydantic import BaseModel


class AttendanceStatus(str, Enum):
    Present = "Present"
    Absent = "Absent"
    Late = "Late"


# --- Request Schemas ---


class AttendanceRecordInput(BaseModel):
    student_id: uuid.UUID
    status: AttendanceStatus


class SubmitAttendanceRequest(BaseModel):
    class_id: uuid.UUID
    date: Optional[date_type] = None
    academic_year: str
    records: list[AttendanceRecordInput]


class UpdateAttendanceRequest(BaseModel):
    class_id: uuid.UUID
    date: Optional[date_type] = None
    records: list[AttendanceRecordInput]


# --- Response Schemas ---


class AttendanceSummary(BaseModel):
    total_students: int
    present: int
    absent: int
    late: int
    attendance_rate: float


class StudentAttendanceRecord(BaseModel):
    student_id: uuid.UUID
    roll_number: str | None = None
    full_name: str | None = None
    status: str


class GetAttendanceResponse(BaseModel):
    class_section: str
    class_name: str
    section: str
    date: Optional[date_type] = None
    is_submitted: bool
    submitted_at: datetime | None = None
    summary: AttendanceSummary | None = None
    records: list[StudentAttendanceRecord]


class SubmitAttendanceResponse(BaseModel):
    message: str
    class_section: str
    date: Optional[date_type] = None
    summary: AttendanceSummary
    submitted_at: datetime


class UpdateAttendanceResponse(BaseModel):
    message: str
    class_section: str
    date: Optional[date_type] = None
    summary: AttendanceSummary
    updated_at: datetime


class AttendanceHistoryItem(BaseModel):
    id: uuid.UUID
    class_name: str | None = None
    section: str | None = None
    class_section: str | None = None
    date: Optional[date_type] = None
    status: str | None = None
    total_students: int = 0
    present: int = 0
    absent: int = 0
    late: int = 0
    submitted_at: datetime | None = None


class AttendanceHistoryResponse(BaseModel):
    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[AttendanceHistoryItem]


class CancelAttendanceResponse(BaseModel):
    id: uuid.UUID
    class_section: str
    date: Optional[date_type] = None
    status: str
    cancelled_on: date
    message: str


class StudentBelowThreshold(BaseModel):
    student_id: uuid.UUID
    full_name: str
    roll_number: str | None = None
    attendance_percentage: float


class AttendanceSummaryResponse(BaseModel):
    class_section: str
    month: int
    year: int
    academic_year: str
    working_days: int
    days_marked: int
    average_attendance_percentage: float
    students_below_75: list[StudentBelowThreshold]
