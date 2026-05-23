from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from src.admin.timetable import service
from src.admin.timetable.schemas import (
    BulkAssignRequest,
    BulkAssignResponse,
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


@router.get("/periods/", response_model=PeriodListResponse)
async def list_periods(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    academic_year: str | None = Query(default=None),
) -> PeriodListResponse:
    """Get period configuration (time slots)."""
    result = await service.list_periods(db, school.id, academic_year)
    return PeriodListResponse(**result)


@router.post("/periods/", response_model=PeriodResponse, status_code=201)
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


@router.put("/periods/{period_id}/", response_model=PeriodResponse)
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


@router.delete("/periods/{period_id}/", response_model=PeriodDeleteResponse)
async def delete_period(
    period_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> PeriodDeleteResponse:
    """Soft-delete a period."""
    period = await service.delete_period(db, school.id, period_id, user.id)
    return PeriodDeleteResponse(
        id=period.id,
        status="Inactive",
        deactivated_on=str(date.today()),
        message="Period removed. Existing timetable entries preserved.",
    )


# ---------------------------------------------------------------------------
# Timetable Grid Endpoints
# ---------------------------------------------------------------------------


@router.get("/", response_model=TimetableGridResponse)
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


@router.post("/slot/", response_model=SlotResponse, status_code=201)
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


@router.put("/slot/{slot_id}/", response_model=SlotResponse)
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


@router.delete("/slot/{slot_id}/", response_model=SlotDeleteResponse)
async def delete_slot(
    slot_id: UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> SlotDeleteResponse:
    """Remove a slot assignment (soft-delete)."""
    slot = await service.delete_slot(db, school.id, slot_id, user.id)
    return SlotDeleteResponse(
        id=slot.id,
        day=slot.day_of_week,
        status="Removed",
        removed_on=str(date.today()),
        message="Slot cleared. Historical record preserved.",
    )


# ---------------------------------------------------------------------------
# Bulk Assign Endpoint
# ---------------------------------------------------------------------------


@router.post("/bulk-assign/")
async def bulk_assign(
    data: BulkAssignRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    academic_year: str | None = Query(default=None),
) -> JSONResponse:
    """Bulk assign multiple slots. Returns 207 on partial success."""
    result = await service.bulk_assign_slots(
        db, school.id, data.model_dump(), user.id, academic_year
    )
    status_code = 207 if result["conflicts"] > 0 else 201
    return JSONResponse(status_code=status_code, content={
        "assigned": result["assigned"],
        "conflicts": result["conflicts"],
        "slots": [
            {
                "id": str(s["id"]) if s["id"] else None,
                "day": s["day"],
                "period_config_id": str(s["period_config_id"]),
                "subject": s["subject"],
                "teacher_name": s["teacher_name"],
                "teacher_id": str(s["teacher_id"]) if s["teacher_id"] else None,
                "slot_type": s["slot_type"],
                "status": s["status"],
                "conflict": s["conflict"],
            }
            for s in result["slots"]
        ],
    })


# ---------------------------------------------------------------------------
# Teacher Timetable Endpoint
# ---------------------------------------------------------------------------


@router.get("/teacher/{teacher_id}/", response_model=TeacherTimetableResponse)
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


@router.get("/conflicts/", response_model=ConflictsResponse)
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
