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
    result = await db.execute(select(Staff).where(Staff.id == user.staff_id))
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

    # Get class section IDs where teacher is class teacher
    ct_result = await db.execute(
        select(ClassAssignment.class_section_id).where(
            ClassAssignment.school_id == school_id,
            ClassAssignment.staff_id == staff.id,
            ClassAssignment.academic_year_id == current_ay.id,
            ClassAssignment.is_class_teacher.is_(True),
            ClassAssignment.is_active.is_(True),
        )
    )
    ct_class_section_ids = list(ct_result.scalars().all())

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
                emergency_contact = parent.phone
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

    return {
        "id": student.id,
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
        "student_type": None,
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
        "transport_info": {
            "transport_service": None,
            "route": None,
            "bus_number": None,
            "pickup_point": None,
        },
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
    return {"count": 0, "page": 1, "page_size": 10, "total_pages": 0, "results": []}


async def get_activities(
    db: AsyncSession, school_id: UUID, student_id: UUID, user: User
) -> dict:
    """Get activities and awards for a student (teacher view)."""
    await _verify_access(db, school_id, student_id, user)
    return {"activities": [], "awards": []}


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
