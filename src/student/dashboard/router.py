from __future__ import annotations

from fastapi import APIRouter, Query

from src.auth.dependencies import SchoolDep, StudentUser
from src.core.dependencies import SessionDep
from src.student.dashboard import service
from src.student.dashboard.schemas import (
    AnnouncementsResponse,
    FeeStatusResponse,
    NotificationsResponse,
    ParentMeetingsResponse,
    RecentResultsResponse,
    StudentDashboardStatsResponse,
    StudentPendingAssignmentsResponse,
    StudentTodayScheduleResponse,
    StudentUpcomingExamsResponse,
    SubjectAttendanceResponse,
)

router = APIRouter(prefix="/student/dashboard", tags=["Student Dashboard"])


@router.get("/stats", response_model=StudentDashboardStatsResponse)
async def get_dashboard_stats(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
) -> StudentDashboardStatsResponse:
    """Get KPI stats for student dashboard."""
    result = await service.get_dashboard_stats(db, school.id, user)
    return StudentDashboardStatsResponse(**result)


@router.get("/today-schedule", response_model=StudentTodayScheduleResponse)
async def get_today_schedule(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
    date: str | None = Query(default=None),
) -> StudentTodayScheduleResponse:
    """Get classes for a given date (defaults to today)."""
    result = await service.get_today_schedule(db, school.id, user, date)
    return StudentTodayScheduleResponse(**result)


@router.get("/pending-assignments", response_model=StudentPendingAssignmentsResponse)
async def get_pending_assignments(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
) -> StudentPendingAssignmentsResponse:
    """Get pending assignments."""
    result = await service.get_pending_assignments(db, school.id, user)
    return StudentPendingAssignmentsResponse(**result)


@router.get("/upcoming-exams", response_model=StudentUpcomingExamsResponse)
async def get_upcoming_exams(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
) -> StudentUpcomingExamsResponse:
    """Get upcoming exams."""
    result = await service.get_upcoming_exams(db, school.id, user)
    return StudentUpcomingExamsResponse(**result)


@router.get("/subject-attendance", response_model=SubjectAttendanceResponse)
async def get_subject_attendance(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
) -> SubjectAttendanceResponse:
    """Get per-subject attendance."""
    result = await service.get_subject_attendance(db, school.id, user)
    return SubjectAttendanceResponse(**result)


@router.get("/recent-results", response_model=RecentResultsResponse)
async def get_recent_results(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
) -> RecentResultsResponse:
    """Get recent exam results."""
    result = await service.get_recent_results(db, school.id, user)
    return RecentResultsResponse(**result)


@router.get("/announcements", response_model=AnnouncementsResponse)
async def get_announcements(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
) -> AnnouncementsResponse:
    """Get recent announcements."""
    result = await service.get_announcements(db, school.id, user)
    return AnnouncementsResponse(**result)


@router.get("/notifications", response_model=NotificationsResponse)
async def get_notifications(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
) -> NotificationsResponse:
    """Get recent notifications."""
    result = await service.get_notifications(db, school.id, user)
    return NotificationsResponse(**result)


@router.get("/fee-status", response_model=FeeStatusResponse)
async def get_fee_status(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
) -> FeeStatusResponse:
    """Get fee overview."""
    result = await service.get_fee_status(db, school.id, user)
    return FeeStatusResponse(**result)


@router.get("/parent-meetings", response_model=ParentMeetingsResponse)
async def get_parent_meetings(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
) -> ParentMeetingsResponse:
    """Get parent meetings."""
    result = await service.get_parent_meetings(db, school.id, user)
    return ParentMeetingsResponse(**result)
