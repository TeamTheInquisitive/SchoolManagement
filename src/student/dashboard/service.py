from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.academic import Class, ClassSection, Section, Subject
from src.models.assignment import Assignment, AssignmentSubmission
from src.models.attendance import AttendanceRecord, AttendanceSession
from src.models.core import AcademicYear, User
from src.models.examination import Exam, ExamResult
from src.models.fee import FeeRecord
from src.models.meeting import ParentMeeting
from src.models.notification import Notification, NotificationRecipient
from src.models.staff import Staff
from src.models.student import Student, StudentEnrollment
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


async def _get_student_enrollment(
    db: AsyncSession, school_id: uuid.UUID, student_id: uuid.UUID, ay_id: uuid.UUID
) -> StudentEnrollment | None:
    result = await db.execute(
        select(StudentEnrollment).where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.student_id == student_id,
            StudentEnrollment.academic_year_id == ay_id,
            StudentEnrollment.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


async def get_dashboard_stats(db: AsyncSession, school_id: uuid.UUID, user: User) -> dict:
    """Get KPI stats for student dashboard."""
    student_id = user.student_id
    ay = await _get_current_academic_year(db, school_id)

    # Attendance percentage
    attendance_pct = 0.0
    if student_id:
        total = (await db.execute(
            select(func.count(AttendanceRecord.id))
            .join(AttendanceSession, AttendanceRecord.attendance_session_id == AttendanceSession.id)
            .where(
                AttendanceSession.school_id == school_id,
                AttendanceSession.is_active.is_(True),
                AttendanceRecord.student_id == student_id,
            )
        )).scalar() or 0

        present = (await db.execute(
            select(func.count(AttendanceRecord.id))
            .join(AttendanceSession, AttendanceRecord.attendance_session_id == AttendanceSession.id)
            .where(
                AttendanceSession.school_id == school_id,
                AttendanceSession.is_active.is_(True),
                AttendanceRecord.student_id == student_id,
                AttendanceRecord.status.in_(["Present", "Late"]),
            )
        )).scalar() or 0

        if total > 0:
            attendance_pct = round((present / total) * 100, 1)

    # Pending assignments
    pending_assignments = 0
    if student_id:
        pending_assignments = (await db.execute(
            select(func.count(AssignmentSubmission.id)).where(
                AssignmentSubmission.student_id == student_id,
                AssignmentSubmission.status == "Pending",
                AssignmentSubmission.is_active.is_(True),
            )
        )).scalar() or 0

    # Fee status
    fee_status = "Clear"
    if student_id and ay:
        pending_fees = (await db.execute(
            select(func.count(FeeRecord.id)).where(
                FeeRecord.school_id == school_id,
                FeeRecord.student_id == student_id,
                FeeRecord.academic_year_id == ay.id,
                FeeRecord.is_active.is_(True),
                FeeRecord.status.in_(["Pending", "Overdue", "Partially Paid"]),
            )
        )).scalar() or 0
        if pending_fees > 0:
            fee_status = "Pending"

    return {
        "attendance_percentage": attendance_pct,
        "average_grade": "",
        "pending_assignments": pending_assignments,
        "fee_status": fee_status,
    }


async def get_today_schedule(db: AsyncSession, school_id: uuid.UUID, user: User, target_date: str | None = None) -> dict:
    """Get classes for a given date (defaults to today)."""
    student_id = user.student_id
    ay = await _get_current_academic_year(db, school_id)
    today = date.fromisoformat(target_date) if target_date else date.today()
    day_name = today.strftime("%A")

    schedule = []
    if ay and student_id:
        enrollment = await _get_student_enrollment(db, school_id, student_id, ay.id)
        if enrollment:
            result = await db.execute(
                select(
                    TimetableSlot,
                    PeriodConfig.start_time,
                    PeriodConfig.end_time,
                    Subject.name,
                    Staff.full_name,
                )
                .join(PeriodConfig, TimetableSlot.period_config_id == PeriodConfig.id)
                .join(Subject, TimetableSlot.subject_id == Subject.id)
                .join(Staff, TimetableSlot.staff_id == Staff.id)
                .where(
                    TimetableSlot.school_id == school_id,
                    TimetableSlot.class_section_id == enrollment.class_section_id,
                    TimetableSlot.academic_year_id == ay.id,
                    TimetableSlot.day_of_week == day_name,
                    TimetableSlot.is_active.is_(True),
                )
                .order_by(PeriodConfig.start_time)
            )
            rows = result.all()

            for i, row in enumerate(rows, 1):
                slot, start_t, end_t, subj_name, teacher_name = row
                schedule.append({
                    "period_number": i,
                    "start_time": start_t.strftime("%H:%M") if start_t else None,
                    "end_time": end_t.strftime("%H:%M") if end_t else None,
                    "subject": subj_name,
                    "teacher_name": teacher_name or "",
                    "slot_type": slot.slot_type or "Lecture",
                })

    return {
        "date": today.isoformat(),
        "day": day_name,
        "total_classes": len(schedule),
        "schedule": schedule,
    }


async def get_pending_assignments(db: AsyncSession, school_id: uuid.UUID, user: User) -> dict:
    """Get pending assignments for the student."""
    student_id = user.student_id
    items = []

    if student_id:
        result = await db.execute(
            select(
                Assignment.id,
                Assignment.title,
                Assignment.due_date,
                Assignment.total_marks,
                Subject.name,
                AssignmentSubmission.status,
            )
            .join(AssignmentSubmission, AssignmentSubmission.assignment_id == Assignment.id)
            .join(Subject, Assignment.subject_id == Subject.id)
            .where(
                Assignment.school_id == school_id,
                Assignment.is_active.is_(True),
                AssignmentSubmission.student_id == student_id,
                AssignmentSubmission.status == "Pending",
                AssignmentSubmission.is_active.is_(True),
            )
            .order_by(Assignment.due_date.asc())
            .limit(10)
        )
        rows = result.all()

        for row in rows:
            items.append({
                "id": row[0],
                "title": row[1],
                "subject": row[4],
                "due_date": row[2].isoformat() if row[2] else "",
                "total_marks": float(row[3]) if row[3] else None,
                "status": row[5],
            })

    return {"total": len(items), "items": items}


async def get_upcoming_exams(db: AsyncSession, school_id: uuid.UUID, user: User) -> dict:
    """Get upcoming exams for the student."""
    student_id = user.student_id
    ay = await _get_current_academic_year(db, school_id)
    today = date.today()
    items = []

    if ay and student_id:
        enrollment = await _get_student_enrollment(db, school_id, student_id, ay.id)
        if enrollment:
            result = await db.execute(
                select(
                    Exam.id,
                    Exam.name,
                    Exam.date,
                    Exam.total_marks,
                    Exam.start_time,
                    Exam.end_time,
                    Subject.name,
                )
                .join(Subject, Exam.subject_id == Subject.id)
                .where(
                    Exam.school_id == school_id,
                    Exam.class_section_id == enrollment.class_section_id,
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
                    "subject": row[6],
                    "date": row[2].isoformat() if row[2] else "",
                    "total_marks": float(row[3]) if row[3] else 0,
                    "start_time": row[4].strftime("%H:%M") if row[4] else None,
                    "end_time": row[5].strftime("%H:%M") if row[5] else None,
                })

    return {"total": len(items), "items": items}


async def get_subject_attendance(db: AsyncSession, school_id: uuid.UUID, user: User) -> dict:
    """Get per-subject attendance for the student."""
    student_id = user.student_id
    subjects = []
    overall_pct = 0.0

    if student_id:
        result = await db.execute(
            select(
                Subject.name,
                func.count(AttendanceRecord.id).label("total"),
                func.count(case((AttendanceRecord.status.in_(["Present", "Late"]), 1))).label("present"),
            )
            .select_from(AttendanceRecord)
            .join(AttendanceSession, AttendanceRecord.attendance_session_id == AttendanceSession.id)
            .join(Subject, AttendanceSession.subject_id == Subject.id)
            .where(
                AttendanceSession.school_id == school_id,
                AttendanceSession.is_active.is_(True),
                AttendanceRecord.student_id == student_id,
                AttendanceSession.subject_id.isnot(None),
            )
            .group_by(Subject.name)
        )
        rows = result.all()

        total_all = 0
        present_all = 0
        for row in rows:
            pct = round((row[2] / row[1]) * 100, 1) if row[1] > 0 else 0
            subjects.append({
                "subject": row[0],
                "total_classes": row[1],
                "attended": row[2],
                "percentage": pct,
            })
            total_all += row[1]
            present_all += row[2]

        if total_all > 0:
            overall_pct = round((present_all / total_all) * 100, 1)

    return {"overall_percentage": overall_pct, "subjects": subjects}


async def get_recent_results(db: AsyncSession, school_id: uuid.UUID, user: User) -> dict:
    """Get recent exam results for the student."""
    student_id = user.student_id
    items = []

    if student_id:
        result = await db.execute(
            select(
                Exam.id,
                Exam.name,
                Exam.total_marks,
                ExamResult.marks_obtained,
                ExamResult.grade,
                ExamResult.percentage,
                Subject.name,
            )
            .join(ExamResult, ExamResult.exam_id == Exam.id)
            .join(Subject, Exam.subject_id == Subject.id)
            .where(
                Exam.school_id == school_id,
                Exam.is_active.is_(True),
                ExamResult.student_id == student_id,
                ExamResult.is_active.is_(True),
            )
            .order_by(Exam.date.desc())
            .limit(10)
        )
        rows = result.all()

        for row in rows:
            items.append({
                "exam_id": row[0],
                "exam_name": row[1],
                "subject": row[6],
                "marks_obtained": float(row[3]) if row[3] else None,
                "total_marks": float(row[2]) if row[2] else 0,
                "grade": row[4],
                "percentage": float(row[5]) if row[5] else None,
            })

    return {"items": items}


async def get_announcements(db: AsyncSession, school_id: uuid.UUID, user: User) -> dict:
    """Get recent announcements for the student."""
    items = []
    result = await db.execute(
        select(
            Notification.id,
            Notification.title,
            Notification.message,
            Notification.sent_at,
            Notification.type,
        )
        .where(
            Notification.school_id == school_id,
            Notification.is_active.is_(True),
            Notification.status == "Sent",
            Notification.target_type.in_(["all", "students"]),
        )
        .order_by(Notification.sent_at.desc())
        .limit(10)
    )
    rows = result.all()

    for row in rows:
        items.append({
            "id": row[0],
            "title": row[1],
            "message": row[2] or "",
            "date": row[3].strftime("%Y-%m-%d") if row[3] else "",
            "type": row[4] or "",
        })

    return {"items": items}


async def get_notifications(db: AsyncSession, school_id: uuid.UUID, user: User) -> dict:
    """Get recent notifications for the student."""
    items = []
    unread_count = 0

    result = await db.execute(
        select(
            Notification.id,
            Notification.title,
            Notification.message,
            NotificationRecipient.is_read,
            Notification.sent_at,
        )
        .join(NotificationRecipient, NotificationRecipient.notification_id == Notification.id)
        .where(
            Notification.school_id == school_id,
            NotificationRecipient.user_id == user.id,
            Notification.is_active.is_(True),
            NotificationRecipient.is_active.is_(True),
        )
        .order_by(Notification.sent_at.desc())
        .limit(10)
    )
    rows = result.all()

    for row in rows:
        items.append({
            "id": row[0],
            "title": row[1],
            "message": row[2] or "",
            "date": row[4].strftime("%Y-%m-%d") if row[4] else "",
            "is_read": row[3],
        })
        if not row[3]:
            unread_count += 1

    return {"unread_count": unread_count, "items": items}


async def get_fee_status(db: AsyncSession, school_id: uuid.UUID, user: User) -> dict:
    """Get fee overview for the student."""
    student_id = user.student_id
    ay = await _get_current_academic_year(db, school_id)
    items = []
    total_fees = 0.0
    total_paid = 0.0
    total_pending = 0.0

    if student_id and ay:
        result = await db.execute(
            select(FeeRecord)
            .where(
                FeeRecord.school_id == school_id,
                FeeRecord.student_id == student_id,
                FeeRecord.academic_year_id == ay.id,
                FeeRecord.is_active.is_(True),
            )
            .order_by(FeeRecord.due_date.asc())
        )
        records = result.scalars().all()

        for record in records:
            total_fees += float(record.net_amount or 0)
            total_paid += float(record.paid_amount or 0)
            total_pending += float(record.balance_amount or 0)
            items.append({
                "fee_type": record.fee_type,
                "amount": float(record.net_amount or 0),
                "paid": float(record.paid_amount or 0),
                "pending": float(record.balance_amount or 0),
                "due_date": record.due_date.isoformat() if record.due_date else "",
                "status": record.status,
            })

    return {
        "total_fees": total_fees,
        "total_paid": total_paid,
        "total_pending": total_pending,
        "items": items,
    }


async def get_parent_meetings(db: AsyncSession, school_id: uuid.UUID, user: User) -> dict:
    """Get parent meetings for the student."""
    student_id = user.student_id
    items = []

    if student_id:
        result = await db.execute(
            select(
                ParentMeeting.id,
                ParentMeeting.meeting_type,
                ParentMeeting.meeting_date,
                ParentMeeting.status,
                ParentMeeting.discussion_notes,
                Staff.full_name,
            )
            .join(Staff, ParentMeeting.conducted_by == Staff.id)
            .where(
                ParentMeeting.school_id == school_id,
                ParentMeeting.student_id == student_id,
                ParentMeeting.is_active.is_(True),
            )
            .order_by(ParentMeeting.meeting_date.desc())
            .limit(10)
        )
        rows = result.all()

        for row in rows:
            items.append({
                "id": row[0],
                "meeting_type": row[1],
                "date": row[2].isoformat() if row[2] else "",
                "conducted_by": row[5] or "",
                "status": row[3] or "",
                "notes": row[4],
            })

    return {"total": len(items), "items": items}
