from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Query

from src.auth.dependencies import AdminUser, SchoolDep
from src.core.dependencies import SessionDep
from src.admin.attendance import service
from src.teacher.attendance.schemas import (
    SubmitAttendanceRequest,
    SubmitAttendanceResponse,
    UpdateAttendanceRequest,
    UpdateAttendanceResponse,
)

router = APIRouter(prefix="/admin/attendance", tags=["Admin Attendance"])


@router.get("")
async def get_attendance(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    class_section_id: uuid.UUID = Query(...),
    date: date = Query(...),
    subject_id: uuid.UUID | None = Query(default=None),
    period: int | None = Query(default=None),
):
    """Get attendance for a class + date (admin has access to all classes).
    Optionally filter by subject_id and period for subject-wise mode."""
    return await service.get_attendance(db, school.id, user, class_section_id, date, subject_id, period)


@router.get("/class-subjects-status")
async def get_class_subjects_status(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    class_section_id: uuid.UUID = Query(...),
    date: date = Query(...),
):
    """Get all subjects for a class with their attendance status for the day.
    Used in subject-wise attendance mode to show subject grid."""
    return await service.get_class_subjects_status(db, school.id, class_section_id, date)


@router.post("", response_model=SubmitAttendanceResponse, status_code=201)
async def submit_attendance(
    data: SubmitAttendanceRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> SubmitAttendanceResponse:
    """Submit attendance for any class (admin)."""
    result = await service.submit_attendance(db, school.id, user, data)
    return SubmitAttendanceResponse(**result)


@router.put("", response_model=UpdateAttendanceResponse)
async def update_attendance(
    data: UpdateAttendanceRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> UpdateAttendanceResponse:
    """Update attendance for any class (admin)."""
    result = await service.update_attendance(db, school.id, user, data)
    return UpdateAttendanceResponse(**result)
