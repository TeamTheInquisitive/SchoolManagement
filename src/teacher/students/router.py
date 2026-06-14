from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query

from src.auth.dependencies import SchoolDep, TeacherUser
from src.core.dependencies import PaginationDep, SessionDep
from src.teacher.students import service
from src.teacher.students.schemas import (
    TeacherMenteesResponse,
    TeacherStudentActivitiesResponse,
    TeacherStudentAssignmentsResponse,
    TeacherStudentAttendanceResponse,
    TeacherStudentBehaviorResponse,
    TeacherStudentDetailResponse,
    TeacherStudentExamResultsResponse,
    TeacherStudentFeeSummaryResponse,
    TeacherStudentListResponse,
    TeacherStudentMeetingsResponse,
)

router = APIRouter(prefix="/teacher/students", tags=["Teacher Students"])


# ---------------------------------------------------------------------------
# List & Detail
# ---------------------------------------------------------------------------


@router.get("", response_model=TeacherStudentListResponse)
async def list_students(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    pagination: PaginationDep,
    search: str | None = Query(default=None),
    class_name: str | None = Query(default=None),
    section: str | None = Query(default=None),
) -> TeacherStudentListResponse:
    """List students (only mentor's mentees + class teacher's students)."""
    result = await service.list_students(db, school.id, user, pagination, search, class_name, section)
    return TeacherStudentListResponse(**result)


@router.get("/mentees", response_model=TeacherMenteesResponse)
async def get_mentees(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> TeacherMenteesResponse:
    """Get teacher's mentee students with details."""
    result = await service.get_mentees(db, school.id, user)
    return TeacherMenteesResponse(**result)


@router.get("/{student_id}", response_model=TeacherStudentDetailResponse)
async def get_student_detail(
    student_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> TeacherStudentDetailResponse:
    """Get full student profile (403 if not mentor/class teacher)."""
    result = await service.get_student_detail(db, school.id, student_id, user)
    return TeacherStudentDetailResponse(**result)


# ---------------------------------------------------------------------------
# Sub-resource endpoints
# ---------------------------------------------------------------------------


@router.get("/{student_id}/exam-results", response_model=TeacherStudentExamResultsResponse)
async def get_exam_results(
    student_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    academic_year: str | None = Query(default=None),
) -> TeacherStudentExamResultsResponse:
    """Get exam results + performance analysis."""
    result = await service.get_exam_results(db, school.id, student_id, user, academic_year)
    return TeacherStudentExamResultsResponse(**result)


@router.get("/{student_id}/parent-meetings", response_model=TeacherStudentMeetingsResponse)
async def get_parent_meetings(
    student_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> TeacherStudentMeetingsResponse:
    """Get parent meeting history."""
    result = await service.get_parent_meetings(db, school.id, student_id, user)
    return TeacherStudentMeetingsResponse(**result)


@router.get("/{student_id}/activities", response_model=TeacherStudentActivitiesResponse)
async def get_activities(
    student_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> TeacherStudentActivitiesResponse:
    """Get activities + awards."""
    result = await service.get_activities(db, school.id, student_id, user)
    return TeacherStudentActivitiesResponse(**result)


@router.get("/{student_id}/fee-summary", response_model=TeacherStudentFeeSummaryResponse)
async def get_fee_summary(
    student_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    academic_year: str | None = Query(default=None),
) -> TeacherStudentFeeSummaryResponse:
    """Get fee overview (read-only)."""
    result = await service.get_fee_summary(db, school.id, student_id, user, academic_year)
    return TeacherStudentFeeSummaryResponse(**result)


@router.get("/{student_id}/behavior", response_model=TeacherStudentBehaviorResponse)
async def get_behavior(
    student_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> TeacherStudentBehaviorResponse:
    """Get behavior + conduct notes."""
    result = await service.get_behavior(db, school.id, student_id, user)
    return TeacherStudentBehaviorResponse(**result)


@router.get("/{student_id}/recent-attendance", response_model=TeacherStudentAttendanceResponse)
async def get_recent_attendance(
    student_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    limit: int = Query(default=10),
) -> TeacherStudentAttendanceResponse:
    """Get recent attendance records."""
    result = await service.get_recent_attendance(db, school.id, student_id, user, limit)
    return TeacherStudentAttendanceResponse(**result)


@router.get("/{student_id}/assignments", response_model=TeacherStudentAssignmentsResponse)
async def get_assignments(
    student_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    academic_year: str | None = Query(default=None),
) -> TeacherStudentAssignmentsResponse:
    """Get assignment submissions."""
    result = await service.get_assignments(db, school.id, student_id, user, academic_year)
    return TeacherStudentAssignmentsResponse(**result)


@router.put("/{student_id}")
async def update_student_by_mentor(
    student_id: UUID,
    data: dict,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
):
    """Update a mentee student's details (mentor access)."""
    return await service.update_student_by_mentor(db, school.id, user, student_id, data)


# ─── CRUD for student sub-resources (meetings, activities, awards, disciplinary) ───

@router.post("/{student_id}/parent-meetings")
async def create_meeting(student_id: UUID, data: dict, db: SessionDep, school: SchoolDep, user: TeacherUser):
    from src.admin.students.service import create_parent_meeting
    return await create_parent_meeting(db, school.id, student_id, data, user.id)

@router.put("/{student_id}/parent-meetings/{meeting_id}")
async def update_meeting(student_id: UUID, meeting_id: UUID, data: dict, db: SessionDep, school: SchoolDep, user: TeacherUser):
    from src.admin.students.service import update_parent_meeting
    return await update_parent_meeting(db, school.id, student_id, meeting_id, data)

@router.delete("/{student_id}/parent-meetings/{meeting_id}")
async def delete_meeting(student_id: UUID, meeting_id: UUID, db: SessionDep, school: SchoolDep, user: TeacherUser):
    from src.admin.students.service import delete_parent_meeting
    return await delete_parent_meeting(db, school.id, student_id, meeting_id)

@router.post("/{student_id}/activities")
async def create_activity(student_id: UUID, data: dict, db: SessionDep, school: SchoolDep, user: TeacherUser):
    from src.admin.students.service import create_activity
    if "activity_name" in data:
        data["name"] = data.pop("activity_name")
    if "date" in data:
        data["start_date"] = data.pop("date")
    return await create_activity(db, school.id, student_id, data, user.id)

@router.put("/{student_id}/activities/{activity_id}")
async def update_activity(student_id: UUID, activity_id: UUID, data: dict, db: SessionDep, school: SchoolDep, user: TeacherUser):
    from src.admin.students.service import update_activity
    if "activity_name" in data:
        data["name"] = data.pop("activity_name")
    if "date" in data:
        data["start_date"] = data.pop("date")
    return await update_activity(db, school.id, student_id, activity_id, data)

@router.delete("/{student_id}/activities/{activity_id}")
async def delete_activity(student_id: UUID, activity_id: UUID, db: SessionDep, school: SchoolDep, user: TeacherUser):
    from src.admin.students.service import delete_activity
    return await delete_activity(db, school.id, student_id, activity_id)

@router.post("/{student_id}/awards")
async def create_award(student_id: UUID, data: dict, db: SessionDep, school: SchoolDep, user: TeacherUser):
    from src.admin.students.service import create_award
    if "award_date" in data:
        data["awarded_date"] = data.pop("award_date")
    return await create_award(db, school.id, student_id, data, user.id)

@router.put("/{student_id}/awards/{award_id}")
async def update_award(student_id: UUID, award_id: UUID, data: dict, db: SessionDep, school: SchoolDep, user: TeacherUser):
    from src.admin.students.service import update_award
    if "award_date" in data:
        data["awarded_date"] = data.pop("award_date")
    return await update_award(db, school.id, student_id, award_id, data)

@router.delete("/{student_id}/awards/{award_id}")
async def delete_award(student_id: UUID, award_id: UUID, db: SessionDep, school: SchoolDep, user: TeacherUser):
    from src.admin.students.service import delete_award
    return await delete_award(db, school.id, student_id, award_id)

@router.post("/{student_id}/disciplinary-records")
async def create_disciplinary(student_id: UUID, data: dict, db: SessionDep, school: SchoolDep, user: TeacherUser):
    from src.admin.students.service import create_disciplinary_record
    return await create_disciplinary_record(db, school.id, student_id, data, user.id)

@router.put("/{student_id}/disciplinary-records/{record_id}")
async def update_disciplinary(student_id: UUID, record_id: UUID, data: dict, db: SessionDep, school: SchoolDep, user: TeacherUser):
    from src.admin.students.service import update_disciplinary_record
    return await update_disciplinary_record(db, school.id, student_id, record_id, data)

@router.delete("/{student_id}/disciplinary-records/{record_id}")
async def delete_disciplinary(student_id: UUID, record_id: UUID, db: SessionDep, school: SchoolDep, user: TeacherUser):
    from src.admin.students.service import delete_disciplinary_record
    return await delete_disciplinary_record(db, school.id, student_id, record_id)


@router.get("/{student_id}/mentor-notes")
async def get_mentor_notes(student_id: UUID, db: SessionDep, school: SchoolDep, user: TeacherUser):
    """Get mentor notes for a student."""
    return await service.get_mentor_notes(db, school.id, user, student_id)


@router.put("/{student_id}/mentor-notes")
async def update_mentor_notes(student_id: UUID, data: dict, db: SessionDep, school: SchoolDep, user: TeacherUser):
    """Update mentor notes for a student."""
    return await service.update_mentor_notes(db, school.id, user, student_id, data.get("notes", ""))
