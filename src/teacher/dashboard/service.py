from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.academic import Class, ClassSection, Section, Subject
from src.models.adhoc_class import AdhocClass
from src.models.assignment import Assignment, AssignmentSubmission
from src.models.core import AcademicYear, User
from src.models.examination import Exam
from src.models.leave import LeaveApplication
from src.models.staff import ClassAssignment
from src.models.student import Student, StudentEnrollment, StudentMentor
from src.models.timetable import PeriodConfig, TimetableSlot


async def _get_current_academic_year(db: AsyncSession, school_id: uuid.UUID) -> AcademicYear | None:
    result = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
            AcademicYear.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


async def get_dashboard_stats(db: AsyncSession, school_id: uuid.UUID, user: User) -> dict:
    """Get KPI stats for teacher dashboard."""
    staff_id = user.staff_id
    ay = await _get_current_academic_year(db, school_id)
    today = date.today()

    # Total students across assigned classes
    total_students = 0
    if ay and staff_id:
        class_section_ids = (await db.execute(
            select(ClassAssignment.class_section_id)
            .where(
                ClassAssignment.school_id == school_id,
                ClassAssignment.staff_id == staff_id,
                ClassAssignment.academic_year_id == ay.id,
                ClassAssignment.is_active.is_(True),
            )
            .distinct()
        )).scalars().all()

        if class_section_ids:
            total_students = (await db.execute(
                select(func.count(StudentEnrollment.id)).where(
                    StudentEnrollment.school_id == school_id,
                    StudentEnrollment.academic_year_id == ay.id,
                    StudentEnrollment.class_section_id.in_(class_section_ids),
                    StudentEnrollment.is_active.is_(True),
                )
            )).scalar() or 0

    # Pending reviews (assignments with ungraded submissions)
    pending_reviews = 0
    if staff_id:
        pending_reviews = (await db.execute(
            select(func.count(AssignmentSubmission.id))
            .join(Assignment, AssignmentSubmission.assignment_id == Assignment.id)
            .where(
                Assignment.school_id == school_id,
                Assignment.staff_id == staff_id,
                Assignment.is_active.is_(True),
                AssignmentSubmission.status == "Submitted",
                AssignmentSubmission.is_active.is_(True),
            )
        )).scalar() or 0

    # Upcoming exams
    upcoming_exams = 0
    if ay and staff_id:
        upcoming_exams = (await db.execute(
            select(func.count(Exam.id)).where(
                Exam.school_id == school_id,
                Exam.examiner_id == staff_id,
                Exam.date > today,
                Exam.is_active.is_(True),
                Exam.status.in_(["Scheduled", "Draft"]),
            )
        )).scalar() or 0

    # Classes today
    day_name = today.strftime("%A")
    classes_today = 0
    if ay and staff_id:
        classes_today = (await db.execute(
            select(func.count(TimetableSlot.id)).where(
                TimetableSlot.school_id == school_id,
                TimetableSlot.staff_id == staff_id,
                TimetableSlot.academic_year_id == ay.id,
                TimetableSlot.day_of_week == day_name,
                TimetableSlot.is_active.is_(True),
            )
        )).scalar() or 0

    return {
        "total_students": total_students,
        "pending_reviews": pending_reviews,
        "upcoming_exams": upcoming_exams,
        "classes_today": classes_today,
    }


async def get_today_schedule(db: AsyncSession, school_id: uuid.UUID, user: User, target_date: str | None = None) -> dict:
    """Get schedule for a specific date (defaults to today)."""
    staff_id = user.staff_id
    ay = await _get_current_academic_year(db, school_id)
    if target_date:
        try:
            today = date.fromisoformat(target_date)
        except ValueError:
            today = date.today()
    else:
        today = date.today()
    day_name = today.strftime("%A")

    schedule = []
    if ay and staff_id:
        result = await db.execute(
            select(
                TimetableSlot,
                PeriodConfig.start_time,
                PeriodConfig.end_time,
                Subject.name,
                Class.name,
                Section.name,
            )
            .join(PeriodConfig, TimetableSlot.period_config_id == PeriodConfig.id)
            .join(Subject, TimetableSlot.subject_id == Subject.id)
            .join(ClassSection, TimetableSlot.class_section_id == ClassSection.id)
            .join(Class, ClassSection.class_id == Class.id)
            .join(Section, ClassSection.section_id == Section.id)
            .where(
                TimetableSlot.school_id == school_id,
                TimetableSlot.staff_id == staff_id,
                TimetableSlot.academic_year_id == ay.id,
                TimetableSlot.day_of_week == day_name,
                TimetableSlot.is_active.is_(True),
            )
            .order_by(PeriodConfig.start_time)
        )
        rows = result.all()

        for i, row in enumerate(rows, 1):
            slot, start_t, end_t, subj_name, cls_name, sec_name = row
            schedule.append({
                "period_number": i,
                "start_time": start_t.strftime("%H:%M") if start_t else None,
                "end_time": end_t.strftime("%H:%M") if end_t else None,
                "subject": subj_name,
                "class_name": cls_name,
                "section": sec_name,
                "slot_type": slot.slot_type or "Lecture",
            })

    return {
        "date": today.isoformat(),
        "day": day_name,
        "total_classes": len(schedule),
        "schedule": schedule,
    }


async def get_pending_reviews(db: AsyncSession, school_id: uuid.UUID, user: User) -> dict:
    """Get assignments needing review."""
    staff_id = user.staff_id
    items = []

    if staff_id:
        result = await db.execute(
            select(
                Assignment.id,
                Assignment.title,
                Assignment.due_date,
                Subject.name,
                Class.name,
                Section.name,
                func.count(AssignmentSubmission.id).label("pending_count"),
            )
            .join(AssignmentSubmission, AssignmentSubmission.assignment_id == Assignment.id)
            .join(Subject, Assignment.subject_id == Subject.id)
            .join(ClassSection, Assignment.class_section_id == ClassSection.id)
            .join(Class, ClassSection.class_id == Class.id)
            .join(Section, ClassSection.section_id == Section.id)
            .where(
                Assignment.school_id == school_id,
                Assignment.staff_id == staff_id,
                Assignment.is_active.is_(True),
                AssignmentSubmission.status == "Submitted",
                AssignmentSubmission.is_active.is_(True),
            )
            .group_by(
                Assignment.id, Assignment.title, Assignment.due_date,
                Subject.name, Class.name, Section.name,
            )
            .order_by(Assignment.due_date.asc())
            .limit(10)
        )
        rows = result.all()

        for row in rows:
            items.append({
                "id": row[0],
                "title": row[1],
                "class_section": f"{row[4]}-{row[5]}",
                "subject": row[3],
                "due_date": row[2].isoformat() if row[2] else "",
                "submissions_pending": row[6],
            })

    return {"total": len(items), "items": items}


async def get_upcoming_exams(db: AsyncSession, school_id: uuid.UUID, user: User) -> dict:
    """Get upcoming exams for the teacher (by assignment or examiner)."""
    staff_id = user.staff_id
    today = date.today()
    items = []

    if staff_id:
        # Get teacher's class-section + subject assignments
        from src.models.staff import ClassAssignment
        ay_result = await db.execute(
            select(AcademicYear).where(
                AcademicYear.school_id == school_id,
                AcademicYear.is_current.is_(True),
                AcademicYear.is_active.is_(True),
            )
        )
        ay = ay_result.scalar_one_or_none()
        if not ay:
            return {"total": 0, "items": []}

        assign_result = await db.execute(
            select(ClassAssignment.class_section_id, ClassAssignment.subject_id).where(
                ClassAssignment.school_id == school_id,
                ClassAssignment.staff_id == staff_id,
                ClassAssignment.academic_year_id == ay.id,
                ClassAssignment.is_active.is_(True),
            )
        )
        pairs = assign_result.all()
        cs_ids = list(set(p[0] for p in pairs))
        subj_ids = list(set(p[1] for p in pairs if p[1]))

        if not cs_ids:
            return {"total": 0, "items": []}

        result = await db.execute(
            select(
                Exam.id,
                Exam.name,
                Exam.date,
                Exam.total_marks,
                Exam.exam_type,
                Exam.start_time,
                Exam.end_time,
                Subject.name,
                Class.name,
                Section.name,
            )
            .join(Subject, Exam.subject_id == Subject.id)
            .join(ClassSection, Exam.class_section_id == ClassSection.id)
            .join(Class, ClassSection.class_id == Class.id)
            .join(Section, ClassSection.section_id == Section.id)
            .where(
                Exam.school_id == school_id,
                Exam.is_active.is_(True),
                Exam.status != "Cancelled",
                Exam.class_section_id.in_(cs_ids),
                Exam.subject_id.in_(subj_ids) if subj_ids else True,
            )
            .order_by(Exam.date.desc().nullslast())
            .limit(20)
        )
        rows = result.all()

        for row in rows:
            items.append({
                "id": row[0],
                "name": row[1],
                "class_section": f"{row[8]}-{row[9]}",
                "subject": row[7],
                "date": row[2].isoformat() if row[2] else "",
                "total_marks": float(row[3]) if row[3] else 0,
                "exam_type": row[4],
                "start_time": str(row[5]) if row[5] else None,
                "end_time": str(row[6]) if row[6] else None,
            })

    return {"total": len(items), "items": items}


async def get_classes_summary(db: AsyncSession, school_id: uuid.UUID, user: User) -> dict:
    """Get classes with progress for the teacher."""
    staff_id = user.staff_id
    ay = await _get_current_academic_year(db, school_id)
    classes = []

    if ay and staff_id:
        result = await db.execute(
            select(
                ClassAssignment.is_class_teacher,
                ClassAssignment.class_section_id,
                Class.name,
                Section.name,
                Subject.name,
            )
            .join(ClassSection, ClassAssignment.class_section_id == ClassSection.id)
            .join(Class, ClassSection.class_id == Class.id)
            .join(Section, ClassSection.section_id == Section.id)
            .outerjoin(Subject, ClassAssignment.subject_id == Subject.id)
            .where(
                ClassAssignment.school_id == school_id,
                ClassAssignment.staff_id == staff_id,
                ClassAssignment.academic_year_id == ay.id,
                ClassAssignment.is_active.is_(True),
            )
            .order_by(Class.sort_order, Section.name)
        )
        rows = result.all()

        student_count_cache = {}
        for row in rows:
            cs_id = row[1]
            cs_id_str = str(cs_id)
            subject_name = row[4]

            # For class teacher assignment without subject, check if we already have it
            if not subject_name:
                if any(c["class_section_id"] == cs_id_str and not c.get("subject") for c in classes):
                    continue
            else:
                # For subject assignments, skip duplicates of same class+subject
                if any(c["class_section_id"] == cs_id_str and c.get("subject") == subject_name for c in classes):
                    continue

            # Count students (cached per class_section)
            if cs_id_str not in student_count_cache:
                count_result = await db.execute(
                    select(func.count(StudentEnrollment.id)).where(
                        StudentEnrollment.class_section_id == cs_id,
                        StudentEnrollment.is_active.is_(True),
                    )
                )
                student_count_cache[cs_id_str] = count_result.scalar() or 0

            classes.append({
                "class_section_id": cs_id_str,
                "class_name": row[2],
                "section": row[3],
                "class_section": f"{row[2]}-{row[3]}",
                "subject": subject_name,
                "student_count": student_count_cache[cs_id_str],
                "is_class_teacher": row[0],
            })

    return {"total_classes": len(classes), "classes": classes}


async def get_leave_updates(db: AsyncSession, school_id: uuid.UUID, user: User) -> dict:
    """Get recent leave status for the teacher."""
    staff_id = user.staff_id
    items = []

    if staff_id:
        result = await db.execute(
            select(
                LeaveApplication.id,
                LeaveApplication.leave_type,
                LeaveApplication.from_date,
                LeaveApplication.to_date,
                LeaveApplication.days,
                LeaveApplication.status,
            )
            .where(
                LeaveApplication.school_id == school_id,
                LeaveApplication.staff_id == staff_id,
                LeaveApplication.is_active.is_(True),
            )
            .order_by(LeaveApplication.applied_on.desc())
            .limit(5)
        )
        rows = result.all()

        for row in rows:
            items.append({
                "id": row[0],
                "leave_type": row[1],
                "from_date": row[2].isoformat() if row[2] else "",
                "to_date": row[3].isoformat() if row[3] else "",
                "days": float(row[4]) if row[4] else 0,
                "status": row[5],
            })

    return {"items": items}


async def get_mentees_summary(db: AsyncSession, school_id: uuid.UUID, user: User) -> dict:
    """Get mentees list for the teacher."""
    staff_id = user.staff_id
    ay = await _get_current_academic_year(db, school_id)
    mentees = []

    if ay and staff_id:
        result = await db.execute(
            select(
                Student.id,
                Student.full_name,
                Class.name,
                Section.name,
            )
            .join(StudentMentor, StudentMentor.student_id == Student.id)
            .join(StudentEnrollment, and_(
                StudentEnrollment.student_id == Student.id,
                StudentEnrollment.academic_year_id == ay.id,
                StudentEnrollment.is_active.is_(True),
            ))
            .join(ClassSection, StudentEnrollment.class_section_id == ClassSection.id)
            .join(Class, ClassSection.class_id == Class.id)
            .join(Section, ClassSection.section_id == Section.id)
            .where(
                StudentMentor.school_id == school_id,
                StudentMentor.staff_id == staff_id,
                StudentMentor.academic_year_id == ay.id,
                StudentMentor.is_active.is_(True),
                Student.is_active.is_(True),
            )
        )
        rows = result.all()

        for row in rows:
            mentees.append({
                "student_id": row[0],
                "name": row[1],
                "class_section": f"{row[2]}-{row[3]}",
                "attendance_percentage": 0,
            })

    return {"total": len(mentees), "mentees": mentees}


async def get_adhoc_classes_dashboard(db: AsyncSession, school_id: uuid.UUID, user: User) -> dict:
    """Get adhoc classes for the teacher dashboard."""
    staff_id = user.staff_id
    items = []

    if staff_id:
        result = await db.execute(
            select(
                AdhocClass.id,
                AdhocClass.date,
                AdhocClass.type,
                AdhocClass.status,
                Class.name,
                Section.name,
                Subject.name,
            )
            .join(ClassSection, AdhocClass.class_section_id == ClassSection.id)
            .join(Class, ClassSection.class_id == Class.id)
            .join(Section, ClassSection.section_id == Section.id)
            .join(Subject, AdhocClass.subject_id == Subject.id)
            .where(
                AdhocClass.school_id == school_id,
                AdhocClass.staff_id == staff_id,
                AdhocClass.is_active.is_(True),
            )
            .order_by(AdhocClass.date.desc())
            .limit(10)
        )
        rows = result.all()

        for row in rows:
            items.append({
                "id": row[0],
                "class_name": row[4],
                "section": row[5],
                "subject": row[6],
                "date": row[1].isoformat() if row[1] else "",
                "type": row[2],
                "status": row[3],
            })

    return {"total": len(items), "items": items}


async def get_class_teacher_attendance_status(
    db: AsyncSession, school_id: uuid.UUID, user: User
) -> dict:
    """Get attendance status for last 7 working days for class teacher's classes."""
    from datetime import timedelta
    from src.models.attendance import AttendanceSession
    from src.models.core import Settings

    staff_id = user.staff_id
    if not staff_id:
        return {"is_class_teacher": False, "pending_days": []}

    ay = await _get_current_academic_year(db, school_id)
    if not ay:
        return {"is_class_teacher": False, "pending_days": []}

    # Get class sections where teacher is class teacher
    ct_result = await db.execute(
        select(ClassAssignment).where(
            ClassAssignment.school_id == school_id,
            ClassAssignment.staff_id == staff_id,
            ClassAssignment.academic_year_id == ay.id,
            ClassAssignment.is_class_teacher.is_(True),
            ClassAssignment.is_active.is_(True),
        )
    )
    ct_assignments = ct_result.scalars().all()

    if not ct_assignments:
        return {"is_class_teacher": False, "pending_days": []}

    # Get working days from settings
    wd_result = await db.execute(
        select(Settings).where(
            Settings.school_id == school_id,
            Settings.category == "general",
            Settings.key == "working_days",
            Settings.is_active.is_(True),
        )
    )
    wd_row = wd_result.scalar_one_or_none()
    working_days = wd_row.value if wd_row and wd_row.value else ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    working_day_indices = [["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(d) for d in working_days if d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]]

    # Get holidays
    ay_key = f"holidays_{ay.id}"
    hol_result = await db.execute(
        select(Settings).where(
            Settings.school_id == school_id,
            Settings.category == "school",
            Settings.key == ay_key,
            Settings.is_active.is_(True),
        )
    )
    hol_row = hol_result.scalar_one_or_none()
    holidays_list = hol_row.value if hol_row and hol_row.value else []
    holiday_dates = set()
    for h in holidays_list:
        if isinstance(h, dict) and h.get("date"):
            holiday_dates.add(h["date"])
        elif isinstance(h, str):
            holiday_dates.add(h)

    # Compute last 7 working days (excluding today, holidays, non-working days)
    today = date.today()
    check_dates = []
    d = today
    for _ in range(14):
        if len(check_dates) >= 7:
            break
        if d.weekday() in working_day_indices and d.isoformat() not in holiday_dates and d <= today:
            check_dates.append(d)
        d -= timedelta(days=1)

    # Get class info
    class_infos = []
    for assignment in ct_assignments:
        cs_id = assignment.class_section_id
        cs_result = await db.execute(select(ClassSection).where(ClassSection.id == cs_id))
        cs = cs_result.scalar_one_or_none()
        if not cs:
            continue
        cls_result = await db.execute(select(Class).where(Class.id == cs.class_id))
        sec_result = await db.execute(select(Section).where(Section.id == cs.section_id))
        cls = cls_result.scalar_one_or_none()
        sec = sec_result.scalar_one_or_none()
        class_section = f"{cls.name}-{sec.name}" if cls and sec else str(cs_id)

        enroll_count = await db.execute(
            select(func.count(StudentEnrollment.id)).where(
                StudentEnrollment.school_id == school_id,
                StudentEnrollment.class_section_id == cs_id,
                StudentEnrollment.academic_year_id == ay.id,
                StudentEnrollment.is_active.is_(True),
            )
        )
        student_count = enroll_count.scalar() or 0
        class_infos.append({"cs_id": cs_id, "class_section": class_section, "student_count": student_count})

    # Check attendance for each date + class
    pending_days = []
    for check_date in check_dates:
        for ci in class_infos:
            att_result = await db.execute(
                select(AttendanceSession).where(
                    AttendanceSession.school_id == school_id,
                    AttendanceSession.class_section_id == ci["cs_id"],
                    AttendanceSession.date == check_date,
                    AttendanceSession.subject_id.is_(None),
                )
            )
            if not att_result.scalar_one_or_none():
                pending_days.append({
                    "date": check_date.isoformat(),
                    "day": check_date.strftime("%A"),
                    "class_section": ci["class_section"],
                    "class_section_id": str(ci["cs_id"]),
                    "student_count": ci["student_count"],
                    "is_today": check_date == today,
                })

    return {
        "is_class_teacher": True,
        "pending_count": len(pending_days),
        "pending_days": pending_days,
    }
