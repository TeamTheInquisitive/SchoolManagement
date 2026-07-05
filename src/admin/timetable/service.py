from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import date, time

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.admin.timetable.exceptions import TeacherConflict, TimeOverlap
from src.core.exceptions import NotFound
from src.models.academic import ClassSection, Subject
from src.models.core import AcademicYear
from src.models.staff import Staff
from src.models.timetable import PeriodConfig, TimetableSlot

WORKING_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_current_academic_year(
    db: AsyncSession, school_id: uuid.UUID, academic_year_name: str | None = None
) -> AcademicYear:
    """Get the academic year by name or the current one."""
    if academic_year_name:
        result = await db.execute(
            select(AcademicYear).where(
                AcademicYear.school_id == school_id,
                AcademicYear.name == academic_year_name,
                AcademicYear.is_active.is_(True),
            )
        )
    else:
        result = await db.execute(
            select(AcademicYear).where(
                AcademicYear.school_id == school_id,
                AcademicYear.is_current.is_(True),
                AcademicYear.is_active.is_(True),
            )
        )
    ay = result.scalar_one_or_none()
    if not ay:
        raise NotFound("AcademicYear")
    return ay


async def _get_class_section(
    db: AsyncSession, school_id: uuid.UUID, class_section_id: uuid.UUID
) -> ClassSection:
    """Get a class section by ID."""
    result = await db.execute(
        select(ClassSection).where(
            ClassSection.id == class_section_id,
            ClassSection.school_id == school_id,
            ClassSection.is_active.is_(True),
        )
    )
    cs = result.scalar_one_or_none()
    if not cs:
        raise NotFound("ClassSection", str(class_section_id))
    return cs


async def _check_time_overlap(
    db: AsyncSession,
    school_id: uuid.UUID,
    academic_year_id: uuid.UUID,
    start_time: time,
    end_time: time,
    exclude_id: uuid.UUID | None = None,
) -> None:
    """Check for time overlaps with existing periods."""
    query = select(PeriodConfig).where(
        PeriodConfig.school_id == school_id,
        PeriodConfig.academic_year_id == academic_year_id,
        # Overlap condition: existing.start < new.end AND existing.end > new.start
        PeriodConfig.start_time < end_time,
        PeriodConfig.end_time > start_time,
    )
    if exclude_id:
        query = query.where(PeriodConfig.id != exclude_id)

    result = await db.execute(query)
    existing = result.scalars().first()
    if existing:
        name = existing.name or f"Period ({existing.start_time.strftime('%H:%M')})"
        raise TimeOverlap(
            name,
            existing.start_time.strftime("%H:%M"),
            existing.end_time.strftime("%H:%M"),
        )


async def get_teacher_availability(
    db: AsyncSession, school_id: uuid.UUID, period_config_id: uuid.UUID, day: str
) -> dict:
    """Return which teachers are busy at a given period+day and what they're teaching."""
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(TimetableSlot)
        .options(
            selectinload(TimetableSlot.staff),
            selectinload(TimetableSlot.subject),
            selectinload(TimetableSlot.class_section).selectinload(ClassSection.class_),
            selectinload(TimetableSlot.class_section).selectinload(ClassSection.section),
        )
        .where(
            TimetableSlot.school_id == school_id,
            TimetableSlot.period_config_id == period_config_id,
            TimetableSlot.day_of_week == day,
        )
    )
    slots = result.scalars().all()

    busy_teachers = {}
    for slot in slots:
        if slot.staff_id:
            staff_id = str(slot.staff_id)
            class_name = slot.class_section.class_.name if slot.class_section and slot.class_section.class_ else "?"
            section = slot.class_section.section.name if slot.class_section and slot.class_section.section else "?"
            subject_name = slot.subject.name if slot.subject else "?"
            busy_teachers[staff_id] = {
                "class": f"{class_name}-{section}",
                "subject": subject_name,
            }

    return {"busy_teachers": busy_teachers}


async def _check_teacher_conflict(
    db: AsyncSession,
    school_id: uuid.UUID,
    academic_year_id: uuid.UUID,
    staff_id: uuid.UUID,
    period_config_id: uuid.UUID,
    day_of_week: str,
    exclude_slot_id: uuid.UUID | None = None,
) -> None:
    """Check if a teacher already has an assignment at the same period+day."""
    query = select(TimetableSlot).where(
        TimetableSlot.school_id == school_id,
        TimetableSlot.academic_year_id == academic_year_id,
        TimetableSlot.staff_id == staff_id,
        TimetableSlot.period_config_id == period_config_id,
        TimetableSlot.day_of_week == day_of_week,
    )
    if exclude_slot_id:
        query = query.where(TimetableSlot.id != exclude_slot_id)

    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    if existing:
        # Fetch details for error message
        staff = existing.staff
        teacher_name = staff.full_name if staff else "Unknown"
        cs = existing.class_section
        class_name = cs.class_.name if cs and cs.class_ else "?"
        section = cs.section.name if cs and cs.section else "?"
        subject_name = existing.subject.name if existing.subject else "?"
        period = existing.period_config
        period_start = period.start_time.strftime("%H:%M") if period else "?"

        raise TeacherConflict(
            teacher_name=teacher_name,
            existing_class=f"{class_name}-{section}",
            existing_subject=subject_name,
            day=day_of_week,
            period_start_time=period_start,
        )


def _compute_duration(start: time, end: time) -> int:
    """Compute duration in minutes between two time values."""
    start_minutes = start.hour * 60 + start.minute
    end_minutes = end.hour * 60 + end.minute
    return end_minutes - start_minutes


# ---------------------------------------------------------------------------
# Period Config Service
# ---------------------------------------------------------------------------


async def list_periods(
    db: AsyncSession,
    school_id: uuid.UUID,
    academic_year_name: str | None = None,
) -> dict:
    """Get all period configs for the school/academic year."""
    ay = await _get_current_academic_year(db, school_id, academic_year_name)

    result = await db.execute(
        select(PeriodConfig).where(
            PeriodConfig.school_id == school_id,
            PeriodConfig.academic_year_id == ay.id,
            ).order_by(PeriodConfig.start_time)
    )
    all_periods = result.scalars().all()

    periods = [p for p in all_periods if not p.is_break]
    breaks = [p for p in all_periods if p.is_break]

    return {
        "academic_year": ay.name,
        "total_periods": len(periods),
        "periods": periods,
        "breaks": breaks,
        "working_days": WORKING_DAYS,
    }


async def create_period(
    db: AsyncSession,
    school_id: uuid.UUID,
    data: dict,
    academic_year_name: str | None = None,
) -> PeriodConfig:
    """Create a new period config."""
    # Validate required fields
    if not data.get("start_time"):
        raise HTTPException(status_code=400, detail="start_time must not be empty")
    if not data.get("end_time"):
        raise HTTPException(status_code=400, detail="end_time must not be empty")
    if data.get("end_time") <= data.get("start_time"):
        raise HTTPException(status_code=400, detail="end_time must be after start_time")
    if "name" in data and data["name"] is not None and not str(data["name"]).strip():
        raise HTTPException(status_code=400, detail="Period name must not be empty if provided")

    ay = await _get_current_academic_year(db, school_id, academic_year_name)

    start_time = data["start_time"]
    end_time = data["end_time"]

    # Check for time overlap
    await _check_time_overlap(db, school_id, ay.id, start_time, end_time)

    duration = _compute_duration(start_time, end_time)

    # Determine sort_order based on start_time
    result = await db.execute(
        select(PeriodConfig).where(
            PeriodConfig.school_id == school_id,
            PeriodConfig.academic_year_id == ay.id,
            ).order_by(PeriodConfig.start_time.desc())
    )
    last_period = result.scalars().first()
    sort_order = (last_period.sort_order + 1) if last_period else 0

    period = PeriodConfig(
        school_id=school_id,
        academic_year_id=ay.id,
        name=data.get("name"),
        start_time=start_time,
        end_time=end_time,
        duration_minutes=duration,
        is_break=data.get("is_break", False),
        sort_order=sort_order,
    )
    db.add(period)
    await db.commit()
    await db.refresh(period)
    return period


async def update_period(
    db: AsyncSession,
    school_id: uuid.UUID,
    period_id: uuid.UUID,
    data: dict,
) -> PeriodConfig:
    """Update an existing period config."""
    # Validate fields when provided
    if "name" in data and data["name"] is not None and not str(data["name"]).strip():
        raise HTTPException(status_code=400, detail="Period name must not be empty if provided")

    result = await db.execute(
        select(PeriodConfig).where(
            PeriodConfig.id == period_id,
            PeriodConfig.school_id == school_id,
            )
    )
    period = result.scalar_one_or_none()
    if not period:
        raise NotFound("PeriodConfig", str(period_id))

    start_time = data.get("start_time", period.start_time)
    end_time = data.get("end_time", period.end_time)

    # Validate end_time is after start_time when either is provided
    if end_time <= start_time:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    # Check for time overlap (excluding self)
    await _check_time_overlap(
        db, school_id, period.academic_year_id, start_time, end_time,
        exclude_id=period_id,
    )

    if "start_time" in data:
        period.start_time = data["start_time"]
    if "end_time" in data:
        period.end_time = data["end_time"]
    if "name" in data:
        period.name = data["name"]
    if "is_break" in data:
        period.is_break = data["is_break"]

    period.duration_minutes = _compute_duration(period.start_time, period.end_time)

    await db.commit()
    await db.refresh(period)
    return period


async def delete_period(
    db: AsyncSession,
    school_id: uuid.UUID,
    period_id: uuid.UUID,
    deleted_by: uuid.UUID,
) -> None:
    """Delete a period config."""
    result = await db.execute(
        select(PeriodConfig).where(
            PeriodConfig.id == period_id,
            PeriodConfig.school_id == school_id,
        )
    )
    period = result.scalar_one_or_none()
    if not period:
        raise NotFound("PeriodConfig", str(period_id))

    await db.delete(period)
    await db.commit()


# ---------------------------------------------------------------------------
# Timetable Grid Service
# ---------------------------------------------------------------------------


async def get_timetable_grid(
    db: AsyncSession,
    school_id: uuid.UUID,
    class_section_id: uuid.UUID,
    academic_year_name: str | None = None,
) -> dict:
    """Get the full timetable grid for a class/section."""
    ay = await _get_current_academic_year(db, school_id, academic_year_name)
    cs = await _get_class_section(db, school_id, class_section_id)

    # Get periods (respect class max_periods if set)
    periods_result = await db.execute(
        select(PeriodConfig).where(
            PeriodConfig.school_id == school_id,
            PeriodConfig.academic_year_id == ay.id,
                PeriodConfig.is_break.is_(False),
        ).order_by(PeriodConfig.start_time)
    )
    periods = list(periods_result.scalars().all())
    max_periods = cs.class_.max_periods if cs.class_ else None
    if max_periods:
        periods = periods[:max_periods]

    # Get slots for this class
    slots_result = await db.execute(
        select(TimetableSlot).where(
            TimetableSlot.school_id == school_id,
            TimetableSlot.academic_year_id == ay.id,
            TimetableSlot.class_section_id == class_section_id,
        )
    )
    slots = slots_result.scalars().all()

    # Build lookup: (day, period_config_id) -> slot
    slot_map: dict[tuple[str, uuid.UUID], TimetableSlot] = {}
    for slot in slots:
        slot_map[(slot.day_of_week, slot.period_config_id)] = slot

    # Build grid
    timetable: dict[str, list[dict | None]] = {}
    filled_count = 0
    total_count = 0

    for day in WORKING_DAYS:
        day_slots: list[dict | None] = []
        for period in periods:
            total_count += 1
            slot = slot_map.get((day, period.id))
            if slot:
                filled_count += 1
                day_slots.append({
                    "id": slot.id,
                    "subject": slot.subject.name if slot.subject else slot.slot_type,
                    "subject_id": slot.subject_id,
                    "teacher_name": slot.staff.full_name if slot.staff else None,
                    "teacher_id": slot.staff_id,
                    "slot_type": slot.slot_type,
                    "start_time": period.start_time.strftime("%H:%M"),
                    "end_time": period.end_time.strftime("%H:%M"),
                })
            else:
                day_slots.append(None)
        timetable[day] = day_slots

    class_name = cs.class_.name if cs.class_ else ""
    section = cs.section.name if cs.section else ""

    return {
        "class_name": class_name,
        "section": section,
        "academic_year": ay.name,
        "periods": periods,
        "working_days": WORKING_DAYS,
        "timetable": timetable,
        "stats": {
            "total_slots": total_count,
            "filled_slots": filled_count,
            "empty_slots": total_count - filled_count,
            "completion_percentage": round((filled_count / total_count * 100), 1) if total_count > 0 else 0,
        },
    }


# ---------------------------------------------------------------------------
# Slot Assignment Service
# ---------------------------------------------------------------------------


async def create_slot(
    db: AsyncSession,
    school_id: uuid.UUID,
    data: dict,
    academic_year_name: str | None = None,
) -> dict:
    """Assign a subject+teacher to a specific slot."""
    slot_type = data.get("slot_type", "Subject")
    is_subject_slot = slot_type == "Subject"

    # Validate required fields
    if is_subject_slot and not data.get("subject_id"):
        raise HTTPException(status_code=400, detail="subject_id must not be empty")
    if not data.get("teacher_id"):
        raise HTTPException(status_code=400, detail="teacher_id must not be empty")
    if not data.get("period_config_id"):
        raise HTTPException(status_code=400, detail="period_config_id must not be empty")
    if not data.get("day") or not str(data["day"]).strip():
        raise HTTPException(status_code=400, detail="day must not be empty")
    if data["day"] not in WORKING_DAYS:
        raise HTTPException(status_code=400, detail=f"day must be one of: {', '.join(WORKING_DAYS)}")

    ay = await _get_current_academic_year(db, school_id, academic_year_name)
    cs = await _get_class_section(db, school_id, data["class_section_id"])

    # Validate period
    period_result = await db.execute(
        select(PeriodConfig).where(
            PeriodConfig.id == data["period_config_id"],
            PeriodConfig.school_id == school_id,
            )
    )
    period = period_result.scalar_one_or_none()
    if not period:
        raise NotFound("PeriodConfig", str(data["period_config_id"]))

    day = data["day"]

    # Check if slot already exists at this position (upsert behavior)
    existing_result = await db.execute(
        select(TimetableSlot).where(
            TimetableSlot.school_id == school_id,
            TimetableSlot.academic_year_id == ay.id,
            TimetableSlot.class_section_id == cs.id,
            TimetableSlot.period_config_id == period.id,
            TimetableSlot.day_of_week == day,
        )
    )
    existing_slot = existing_result.scalar_one_or_none()
    if existing_slot:
        new_teacher_id = data.get("teacher_id")
        # Check teacher conflict only if teacher is changing
        if is_subject_slot and new_teacher_id and new_teacher_id != existing_slot.staff_id:
            await _check_teacher_conflict(
                db, school_id, ay.id, new_teacher_id, period.id, day,
                exclude_slot_id=existing_slot.id,
            )
        existing_slot.subject_id = data.get("subject_id") if is_subject_slot else None
        existing_slot.staff_id = new_teacher_id
        existing_slot.slot_type = slot_type
        await db.commit()
        await db.refresh(existing_slot)
        cs_ref = existing_slot.class_section
        return {
            "id": existing_slot.id,
            "class_name": cs_ref.class_.name if cs_ref and cs_ref.class_ else "",
            "section": cs_ref.section.name if cs_ref and cs_ref.section else "",
            "day": existing_slot.day_of_week,
            "period_start_time": period.start_time.strftime("%H:%M"),
            "period_end_time": period.end_time.strftime("%H:%M"),
            "subject": existing_slot.subject.name if existing_slot.subject else existing_slot.slot_type,
            "subject_id": existing_slot.subject_id,
            "teacher_name": existing_slot.staff.full_name if existing_slot.staff else None,
            "teacher_id": existing_slot.staff_id,
            "slot_type": existing_slot.slot_type,
        }

    # New slot: check teacher conflict only for Subject slots
    if is_subject_slot:
        await _check_teacher_conflict(
            db, school_id, ay.id, data["teacher_id"], period.id, day
        )

    # Get subject if applicable
    subject = None
    if is_subject_slot:
        subject_result = await db.execute(select(Subject).where(Subject.id == data["subject_id"]))
        subject = subject_result.scalar_one_or_none()
        if not subject:
            raise NotFound("Subject", str(data["subject_id"]))

    staff_result = await db.execute(select(Staff).where(Staff.id == data["teacher_id"]))
    staff = staff_result.scalar_one_or_none()
    if not staff:
        raise NotFound("Staff", str(data["teacher_id"]))

    slot = TimetableSlot(
        school_id=school_id,
        academic_year_id=ay.id,
        class_section_id=cs.id,
        period_config_id=period.id,
        day_of_week=day,
        subject_id=data.get("subject_id") if is_subject_slot else None,
        staff_id=data["teacher_id"],
        slot_type=slot_type,
    )
    db.add(slot)
    await db.commit()
    await db.refresh(slot)

    class_name = cs.class_.name if cs.class_ else ""
    section = cs.section.name if cs.section else ""

    return {
        "id": slot.id,
        "class_name": class_name,
        "section": section,
        "day": day,
        "period_start_time": period.start_time.strftime("%H:%M"),
        "period_end_time": period.end_time.strftime("%H:%M"),
        "subject": subject.name if subject else slot_type,
        "subject_id": subject.id if subject else None,
        "teacher_name": staff.full_name,
        "teacher_id": staff.id,
        "slot_type": slot.slot_type,
        "created_at": slot.created_at,
    }


async def update_slot(
    db: AsyncSession,
    school_id: uuid.UUID,
    slot_id: uuid.UUID,
    data: dict,
) -> dict:
    """Update an existing timetable slot."""
    # Validate fields when provided
    if "day" in data:
        if not data["day"] or not str(data["day"]).strip():
            raise HTTPException(status_code=400, detail="day must not be empty")
        if data["day"] not in WORKING_DAYS:
            raise HTTPException(status_code=400, detail=f"day must be one of: {', '.join(WORKING_DAYS)}")

    result = await db.execute(
        select(TimetableSlot).where(
            TimetableSlot.id == slot_id,
            TimetableSlot.school_id == school_id,
        )
    )
    slot = result.scalar_one_or_none()
    if not slot:
        raise NotFound("TimetableSlot", str(slot_id))

    new_slot_type = data.get("slot_type", slot.slot_type)
    is_subject_slot = new_slot_type == "Subject"
    new_teacher_id = data.get("teacher_id", slot.staff_id)
    new_day = data.get("day", slot.day_of_week)
    new_period_id = data.get("period_config_id", slot.period_config_id)

    # If day or period is changing, check for slot position conflict in same class-section
    if new_day != slot.day_of_week or new_period_id != slot.period_config_id:
        position_result = await db.execute(
            select(TimetableSlot).where(
                TimetableSlot.school_id == school_id,
                TimetableSlot.academic_year_id == slot.academic_year_id,
                TimetableSlot.class_section_id == slot.class_section_id,
                TimetableSlot.period_config_id == new_period_id,
                TimetableSlot.day_of_week == new_day,
                TimetableSlot.id != slot_id,
            )
        )
        if position_result.scalar_one_or_none():
            period = slot.period_config
            cs = slot.class_section
            class_name = cs.class_.name if cs and cs.class_ else "?"
            section = cs.section.name if cs and cs.section else "?"
            period_start = period.start_time.strftime("%H:%M") if period else "?"
            from src.admin.timetable.exceptions import SlotAlreadyOccupied
            raise SlotAlreadyOccupied(day=new_day, period_start_time=period_start, class_section=f"{class_name}-{section}")

    # If teacher is changing, check for teacher conflicts (only for Subject slots)
    if is_subject_slot and new_teacher_id and new_teacher_id != slot.staff_id:
        await _check_teacher_conflict(
            db, school_id, slot.academic_year_id, new_teacher_id,
            new_period_id, new_day, exclude_slot_id=slot_id,
        )

    if "subject_id" in data:
        if data["subject_id"]:
            subject_result = await db.execute(select(Subject).where(Subject.id == data["subject_id"]))
            if not subject_result.scalar_one_or_none():
                raise NotFound("Subject", str(data["subject_id"]))
            slot.subject_id = data["subject_id"]
        else:
            slot.subject_id = None

    if "teacher_id" in data:
        staff_result = await db.execute(select(Staff).where(Staff.id == data["teacher_id"]))
        if not staff_result.scalar_one_or_none():
            raise NotFound("Staff", str(data["teacher_id"]))
        slot.staff_id = data["teacher_id"]

    if "slot_type" in data:
        slot.slot_type = data["slot_type"]
        if data["slot_type"] != "Subject":
            slot.subject_id = None

    if "day" in data:
        slot.day_of_week = data["day"]
    if "period_config_id" in data:
        slot.period_config_id = data["period_config_id"]

    await db.commit()
    await db.refresh(slot)

    cs = slot.class_section
    class_name = cs.class_.name if cs and cs.class_ else ""
    section = cs.section.name if cs and cs.section else ""
    period = slot.period_config

    return {
        "id": slot.id,
        "class_name": class_name,
        "section": section,
        "day": slot.day_of_week,
        "period_start_time": period.start_time.strftime("%H:%M") if period else None,
        "period_end_time": period.end_time.strftime("%H:%M") if period else None,
        "subject": slot.subject.name if slot.subject else slot.slot_type,
        "subject_id": slot.subject_id,
        "teacher_name": slot.staff.full_name if slot.staff else None,
        "teacher_id": slot.staff_id,
        "slot_type": slot.slot_type,
        "updated_at": slot.updated_at,
    }


async def delete_slot(
    db: AsyncSession,
    school_id: uuid.UUID,
    slot_id: uuid.UUID,
    deleted_by: uuid.UUID,
) -> None:
    """Delete a timetable slot."""
    result = await db.execute(
        select(TimetableSlot).where(
            TimetableSlot.id == slot_id,
            TimetableSlot.school_id == school_id,
        )
    )
    slot = result.scalar_one_or_none()
    if not slot:
        raise NotFound("TimetableSlot", str(slot_id))

    await db.delete(slot)
    await db.commit()


async def reset_class_section_slots(
    db: AsyncSession,
    school_id: uuid.UUID,
    class_section_id: uuid.UUID,
) -> int:
    """Delete all timetable slots for a class-section (hard delete)."""
    result = await db.execute(
        select(TimetableSlot).where(
            TimetableSlot.school_id == school_id,
            TimetableSlot.class_section_id == class_section_id,
        )
    )
    slots = result.scalars().all()
    count = len(slots)
    for slot in slots:
        await db.delete(slot)
    await db.commit()
    return count


# ---------------------------------------------------------------------------
# Teacher Timetable Service
# ---------------------------------------------------------------------------


async def get_teacher_timetable(
    db: AsyncSession,
    school_id: uuid.UUID,
    teacher_id: uuid.UUID,
    academic_year_name: str | None = None,
) -> dict:
    """Get a teacher's weekly timetable across all classes."""
    ay = await _get_current_academic_year(db, school_id, academic_year_name)

    # Validate teacher exists
    staff_result = await db.execute(
        select(Staff).where(Staff.id == teacher_id, Staff.school_id == school_id)
    )
    staff = staff_result.scalar_one_or_none()
    if not staff:
        raise NotFound("Staff", str(teacher_id))

    # Get all periods for the academic year
    periods_result = await db.execute(
        select(PeriodConfig).where(
            PeriodConfig.school_id == school_id,
            PeriodConfig.academic_year_id == ay.id,
                PeriodConfig.is_break.is_(False),
        ).order_by(PeriodConfig.start_time)
    )
    all_periods = periods_result.scalars().all()

    # Get teacher's slots
    slots_result = await db.execute(
        select(TimetableSlot).where(
            TimetableSlot.school_id == school_id,
            TimetableSlot.academic_year_id == ay.id,
            TimetableSlot.staff_id == teacher_id,
        )
    )
    slots = slots_result.scalars().all()

    # Build timetable by day
    timetable: dict[str, list[dict]] = {day: [] for day in WORKING_DAYS}
    assigned_periods: dict[str, set[uuid.UUID]] = {day: set() for day in WORKING_DAYS}

    for slot in slots:
        period = slot.period_config
        cs = slot.class_section
        class_name = cs.class_.name if cs and cs.class_ else ""
        section = cs.section.name if cs and cs.section else ""
        subject_name = slot.subject.name if slot.subject else ""

        timetable[slot.day_of_week].append({
            "period_start_time": period.start_time.strftime("%H:%M") if period else "",
            "period_end_time": period.end_time.strftime("%H:%M") if period else "",
            "class_name": class_name,
            "section": section,
            "subject": subject_name,
            "slot_type": slot.slot_type,
        })
        if period:
            assigned_periods[slot.day_of_week].add(period.id)

    # Sort each day's slots by start_time
    for day in WORKING_DAYS:
        timetable[day].sort(key=lambda x: x["period_start_time"])

    # Compute free slots
    free_slots: dict[str, list[str]] = {}
    for day in WORKING_DAYS:
        free_slots[day] = [
            p.start_time.strftime("%H:%M")
            for p in all_periods
            if p.id not in assigned_periods[day]
        ]

    total_periods = sum(len(timetable[day]) for day in WORKING_DAYS)

    return {
        "teacher_id": staff.id,
        "teacher_name": staff.full_name,
        "academic_year": ay.name,
        "total_periods_per_week": total_periods,
        "timetable": timetable,
        "free_slots": free_slots,
    }


# ---------------------------------------------------------------------------
# Conflict Detection Service
# ---------------------------------------------------------------------------


async def detect_conflicts(
    db: AsyncSession,
    school_id: uuid.UUID,
    academic_year_name: str | None = None,
    class_section_id: uuid.UUID | None = None,
) -> dict:
    """Detect scheduling conflicts (teacher double-booking)."""
    ay = await _get_current_academic_year(db, school_id, academic_year_name)

    query = select(TimetableSlot).where(
        TimetableSlot.school_id == school_id,
        TimetableSlot.academic_year_id == ay.id,
        TimetableSlot.staff_id.isnot(None),
    )
    if class_section_id:
        query = query.where(TimetableSlot.class_section_id == class_section_id)

    result = await db.execute(query)
    slots = result.scalars().all()

    # Group by (teacher, day, period) to find double-bookings
    teacher_slots: dict[tuple[uuid.UUID, str, uuid.UUID], list[TimetableSlot]] = defaultdict(list)
    for slot in slots:
        key = (slot.staff_id, slot.day_of_week, slot.period_config_id)
        teacher_slots[key].append(slot)

    conflicts: list[dict] = []
    for key, slot_list in teacher_slots.items():
        if len(slot_list) > 1:
            staff_id, day, period_config_id = key
            staff = slot_list[0].staff
            teacher_name = staff.full_name if staff else "Unknown"
            period = slot_list[0].period_config
            period_start = period.start_time.strftime("%H:%M") if period else "?"

            assignments = []
            for s in slot_list:
                cs = s.class_section
                class_name = cs.class_.name if cs and cs.class_ else "?"
                section = cs.section.name if cs and cs.section else "?"
                subject_name = s.subject.name if s.subject else "?"
                assignments.append({
                    "class_name": class_name,
                    "section": section,
                    "subject": subject_name,
                })

            conflicts.append({
                "type": "teacher_double_booked",
                "teacher_id": staff_id,
                "teacher_name": teacher_name,
                "day": day,
                "period_start_time": period_start,
                "assignments": assignments,
            })

    return {
        "total_conflicts": len(conflicts),
        "conflicts": conflicts,
    }
