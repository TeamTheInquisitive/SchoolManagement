from typing import Optional

from datetime import datetime, time
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Period Config Schemas
# ---------------------------------------------------------------------------


class CreatePeriodRequest(BaseModel):
    start_time: time
    end_time: time
    name: str | None = None
    is_break: bool = False
    day_of_week: str | None = None


class UpdatePeriodRequest(BaseModel):
    start_time: time | None = None
    end_time: time | None = None
    name: str | None = None
    is_break: bool | None = None
    day_of_week: str | None = None


class PeriodResponse(BaseModel):
    id: UUID
    name: str | None = None
    start_time: time
    end_time: time
    duration_minutes: int | None = None
    is_break: bool = False
    day_of_week: str | None = None
    sort_order: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class PeriodListResponse(BaseModel):
    academic_year: str
    total_periods: int
    periods: list[PeriodResponse]
    breaks: list[PeriodResponse]
    working_days: list[str]


class PeriodDeleteResponse(BaseModel):
    id: UUID
    status: str = "Inactive"
    deactivated_on: str
    message: str = "Period removed. Existing timetable entries preserved."


# ---------------------------------------------------------------------------
# Timetable Slot Schemas
# ---------------------------------------------------------------------------


class CreateSlotRequest(BaseModel):
    class_section_id: UUID
    day: str
    period_config_id: UUID
    subject_id: UUID
    teacher_id: UUID
    slot_type: str = "Lecture"


class UpdateSlotRequest(BaseModel):
    subject_id: UUID | None = None
    teacher_id: UUID | None = None
    slot_type: str | None = None


class SlotResponse(BaseModel):
    id: UUID
    class_name: str | None = None
    section: str | None = None
    day: str
    period_start_time: str | None = None
    period_end_time: str | None = None
    subject: str | None = None
    subject_id: UUID | None = None
    teacher_name: str | None = None
    teacher_id: UUID | None = None
    slot_type: str = "Lecture"
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SlotDeleteResponse(BaseModel):
    id: UUID
    day: str
    status: str = "Removed"
    removed_on: str
    message: str = "Slot cleared. Historical record preserved."


# ---------------------------------------------------------------------------
# Bulk Assign Schemas
# ---------------------------------------------------------------------------


class BulkSlotItem(BaseModel):
    day: str
    period_config_id: UUID
    subject_id: UUID
    teacher_id: UUID
    slot_type: str = "Lecture"


class BulkAssignRequest(BaseModel):
    class_section_id: UUID
    slots: list[BulkSlotItem]


class BulkSlotResultItem(BaseModel):
    id: UUID | None = None
    day: str
    period_config_id: UUID
    subject: str | None = None
    teacher_name: str | None = None
    teacher_id: UUID | None = None
    slot_type: str = "Lecture"
    status: str = "Assigned"
    conflict: dict | None = None


class BulkAssignResponse(BaseModel):
    assigned: int
    conflicts: int
    slots: list[BulkSlotResultItem]


# ---------------------------------------------------------------------------
# Timetable Grid Schemas
# ---------------------------------------------------------------------------


class TimetableGridSlot(BaseModel):
    id: UUID
    subject: str | None = None
    teacher_name: str | None = None
    teacher_id: UUID | None = None
    slot_type: str | None = None
    start_time: str | None = None
    end_time: str | None = None


class TimetableGridStats(BaseModel):
    total_slots: int
    filled_slots: int
    empty_slots: int
    completion_percentage: float


class TimetableGridResponse(BaseModel):
    class_name: str
    section: str
    academic_year: str
    periods: list[PeriodResponse]
    working_days: list[str]
    timetable: dict[str, list[TimetableGridSlot | None]]
    stats: TimetableGridStats


# ---------------------------------------------------------------------------
# Teacher Timetable Schemas
# ---------------------------------------------------------------------------


class TeacherSlotItem(BaseModel):
    period_start_time: str
    period_end_time: str
    class_name: str
    section: str
    subject: str
    slot_type: str


class TeacherTimetableResponse(BaseModel):
    teacher_id: UUID
    teacher_name: str
    academic_year: str
    total_periods_per_week: int
    timetable: dict[str, list[TeacherSlotItem]]
    free_slots: dict[str, list[str]]


# ---------------------------------------------------------------------------
# Conflict Schemas
# ---------------------------------------------------------------------------


class ConflictAssignment(BaseModel):
    class_name: str
    section: str
    subject: str


class ConflictItem(BaseModel):
    type: str = "teacher_double_booked"
    teacher_id: UUID
    teacher_name: str
    day: str
    period_start_time: str
    assignments: list[ConflictAssignment]


class ConflictsResponse(BaseModel):
    total_conflicts: int
    conflicts: list[ConflictItem]
