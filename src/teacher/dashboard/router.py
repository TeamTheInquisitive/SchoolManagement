from __future__ import annotations

from fastapi import APIRouter

from src.auth.dependencies import SchoolDep, TeacherUser
from src.core.dependencies import SessionDep
from src.teacher.dashboard import service
from src.teacher.dashboard.schemas import (
    AdhocClassesDashboardResponse,
    ClassesSummaryResponse,
    LeaveUpdatesResponse,
    MenteesSummaryResponse,
    PendingReviewsResponse,
    TeacherDashboardStatsResponse,
    TodayScheduleResponse,
    UpcomingExamsResponse,
)

router = APIRouter(prefix="/teacher/dashboard", tags=["Teacher Dashboard"])


@router.get("/stats/", response_model=TeacherDashboardStatsResponse)
async def get_dashboard_stats(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> TeacherDashboardStatsResponse:
    """Get KPI stats for teacher dashboard."""
    result = await service.get_dashboard_stats(db, school.id, user)
    return TeacherDashboardStatsResponse(**result)


@router.get("/today-schedule/", response_model=TodayScheduleResponse)
async def get_today_schedule(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> TodayScheduleResponse:
    """Get today's classes."""
    result = await service.get_today_schedule(db, school.id, user)
    return TodayScheduleResponse(**result)


@router.get("/pending-reviews/", response_model=PendingReviewsResponse)
async def get_pending_reviews(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> PendingReviewsResponse:
    """Get assignments needing review."""
    result = await service.get_pending_reviews(db, school.id, user)
    return PendingReviewsResponse(**result)


@router.get("/upcoming-exams/", response_model=UpcomingExamsResponse)
async def get_upcoming_exams(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> UpcomingExamsResponse:
    """Get upcoming exams."""
    result = await service.get_upcoming_exams(db, school.id, user)
    return UpcomingExamsResponse(**result)


@router.get("/classes-summary/", response_model=ClassesSummaryResponse)
async def get_classes_summary(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> ClassesSummaryResponse:
    """Get classes with progress."""
    result = await service.get_classes_summary(db, school.id, user)
    return ClassesSummaryResponse(**result)


@router.get("/leave-updates/", response_model=LeaveUpdatesResponse)
async def get_leave_updates(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> LeaveUpdatesResponse:
    """Get recent leave status."""
    result = await service.get_leave_updates(db, school.id, user)
    return LeaveUpdatesResponse(**result)


@router.get("/mentees-summary/", response_model=MenteesSummaryResponse)
async def get_mentees_summary(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> MenteesSummaryResponse:
    """Get mentees list."""
    result = await service.get_mentees_summary(db, school.id, user)
    return MenteesSummaryResponse(**result)


@router.get("/adhoc-classes/", response_model=AdhocClassesDashboardResponse)
async def get_adhoc_classes(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> AdhocClassesDashboardResponse:
    """Get adhoc classes summary."""
    result = await service.get_adhoc_classes_dashboard(db, school.id, user)
    return AdhocClassesDashboardResponse(**result)


@router.get("/profile/")
async def get_teacher_profile(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> dict:
    """Get teacher's profile info."""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from src.models.staff import Staff, StaffSubject
    staff = None
    if user.staff_id:
        result = await db.execute(
            select(Staff).options(selectinload(Staff.subjects)).where(Staff.id == user.staff_id, Staff.is_active.is_(True))
        )
        staff = result.scalar_one_or_none()
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "employee_id": staff.employee_id if staff else None,
        "department": staff.department if staff else None,
        "designation": staff.designation if staff else None,
        "qualification": staff.qualification if staff else None,
        "joining_date": staff.joining_date if staff else None,
        "subject": next(
            (ss.subject.name for ss in staff.subjects if ss.is_primary and ss.subject),
            staff.subjects[0].subject.name if staff.subjects and staff.subjects[0].subject else None,
        ) if staff else None,
    }
