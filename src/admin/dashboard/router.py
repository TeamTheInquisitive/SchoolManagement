from __future__ import annotations

from fastapi import APIRouter, Query

from src.auth.dependencies import AdminUser, SchoolDep
from src.core.dependencies import SessionDep
from src.admin.dashboard import service
from src.admin.dashboard.schemas import (
    AttendanceTrendsResponse,
    DashboardStatsResponse,
    FeeCollectionStatusResponse,
    LeaveOverviewResponse,
    LowAttendanceResponse,
    RecentActivitiesResponse,
    StudentDistributionResponse,
)

router = APIRouter(prefix="/admin/dashboard", tags=["Admin Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> DashboardStatsResponse:
    """Get KPI summary cards for the admin dashboard."""
    result = await service.get_dashboard_stats(db, school.id)
    return DashboardStatsResponse(**result)


@router.get("/attendance-trends", response_model=AttendanceTrendsResponse)
async def get_attendance_trends(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    year: int | None = Query(default=None),
) -> AttendanceTrendsResponse:
    """Get monthly attendance line chart data."""
    result = await service.get_attendance_trends(db, school.id, year)
    return AttendanceTrendsResponse(**result)


@router.get("/fee-collection-status", response_model=FeeCollectionStatusResponse)
async def get_fee_collection_status(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> FeeCollectionStatusResponse:
    """Get fee pie chart data."""
    result = await service.get_fee_collection_status(db, school.id)
    return FeeCollectionStatusResponse(**result)


@router.get("/student-distribution", response_model=StudentDistributionResponse)
async def get_student_distribution(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> StudentDistributionResponse:
    """Get class/gender bar chart data."""
    result = await service.get_student_distribution(db, school.id)
    return StudentDistributionResponse(**result)


@router.get("/recent-activities", response_model=RecentActivitiesResponse)
async def get_recent_activities(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    limit: int = Query(default=10, le=50),
) -> RecentActivitiesResponse:
    """Get recent activity feed."""
    result = await service.get_recent_activities(db, school.id, limit)
    return RecentActivitiesResponse(**result)


@router.get("/leave-overview", response_model=LeaveOverviewResponse)
async def get_leave_overview(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> LeaveOverviewResponse:
    """Get teacher leave summary + pending approvals."""
    result = await service.get_leave_overview(db, school.id)
    return LeaveOverviewResponse(**result)


@router.get("/low-attendance", response_model=LowAttendanceResponse)
async def get_low_attendance(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    threshold: int = Query(default=75),
    limit: int = Query(default=10, le=50),
) -> LowAttendanceResponse:
    """Get students below attendance threshold."""
    result = await service.get_low_attendance(db, school.id, threshold, limit)
    return LowAttendanceResponse(**result)
