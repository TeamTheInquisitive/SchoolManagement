from __future__ import annotations

from fastapi import APIRouter, Query

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


@router.get("/stats", response_model=TeacherDashboardStatsResponse)
async def get_dashboard_stats(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> TeacherDashboardStatsResponse:
    """Get KPI stats for teacher dashboard."""
    result = await service.get_dashboard_stats(db, school.id, user)
    return TeacherDashboardStatsResponse(**result)


@router.get("/today-schedule", response_model=TodayScheduleResponse)
async def get_today_schedule(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    date: str | None = Query(default=None),
) -> TodayScheduleResponse:
    """Get schedule for a specific date (defaults to today)."""
    result = await service.get_today_schedule(db, school.id, user, date)
    return TodayScheduleResponse(**result)


@router.get("/pending-reviews", response_model=PendingReviewsResponse)
async def get_pending_reviews(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> PendingReviewsResponse:
    """Get assignments needing review."""
    result = await service.get_pending_reviews(db, school.id, user)
    return PendingReviewsResponse(**result)


@router.get("/upcoming-exams", response_model=UpcomingExamsResponse)
async def get_upcoming_exams(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> UpcomingExamsResponse:
    """Get upcoming exams."""
    result = await service.get_upcoming_exams(db, school.id, user)
    return UpcomingExamsResponse(**result)


@router.get("/classes-summary", response_model=ClassesSummaryResponse)
async def get_classes_summary(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> ClassesSummaryResponse:
    """Get classes with progress."""
    result = await service.get_classes_summary(db, school.id, user)
    return ClassesSummaryResponse(**result)


@router.get("/leave-updates", response_model=LeaveUpdatesResponse)
async def get_leave_updates(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> LeaveUpdatesResponse:
    """Get recent leave status."""
    result = await service.get_leave_updates(db, school.id, user)
    return LeaveUpdatesResponse(**result)


@router.get("/mentees-summary", response_model=MenteesSummaryResponse)
async def get_mentees_summary(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> MenteesSummaryResponse:
    """Get mentees list."""
    result = await service.get_mentees_summary(db, school.id, user)
    return MenteesSummaryResponse(**result)


@router.get("/adhoc-classes", response_model=AdhocClassesDashboardResponse)
async def get_adhoc_classes(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> AdhocClassesDashboardResponse:
    """Get adhoc classes summary."""
    result = await service.get_adhoc_classes_dashboard(db, school.id, user)
    return AdhocClassesDashboardResponse(**result)


@router.get("/attendance-status")
async def get_attendance_status(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
):
    """Get attendance status for class teacher's classes (today)."""
    result = await service.get_class_teacher_attendance_status(db, school.id, user)
    return result


@router.get("/upcoming-meetings")
async def get_upcoming_meetings(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
):
    """Get upcoming parent-teacher meetings for the logged-in teacher."""
    result = await service.get_upcoming_meetings(db, school.id, user)
    return result


@router.get("/profile")
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
    subjects = [ss.subject.name for ss in (staff.subjects if staff else []) if ss.subject] if staff else []
    primary_subject = next((ss.subject.name for ss in (staff.subjects if staff else []) if ss.is_primary and ss.subject), subjects[0] if subjects else None)
    return {
        "id": user.id,
        "staff_id": staff.id if staff else None,
        "full_name": user.full_name or (staff.full_name if staff else ''),
        "email": user.email or (staff.email if staff else ''),
        "phone": user.phone or (staff.phone if staff else ''),
        "role": user.role,
        "employee_id": staff.employee_id if staff else None,
        "department": staff.department if staff else None,
        "designation": staff.designation if staff else None,
        "qualification": staff.qualification if staff else None,
        "joining_date": staff.joining_date if staff else None,
        "date_of_birth": staff.date_of_birth if staff else None,
        "gender": staff.gender if staff else None,
        "employment_type": staff.employment_type if staff else None,
        "address": staff.address_line1 if staff else None,
        "city": staff.city if staff else None,
        "state": staff.state if staff else None,
        "pincode": staff.pincode if staff else None,
        "emergency_contact_name": staff.emergency_contact_name if staff else None,
        "emergency_contact_phone": staff.emergency_contact_phone if staff else None,
        "emergency_contact_relationship": staff.emergency_contact_relationship if staff else None,
        "blood_group": staff.blood_group if staff else None,
        "primary_subject": primary_subject,
        "subjects": subjects,
        "max_workload_hours": staff.max_workload_hours if staff else None,
        "experience_years": float(staff.experience_years) if staff and staff.experience_years else None,
    }


@router.put("/profile")
async def update_teacher_profile(
    data: dict,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> dict:
    """Update teacher's own profile."""
    from sqlalchemy import select
    from src.models.staff import Staff
    if not user.staff_id:
        return {"error": "No staff record linked"}
    result = await db.execute(select(Staff).where(Staff.id == user.staff_id, Staff.is_active.is_(True)))
    staff = result.scalar_one_or_none()
    if not staff:
        return {"error": "Staff not found"}

    field_map = {
        "phone": "phone", "address": "address_line1", "city": "city", "state": "state",
        "pincode": "pincode", "emergency_contact_name": "emergency_contact_name",
        "emergency_contact_phone": "emergency_contact_phone",
        "emergency_contact_relationship": "emergency_contact_relationship",
        "blood_group": "blood_group", "date_of_birth": "date_of_birth",
        "gender": "gender", "qualification": "qualification",
    }
    for req_field, model_field in field_map.items():
        if req_field in data and data[req_field] is not None and data[req_field] != '':
            setattr(staff, model_field, data[req_field])

    # Also update user phone if changed
    if "phone" in data and data["phone"]:
        user.phone = data["phone"]

    await db.commit()
    return {"message": "Profile updated successfully"}


# ---------------------------------------------------------------------------
# All class-sections in the school (for student list dropdown)
# ---------------------------------------------------------------------------


@router.get("/all-classes")
async def get_all_classes(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
):
    """Get all class-sections in the school for dropdown."""
    from src.models.academic import Class, ClassSection, Section
    from src.models.core import AcademicYear
    from sqlalchemy import select as sa_select

    ay_result = await db.execute(
        sa_select(AcademicYear).where(
            AcademicYear.school_id == school.id,
            AcademicYear.is_current.is_(True),
        )
    )
    ay = ay_result.scalar_one_or_none()
    if not ay:
        return {"classes": []}

    cs_result = await db.execute(
        sa_select(ClassSection, Class.name.label("class_name"), Section.name.label("section_name"))
        .join(Class, ClassSection.class_id == Class.id)
        .join(Section, ClassSection.section_id == Section.id)
        .where(
            ClassSection.school_id == school.id,
            ClassSection.academic_year_id == ay.id,
            ClassSection.is_active.is_(True),
        )
        .order_by(Class.name, Section.name)
    )
    rows = cs_result.all()
    classes = [{"class_name": r.class_name, "section": r.section_name, "class_section": f"{r.class_name}-{r.section_name}"} for r in rows]
    return {"classes": classes}


# ---------------------------------------------------------------------------
# Awards (self-managed by teacher)
# ---------------------------------------------------------------------------


@router.get("/awards")
async def get_my_awards(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
):
    """Get authenticated teacher's awards."""
    from src.admin.teachers.service import get_teacher_awards
    return await get_teacher_awards(db, school.id, user.staff_id)


@router.post("/awards", status_code=201)
async def add_my_award(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    data: dict,
):
    """Add an award to own profile."""
    from src.admin.teachers.service import add_teacher_award
    return await add_teacher_award(db, school.id, user.staff_id, data)


@router.put("/awards/{award_id}")
async def update_my_award(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    award_id: str,
    data: dict,
):
    """Update an award on own profile."""
    from src.admin.teachers.service import update_teacher_award
    return await update_teacher_award(db, school.id, user.staff_id, award_id, data)


@router.delete("/awards/{award_id}", status_code=204)
async def delete_my_award(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    award_id: str,
):
    """Delete an award from own profile."""
    from src.admin.teachers.service import delete_teacher_award
    await delete_teacher_award(db, school.id, user.staff_id, award_id)
