from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Query

from src.admin.timetable import service
from src.admin.timetable.schemas import (
    ConflictsResponse,
    CreatePeriodRequest,
    CreateSlotRequest,
    PeriodDeleteResponse,
    PeriodListResponse,
    PeriodResponse,
    SlotDeleteResponse,
    SlotResponse,
    TeacherTimetableResponse,
    TimetableGridResponse,
    UpdatePeriodRequest,
    UpdateSlotRequest,
)
from src.auth.dependencies import AdminUser, SchoolDep
from src.core.dependencies import SessionDep

router = APIRouter(prefix="/admin/timetable", tags=["Admin Timetable"])


# ---------------------------------------------------------------------------
# Period Configuration Endpoints
# ---------------------------------------------------------------------------


@router.get("/periods", response_model=PeriodListResponse)
async def list_periods(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    academic_year: str | None = Query(default=None),
) -> PeriodListResponse:
    """Get period configuration (time slots)."""
    result = await service.list_periods(db, school.id, academic_year)
    return PeriodListResponse(**result)


@router.post("/periods", response_model=PeriodResponse, status_code=201)
async def create_period(
    data: CreatePeriodRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    academic_year: str | None = Query(default=None),
) -> PeriodResponse:
    """Add a new period to the configuration."""
    period = await service.create_period(
        db, school.id, data.model_dump(exclude_none=True), user.id, academic_year
    )
    return PeriodResponse.model_validate(period)


@router.put("/periods/{period_id}", response_model=PeriodResponse)
async def update_period(
    period_id: UUID,
    data: UpdatePeriodRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> PeriodResponse:
    """Update an existing period's timing."""
    period = await service.update_period(
        db, school.id, period_id, data.model_dump(exclude_none=True), user.id
    )
    return PeriodResponse.model_validate(period)


@router.delete("/periods/{period_id}", response_model=PeriodDeleteResponse)
async def delete_period(
    period_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> PeriodDeleteResponse:
    """Delete a period."""
    await service.delete_period(db, school.id, period_id, user.id)
    return PeriodDeleteResponse(
        id=period_id,
        status="Deleted",
        deactivated_on=str(date.today()),
        message="Period deleted successfully.",
    )


# ---------------------------------------------------------------------------
# Timetable Grid Endpoints
# ---------------------------------------------------------------------------


@router.get("", response_model=TimetableGridResponse)
async def get_timetable(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    class_section_id: UUID = Query(...),
    academic_year: str | None = Query(default=None),
) -> TimetableGridResponse:
    """Get the full timetable grid for a class/section."""
    result = await service.get_timetable_grid(db, school.id, class_section_id, academic_year)
    return TimetableGridResponse(**result)


# ---------------------------------------------------------------------------
# Slot Assignment Endpoints
# ---------------------------------------------------------------------------


@router.post("/slot", response_model=SlotResponse, status_code=201)
async def create_slot(
    data: CreateSlotRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    academic_year: str | None = Query(default=None),
) -> SlotResponse:
    """Assign a subject + teacher to a specific slot."""
    result = await service.create_slot(
        db, school.id, data.model_dump(), user.id, academic_year
    )
    return SlotResponse(**result)


@router.put("/slot/{slot_id}", response_model=SlotResponse)
async def update_slot(
    slot_id: UUID,
    data: UpdateSlotRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> SlotResponse:
    """Update an existing timetable slot."""
    result = await service.update_slot(
        db, school.id, slot_id, data.model_dump(exclude_none=True), user.id
    )
    return SlotResponse(**result)


@router.delete("/slot/{slot_id}", response_model=SlotDeleteResponse)
async def delete_slot(
    slot_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> SlotDeleteResponse:
    """Delete a slot assignment."""
    await service.delete_slot(db, school.id, slot_id, user.id)
    return SlotDeleteResponse(
        id=slot_id,
        day="",
        status="Deleted",
        removed_on=str(date.today()),
        message="Slot deleted successfully.",
    )


@router.delete("/slots/class-section/{class_section_id}")
async def reset_class_section_slots(
    class_section_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Delete all timetable slots for a class-section (hard delete)."""
    deleted = await service.reset_class_section_slots(db, school.id, class_section_id)
    return {"deleted": deleted, "message": f"All {deleted} slot(s) deleted successfully."}


# ---------------------------------------------------------------------------
# Teacher Timetable Endpoint
# ---------------------------------------------------------------------------


@router.get("/teacher/{teacher_id}", response_model=TeacherTimetableResponse)
async def get_teacher_timetable(
    teacher_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    academic_year: str | None = Query(default=None),
) -> TeacherTimetableResponse:
    """Get a teacher's weekly timetable."""
    result = await service.get_teacher_timetable(db, school.id, teacher_id, academic_year)
    return TeacherTimetableResponse(**result)


# ---------------------------------------------------------------------------
# Conflicts Endpoint
# ---------------------------------------------------------------------------


@router.get("/teacher-availability")
async def get_teacher_availability(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    period_config_id: UUID = Query(...),
    day: str = Query(...),
) -> dict:
    """Get teacher availability for a specific period+day. Returns which teachers are busy and where."""
    return await service.get_teacher_availability(db, school.id, period_config_id, day)


@router.get("/conflicts", response_model=ConflictsResponse)
async def detect_conflicts(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    academic_year: str | None = Query(default=None),
    class_section_id: UUID | None = Query(default=None),
) -> ConflictsResponse:
    """Detect scheduling conflicts across all timetables."""
    result = await service.detect_conflicts(db, school.id, academic_year, class_section_id)
    return ConflictsResponse(**result)
