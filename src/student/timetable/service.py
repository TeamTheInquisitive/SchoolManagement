from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFound
from src.models.core import AcademicYear, User
from src.models.student import StudentEnrollment
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


async def _get_student_enrollment(
    db: AsyncSession, school_id: uuid.UUID, user: User, academic_year_id: uuid.UUID
) -> StudentEnrollment:
    """Get the student's current enrollment (class_section)."""
    if not user.student_id:
        raise NotFound("Student", "No student record linked to this user")

    result = await db.execute(
        select(StudentEnrollment).where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.student_id == user.student_id,
            StudentEnrollment.academic_year_id == academic_year_id,
            StudentEnrollment.is_active.is_(True),
        )
    )
    enrollment = result.scalar_one_or_none()
    if not enrollment:
        raise NotFound("StudentEnrollment", "Student not enrolled in any class for this academic year")
    return enrollment


def _slot_type_to_student_type(slot_type: str) -> str:
    """Map slot_type to student-friendly type."""
    mapping = {
        "Lecture": "class",
        "Practical": "lab",
        "Free": "free",
        "Break": "break",
    }
    return mapping.get(slot_type, "class")


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
) -> dict:
    """Get the weekly timetable grid for the student's class."""
    try:
        ay = await _get_current_academic_year(db, school_id, academic_year_name)
        enrollment = await _get_student_enrollment(db, school_id, user, ay.id)
    except NotFound:
        from datetime import date as _date
        return {
            "class_info": {"class_name": "-", "section": "-", "display_label": "Not Enrolled"},
            "academic_year": "",
            "current_day": DAY_NAMES[_date.today().weekday()],
            "is_today_holiday": False,
            "total_periods": 0,
            "periods": [],
            "timetable": {day: [] for day in WORKING_DAYS},
            "subject_summary": [],
        }

    class_section_id = enrollment.class_section_id

    # Load class_section with relationships
    from src.models.academic import ClassSection
    cs_result = await db.execute(
        select(ClassSection).where(ClassSection.id == class_section_id)
    )
    cs = cs_result.scalar_one_or_none()
    if not cs:
        raise NotFound("ClassSection", str(class_section_id))

    class_name = cs.class_.name if cs.class_ else ""
    section = cs.section.name if cs.section else ""

    # Get periods (non-break) for header
    periods_result = await db.execute(
        select(PeriodConfig).where(
            PeriodConfig.school_id == school_id,
            PeriodConfig.academic_year_id == ay.id,
            PeriodConfig.is_active.is_(True),
            PeriodConfig.is_break.is_(False),
        ).order_by(PeriodConfig.start_time)
    )
    periods = periods_result.scalars().all()

    # Get timetable slots for this class
    slots_result = await db.execute(
        select(TimetableSlot).where(
            TimetableSlot.school_id == school_id,
            TimetableSlot.academic_year_id == ay.id,
            TimetableSlot.class_section_id == class_section_id,
            TimetableSlot.is_active.is_(True),
        )
    )
    slots = slots_result.scalars().all()

    # Build slot lookup: (day, period_config_id) -> slot
    slot_map: dict[tuple[str, uuid.UUID], TimetableSlot] = {}
    for slot in slots:
        slot_map[(slot.day_of_week, slot.period_config_id)] = slot

    # Build timetable grid
    timetable: dict[str, list[dict]] = {}
    subject_counter: dict[str, dict] = {}  # subject -> {teacher, count, type}

    for day in WORKING_DAYS:
        day_slots: list[dict] = []
        for period in periods:
            duration = _compute_duration(period.start_time, period.end_time)
            slot = slot_map.get((day, period.id))

            if slot and slot.subject:
                subject_name = slot.subject.name if slot.subject else None
                teacher_name = slot.staff.full_name if slot.staff else None
                slot_type = _slot_type_to_student_type(slot.slot_type)

                day_slots.append({
                    "id": slot.id,
                    "subject": subject_name,
                    "teacher": teacher_name,
                    "type": slot_type,
                    "duration_minutes": duration,
                })

                # Track for subject_summary
                if subject_name:
                    if subject_name not in subject_counter:
                        subject_counter[subject_name] = {
                            "teacher": teacher_name or "",
                            "count": 0,
                            "type": slot_type,
                        }
                    subject_counter[subject_name]["count"] += 1
            else:
                # Empty / free slot - use period id as identifier
                day_slots.append({
                    "id": period.id,
                    "subject": None,
                    "teacher": None,
                    "type": "free",
                    "duration_minutes": duration,
                })

        timetable[day] = day_slots

    # Build subject summary
    subject_summary = [
        {
            "subject": subj,
            "teacher": info["teacher"],
            "sessions_per_week": info["count"],
            "type": info["type"],
        }
        for subj, info in sorted(subject_counter.items(), key=lambda x: -x[1]["count"])
    ]

    today_name = DAY_NAMES[date.today().weekday()]

    return {
        "class_info": {
            "class_name": f"Class {class_name}",
            "section": f"Section {section}",
            "display_label": f"Class {class_name} - Section {section}",
        },
        "academic_year": ay.name,
        "current_day": today_name,
        "is_today_holiday": False,
        "total_periods": len(periods),
        "periods": [
            {
                "id": p.id,
                "start_time": p.start_time.strftime("%H:%M"),
                "end_time": p.end_time.strftime("%H:%M"),
                "duration_minutes": _compute_duration(p.start_time, p.end_time),
            }
            for p in periods
        ],
        "timetable": timetable,
        "subject_summary": subject_summary,
    }


async def get_day_schedule(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    target_date: date | None = None,
) -> dict:
    """Get the schedule for a specific day (defaults to today)."""
    if target_date is None:
        target_date = date.today()

    day_name = DAY_NAMES[target_date.weekday()]
    is_today = target_date == date.today()

    _empty_class_info = {"class_name": "-", "section": "-", "display_label": "Not Enrolled"}
    try:
        ay = await _get_current_academic_year(db, school_id)
    except NotFound:
        return {"class_info": _empty_class_info, "date": str(target_date), "day": day_name, "is_today": is_today, "is_holiday": False, "periods": []}
    try:
        enrollment = await _get_student_enrollment(db, school_id, user, ay.id)
    except NotFound:
        return {"class_info": _empty_class_info, "date": str(target_date), "day": day_name, "is_today": is_today, "is_holiday": False, "periods": []}

    class_section_id = enrollment.class_section_id

    # Load class_section
    from src.models.academic import ClassSection
    cs_result = await db.execute(
        select(ClassSection).where(ClassSection.id == class_section_id)
    )
    cs = cs_result.scalar_one_or_none()
    if not cs:
        raise NotFound("ClassSection", str(class_section_id))

    class_name = cs.class_.name if cs.class_ else ""
    section = cs.section.name if cs.section else ""

    # Get non-break periods
    periods_result = await db.execute(
        select(PeriodConfig).where(
            PeriodConfig.school_id == school_id,
            PeriodConfig.academic_year_id == ay.id,
            PeriodConfig.is_active.is_(True),
            PeriodConfig.is_break.is_(False),
        ).order_by(PeriodConfig.start_time)
    )
    periods = periods_result.scalars().all()

    # Get slots for this class and day
    slots_result = await db.execute(
        select(TimetableSlot).where(
            TimetableSlot.school_id == school_id,
            TimetableSlot.academic_year_id == ay.id,
            TimetableSlot.class_section_id == class_section_id,
            TimetableSlot.day_of_week == day_name,
            TimetableSlot.is_active.is_(True),
        )
    )
    slots = slots_result.scalars().all()

    # Build slot lookup: period_config_id -> slot
    slot_map: dict[uuid.UUID, TimetableSlot] = {}
    for slot in slots:
        slot_map[slot.period_config_id] = slot

    # Build schedule
    schedule: list[dict] = []
    for period in periods:
        duration = _compute_duration(period.start_time, period.end_time)
        slot = slot_map.get(period.id)

        if slot and slot.subject:
            subject_name = slot.subject.name if slot.subject else None
            teacher_name = slot.staff.full_name if slot.staff else None
            slot_type = _slot_type_to_student_type(slot.slot_type)

            schedule.append({
                "id": slot.id,
                "subject": subject_name,
                "teacher": teacher_name,
                "start_time": period.start_time.strftime("%H:%M"),
                "end_time": period.end_time.strftime("%H:%M"),
                "duration_minutes": duration,
                "type": slot_type,
            })
        else:
            schedule.append({
                "id": period.id,
                "subject": None,
                "teacher": None,
                "start_time": period.start_time.strftime("%H:%M"),
                "end_time": period.end_time.strftime("%H:%M"),
                "duration_minutes": duration,
                "type": "free",
            })

    return {
        "class_info": {
            "class_name": f"Class {class_name}",
            "section": f"Section {section}",
            "display_label": f"Class {class_name} - Section {section}",
        },
        "date": str(target_date),
        "day": day_name,
        "is_today": is_today,
        "is_holiday": False,
        "periods": schedule,
    }
