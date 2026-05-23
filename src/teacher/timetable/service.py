from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFound
from src.models.core import AcademicYear, User
from src.models.staff import Staff
from src.models.timetable import PeriodConfig, TimetableSlot

WORKING_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


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


async def _get_staff_for_user(
    db: AsyncSession, school_id: uuid.UUID, user: User
) -> Staff:
    """Get the Staff record linked to the user."""
    if not user.staff_id:
        raise NotFound("Staff", "No staff record linked to this user")
    result = await db.execute(
        select(Staff).where(
            Staff.id == user.staff_id,
            Staff.school_id == school_id,
            Staff.is_active.is_(True),
        )
    )
    staff = result.scalar_one_or_none()
    if not staff:
        raise NotFound("Staff", str(user.staff_id))
    return staff


def _compute_duration(start_time, end_time) -> int:
    """Compute duration in minutes."""
    start_minutes = start_time.hour * 60 + start_time.minute
    end_minutes = end_time.hour * 60 + end_time.minute
    return end_minutes - start_minutes


async def get_weekly_timetable(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    academic_year_name: str | None = None,
    day_filter: str | None = None,
) -> dict:
    """Get teacher's weekly timetable with KPI stats."""
    ay = await _get_current_academic_year(db, school_id, academic_year_name)
    staff = await _get_staff_for_user(db, school_id, user)

    # Get all periods (including breaks)
    periods_result = await db.execute(
        select(PeriodConfig).where(
            PeriodConfig.school_id == school_id,
            PeriodConfig.academic_year_id == ay.id,
            PeriodConfig.is_active.is_(True),
        ).order_by(PeriodConfig.start_time)
    )
    all_periods = periods_result.scalars().all()

    # Get teacher's assigned slots
    slots_query = select(TimetableSlot).where(
        TimetableSlot.school_id == school_id,
        TimetableSlot.academic_year_id == ay.id,
        TimetableSlot.staff_id == staff.id,
        TimetableSlot.is_active.is_(True),
    )
    if day_filter:
        slots_query = slots_query.where(TimetableSlot.day_of_week == day_filter)

    slots_result = await db.execute(slots_query)
    slots = slots_result.scalars().all()

    # Build slot lookup: (day, period_config_id) -> slot
    slot_map: dict[tuple[str, uuid.UUID], TimetableSlot] = {}
    for slot in slots:
        slot_map[(slot.day_of_week, slot.period_config_id)] = slot

    # Build timetable for each day
    days_to_process = [day_filter] if day_filter else WORKING_DAYS
    timetable: dict[str, list[dict]] = {}

    total_classes = 0
    practical_sessions = 0
    free_periods = 0

    for day in days_to_process:
        day_items: list[dict] = []
        for period in all_periods:
            # Skip day-specific periods not matching this day
            if period.day_of_week and period.day_of_week != day:
                continue

            duration = _compute_duration(period.start_time, period.end_time)

            if period.is_break:
                day_items.append({
                    "id": period.id,
                    "start_time": period.start_time.strftime("%H:%M"),
                    "end_time": period.end_time.strftime("%H:%M"),
                    "duration_minutes": duration,
                    "subject": None,
                    "type": "Break",
                    "class_name": None,
                    "section": None,
                    "class_section": None,
                    "label": period.name or "Break",
                })
                continue

            slot = slot_map.get((day, period.id))
            if slot:
                cs = slot.class_section
                class_name = cs.class_.name if cs and cs.class_ else None
                section = cs.section.name if cs and cs.section else None
                class_section = f"{class_name}-{section}" if class_name and section else None
                subject_name = slot.subject.name if slot.subject else None
                slot_type = slot.slot_type

                total_classes += 1
                if slot_type == "Practical":
                    practical_sessions += 1

                day_items.append({
                    "id": slot.id,
                    "start_time": period.start_time.strftime("%H:%M"),
                    "end_time": period.end_time.strftime("%H:%M"),
                    "duration_minutes": duration,
                    "subject": subject_name,
                    "type": slot_type,
                    "class_name": class_name,
                    "section": section,
                    "class_section": class_section,
                    "label": None,
                })
            else:
                free_periods += 1
                day_items.append({
                    "id": period.id,
                    "start_time": period.start_time.strftime("%H:%M"),
                    "end_time": period.end_time.strftime("%H:%M"),
                    "duration_minutes": duration,
                    "subject": None,
                    "type": "Free",
                    "class_name": None,
                    "section": None,
                    "class_section": None,
                    "label": None,
                })

        timetable[day] = day_items

    return {
        "academic_year": ay.name,
        "stats": {
            "total_classes_per_week": total_classes,
            "practical_sessions": practical_sessions,
            "free_periods": free_periods,
        },
        "working_days": WORKING_DAYS,
        "timetable": timetable,
    }


async def get_today_schedule(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    target_date: date | None = None,
) -> dict:
    """Get today's schedule for the teacher."""
    if target_date is None:
        target_date = date.today()

    day_name = DAY_NAMES[target_date.weekday()]

    ay = await _get_current_academic_year(db, school_id)
    staff = await _get_staff_for_user(db, school_id, user)

    # Get all periods (including breaks)
    periods_result = await db.execute(
        select(PeriodConfig).where(
            PeriodConfig.school_id == school_id,
            PeriodConfig.academic_year_id == ay.id,
            PeriodConfig.is_active.is_(True),
        ).order_by(PeriodConfig.start_time)
    )
    all_periods = periods_result.scalars().all()

    # Get teacher's slots for this day
    slots_result = await db.execute(
        select(TimetableSlot).where(
            TimetableSlot.school_id == school_id,
            TimetableSlot.academic_year_id == ay.id,
            TimetableSlot.staff_id == staff.id,
            TimetableSlot.day_of_week == day_name,
            TimetableSlot.is_active.is_(True),
        )
    )
    slots = slots_result.scalars().all()

    # Build slot lookup: period_config_id -> slot
    slot_map: dict[uuid.UUID, TimetableSlot] = {}
    for slot in slots:
        slot_map[slot.period_config_id] = slot

    schedule: list[dict] = []
    total_classes = 0
    practical_sessions = 0
    free_periods = 0

    for period in all_periods:
        # Skip day-specific periods not matching this day
        if period.day_of_week and period.day_of_week != day_name:
            continue

        duration = _compute_duration(period.start_time, period.end_time)

        if period.is_break:
            schedule.append({
                "id": period.id,
                "start_time": period.start_time.strftime("%H:%M"),
                "end_time": period.end_time.strftime("%H:%M"),
                "duration_minutes": duration,
                "subject": None,
                "type": "Break",
                "class_name": None,
                "section": None,
                "class_section": None,
                "label": period.name or "Break",
            })
            continue

        slot = slot_map.get(period.id)
        if slot:
            cs = slot.class_section
            class_name = cs.class_.name if cs and cs.class_ else None
            section = cs.section.name if cs and cs.section else None
            class_section = f"{class_name}-{section}" if class_name and section else None
            subject_name = slot.subject.name if slot.subject else None
            slot_type = slot.slot_type

            total_classes += 1
            if slot_type == "Practical":
                practical_sessions += 1

            schedule.append({
                "id": slot.id,
                "start_time": period.start_time.strftime("%H:%M"),
                "end_time": period.end_time.strftime("%H:%M"),
                "duration_minutes": duration,
                "subject": subject_name,
                "type": slot_type,
                "class_name": class_name,
                "section": section,
                "class_section": class_section,
                "label": None,
            })
        else:
            free_periods += 1
            schedule.append({
                "id": period.id,
                "start_time": period.start_time.strftime("%H:%M"),
                "end_time": period.end_time.strftime("%H:%M"),
                "duration_minutes": duration,
                "subject": None,
                "type": "Free",
                "class_name": None,
                "section": None,
                "class_section": None,
                "label": None,
            })

    return {
        "date": str(target_date),
        "day": day_name,
        "stats": {
            "total_classes_today": total_classes,
            "practical_sessions_today": practical_sessions,
            "free_periods_today": free_periods,
        },
        "schedule": schedule,
    }
