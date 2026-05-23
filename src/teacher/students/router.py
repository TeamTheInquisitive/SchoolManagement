from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query

from src.auth.dependencies import SchoolDep, TeacherUser
from src.core.dependencies import PaginationDep, SessionDep
from src.teacher.students import service
from src.teacher.students.schemas import (
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


@router.get("/", response_model=TeacherStudentListResponse)
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


@router.get("/{student_id}/", response_model=TeacherStudentDetailResponse)
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


@router.get("/{student_id}/exam-results/", response_model=TeacherStudentExamResultsResponse)
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


@router.get("/{student_id}/parent-meetings/", response_model=TeacherStudentMeetingsResponse)
async def get_parent_meetings(
    student_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> TeacherStudentMeetingsResponse:
    """Get parent meeting history."""
    result = await service.get_parent_meetings(db, school.id, student_id, user)
    return TeacherStudentMeetingsResponse(**result)


@router.get("/{student_id}/activities/", response_model=TeacherStudentActivitiesResponse)
async def get_activities(
    student_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> TeacherStudentActivitiesResponse:
    """Get activities + awards."""
    result = await service.get_activities(db, school.id, student_id, user)
    return TeacherStudentActivitiesResponse(**result)


@router.get("/{student_id}/fee-summary/", response_model=TeacherStudentFeeSummaryResponse)
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


@router.get("/{student_id}/behavior/", response_model=TeacherStudentBehaviorResponse)
async def get_behavior(
    student_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> TeacherStudentBehaviorResponse:
    """Get behavior + conduct notes."""
    result = await service.get_behavior(db, school.id, student_id, user)
    return TeacherStudentBehaviorResponse(**result)


@router.get("/{student_id}/recent-attendance/", response_model=TeacherStudentAttendanceResponse)
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


@router.get("/{student_id}/assignments/", response_model=TeacherStudentAssignmentsResponse)
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
