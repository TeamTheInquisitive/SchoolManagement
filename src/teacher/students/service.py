from __future__ import annotations

from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AccessDenied, NotFound
from src.core.pagination import PaginationParams, paginate
from src.models.academic import Class, ClassSection, Section
from src.models.core import AcademicYear, User
from src.models.staff import ClassAssignment, Staff
from src.models.student import Parent, Student, StudentEnrollment, StudentMentor, StudentParent


# ---------------------------------------------------------------------------
# Access control helpers
# ---------------------------------------------------------------------------


async def _get_staff_for_user(db: AsyncSession, user: User) -> Staff | None:
    """Get the staff record linked to a user."""
    if not user.staff_id:
        return None
    result = await db.execute(select(Staff).where(Staff.id == user.staff_id, Staff.is_active.is_(True)))
    return result.scalar_one_or_none()


async def _get_current_academic_year(db: AsyncSession, school_id: UUID) -> AcademicYear | None:
    """Get the current academic year for a school."""
    result = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
        )
    )
    return result.scalar_one_or_none()


async def _get_teacher_class_section_ids(
    db: AsyncSession, school_id: UUID, staff_id: UUID, academic_year_id: UUID
) -> list[UUID]:
    """Get all class_section_ids that a teacher is assigned to (as class teacher or subject teacher)."""
    result = await db.execute(
        select(ClassAssignment.class_section_id).where(
            ClassAssignment.school_id == school_id,
            ClassAssignment.staff_id == staff_id,
            ClassAssignment.academic_year_id == academic_year_id,
            ClassAssignment.is_active.is_(True),
        )
    )
    return list(result.scalars().all())


async def _get_mentee_ids(
    db: AsyncSession, school_id: UUID, staff_id: UUID, academic_year_id: UUID
) -> list[UUID]:
    """Get all student_ids that are mentees of this staff member."""
    result = await db.execute(
        select(StudentMentor.student_id).where(
            StudentMentor.school_id == school_id,
            StudentMentor.staff_id == staff_id,
            StudentMentor.academic_year_id == academic_year_id,
            StudentMentor.is_active.is_(True),
        )
    )
    return list(result.scalars().all())


async def _is_class_teacher_of(
    db: AsyncSession, school_id: UUID, staff_id: UUID, academic_year_id: UUID, class_section_id: UUID
) -> bool:
    """Check if a teacher is the class teacher for a given class section."""
    result = await db.execute(
        select(ClassAssignment).where(
            ClassAssignment.school_id == school_id,
            ClassAssignment.staff_id == staff_id,
            ClassAssignment.academic_year_id == academic_year_id,
            ClassAssignment.class_section_id == class_section_id,
            ClassAssignment.is_class_teacher.is_(True),
            ClassAssignment.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none() is not None


async def _check_access_to_student(
    db: AsyncSession, school_id: UUID, staff_id: UUID, student_id: UUID, academic_year_id: UUID
) -> bool:
    """Check if teacher is mentor or class teacher of the student. Returns True if access allowed."""
    # Check if mentor
    mentee_ids = await _get_mentee_ids(db, school_id, staff_id, academic_year_id)
    if student_id in mentee_ids:
        return True

    # Check if class teacher of student's class
    enrollment_result = await db.execute(
        select(StudentEnrollment).where(
            StudentEnrollment.student_id == student_id,
            StudentEnrollment.academic_year_id == academic_year_id,
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.is_active.is_(True),
        )
    )
    enrollment = enrollment_result.scalar_one_or_none()
    if enrollment:
        is_ct = await _is_class_teacher_of(
            db, school_id, staff_id, academic_year_id, enrollment.class_section_id
        )
        if is_ct:
            return True

    return False


# ---------------------------------------------------------------------------
# Helper: get transport info for a student
# ---------------------------------------------------------------------------


async def _get_transport_info(db: AsyncSession, school_id: UUID, student_id: UUID, current_ay) -> dict:
    """Get transport enrollment info for a student."""
    if not current_ay:
        return {"enrolled": False}
    from src.models.transport import StudentTransport, Route, Vehicle, RouteAssignment
    st_result = await db.execute(
        select(StudentTransport).where(
            StudentTransport.student_id == student_id,
            StudentTransport.school_id == school_id,
            StudentTransport.academic_year_id == current_ay.id,
            StudentTransport.is_active.is_(True),
        )
    )
    st_record = st_result.scalar_one_or_none()
    if not st_record:
        return {"enrolled": False}
    route_r = await db.execute(select(Route).where(Route.id == st_record.route_id, Route.is_active.is_(True)))
    route_obj = route_r.scalar_one_or_none()
    bus_number = None
    ra_r = await db.execute(select(RouteAssignment.vehicle_id).where(RouteAssignment.route_id == st_record.route_id, RouteAssignment.is_active.is_(True)))
    vid = ra_r.scalar_one_or_none()
    if vid:
        v_r = await db.execute(select(Vehicle.vehicle_number).where(Vehicle.id == vid))
        bus_number = v_r.scalar_one_or_none()
    return {
        "enrolled": True,
        "route_name": route_obj.name if route_obj else None,
        "bus_number": bus_number,
        "pickup_point": st_record.pickup_point,
        "drop_point": st_record.drop_point,
    }


# ---------------------------------------------------------------------------
# Helper: get class/section names for a student
# ---------------------------------------------------------------------------


async def _get_student_class_info(
    db: AsyncSession, student_id: UUID, school_id: UUID, academic_year_id: UUID
) -> tuple[str | None, str | None]:
    """Returns (class_name, section_name) for a student in the given year."""
    enrollment_result = await db.execute(
        select(StudentEnrollment).where(
            StudentEnrollment.student_id == student_id,
            StudentEnrollment.academic_year_id == academic_year_id,
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.is_active.is_(True),
        )
    )
    enrollment = enrollment_result.scalar_one_or_none()
    if not enrollment:
        return None, None

    cs_result = await db.execute(
        select(ClassSection).where(ClassSection.id == enrollment.class_section_id)
    )
    cs = cs_result.scalar_one_or_none()
    if not cs:
        return None, None

    cls_r = await db.execute(select(Class).where(Class.id == cs.class_id))
    sec_r = await db.execute(select(Section).where(Section.id == cs.section_id))
    cls = cls_r.scalar_one_or_none()
    sec = sec_r.scalar_one_or_none()
    return (cls.name if cls else None, sec.name if sec else None)


# ---------------------------------------------------------------------------
# List students (mentor's mentees + class teacher's students)
# ---------------------------------------------------------------------------


async def get_mentees(
    db: AsyncSession,
    school_id: UUID,
    user: User,
) -> dict:
    """Get teacher's mentee students with contact details."""
    staff = await _get_staff_for_user(db, user)
    if not staff:
        raise AccessDenied("No staff record associated with this user")

    current_ay = await _get_current_academic_year(db, school_id)
    if not current_ay:
        return {"total": 0, "mentees": []}

    result = await db.execute(
        select(
            Student.id,
            Student.full_name,
            Student.admission_number,
            Student.email,
            Student.phone,
            Student.photo_url,
            Class.name,
            Section.name,
            StudentMentor.assigned_date,
            StudentMentor.notes,
            StudentMentor.updated_at,
        )
        .join(StudentMentor, StudentMentor.student_id == Student.id)
        .join(StudentEnrollment, and_(
            StudentEnrollment.student_id == Student.id,
            StudentEnrollment.academic_year_id == current_ay.id,
            StudentEnrollment.is_active.is_(True),
        ))
        .join(ClassSection, StudentEnrollment.class_section_id == ClassSection.id)
        .join(Class, ClassSection.class_id == Class.id)
        .join(Section, ClassSection.section_id == Section.id)
        .where(
            StudentMentor.school_id == school_id,
            StudentMentor.staff_id == staff.id,
            StudentMentor.academic_year_id == current_ay.id,
            StudentMentor.is_active.is_(True),
            Student.is_active.is_(True),
        )
        .order_by(Student.full_name)
    )
    rows = result.all()

    mentees = []
    for row in rows:
        mentees.append({
            "id": row[0],
            "full_name": row[1],
            "roll_number": row[2],
            "email": row[3],
            "phone": row[4],
            "avatar_url": row[5],
            "class_name": row[6],
            "section": row[7],
            "class_section": f"{row[6]}-{row[7]}",
            "assigned_date": row[8],
            "notes": row[9] or "",
            "notes_updated_at": row[10],
        })

    return {"total": len(mentees), "mentees": mentees}


async def list_students(
    db: AsyncSession,
    school_id: UUID,
    user: User,
    pagination: PaginationParams,
    search: str | None = None,
    class_name: str | None = None,
    section: str | None = None,
) -> dict:
    """List students accessible to teacher (mentees + class teacher's students)."""
    staff = await _get_staff_for_user(db, user)
    if not staff:
        raise AccessDenied("No staff record associated with this user")

    current_ay = await _get_current_academic_year(db, school_id)
    if not current_ay:
        return paginate([], 0, pagination)

    # Get mentee student IDs
    mentee_ids = await _get_mentee_ids(db, school_id, staff.id, current_ay.id)

    # Get class section IDs where teacher has ANY assignment (class teacher or subject teacher)
    ct_result = await db.execute(
        select(ClassAssignment.class_section_id).where(
            ClassAssignment.school_id == school_id,
            ClassAssignment.staff_id == staff.id,
            ClassAssignment.academic_year_id == current_ay.id,
            ClassAssignment.is_active.is_(True),
        )
    )
    ct_class_section_ids = list(set(ct_result.scalars().all()))

    # Get student IDs enrolled in those class sections
    ct_student_ids: list[UUID] = []
    if ct_class_section_ids:
        enroll_result = await db.execute(
            select(StudentEnrollment.student_id).where(
                StudentEnrollment.school_id == school_id,
                StudentEnrollment.academic_year_id == current_ay.id,
                StudentEnrollment.class_section_id.in_(ct_class_section_ids),
                StudentEnrollment.is_active.is_(True),
            )
        )
        ct_student_ids = list(enroll_result.scalars().all())

    # Combine (unique)
    all_student_ids = list(set(mentee_ids + ct_student_ids))

    if not all_student_ids:
        return paginate([], 0, pagination)

    # Query students
    query = select(Student).where(
        Student.id.in_(all_student_ids),
        Student.school_id == school_id,
        Student.is_active.is_(True),
    )

    if search:
        search_pattern = f"%{search}%"
        query = query.where(Student.full_name.ilike(search_pattern))

    result = await db.execute(query.order_by(Student.full_name))
    students = result.scalars().all()

    # Build items with class/section info
    items = []
    for student in students:
        cls_name, sec_name = await _get_student_class_info(
            db, student.id, school_id, current_ay.id
        )
        # Apply class/section filter
        if class_name and cls_name != class_name:
            continue
        if section and sec_name != section:
            continue

        class_section = f"{cls_name}-{sec_name}" if cls_name and sec_name else None
        items.append({
            "id": student.id,
            "roll_number": student.admission_number,
            "full_name": student.full_name,
            "email": student.email,
            "class_name": cls_name,
            "section": sec_name,
            "class_section": class_section,
            "avatar_url": student.photo_url,
            "status": student.status,
        })

    total = len(items)
    # Manual pagination on filtered results
    start = pagination.offset
    end = start + pagination.page_size
    page_items = items[start:end]

    return paginate(page_items, total, pagination)


# ---------------------------------------------------------------------------
# Get student detail (with access control)
# ---------------------------------------------------------------------------


async def get_student_detail(
    db: AsyncSession,
    school_id: UUID,
    student_id: UUID,
    user: User,
) -> dict:
    """Get full student profile. Only mentor or class teacher can access."""
    staff = await _get_staff_for_user(db, user)
    if not staff:
        raise AccessDenied("No staff record associated with this user")

    current_ay = await _get_current_academic_year(db, school_id)
    if not current_ay:
        raise NotFound("Academic Year", "current")

    # Check access
    has_access = await _check_access_to_student(
        db, school_id, staff.id, student_id, current_ay.id
    )
    if not has_access:
        raise AccessDenied(
            "Access denied. Student details are only accessible to the student's assigned mentor or class teacher."
        )

    # Get student
    result = await db.execute(
        select(Student).where(
            Student.id == student_id,
            Student.school_id == school_id,
            Student.is_active.is_(True),
        )
    )
    student = result.scalar_one_or_none()
    if not student:
        raise NotFound("Student", str(student_id))

    cls_name, sec_name = await _get_student_class_info(db, student.id, school_id, current_ay.id)
    class_section = f"{cls_name}-{sec_name}" if cls_name and sec_name else None

    # Get parent info
    parent_info = None
    sp_result = await db.execute(
        select(StudentParent).where(
            StudentParent.student_id == student.id,
            StudentParent.school_id == school_id,
            StudentParent.is_active.is_(True),
        )
    )
    parents_links = sp_result.scalars().all()
    father_name = father_phone = father_email = None
    mother_name = mother_phone = mother_email = None
    emergency_contact = None
    relationship = None

    for sp in parents_links:
        p_result = await db.execute(select(Parent).where(Parent.id == sp.parent_id))
        parent = p_result.scalar_one_or_none()
        if parent:
            if parent.relation and parent.relation.lower() == "father":
                father_name = parent.full_name
                father_phone = parent.phone
                father_email = parent.email
            elif parent.relation and parent.relation.lower() == "mother":
                mother_name = parent.full_name
                mother_phone = parent.phone
                mother_email = parent.email
            else:
                father_name = father_name or parent.full_name
                father_phone = father_phone or parent.phone
                father_email = father_email or parent.email
            if parent.is_primary_contact:
                emergency_contact = parent.alternate_phone or parent.phone
                relationship = parent.relation

    if not emergency_contact and father_phone:
        emergency_contact = father_phone
        relationship = "Father"

    parent_info = {
        "father_name": father_name,
        "father_phone": father_phone,
        "father_email": father_email,
        "mother_name": mother_name,
        "mother_phone": mother_phone,
        "mother_email": mother_email,
        "emergency_contact": emergency_contact,
        "relationship": relationship,
    }

    # Get mentor info
    mentor_info = None
    mentor_result = await db.execute(
        select(StudentMentor).where(
            StudentMentor.student_id == student.id,
            StudentMentor.academic_year_id == current_ay.id,
            StudentMentor.school_id == school_id,
            StudentMentor.is_active.is_(True),
        )
    )
    mentor_record = mentor_result.scalar_one_or_none()
    if mentor_record:
        staff_result = await db.execute(select(Staff).where(Staff.id == mentor_record.staff_id))
        mentor_staff = staff_result.scalar_one_or_none()
        if mentor_staff:
            mentor_info = {
                "id": mentor_staff.id,
                "full_name": mentor_staff.full_name,
                "subject": None,
                "qualification": mentor_staff.qualification,
                "email": mentor_staff.email,
                "phone": mentor_staff.phone,
            }

    # Check if teacher is mentor or class teacher (can edit)
    mentor_result = await db.execute(
        select(StudentMentor).where(
            StudentMentor.staff_id == staff.id, StudentMentor.student_id == student_id,
            StudentMentor.academic_year_id == current_ay.id, StudentMentor.is_active.is_(True),
        )
    )
    is_mentor = mentor_result.scalar_one_or_none() is not None

    # Also check if teacher is assigned to this student's class (any assignment)
    is_assigned_class = False
    enr_r = await db.execute(
        select(StudentEnrollment.class_section_id).where(
            StudentEnrollment.student_id == student_id,
            StudentEnrollment.academic_year_id == current_ay.id,
            StudentEnrollment.is_active.is_(True),
        )
    )
    cs_id = enr_r.scalar_one_or_none()
    if cs_id:
        assign_check = await db.execute(
            select(ClassAssignment).where(
                ClassAssignment.school_id == school_id,
                ClassAssignment.staff_id == staff.id,
                ClassAssignment.academic_year_id == current_ay.id,
                ClassAssignment.class_section_id == cs_id,
                ClassAssignment.is_active.is_(True),
            )
        )
        is_assigned_class = assign_check.scalar_one_or_none() is not None

    can_edit = is_mentor or is_assigned_class

    detail = {
        "id": student.id,
        "can_edit": can_edit,
        "roll_number": student.admission_number,
        "full_name": student.full_name,
        "email": student.email,
        "phone": student.phone,
        "class_name": cls_name,
        "section": sec_name,
        "class_section": class_section,
        "date_of_birth": student.date_of_birth,
        "gender": student.gender,
        "admission_date": student.admission_date,
        "student_type": (student.metadata_ or {}).get("student_type"),
        "blood_group": student.blood_group,
        "religion": student.religion,
        "address": student.address_line1,
        "avatar_url": student.photo_url,
        "status": student.status,
        "is_active": student.is_active,
        "quick_stats": {
            "attendance_percentage": None,
            "average_grade": None,
            "assignments_submitted": None,
            "fee_due": None,
        },
        "personal_info": {
            "date_of_birth": student.date_of_birth,
            "admission_date": student.admission_date,
            "address": student.address_line1,
            "nationality": student.nationality,
        },
        "parent_info": parent_info,
        "medical_info": {
            "blood_group": student.blood_group,
            "gender": student.gender,
            "religion": student.religion,
            "medical_conditions": student.medical_conditions or "None",
            "allergies": student.allergies,
        },
        "transport_info": await _get_transport_info(db, school_id, student.id, current_ay),
        "assigned_mentor": mentor_info,
        "academic_summary": {
            "overall_attendance": None,
            "overall_grade": None,
            "assignments_submitted": None,
            "assignments_total": None,
            "class_rank": None,
            "class_strength": None,
        },
        "behavior_conduct": {
            "overall_rating": None,
            "discipline_percentage": None,
            "punctuality_percentage": None,
        },
        "metadata": {},
    }

    # Fetch parent meetings
    from src.models.meeting import ParentMeeting
    meetings_result = await db.execute(
        select(ParentMeeting).where(
            ParentMeeting.student_id == student.id, ParentMeeting.school_id == school_id, ParentMeeting.is_active.is_(True)
        ).order_by(ParentMeeting.meeting_date.desc())
    )
    meetings = meetings_result.scalars().all()
    staff_ids = {m.conducted_by for m in meetings}
    staff_map = {}
    if staff_ids:
        sr = await db.execute(select(Staff).where(Staff.id.in_(staff_ids)))
        staff_map = {s.id: s.full_name for s in sr.scalars().all()}
    detail["parent_meetings"] = [
        {
            "id": m.id,
            "meeting_date": m.meeting_date,
            "date": m.meeting_date,
            "meeting_type": m.meeting_type,
            "conducted_by": staff_map.get(m.conducted_by),
            "discussion_notes": m.discussion_notes,
            "notes": m.discussion_notes,
            "status": m.status,
            "agenda": m.agenda,
            "remarks": m.remarks,
            "follow_up_required": m.follow_up_required,
            "parent_attended": m.parent_attended,
            "next_meeting_date": m.next_meeting_date,
        }
        for m in meetings
    ]

    # Fetch activities and awards
    from src.models.activity import Activity, Award
    activities_result = await db.execute(
        select(Activity).where(
            Activity.student_id == student.id, Activity.school_id == school_id, Activity.is_active.is_(True)
        ).order_by(Activity.start_date.desc())
    )
    detail["extra_curricular"] = [
        {
            "id": a.id,
            "name": a.name,
            "activity_name": a.name,
            "activity_type": a.activity_type,
            "description": a.description,
            "role": a.role,
            "start_date": a.start_date,
            "date": a.start_date,
            "end_date": a.end_date,
            "achievement": a.achievement,
            "since": str(a.start_date.year) if a.start_date else None,
            "status": a.status,
        }
        for a in activities_result.scalars().all()
    ]

    awards_result = await db.execute(
        select(Award).where(
            Award.student_id == student.id, Award.school_id == school_id, Award.is_active.is_(True)
        ).order_by(Award.awarded_date.desc())
    )
    detail["awards"] = [
        {
            "id": a.id,
            "title": a.title,
            "name": a.title,
            "category": a.category,
            "year": str(a.awarded_date.year) if a.awarded_date else None,
            "awarded_date": a.awarded_date,
            "award_date": a.awarded_date,
            "date": a.awarded_date,
            "awarded_by": a.awarded_by,
            "level": a.level,
            "description": a.description,
        }
        for a in awards_result.scalars().all()
    ]

    # Fetch disciplinary records
    from src.models.activity import DisciplinaryRecord
    disc_result = await db.execute(
        select(DisciplinaryRecord).where(
            DisciplinaryRecord.student_id == student.id, DisciplinaryRecord.school_id == school_id, DisciplinaryRecord.is_active.is_(True)
        ).order_by(DisciplinaryRecord.incident_date.desc())
    )
    detail["disciplinary_records"] = [
        {
            "id": d.id,
            "incident_date": d.incident_date,
            "category": d.category,
            "severity": d.severity,
            "description": d.description,
            "action_taken": d.action_taken,
            "status": d.status,
            "parent_notified": d.parent_notified,
        }
        for d in disc_result.scalars().all()
    ]

    return detail


# ---------------------------------------------------------------------------
# Sub-resource stubs (all require access check)
# ---------------------------------------------------------------------------


async def _verify_access(
    db: AsyncSession, school_id: UUID, student_id: UUID, user: User
) -> None:
    """Verify teacher has access to student. Raises AccessDenied if not."""
    staff = await _get_staff_for_user(db, user)
    if not staff:
        raise AccessDenied("No staff record associated with this user")
    current_ay = await _get_current_academic_year(db, school_id)
    if not current_ay:
        raise NotFound("Academic Year", "current")
    has_access = await _check_access_to_student(db, school_id, staff.id, student_id, current_ay.id)
    if not has_access:
        raise AccessDenied(
            "Access denied. Student details are only accessible to the student's assigned mentor or class teacher."
        )
    # Also verify student exists
    result = await db.execute(
        select(Student).where(
            Student.id == student_id, Student.school_id == school_id, Student.is_active.is_(True)
        )
    )
    if not result.scalar_one_or_none():
        raise NotFound("Student", str(student_id))


async def get_exam_results(
    db: AsyncSession, school_id: UUID, student_id: UUID, user: User, academic_year: str | None = None
) -> dict:
    """Get exam results for a student (teacher view)."""
    await _verify_access(db, school_id, student_id, user)
    student_r = await db.execute(select(Student).where(Student.id == student_id))
    student = student_r.scalar_one()
    return {
        "student_id": student.id,
        "student_name": student.full_name,
        "academic_year": academic_year,
        "exams": [],
        "performance_analysis": {
            "subject_wise_marks": [],
            "subject_strengths_radar": [],
            "performance_trend_over_time": [],
        },
    }


async def get_parent_meetings(
    db: AsyncSession, school_id: UUID, student_id: UUID, user: User
) -> dict:
    """Get parent meetings for a student (teacher view)."""
    await _verify_access(db, school_id, student_id, user)
    from src.models.meeting import ParentMeeting

    result = await db.execute(
        select(ParentMeeting)
        .where(ParentMeeting.student_id == student_id, ParentMeeting.school_id == school_id, ParentMeeting.is_active.is_(True))
        .order_by(ParentMeeting.meeting_date.desc())
    )
    meetings = result.scalars().all()

    # Resolve conductor names
    staff_ids = {m.conducted_by for m in meetings}
    staff_map = {}
    if staff_ids:
        from src.models.staff import Staff
        sr = await db.execute(select(Staff).where(Staff.id.in_(staff_ids)))
        staff_map = {s.id: s.full_name for s in sr.scalars().all()}

    results = [
        {
            "id": m.id,
            "meeting_type": m.meeting_type,
            "date": m.meeting_date,
            "conducted_by": staff_map.get(m.conducted_by),
            "attendee": None,
            "notes": m.discussion_notes,
            "attendance_status": m.status,
            "follow_up_required": m.follow_up_required,
            "parent_attended": m.parent_attended,
            "metadata": {
                "agenda": m.agenda,
                "remarks": m.remarks,
                "next_meeting_date": str(m.next_meeting_date) if m.next_meeting_date else None,
            },
        }
        for m in meetings
    ]
    return {"count": len(results), "page": 1, "page_size": len(results) or 10, "total_pages": 1 if results else 0, "results": results}


async def get_activities(
    db: AsyncSession, school_id: UUID, student_id: UUID, user: User
) -> dict:
    """Get activities and awards for a student (teacher view)."""
    await _verify_access(db, school_id, student_id, user)
    from src.models.activity import Activity, Award

    activities_result = await db.execute(
        select(Activity).where(
            Activity.student_id == student_id, Activity.school_id == school_id, Activity.is_active.is_(True)
        ).order_by(Activity.start_date.desc())
    )
    activities = [
        {
            "id": a.id,
            "activity_name": a.name,
            "year_joined": a.start_date.year if a.start_date else None,
            "role": a.role,
            "is_active": a.status == "Active" if a.status else True,
            "metadata": {"description": a.description, "achievement": a.achievement},
        }
        for a in activities_result.scalars().all()
    ]

    awards_result = await db.execute(
        select(Award).where(
            Award.student_id == student_id, Award.school_id == school_id, Award.is_active.is_(True)
        ).order_by(Award.awarded_date.desc())
    )
    awards = [
        {
            "id": a.id,
            "award_name": a.title,
            "category": a.category,
            "year": a.awarded_date.year if a.awarded_date else None,
            "description": a.description,
            "metadata": {"level": a.level, "awarded_by": a.awarded_by},
        }
        for a in awards_result.scalars().all()
    ]

    return {"activities": activities, "awards": awards}


async def get_fee_summary(
    db: AsyncSession, school_id: UUID, student_id: UUID, user: User, academic_year: str | None = None
) -> dict:
    """Get fee summary for a student (teacher view, read-only)."""
    await _verify_access(db, school_id, student_id, user)
    student_r = await db.execute(select(Student).where(Student.id == student_id))
    student = student_r.scalar_one()
    return {
        "student_id": student.id,
        "student_name": student.full_name,
        "academic_year": academic_year,
        "summary": {"total_fee": 0, "total_paid": 0, "total_due": 0, "payment_status": "N/A"},
        "fee_structure": [],
        "recent_payments": [],
    }


async def get_behavior(
    db: AsyncSession, school_id: UUID, student_id: UUID, user: User
) -> dict:
    """Get behavior and conduct for a student (teacher view)."""
    await _verify_access(db, school_id, student_id, user)
    student_r = await db.execute(select(Student).where(Student.id == student_id))
    student = student_r.scalar_one()
    return {
        "student_id": student.id,
        "student_name": student.full_name,
        "behavior_summary": {
            "overall_rating": None,
            "discipline_percentage": None,
            "punctuality_percentage": None,
        },
        "recent_conduct_notes": [],
        "disciplinary_records": [],
        "has_clean_record": True,
        "metadata": {},
    }


async def get_recent_attendance(
    db: AsyncSession, school_id: UUID, student_id: UUID, user: User, limit: int = 10
) -> dict:
    """Get recent attendance records for a student (teacher view)."""
    await _verify_access(db, school_id, student_id, user)
    student_r = await db.execute(select(Student).where(Student.id == student_id))
    student = student_r.scalar_one()
    return {
        "student_id": student.id,
        "student_name": student.full_name,
        "records": [],
    }


async def get_assignments(
    db: AsyncSession, school_id: UUID, student_id: UUID, user: User, academic_year: str | None = None
) -> dict:
    """Get assignment submissions for a student (teacher view)."""
    await _verify_access(db, school_id, student_id, user)
    student_r = await db.execute(select(Student).where(Student.id == student_id))
    student = student_r.scalar_one()
    return {
        "student_id": student.id,
        "student_name": student.full_name,
        "count": 0,
        "page": 1,
        "page_size": 20,
        "total_pages": 0,
        "results": [],
    }


async def update_student_by_mentor(
    db: AsyncSession, school_id: UUID, user: User, student_id: UUID, data: dict
) -> dict:
    """Update a student's details by their mentor."""
    staff = await _get_staff_for_user(db, user)
    if not staff:
        raise AccessDenied("No staff record")

    # Verify this teacher is the student's mentor
    # Verify teacher is mentor or class teacher
    current_ay = await _get_current_academic_year(db, school_id)
    has_access = False
    if current_ay:
        mentor_check = await db.execute(
            select(StudentMentor).where(
                StudentMentor.staff_id == staff.id,
                StudentMentor.student_id == student_id,
                StudentMentor.academic_year_id == current_ay.id,
                StudentMentor.is_active.is_(True),
            )
        )
        if mentor_check.scalar_one_or_none():
            has_access = True
        else:
            # Check any class assignment
            enr_r = await db.execute(
                select(StudentEnrollment.class_section_id).where(
                    StudentEnrollment.student_id == student_id,
                    StudentEnrollment.academic_year_id == current_ay.id,
                    StudentEnrollment.is_active.is_(True),
                )
            )
            cs_id = enr_r.scalar_one_or_none()
            if cs_id:
                assign_r = await db.execute(
                    select(ClassAssignment).where(
                        ClassAssignment.school_id == school_id,
                        ClassAssignment.staff_id == staff.id,
                        ClassAssignment.academic_year_id == current_ay.id,
                        ClassAssignment.class_section_id == cs_id,
                        ClassAssignment.is_active.is_(True),
                    )
                )
                has_access = assign_r.scalar_one_or_none() is not None
    if not has_access:
        raise AccessDenied("You don't have permission to edit this student")

    # Get student
    result = await db.execute(
        select(Student).where(Student.id == student_id, Student.school_id == school_id, Student.is_active.is_(True))
    )
    student = result.scalar_one_or_none()
    if not student:
        raise AccessDenied("Student not found")

    # Update allowed fields
    field_map = {
        "full_name": "full_name", "phone": "phone", "email": "email", "address": "address_line1",
        "date_of_birth": "date_of_birth", "admission_date": "admission_date", "gender": "gender",
        "blood_group": "blood_group", "religion": "religion", "medical_conditions": "medical_conditions",
    }
    for req_field, model_field in field_map.items():
        if req_field in data and data[req_field] is not None and data[req_field] != '':
            setattr(student, model_field, data[req_field])

    # Update student_type in metadata
    if "student_type" in data:
        from sqlalchemy.orm.attributes import flag_modified
        meta = dict(student.metadata_ or {})
        meta["student_type"] = data["student_type"]
        student.metadata_ = meta
        flag_modified(student, "metadata_")

    # Update parent info
    from src.models.student import StudentParent, Parent
    parent_fields = ["parent_name", "parent_phone", "parent_email", "parent_emergency", "parent_relationship"]
    if any(f in data and data[f] for f in parent_fields):
        sp_r = await db.execute(
            select(StudentParent).where(StudentParent.student_id == student_id, StudentParent.is_active.is_(True))
        )
        sp = sp_r.scalar_one_or_none()
        parent = None
        if sp:
            p_r = await db.execute(select(Parent).where(Parent.id == sp.parent_id))
            parent = p_r.scalar_one_or_none()

        if not parent:
            # Create a new parent record if none exists
            name = data.get("parent_name", "Parent")
            parts = name.split(" ", 1)
            parent = Parent(
                school_id=school_id,
                first_name=parts[0],
                last_name=parts[1] if len(parts) > 1 else None,
                full_name=name,
                phone=data.get("parent_phone"),
                email=data.get("parent_email"),
                relation=data.get("parent_relationship", "Parent/Guardian"),
                alternate_phone=data.get("parent_emergency"),
                created_by=user.id,
            )
            db.add(parent)
            await db.flush()
            # Link parent to student
            if not sp:
                sp = StudentParent(
                    school_id=school_id,
                    student_id=student_id,
                    parent_id=parent.id,
                    relationship=data.get("parent_relationship", "Parent/Guardian"),
                    created_by=user.id,
                )
                db.add(sp)
        else:
            if "parent_name" in data and data["parent_name"]:
                parent.full_name = data["parent_name"]
                parts = data["parent_name"].split(" ", 1)
                parent.first_name = parts[0]
                parent.last_name = parts[1] if len(parts) > 1 else None
            if "parent_phone" in data and data["parent_phone"]:
                parent.phone = data["parent_phone"]
            if "parent_email" in data:
                parent.email = data["parent_email"] or None
            if "parent_emergency" in data and data["parent_emergency"]:
                parent.alternate_phone = data["parent_emergency"]
            if "parent_relationship" in data and data["parent_relationship"]:
                parent.relation = data["parent_relationship"]

    await db.commit()
    return {"message": "Student updated successfully"}


# ---------------------------------------------------------------------------
# Mentor Notes
# ---------------------------------------------------------------------------


async def get_mentor_notes(
    db: AsyncSession, school_id: UUID, user: User, student_id: UUID
) -> dict:
    """Get the mentor's notes for a student."""
    staff = await _get_staff_for_user(db, user)
    if not staff:
        raise AccessDenied("No staff record associated with this user")
    current_ay = await _get_current_academic_year(db, school_id)
    if not current_ay:
        return {"student_id": student_id, "notes": "", "updated_at": None}

    result = await db.execute(
        select(StudentMentor).where(
            StudentMentor.staff_id == staff.id,
            StudentMentor.student_id == student_id,
            StudentMentor.academic_year_id == current_ay.id,
            StudentMentor.school_id == school_id,
            StudentMentor.is_active.is_(True),
        )
    )
    mentor_record = result.scalar_one_or_none()
    if not mentor_record:
        raise AccessDenied("You are not the mentor of this student")

    return {
        "student_id": student_id,
        "notes": mentor_record.notes or "",
        "updated_at": mentor_record.updated_at,
    }


async def update_mentor_notes(
    db: AsyncSession, school_id: UUID, user: User, student_id: UUID, notes: str
) -> dict:
    """Update the mentor's notes for a student."""
    staff = await _get_staff_for_user(db, user)
    if not staff:
        raise AccessDenied("No staff record associated with this user")
    current_ay = await _get_current_academic_year(db, school_id)
    if not current_ay:
        raise NotFound("Academic Year", "current")

    result = await db.execute(
        select(StudentMentor).where(
            StudentMentor.staff_id == staff.id,
            StudentMentor.student_id == student_id,
            StudentMentor.academic_year_id == current_ay.id,
            StudentMentor.school_id == school_id,
            StudentMentor.is_active.is_(True),
        )
    )
    mentor_record = result.scalar_one_or_none()
    if not mentor_record:
        raise AccessDenied("You are not the mentor of this student")

    mentor_record.notes = notes
    mentor_record.updated_by = user.id
    await db.commit()
    await db.refresh(mentor_record)

    return {
        "student_id": student_id,
        "notes": mentor_record.notes or "",
        "updated_at": mentor_record.updated_at,
        "message": "Notes updated successfully",
    }
