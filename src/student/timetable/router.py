from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Query

from src.auth.dependencies import SchoolDep, StudentUser
from src.core.dependencies import SessionDep
from src.student.timetable import service
from src.student.timetable.schemas import (
    StudentDayResponse,
    StudentWeeklyTimetableResponse,
)

router = APIRouter(prefix="/student/timetable", tags=["Student Timetable"])


@router.get("", response_model=StudentWeeklyTimetableResponse)
async def get_weekly_timetable(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
    academic_year: str | None = Query(default=None),
) -> StudentWeeklyTimetableResponse:
    """Get the weekly timetable grid for the student's class."""
    result = await service.get_weekly_timetable(db, school.id, user, academic_year)
    return StudentWeeklyTimetableResponse(**result)


@router.get("/day", response_model=StudentDayResponse)
async def get_day_schedule(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
    target_date: date | None = Query(default=None, alias="date"),
) -> StudentDayResponse:
    """Get the schedule for a specific day (defaults to today)."""
    result = await service.get_day_schedule(db, school.id, user, target_date)
    return StudentDayResponse(**result)
