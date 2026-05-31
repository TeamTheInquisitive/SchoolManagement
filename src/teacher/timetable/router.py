from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Query

from src.auth.dependencies import SchoolDep, TeacherUser
from src.core.dependencies import SessionDep
from src.teacher.timetable import service
from src.teacher.timetable.schemas import (
    TeacherTodayResponse,
    TeacherWeeklyTimetableResponse,
)

router = APIRouter(prefix="/teacher/timetable", tags=["Teacher Timetable"])


@router.get("", response_model=TeacherWeeklyTimetableResponse)
async def get_weekly_timetable(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    academic_year: str | None = Query(default=None),
    day: str | None = Query(default=None),
) -> TeacherWeeklyTimetableResponse:
    """Get the teacher's weekly timetable with KPI stats. Supports day filtering."""
    result = await service.get_weekly_timetable(db, school.id, user, academic_year, day)
    return TeacherWeeklyTimetableResponse(**result)


@router.get("/today", response_model=TeacherTodayResponse)
async def get_today_schedule(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    target_date: date | None = Query(default=None, alias="date"),
) -> TeacherTodayResponse:
    """Get today's schedule (or a specific date)."""
    result = await service.get_today_schedule(db, school.id, user, target_date)
    return TeacherTodayResponse(**result)
