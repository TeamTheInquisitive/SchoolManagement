from typing import Optional

from datetime import time
from uuid import UUID

from pydantic import BaseModel


class TeacherTimetableStats(BaseModel):
    total_classes_per_week: int
    practical_sessions: int
    free_periods: int


class TeacherSlotItem(BaseModel):
    id: UUID
    start_time: str
    end_time: str
    duration_minutes: int
    subject: str | None = None
    type: str  # Lecture/Practical/Free/Break
    class_name: str | None = None
    section: str | None = None
    class_section: str | None = None
    label: str | None = None  # For breaks


class TeacherWeeklyTimetableResponse(BaseModel):
    academic_year: str
    stats: TeacherTimetableStats
    working_days: list[str]
    timetable: dict[str, list[TeacherSlotItem]]


class TeacherTodayStats(BaseModel):
    total_classes_today: int
    practical_sessions_today: int
    free_periods_today: int


class TeacherTodayResponse(BaseModel):
    date: str
    day: str
    stats: TeacherTodayStats
    schedule: list[TeacherSlotItem]
