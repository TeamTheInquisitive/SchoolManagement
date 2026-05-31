from typing import Optional

from uuid import UUID

from pydantic import BaseModel


class ClassInfo(BaseModel):
    class_name: str
    section: str
    display_label: str


class PeriodInfo(BaseModel):
    id: UUID
    start_time: str
    end_time: str
    duration_minutes: int


class StudentSlotItem(BaseModel):
    id: UUID
    subject: str | None = None
    teacher: str | None = None
    type: str  # class/lab/free
    duration_minutes: int


class SubjectSummaryItem(BaseModel):
    subject: str
    teacher: str
    sessions_per_week: int
    type: str


class StudentWeeklyTimetableResponse(BaseModel):
    class_info: ClassInfo
    academic_year: str
    current_day: str
    is_today_holiday: bool = False
    total_periods: int
    periods: list[PeriodInfo]
    timetable: dict[str, list[StudentSlotItem]]
    subject_summary: list[SubjectSummaryItem]


class StudentDayPeriod(BaseModel):
    id: UUID
    subject: str | None = None
    teacher: str | None = None
    start_time: str
    end_time: str
    duration_minutes: int
    type: str  # class/lab/free


class StudentDayResponse(BaseModel):
    class_info: ClassInfo
    date: str
    day: str
    is_today: bool = False
    is_holiday: bool = False
    periods: list[StudentDayPeriod]
