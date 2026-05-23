from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFound
from src.models.academic import Class, ClassSection, Section
from src.models.core import AcademicYear, User
from src.models.staff import Staff
from src.models.student import Parent, Student, StudentEnrollment, StudentMentor, StudentParent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_student_for_user(db: AsyncSession, user: User) -> Student:
    """Get the student record linked to the current user."""
    if not user.student_id:
        raise NotFound("Student", "linked to user")
    result = await db.execute(
        select(Student).where(Student.id == user.student_id, Student.is_active.is_(True))
    )
    student = result.scalar_one_or_none()
    if not student:
        raise NotFound("Student", str(user.student_id))
    return student


def _get_initials(full_name: str) -> str:
    """Get initials from full name."""
    parts = full_name.split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[-1][0]}".upper()
    return parts[0][0].upper() if parts else ""


# ---------------------------------------------------------------------------
# Get profile
# ---------------------------------------------------------------------------


async def get_profile(db: AsyncSession, school_id: UUID, user: User) -> dict:
    """Get the student's own full profile."""
    student = await _get_student_for_user(db, user)

    # Get current academic year
    ay_result = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
        )
    )
    current_ay = ay_result.scalar_one_or_none()

    # Get enrollment for class/section info
    class_name = None
    section_name = None
    if current_ay:
        enrollment_result = await db.execute(
            select(StudentEnrollment).where(
                StudentEnrollment.student_id == student.id,
                StudentEnrollment.academic_year_id == current_ay.id,
                StudentEnrollment.school_id == school_id,
                StudentEnrollment.is_active.is_(True),
            )
        )
        enrollment = enrollment_result.scalar_one_or_none()
        if enrollment:
            cs_result = await db.execute(
                select(ClassSection).where(ClassSection.id == enrollment.class_section_id)
            )
            cs = cs_result.scalar_one_or_none()
            if cs:
                cls_r = await db.execute(select(Class).where(Class.id == cs.class_id))
                sec_r = await db.execute(select(Section).where(Section.id == cs.section_id))
                cls = cls_r.scalar_one_or_none()
                sec = sec_r.scalar_one_or_none()
                if cls:
                    class_name = cls.name
                if sec:
                    section_name = sec.name

    class_section = f"{class_name}-{section_name}" if class_name and section_name else None

    # Get parent info
    parent_section = None
    sp_result = await db.execute(
        select(StudentParent).where(
            StudentParent.student_id == student.id,
            StudentParent.school_id == school_id,
            StudentParent.is_active.is_(True),
        )
    )
    sp = sp_result.scalars().first()
    if sp:
        p_result = await db.execute(select(Parent).where(Parent.id == sp.parent_id))
        parent = p_result.scalar_one_or_none()
        if parent:
            parent_section = {
                "parent_name": parent.full_name,
                "relationship": parent.relation,
                "phone": parent.phone,
                "email": parent.email,
                "occupation": parent.occupation,
                "emergency_contact": parent.alternate_phone or parent.phone,
                "address": {
                    "street": parent.address_line1,
                    "city": parent.city,
                    "state": parent.state,
                    "pincode": parent.pincode,
                    "country": "India",
                },
            }

    # Get mentor info
    mentor_section = None
    if current_ay:
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
            staff_result = await db.execute(
                select(Staff).where(Staff.id == mentor_record.staff_id)
            )
            mentor_staff = staff_result.scalar_one_or_none()
            if mentor_staff:
                mentor_section = {
                    "teacher_id": mentor_staff.id,
                    "name": mentor_staff.full_name,
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
        "class_name": class_name,
        "section": section_name,
        "class_section": class_section,
        "academic_year": current_ay.name if current_ay else None,
        "student_type": None,
        "avatar_url": student.photo_url,
        "avatar_initials": _get_initials(student.full_name),
        "quick_stats": {
            "attendance_percentage": None,
            "avg_grade": None,
            "pending_assignments": None,
            "fee_due": None,
        },
        "personal": {
            "date_of_birth": student.date_of_birth,
            "gender": student.gender,
            "admission_date": student.admission_date,
            "blood_group": student.blood_group,
            "religion": student.religion,
            "nationality": student.nationality,
            "student_type": None,
            "address": {
                "street": student.address_line1,
                "city": student.city,
                "state": student.state,
                "pincode": student.pincode,
                "country": "India",
            },
            "phone": student.phone,
            "alternate_phone": None,
        },
        "parent": parent_section,
        "medical": {
            "blood_group": student.blood_group,
            "gender": student.gender,
            "religion": student.religion,
            "conditions": student.medical_conditions or "None reported",
            "allergies": student.allergies or "None reported",
            "medications": None,
            "doctor_name": None,
            "doctor_phone": None,
            "insurance_id": None,
        },
        "transport": {
            "enrolled": False,
            "route_name": None,
            "bus_number": None,
            "pickup_point": None,
            "pickup_time": None,
            "drop_time": None,
            "driver_name": None,
            "driver_phone": None,
        },
        "mentor": mentor_section,
        "recent_attendance": [],
        "created_at": student.created_at,
        "updated_at": student.updated_at,
        "metadata": {},
    }


# ---------------------------------------------------------------------------
# Update profile (limited fields)
# ---------------------------------------------------------------------------


async def update_profile(db: AsyncSession, school_id: UUID, user: User, data: dict) -> dict:
    """Update editable profile fields (phone, address, emergency_contact)."""
    student = await _get_student_for_user(db, user)

    updated_fields: list[str] = []

    if "phone" in data and data["phone"] is not None:
        student.phone = data["phone"]
        updated_fields.append("phone")

    if "alternate_phone" in data and data["alternate_phone"] is not None:
        updated_fields.append("alternate_phone")

    if "address" in data and data["address"] is not None:
        addr = data["address"]
        if isinstance(addr, dict):
            if addr.get("street"):
                student.address_line1 = addr["street"]
            if addr.get("city"):
                student.city = addr["city"]
            if addr.get("state"):
                student.state = addr["state"]
            if addr.get("pincode"):
                student.pincode = addr["pincode"]
            updated_fields.append("address")

    if "emergency_contact" in data and data["emergency_contact"] is not None:
        # Update primary parent's phone as emergency contact
        sp_result = await db.execute(
            select(StudentParent).where(
                StudentParent.student_id == student.id,
                StudentParent.school_id == school_id,
                StudentParent.is_active.is_(True),
            )
        )
        sp = sp_result.scalars().first()
        if sp:
            p_result = await db.execute(select(Parent).where(Parent.id == sp.parent_id))
            parent = p_result.scalar_one_or_none()
            if parent:
                parent.alternate_phone = data["emergency_contact"]
        updated_fields.append("emergency_contact")

    student.updated_by = user.id
    await db.commit()

    return {
        "message": "Profile updated successfully",
        "updated_fields": updated_fields,
        "updated_at": datetime.utcnow(),
        "metadata": {},
    }


# ---------------------------------------------------------------------------
# Get mentor details
# ---------------------------------------------------------------------------


async def get_mentor(db: AsyncSession, school_id: UUID, user: User) -> dict:
    """Get assigned mentor details."""
    student = await _get_student_for_user(db, user)

    # Get current academic year
    ay_result = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
        )
    )
    current_ay = ay_result.scalar_one_or_none()
    if not current_ay:
        raise NotFound("Mentor", "No current academic year")

    mentor_result = await db.execute(
        select(StudentMentor).where(
            StudentMentor.student_id == student.id,
            StudentMentor.academic_year_id == current_ay.id,
            StudentMentor.school_id == school_id,
            StudentMentor.is_active.is_(True),
        )
    )
    mentor_record = mentor_result.scalar_one_or_none()
    if not mentor_record:
        raise NotFound("Mentor", "not assigned")

    staff_result = await db.execute(select(Staff).where(Staff.id == mentor_record.staff_id))
    mentor_staff = staff_result.scalar_one_or_none()
    if not mentor_staff:
        raise NotFound("Mentor", "staff record")

    # Count total mentees
    mentee_count_result = await db.execute(
        select(func.count()).select_from(StudentMentor).where(
            StudentMentor.staff_id == mentor_staff.id,
            StudentMentor.academic_year_id == current_ay.id,
            StudentMentor.school_id == school_id,
            StudentMentor.is_active.is_(True),
        )
    )
    total_mentees = mentee_count_result.scalar() or 0

    return {
        "teacher_id": mentor_staff.id,
        "name": mentor_staff.full_name,
        "subject": None,
        "qualification": mentor_staff.qualification,
        "email": mentor_staff.email,
        "phone": mentor_staff.phone,
        "avatar_url": mentor_staff.photo_url,
        "avatar_initials": _get_initials(mentor_staff.full_name),
        "designation": mentor_staff.designation,
        "experience_years": float(mentor_staff.experience_years) if mentor_staff.experience_years else None,
        "assigned_since": mentor_record.assigned_date,
        "total_mentees": total_mentees,
        "available_hours": None,
        "metadata": {},
    }
