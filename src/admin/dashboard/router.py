from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Query
from sqlalchemy import select

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
from src.models.core import School
from src.models.subscription import Subscription
from src.models.platform_settings import PlatformSettings

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
    """Get students below attendance threshold (only after min_days of attendance recorded)."""
    from src.models.core import Settings
    config_result = await db.execute(
        select(Settings.value).where(
            Settings.school_id == school.id,
            Settings.category == "attendance",
            Settings.key == "config",
            Settings.is_active.is_(True),
        )
    )
    config = config_result.scalar_one_or_none()
    min_days = config.get("min_days", 30) if isinstance(config, dict) else 30
    result = await service.get_low_attendance(db, school.id, threshold, limit, min_days)
    return LowAttendanceResponse(**result)


@router.get("/subscription-banner")
async def get_subscription_banner(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Get subscription/trial banner info for the admin module."""
    today = date.today()

    # Get school subscription status and trial dates
    school_result = await db.execute(select(School).where(School.id == school.id))
    school_obj = school_result.scalar_one()

    if school_obj.subscription_status == "trial":
        if school_obj.trial_end_date:
            days_left = (school_obj.trial_end_date - today).days
        else:
            days_left = None
        return {
            "show_banner": True,
            "type": "trial",
            "message": f"Your free trial ends in {days_left} day{'s' if days_left != 1 else ''}" if days_left is not None else "You are on a free trial",
            "days_left": days_left,
        }

    if school_obj.subscription_status == "active":
        # Get banner_days_before_expiry from platform settings
        banner_setting = await db.execute(
            select(PlatformSettings).where(PlatformSettings.key == "banner_days_before_expiry")
        )
        banner_days_row = banner_setting.scalar_one_or_none()
        banner_days = int(banner_days_row.value) if banner_days_row else 3

        sub_result = await db.execute(
            select(Subscription).where(
                Subscription.school_id == school.id, Subscription.is_active.is_(True)
            )
        )
        sub = sub_result.scalar_one_or_none()
        if sub:
            days_left = (sub.end_date - today).days
            if days_left <= banner_days:
                return {
                    "show_banner": True,
                    "type": "expiring",
                    "message": f"Your subscription expires in {days_left} day{'s' if days_left != 1 else ''}" if days_left > 0 else "Your subscription expires today",
                    "days_left": days_left,
                }
        return {"show_banner": False}

    if school_obj.subscription_status == "expired":
        return {
            "show_banner": True,
            "type": "expired",
            "message": "Your subscription has expired. Please contact support.",
            "days_left": 0,
        }

    return {"show_banner": False}
