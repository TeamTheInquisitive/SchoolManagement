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
    """Get upcoming exams for the teacher."""
    staff_id = user.staff_id
    today = date.today()
    items = []

    if staff_id:
        result = await db.execute(
            select(
                Exam.id,
                Exam.name,
                Exam.date,
                Exam.total_marks,
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
                Exam.examiner_id == staff_id,
                Exam.date > today,
                Exam.is_active.is_(True),
                Exam.status.in_(["Scheduled", "Draft"]),
            )
            .order_by(Exam.date.asc())
            .limit(10)
        )
        rows = result.all()

        for row in rows:
            items.append({
                "id": row[0],
                "name": row[1],
                "class_section": f"{row[5]}-{row[6]}",
                "subject": row[4],
                "date": row[2].isoformat() if row[2] else "",
                "total_marks": float(row[3]) if row[3] else 0,
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
            .join(Subject, ClassAssignment.subject_id == Subject.id)
            .where(
                ClassAssignment.school_id == school_id,
                ClassAssignment.staff_id == staff_id,
                ClassAssignment.academic_year_id == ay.id,
                ClassAssignment.is_active.is_(True),
            )
            .order_by(Class.sort_order, Section.name)
        )
        rows = result.all()

        for row in rows:
            # Count students enrolled in this class section
            count_result = await db.execute(
                select(func.count(StudentEnrollment.id)).where(
                    StudentEnrollment.class_section_id == row[1],
                    StudentEnrollment.is_active.is_(True),
                )
            )
            student_count = count_result.scalar() or 0

            classes.append({
                "class_name": row[2],
                "section": row[3],
                "subject": row[4],
                "student_count": student_count,
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
