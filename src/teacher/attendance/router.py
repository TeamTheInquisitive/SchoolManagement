from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Query

from src.auth.dependencies import SchoolDep, TeacherUser
from src.core.dependencies import PaginationDep, SessionDep
from src.teacher.attendance import service
from src.teacher.attendance.schemas import (
    AttendanceHistoryResponse,
    AttendanceSummaryResponse,
    CancelAttendanceResponse,
    GetAttendanceResponse,
    SubmitAttendanceRequest,
    SubmitAttendanceResponse,
    UpdateAttendanceRequest,
    UpdateAttendanceResponse,
)

router = APIRouter(prefix="/teacher/attendance", tags=["Teacher Attendance"])


@router.get("")
async def get_attendance(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    class_section_id: uuid.UUID = Query(...),
    date: date = Query(...),
):
    """Get attendance for a class + date (form data or already submitted)."""
    result = await service.get_attendance(db, school.id, user, class_section_id, date)
    return result


@router.post("", response_model=SubmitAttendanceResponse, status_code=201)
async def submit_attendance(
    data: SubmitAttendanceRequest,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> SubmitAttendanceResponse:
    """Submit attendance for a class on a specific date."""
    result = await service.submit_attendance(db, school.id, user, data)
    return SubmitAttendanceResponse(**result)


@router.put("", response_model=UpdateAttendanceResponse)
async def update_attendance(
    data: UpdateAttendanceRequest,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> UpdateAttendanceResponse:
    """Update attendance for a class on a specific date (corrections)."""
    result = await service.update_attendance(db, school.id, user, data)
    return UpdateAttendanceResponse(**result)


@router.get("/history")
async def get_attendance_history(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    pagination: PaginationDep,
    class_section_id: uuid.UUID | None = Query(default=None),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
):
    """Get past attendance submissions by this teacher."""
    return await service.get_attendance_history(
        db, school.id, user, pagination, class_section_id, from_date, to_date
    )


@router.delete("/{session_id}", response_model=CancelAttendanceResponse)
async def cancel_attendance(
    session_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> CancelAttendanceResponse:
    """Cancel an attendance session (soft cancel, not hard delete)."""
    result = await service.cancel_attendance(db, school.id, user, session_id)
    return CancelAttendanceResponse(**result)


@router.get("/summary", response_model=AttendanceSummaryResponse)
async def get_attendance_summary(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    class_section_id: uuid.UUID = Query(...),
    month: int = Query(..., ge=1, le=12),
    year: int = Query(...),
    academic_year: str | None = Query(default=None),
) -> AttendanceSummaryResponse:
    """Get attendance summary/statistics for a class over a period."""
    result = await service.get_attendance_summary(
        db, school.id, user, class_section_id, month, year, academic_year
    )
    return AttendanceSummaryResponse(**result)
