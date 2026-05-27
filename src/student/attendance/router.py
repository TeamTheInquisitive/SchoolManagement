from __future__ import annotations

from fastapi import APIRouter, Query

from src.auth.dependencies import SchoolDep, StudentUser
from src.core.dependencies import PaginationDep, SessionDep
from src.student.attendance import service
from src.student.attendance.schemas import (
    StudentAttendanceHistoryResponse,
    StudentAttendanceOverviewResponse,
    StudentAttendanceWarningsResponse,
)

router = APIRouter(prefix="/student/attendance", tags=["Student Attendance"])


@router.get("/", response_model=StudentAttendanceOverviewResponse)
async def get_attendance_overview(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
    academic_year: str | None = Query(default=None),
    month: str | None = Query(default=None, description="Filter by month (YYYY-MM)"),
) -> StudentAttendanceOverviewResponse:
    """Get overall attendance summary with stats, distribution, subject-wise, and warning."""
    result = await service.get_attendance_overview(
        db, school.id, user, academic_year, month
    )
    return StudentAttendanceOverviewResponse(**result)


@router.get("/history/", response_model=StudentAttendanceHistoryResponse)
async def get_attendance_history(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
    pagination: PaginationDep,
    subject: str | None = Query(default=None),
    month: str | None = Query(default=None, description="Filter by month (YYYY-MM)"),
    status: str | None = Query(default=None),
) -> StudentAttendanceHistoryResponse:
    """Get detailed attendance history (paginated, filterable)."""
    result = await service.get_attendance_history(
        db, school.id, user, pagination, subject, month, status
    )
    return StudentAttendanceHistoryResponse(**result)


@router.get("/warnings/", response_model=StudentAttendanceWarningsResponse)
async def get_attendance_warnings(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
    academic_year: str | None = Query(default=None),
) -> StudentAttendanceWarningsResponse:
    """Get attendance warnings and compliance status."""
    result = await service.get_attendance_warnings(
        db, school.id, user, academic_year
    )
    return StudentAttendanceWarningsResponse(**result)


@router.get("/summary/", response_model=StudentAttendanceOverviewResponse)
async def get_attendance_summary(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
    academic_year: str | None = Query(default=None),
) -> StudentAttendanceOverviewResponse:
    """Alias for attendance overview (summary)."""
    result = await service.get_attendance_overview(db, school.id, user, academic_year, None)
    return StudentAttendanceOverviewResponse(**result)


@router.get("/monthly/", response_model=StudentAttendanceOverviewResponse)
async def get_attendance_monthly(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
    month: str | None = Query(default=None),
) -> StudentAttendanceOverviewResponse:
    """Get attendance for a specific month."""
    result = await service.get_attendance_overview(db, school.id, user, None, month)
    return StudentAttendanceOverviewResponse(**result)
