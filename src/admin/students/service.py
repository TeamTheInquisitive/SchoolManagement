from __future__ import annotations

import csv
import io
from datetime import date
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.admin.students.exceptions import DuplicateRollNumber, StudentNotFound
from src.core.pagination import PaginationParams, paginate
from src.core.security import hash_password
from src.models.academic import Class, ClassSection, Section
from src.models.core import AcademicYear, User
from src.models.staff import Staff
from src.models.student import Parent, Student, StudentEnrollment, StudentMentor, StudentParent
from src.models.attendance import AttendanceRecord, AttendanceSession
from src.models.examination import Exam, ExamResult
from src.models.fee import FeeRecord, FeeStructure


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _resolve_staff_id(db: AsyncSession, user_id: UUID, school_id: UUID) -> UUID:
    """Resolve staff.id from a user_id. Tries user_id link first, then email fallback."""
    staff_result = await db.execute(select(Staff).where(Staff.user_id == user_id, Staff.school_id == school_id))
    staff = staff_result.scalar_one_or_none()
    if staff:
        return staff.id
    # Fallback: match by email
    from src.models.core import User as UserModel
    user_result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user_obj = user_result.scalar_one_or_none()
    if user_obj:
        staff_result = await db.execute(
            select(Staff).where(Staff.email == user_obj.email, Staff.school_id == school_id, Staff.is_active.is_(True))
        )
        staff = staff_result.scalar_one_or_none()
        if staff:
            staff.user_id = user_id
            return staff.id
    raise HTTPException(status_code=400, detail="No staff record found for this user")


# ---------------------------------------------------------------------------
# List students
# ---------------------------------------------------------------------------


async def list_students(
    db: AsyncSession,
    school_id: UUID,
    pagination: PaginationParams,
    search: str | None = None,
    class_name: str | None = None,
    section: str | None = None,
    status: str | None = None,
    gender: str | None = None,
) -> dict:
    """List students with filters and pagination."""
    # Base query
    query = select(Student).where(
        Student.school_id == school_id,
        Student.is_active.is_(True),
    )

    if status:
        query = query.where(Student.status == status)

    if gender:
        query = query.where(Student.gender == gender)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Student.full_name.ilike(search_pattern),
                Student.admission_number.ilike(search_pattern),
                Student.email.ilike(search_pattern),
            )
        )

    # Count query
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Apply pagination
    query = query.offset(pagination.offset).limit(pagination.page_size).order_by(Student.full_name)
    result = await db.execute(query)
    students = result.scalars().all()

    # Get current academic year for enrollment info
    ay_result = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
        )
    )
    current_ay = ay_result.scalar_one_or_none()

    items = []
    for student in students:
        class_name_val = None
        section_val = None

        if current_ay:
            enrollment_result = await db.execute(
                select(StudentEnrollment)
                .options(selectinload(StudentEnrollment.class_section))
                .where(
                    StudentEnrollment.student_id == student.id,
                    StudentEnrollment.academic_year_id == current_ay.id,
                    StudentEnrollment.is_active.is_(True),
                )
            )
            enrollment = enrollment_result.scalar_one_or_none()
            if enrollment and enrollment.class_section:
                cs = enrollment.class_section
                # Get class and section names
                cls_result = await db.execute(select(Class).where(Class.id == cs.class_id))
                cls = cls_result.scalar_one_or_none()
                sec_result = await db.execute(select(Section).where(Section.id == cs.section_id))
                sec = sec_result.scalar_one_or_none()
                if cls:
                    class_name_val = cls.name
                if sec:
                    section_val = sec.name

        # Apply class/section filters
        if class_name and class_name_val != class_name:
            continue
        if section and section_val != section:
            continue

        items.append({
            "id": student.id,
            "roll_number": student.admission_number,
            "full_name": student.full_name,
            "email": student.email,
            "phone": student.phone,
            "class_name": class_name_val,
            "section": section_val,
            "status": student.status,
            "gender": student.gender,
            "date_of_birth": student.date_of_birth,
            "admission_date": student.admission_date,
            "blood_group": student.blood_group,
            "religion": student.religion,
            "address": student.address_line1,
            "student_type": (student.metadata_ or {}).get("student_type"),
            "previous_school": (student.metadata_ or {}).get("previous_school"),
            "token_advance": (student.metadata_ or {}).get("token_advance"),
            "token_payment_method": (student.metadata_ or {}).get("token_payment_method"),
            "password_changed": False,
        })

    # Lookup password_changed for all students in the list
    student_ids = [i["id"] for i in items]
    if student_ids:
        user_result = await db.execute(
            select(User.student_id, User.password_changed).where(
                User.school_id == school_id, User.student_id.in_(student_ids)
            )
        )
        pw_changed_map = {row.student_id: row.password_changed for row in user_result}

        # Lookup parent info
        sp_result = await db.execute(
            select(StudentParent.student_id, Parent.full_name, Parent.phone, Parent.email, Parent.relation)
            .join(Parent, Parent.id == StudentParent.parent_id)
            .where(StudentParent.student_id.in_(student_ids), StudentParent.is_active.is_(True))
        )
        parent_map = {row.student_id: {"parent_name": row.full_name, "parent_phone": row.phone, "parent_email": row.email, "parent_relationship": row.relation} for row in sp_result}

        for item in items:
            item["password_changed"] = pw_changed_map.get(item["id"], False)
            item.update(parent_map.get(item["id"], {}))

    # Compute summary scoped to current academic year
    total_all_result = await db.execute(
        select(func.count()).where(Student.school_id == school_id, Student.is_active.is_(True))
    )
    total_all = total_all_result.scalar() or 0

    # Active = enrolled in current academic year with Active status
    if current_ay:
        active_result = await db.execute(
            select(func.count(func.distinct(StudentEnrollment.student_id)))
            .join(Student, Student.id == StudentEnrollment.student_id)
            .where(
                StudentEnrollment.school_id == school_id,
                StudentEnrollment.academic_year_id == current_ay.id,
                StudentEnrollment.is_active.is_(True),
                StudentEnrollment.status == "Active",
                Student.is_active.is_(True),
                Student.status == "Active",
            )
        )
        active_count = active_result.scalar() or 0
    else:
        active_result = await db.execute(
            select(func.count()).where(Student.school_id == school_id, Student.is_active.is_(True), Student.status == "Active")
        )
        active_count = active_result.scalar() or 0

    inactive_count = total_all - active_count

    paginated = paginate(items, total, pagination)
    paginated["summary"] = {
        "total": total_all,
        "active": active_count,
        "inactive": inactive_count,
    }
    return paginated


# ---------------------------------------------------------------------------
# Create student
# ---------------------------------------------------------------------------


async def create_student(
    db: AsyncSession,
    school_id: UUID,
    data: dict,
    created_by: UUID,
) -> dict:
    """Create a new student with optional user account and enrollment."""
    roll_number = data["roll_number"]

    # Check duplicate
    existing = await db.execute(
        select(Student).where(
            Student.school_id == school_id,
            Student.admission_number == roll_number,
        )
    )
    if existing.scalar_one_or_none():
        raise DuplicateRollNumber(roll_number)

    # Parse full name
    name_parts = data["full_name"].split(" ", 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else None

    # Create student
    student = Student(
        school_id=school_id,
        admission_number=roll_number,
        first_name=first_name,
        last_name=last_name,
        full_name=data["full_name"],
        email=data.get("email"),
        phone=data.get("phone"),
        gender=data.get("gender"),
        date_of_birth=data.get("date_of_birth"),
        admission_date=data.get("admission_date"),
        blood_group=data.get("blood_group"),
        religion=data.get("religion"),
        address_line1=data.get("address"),
        address_line2=data.get("address_line2"),
        city=data.get("city"),
        state=data.get("state"),
        pincode=data.get("pincode"),
        metadata_={k: v for k, v in {
            "student_type": data.get("student_type"),
            "previous_school": data.get("previous_school"),
            "token_advance": data.get("token_advance"),
            "token_payment_method": data.get("token_payment_method"),
            "parent_occupation": data.get("parent_occupation"),
        }.items() if v} or {},
        status=data.get("status", "Active"),
        created_by=created_by,
    )
    db.add(student)
    await db.flush()

    # Create user account if not already exists (rollnumber as username)
    from src.models.core import School
    school_result = await db.execute(select(School).where(School.id == school_id))
    school_obj = school_result.scalar_one()
    user_email = data.get("email") or f"{roll_number}@{school_obj.code}.com"
    user_password = roll_number
    existing_user = await db.execute(
        select(User).where(User.school_id == school_id, User.email == user_email)
    )
    if not existing_user.scalar_one_or_none():
        user = User(
            school_id=school_id,
            email=user_email,
            password_hash=hash_password(user_password),
            full_name=data["full_name"],
            role="student",
            student_id=student.id,
            created_by=created_by,
        )
        db.add(user)

    # Create enrollment if class/section provided
    class_name = data.get("class_name")
    section_name = data.get("section")
    class_name_val = None
    section_val = None

    if class_name and section_name:
        # Find class and section
        cls_result = await db.execute(
            select(Class).where(Class.school_id == school_id, Class.name == class_name)
        )
        cls = cls_result.scalar_one_or_none()
        sec_result = await db.execute(
            select(Section).where(Section.school_id == school_id, Section.name == section_name)
        )
        sec = sec_result.scalar_one_or_none()

        if cls and sec:
            class_name_val = cls.name
            section_val = sec.name
            # Find class_section
            cs_result = await db.execute(
                select(ClassSection).where(
                    ClassSection.school_id == school_id,
                    ClassSection.class_id == cls.id,
                    ClassSection.section_id == sec.id,
                )
            )
            cs = cs_result.scalar_one_or_none()

            if cs:
                # Get current academic year
                ay_result = await db.execute(
                    select(AcademicYear).where(
                        AcademicYear.school_id == school_id,
                        AcademicYear.is_current.is_(True),
                    )
                )
                ay = ay_result.scalar_one_or_none()
                if ay:
                    enrollment = StudentEnrollment(
                        school_id=school_id,
                        academic_year_id=ay.id,
                        student_id=student.id,
                        class_section_id=cs.id,
                        roll_number=roll_number,
                        enrollment_date=data.get("admission_date") or date.today(),
                        status="Active",
                        created_by=created_by,
                    )
                    db.add(enrollment)

    # Create parent if provided
    if data.get("parent_name"):
        parent_name_parts = data["parent_name"].split(" ", 1)
        parent = Parent(
            school_id=school_id,
            first_name=parent_name_parts[0],
            last_name=parent_name_parts[1] if len(parent_name_parts) > 1 else None,
            full_name=data["parent_name"],
            relation=data.get("parent_relationship", "Parent/Guardian"),
            phone=data.get("parent_phone"),
            email=data.get("parent_email"),
            is_primary_contact=True,
            created_by=created_by,
        )
        db.add(parent)
        await db.flush()

        # Link parent to student
        student_parent = StudentParent(
            school_id=school_id,
            student_id=student.id,
            parent_id=parent.id,
            created_by=created_by,
        )
        db.add(student_parent)

    # Auto-generate fee records based on class fee structure
    ay_result2 = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
        )
    )
    current_ay2 = ay_result2.scalar_one_or_none()
    if current_ay2 and class_name and section_name:
        # Find class_section_id for fee structure lookup
        cs_for_fee = None
        cls_r = await db.execute(select(Class).where(Class.school_id == school_id, Class.name == class_name))
        cls_obj = cls_r.scalar_one_or_none()
        sec_r = await db.execute(select(Section).where(Section.school_id == school_id, Section.name == section_name))
        sec_obj = sec_r.scalar_one_or_none()
        if cls_obj and sec_obj:
            cs_r = await db.execute(
                select(ClassSection).where(ClassSection.school_id == school_id, ClassSection.class_id == cls_obj.id, ClassSection.section_id == sec_obj.id)
            )
            cs_for_fee = cs_r.scalar_one_or_none()

        from datetime import timedelta

        concessions = data.get("concessions") or {}

        if cs_for_fee:
            # Fetch class-specific fees AND general fees (no class_id)
            fee_structures = await db.execute(
                select(FeeStructure).where(
                    FeeStructure.school_id == school_id,
                    FeeStructure.academic_year_id == current_ay2.id,
                    FeeStructure.is_active.is_(True),
                    or_(
                        FeeStructure.class_section_id == cs_for_fee.id,
                        FeeStructure.class_id == cls_obj.id,
                        and_(FeeStructure.class_id.is_(None), FeeStructure.class_section_id.is_(None)),
                    ),
                )
            )
            for fs in fee_structures.scalars().all():
                # Skip excluded fees
                excluded_ids = data.get("excluded_fee_ids") or []
                if str(fs.id) in excluded_ids:
                    continue
                due = date.today() + timedelta(days=30)
                concession_amount = max(0, float(concessions.get(str(fs.id), 0)))
                total = float(fs.amount)
                if concession_amount > total:
                    concession_amount = total
                net_amount = max(0, total - concession_amount)
                fee_record = FeeRecord(
                    school_id=school_id,
                    academic_year_id=current_ay2.id,
                    student_id=student.id,
                    fee_structure_id=fs.id,
                    fee_type=fs.fee_type,
                    fee_category=fs.fee_category,
                    total_amount=net_amount,
                    concession_amount=concession_amount,
                    paid=0,
                    pending=net_amount,
                    due_date=due,
                    status="Pending",
                    is_active=True,
                    description=f"Auto-generated ({fs.frequency}){f' | Concession: ₹{concession_amount:.0f}' if concession_amount > 0 else ''}",
                    created_by=created_by,
                )
                db.add(fee_record)

        # Create custom fee records (outside cs_for_fee - always create)
        custom_fees = data.get("custom_fees") or []
        for cf in custom_fees:
            due = date.today() + timedelta(days=30)
            amount = float(cf.get("amount", 0))
            if amount > 0:
                fee_record = FeeRecord(
                    school_id=school_id,
                    academic_year_id=current_ay2.id,
                    student_id=student.id,
                    fee_type=cf.get("fee_type", "Custom Fee"),
                    fee_category=cf.get("fee_category", "other"),
                    total_amount=amount,
                    concession_amount=0,
                    paid=0,
                    pending=amount,
                    due_date=due,
                    status="Pending",
                    is_active=True,
                    description="Custom fee component (student-specific)",
                    created_by=created_by,
                )
                db.add(fee_record)

    await db.commit()
    await db.refresh(student)

    return {
        "id": student.id,
        "roll_number": student.admission_number,
        "full_name": student.full_name,
        "email": student.email,
        "phone": student.phone,
        "class_name": class_name_val or class_name,
        "section": section_val or section_name,
        "status": student.status,
        "date_of_birth": student.date_of_birth,
        "admission_date": student.admission_date,
        "gender": student.gender,
        "address": student.address_line1,
        "city": student.city,
        "state": student.state,
        "pincode": student.pincode,
        "parent_name": data.get("parent_name"),
        "parent_phone": data.get("parent_phone"),
        "parent_email": data.get("parent_email"),
        "created_at": student.created_at,
    }


# ---------------------------------------------------------------------------
# Student stats helper
# ---------------------------------------------------------------------------


async def _compute_student_stats(
    db: AsyncSession, student_id: UUID, school_id: UUID, current_ay
) -> dict:
    """Compute attendance, grade, and fee stats for a student."""
    stats = {
        "attendance_percentage": None,
        "average_grade": None,
        "assignments_submitted": None,
        "assignments_total": None,
        "fee_due": None,
        "class_rank": None,
        "class_strength": None,
    }
    if not current_ay:
        return stats

    # Attendance: (present + late) / total * 100
    from sqlalchemy import case
    att_result = await db.execute(
        select(
            func.count().label("total"),
            func.sum(case((AttendanceRecord.status.in_(["Present", "Late"]), 1), else_=0)).label("attended"),
        )
        .select_from(AttendanceRecord)
        .join(AttendanceSession, AttendanceRecord.attendance_session_id == AttendanceSession.id)
        .where(
            AttendanceRecord.student_id == student_id,
            AttendanceSession.academic_year_id == current_ay.id,
            AttendanceSession.school_id == school_id,
        )
    )
    row = att_result.one()
    if row.total > 0:
        stats["attendance_percentage"] = round(row.attended / row.total * 100, 1)

    # Average grade: AVG(marks_obtained / exam.total_marks * 100)
    grade_result = await db.execute(
        select(
            func.avg(ExamResult.marks_obtained / Exam.total_marks * 100)
        )
        .select_from(ExamResult)
        .join(Exam, ExamResult.exam_id == Exam.id)
        .where(
            ExamResult.student_id == student_id,
            Exam.academic_year_id == current_ay.id,
            Exam.school_id == school_id,
            ExamResult.marks_obtained.is_not(None),
        )
    )
    avg_grade = grade_result.scalar()
    if avg_grade is not None:
        stats["average_grade"] = round(float(avg_grade), 1)

    # Fee due: sum of pending for current academic year
    fee_result = await db.execute(
        select(func.coalesce(func.sum(FeeRecord.pending), 0)).where(
            FeeRecord.student_id == student_id,
            FeeRecord.academic_year_id == current_ay.id,
            FeeRecord.school_id == school_id,
            FeeRecord.status == "Pending",
        )
    )
    stats["fee_due"] = float(fee_result.scalar())

    return stats


# ---------------------------------------------------------------------------
# Get student detail
# ---------------------------------------------------------------------------


async def get_student(db: AsyncSession, school_id: UUID, student_id: UUID) -> dict:
    """Get full student details."""
    result = await db.execute(
        select(Student).where(
            Student.id == student_id,
            Student.school_id == school_id,
            Student.is_active.is_(True),
        )
    )
    student = result.scalar_one_or_none()
    if not student:
        raise StudentNotFound(str(student_id))

    # Get enrollment info
    ay_result = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
            AcademicYear.is_active.is_(True),
        )
    )
    current_ay = ay_result.scalar_one_or_none()

    class_name_val = None
    section_val = None
    if current_ay:
        enrollment_result = await db.execute(
            select(StudentEnrollment).where(
                StudentEnrollment.student_id == student.id,
                StudentEnrollment.academic_year_id == current_ay.id,
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
                    class_name_val = cls.name
                if sec:
                    section_val = sec.name

    # Get parent info
    parent_info = None
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
            parent_info = {
                "name": parent.full_name,
                "phone": parent.phone,
                "email": parent.email,
                "emergency_contact": parent.alternate_phone or parent.phone,
                "relationship": parent.relation,
            }

    # Get mentor info
    mentor_info = None
    class_teacher_info = None
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
            staff = staff_result.scalar_one_or_none()
            if staff:
                mentor_info = {
                    "id": staff.id,
                    "name": staff.full_name,
                    "subject": None,
                    "qualification": staff.qualification,
                    "email": staff.email,
                    "phone": staff.phone,
                }

        # Get class teacher for this student's class-section
        from src.models.staff import ClassAssignment
        enrollments = student.enrollments or []
        active_enrollment = next((e for e in enrollments if e.academic_year_id == current_ay.id and e.is_active), None)
        if active_enrollment:
            ct_result = await db.execute(
                select(Staff).join(ClassAssignment, ClassAssignment.staff_id == Staff.id).where(
                    ClassAssignment.class_section_id == active_enrollment.class_section_id,
                    ClassAssignment.is_class_teacher.is_(True),
                    ClassAssignment.is_active.is_(True),
                    ClassAssignment.school_id == school_id,
                )
            )
            ct_staff = ct_result.scalar_one_or_none()
            if ct_staff:
                class_teacher_info = {
                    "name": ct_staff.full_name,
                    "email": ct_staff.email,
                    "phone": ct_staff.phone,
                }

    # Get transport info
    transport_info = {"enrolled": False}
    from src.models.transport import StudentTransport as ST2, Route as Route2, Vehicle as Vehicle2, RouteAssignment as RA2
    if current_ay:
        st_result = await db.execute(
            select(ST2).where(
                ST2.student_id == student.id, ST2.school_id == school_id,
                ST2.academic_year_id == current_ay.id, ST2.is_active.is_(True),
            )
        )
        st_record = st_result.scalar_one_or_none()
        if st_record:
            route_r = await db.execute(select(Route2).where(Route2.id == st_record.route_id, Route2.is_active.is_(True)))
            route_obj = route_r.scalar_one_or_none()
            bus_number = None
            ra_r = await db.execute(select(RA2.vehicle_id).where(RA2.route_id == st_record.route_id, RA2.is_active.is_(True)))
            vid = ra_r.scalar_one_or_none()
            if vid:
                v_r = await db.execute(select(Vehicle2.vehicle_number).where(Vehicle2.id == vid))
                bus_number = v_r.scalar_one_or_none()
            transport_info = {"enrolled": True, "route_name": route_obj.name if route_obj else None, "route_code": getattr(route_obj, 'route_code', None), "bus_number": bus_number, "pickup_point": st_record.pickup_point, "drop_point": st_record.drop_point}

    return {
        "id": student.id,
        "roll_number": student.admission_number,
        "full_name": student.full_name,
        "email": student.email,
        "phone": student.phone,
        "class_name": class_name_val,
        "section": section_val,
        "status": student.status,
        "type": (student.metadata_ or {}).get("student_type"),
        "gender": student.gender,
        "date_of_birth": student.date_of_birth,
        "admission_date": student.admission_date,
        "address": student.address_line1,
        "city": student.city,
        "state": student.state,
        "pincode": student.pincode,
        "parent": parent_info,
        "parent_name": parent_info.get("name") if parent_info else None,
        "parent_phone": parent_info.get("phone") if parent_info else None,
        "parent_email": parent_info.get("email") if parent_info else None,
        "parent_relationship": parent_info.get("relationship") if parent_info else None,
        "parent_occupation": (student.metadata_ or {}).get("parent_occupation"),
        "previous_school": (student.metadata_ or {}).get("previous_school"),
        "token_advance": (student.metadata_ or {}).get("token_advance"),
        "medical": {
            "blood_group": student.blood_group,
            "religion": student.religion,
            "conditions": student.medical_conditions or "None reported",
            "allergies": student.allergies.split(",") if student.allergies else [],
        },
        "mentor": mentor_info,
        "class_teacher": class_teacher_info,
        "stats": await _compute_student_stats(db, student.id, school_id, current_ay),
        "behavior": {
            "overall_rating": None,
            "discipline_score": None,
            "punctuality_score": None,
        },
        "created_at": student.created_at,
        "transport": transport_info,
    }


# ---------------------------------------------------------------------------
# Update student
# ---------------------------------------------------------------------------


async def update_student(
    db: AsyncSession,
    school_id: UUID,
    student_id: UUID,
    data: dict,
    updated_by: UUID,
) -> dict:
    """Update a student's details."""
    result = await db.execute(
        select(Student).where(
            Student.id == student_id,
            Student.school_id == school_id,
            Student.is_active.is_(True),
        )
    )
    student = result.scalar_one_or_none()
    if not student:
        raise StudentNotFound(str(student_id))

    # Map request fields to model fields
    field_map = {
        "full_name": "full_name",
        "email": "email",
        "phone": "phone",
        "date_of_birth": "date_of_birth",
        "admission_date": "admission_date",
        "gender": "gender",
        "blood_group": "blood_group",
        "religion": "religion",
        "address": "address_line1",
        "address_line2": "address_line2",
        "city": "city",
        "state": "state",
        "pincode": "pincode",
        "status": "status",
    }

    for req_field, model_field in field_map.items():
        if req_field in data and data[req_field] is not None:
            setattr(student, model_field, data[req_field])

    # Store student_type in metadata
    if "student_type" in data:
        meta = student.metadata_ or {}
        meta["student_type"] = data["student_type"]
        student.metadata_ = meta

    if "parent_occupation" in data:
        meta = student.metadata_ or {}
        meta["parent_occupation"] = data["parent_occupation"]
        student.metadata_ = meta

    # Update name parts if full_name changed
    if "full_name" in data and data["full_name"]:
        name_parts = data["full_name"].split(" ", 1)
        student.first_name = name_parts[0]
        student.last_name = name_parts[1] if len(name_parts) > 1 else None

    # Update parent details if provided
    parent_fields = ["parent_name", "parent_phone", "parent_email", "parent_relationship"]
    if any(f in data for f in parent_fields):
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
                if "parent_name" in data and data["parent_name"]:
                    parent.full_name = data["parent_name"]
                    parts = data["parent_name"].split(" ", 1)
                    parent.first_name = parts[0]
                    parent.last_name = parts[1] if len(parts) > 1 else None
                if "parent_phone" in data:
                    parent.phone = data["parent_phone"]
                if "parent_email" in data:
                    parent.email = data["parent_email"]
                if "parent_relationship" in data:
                    parent.relation = data["parent_relationship"]
        elif data.get("parent_name"):
            # No existing parent - create one
            parent_name_parts = data["parent_name"].split(" ", 1)
            parent = Parent(
                school_id=school_id,
                first_name=parent_name_parts[0],
                last_name=parent_name_parts[1] if len(parent_name_parts) > 1 else None,
                full_name=data["parent_name"],
                relation=data.get("parent_relationship", "Parent/Guardian"),
                phone=data.get("parent_phone"),
                email=data.get("parent_email"),
                is_primary_contact=True,
                created_by=updated_by,
            )
            db.add(parent)
            await db.flush()
            student_parent = StudentParent(
                school_id=school_id,
                student_id=student.id,
                parent_id=parent.id,
                created_by=updated_by,
            )
            db.add(student_parent)

    # Update fee concessions if provided
    concessions = data.get("concessions")
    if concessions:
        from src.models.fee import FeeRecord
        for fee_structure_id, concession_amount in concessions.items():
            fee_result = await db.execute(
                select(FeeRecord).where(
                    FeeRecord.student_id == student.id,
                    FeeRecord.school_id == school_id,
                    FeeRecord.fee_structure_id == fee_structure_id,
                    FeeRecord.is_active.is_(True),
                )
            )
            fee_record = fee_result.scalar_one_or_none()
            if fee_record:
                from decimal import Decimal
                new_concession = Decimal(str(concession_amount))
                original = fee_record.total_amount + (fee_record.concession_amount or Decimal("0"))
                fee_record.concession_amount = new_concession
                fee_record.total_amount = original - new_concession
                fee_record.pending = fee_record.total_amount - (fee_record.paid or Decimal("0"))

    # Add custom fees if provided
    custom_fees = data.get("custom_fees")
    if custom_fees:
        from src.models.fee import FeeRecord
        from src.models.core import AcademicYear
        from decimal import Decimal
        from datetime import date, timedelta
        ay_result = await db.execute(
            select(AcademicYear).where(AcademicYear.school_id == school_id, AcademicYear.is_current.is_(True))
        )
        ay = ay_result.scalar_one_or_none()
        if ay:
            for cf in custom_fees:
                amount = Decimal(str(cf["amount"]))
                record = FeeRecord(
                    school_id=school_id,
                    academic_year_id=ay.id,
                    student_id=student.id,
                    fee_structure_id=None,
                    fee_type=cf["fee_type"],
                    fee_category=cf.get("fee_category", "other"),
                    total_amount=amount,
                    concession_amount=Decimal("0"),
                    paid=Decimal("0"),
                    pending=amount,
                    total_late_fee=Decimal("0"),
                    due_date=date.today() + timedelta(days=30),
                    status="Pending",
                    created_by=updated_by,
                )
                db.add(record)

    student.updated_by = updated_by
    await db.commit()
    await db.refresh(student)

    return await get_student(db, school_id, student_id)


# ---------------------------------------------------------------------------
# Delete (soft-delete) student
# ---------------------------------------------------------------------------


async def delete_student(
    db: AsyncSession,
    school_id: UUID,
    student_id: UUID,
    updated_by: UUID,
    status: str = "Inactive",
    reason: str | None = None,
) -> Student:
    """Soft-delete a student (set status to Inactive/Alumni)."""
    result = await db.execute(
        select(Student).where(
            Student.id == student_id,
            Student.school_id == school_id,
            Student.is_active.is_(True),
        )
    )
    student = result.scalar_one_or_none()
    if not student:
        raise StudentNotFound(str(student_id))

    student.status = status
    student.left_date = date.today()
    student.left_reason = reason
    student.updated_by = updated_by

    # Free transport capacity
    from src.models.transport import StudentTransport, RouteAssignment, Vehicle
    transport_result = await db.execute(
        select(StudentTransport).where(
            StudentTransport.student_id == student_id,
            StudentTransport.school_id == school_id,
            StudentTransport.is_active.is_(True),
        )
    )
    for st in transport_result.scalars().all():
        st.is_active = False
        # Update vehicle occupied_seats
        assign_r = await db.execute(
            select(RouteAssignment.vehicle_id).where(
                RouteAssignment.route_id == st.route_id, RouteAssignment.is_active.is_(True)
            )
        )
        vid = assign_r.scalar_one_or_none()
        if vid:
            from sqlalchemy import func
            count_r = await db.execute(
                select(func.count(StudentTransport.id)).where(
                    StudentTransport.route_id == st.route_id,
                    StudentTransport.is_active.is_(True),
                    StudentTransport.student_id != student_id,
                )
            )
            v_result = await db.execute(select(Vehicle).where(Vehicle.id == vid))
            v = v_result.scalar_one_or_none()
            if v:
                v.occupied_seats = count_r.scalar() or 0

    await db.commit()
    await db.refresh(student)
    return student


# ---------------------------------------------------------------------------
# Sub-resource endpoints (stubs returning appropriate structures)
# ---------------------------------------------------------------------------


async def get_exam_results(
    db: AsyncSession, school_id: UUID, student_id: UUID, academic_year: str | None = None
) -> dict:
    """Get student exam results grouped by exam."""
    from src.models.examination import Exam, ExamResult
    from src.models.academic import Subject

    result = await db.execute(
        select(Student).where(
            Student.id == student_id, Student.school_id == school_id, Student.is_active.is_(True)
        )
    )
    if not result.scalar_one_or_none():
        raise StudentNotFound(str(student_id))

    # Get current academic year
    ay = await db.execute(
        select(AcademicYear).where(AcademicYear.school_id == school_id, AcademicYear.is_current.is_(True))
    )
    current_ay = ay.scalar_one_or_none()
    if not current_ay:
        return {"exams": [], "trend": []}

    # Get all exam results for this student in the current year
    results = await db.execute(
        select(ExamResult, Exam, Subject)
        .join(Exam, ExamResult.exam_id == Exam.id)
        .outerjoin(Subject, Exam.subject_id == Subject.id)
        .where(
            ExamResult.student_id == student_id,
            ExamResult.school_id == school_id,
            Exam.academic_year_id == current_ay.id,
            ExamResult.is_active.is_(True),
        )
        .order_by(Exam.name, Exam.date)
    )
    rows = results.all()

    # Group by exam name
    exam_groups = {}
    for er, exam, subject in rows:
        key = exam.name
        if key not in exam_groups:
            exam_groups[key] = {"name": exam.name, "date": str(exam.date) if exam.date else None, "subjects": []}
        exam_groups[key]["subjects"].append({
            "name": subject.name if subject else exam.subject_id or "Unknown",
            "marks": float(er.marks_obtained or 0),
            "total": float(er.total_marks or exam.total_marks or 100),
            "grade": er.grade,
        })

    exams = list(exam_groups.values())
    return {"exams": exams, "trend": []}


async def get_parent_meetings(
    db: AsyncSession, school_id: UUID, student_id: UUID
) -> dict:
    """Get parent meeting history for a student."""
    from src.models.meeting import ParentMeeting

    result = await db.execute(
        select(Student).where(
            Student.id == student_id, Student.school_id == school_id, Student.is_active.is_(True)
        )
    )
    if not result.scalar_one_or_none():
        raise StudentNotFound(str(student_id))

    meetings_result = await db.execute(
        select(ParentMeeting).where(
            ParentMeeting.student_id == student_id,
            ParentMeeting.school_id == school_id,
            ParentMeeting.is_active.is_(True),
        ).order_by(ParentMeeting.meeting_date.desc())
    )
    meetings = meetings_result.scalars().all()
    total = len(meetings)
    attended = sum(1 for m in meetings if m.status == "Completed")

    return {
        "total_meetings": total,
        "attended": attended,
        "meetings": [
            {
                "id": m.id,
                "type": m.meeting_type,
                "date": m.meeting_date,
                "notes": m.discussion_notes,
                "status": m.status,
                "agenda": m.agenda,
                "remarks": m.remarks,
                "follow_up_required": m.follow_up_required,
                "next_meeting_date": m.next_meeting_date,
            }
            for m in meetings
        ],
    }


async def create_parent_meeting(
    db: AsyncSession, school_id: UUID, student_id: UUID, data: dict, user_id: UUID
) -> dict:
    """Create a parent meeting for a student."""
    from src.models.meeting import ParentMeeting

    result = await db.execute(
        select(Student).where(Student.id == student_id, Student.school_id == school_id, Student.is_active.is_(True))
    )
    if not result.scalar_one_or_none():
        raise StudentNotFound(str(student_id))

    ay_result = await db.execute(
        select(AcademicYear).where(AcademicYear.school_id == school_id, AcademicYear.is_current.is_(True))
    )
    ay = ay_result.scalar_one_or_none()

    # Resolve staff_id from user
    staff_id = await _resolve_staff_id(db, user_id, school_id)

    meeting = ParentMeeting(
        school_id=school_id,
        student_id=student_id,
        academic_year_id=ay.id if ay else None,
        meeting_date=data["meeting_date"],
        meeting_type=data.get("meeting_type"),
        agenda=data.get("agenda"),
        discussion_notes=data.get("discussion_notes"),
        remarks=data.get("remarks"),
        follow_up_required=data.get("follow_up_required", False),
        next_meeting_date=data.get("next_meeting_date"),
        status=data.get("status", "Scheduled"),
        conducted_by=staff_id,
        created_by=user_id,
    )
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)

    return {
        "id": meeting.id,
        "type": meeting.meeting_type,
        "date": meeting.meeting_date,
        "notes": meeting.discussion_notes,
        "status": meeting.status,
        "agenda": meeting.agenda,
        "remarks": meeting.remarks,
        "follow_up_required": meeting.follow_up_required,
        "next_meeting_date": meeting.next_meeting_date,
    }


async def update_parent_meeting(
    db: AsyncSession, school_id: UUID, student_id: UUID, meeting_id: UUID, data: dict
) -> dict:
    """Update a parent meeting."""
    from src.models.meeting import ParentMeeting

    result = await db.execute(
        select(ParentMeeting).where(
            ParentMeeting.id == meeting_id, ParentMeeting.student_id == student_id,
            ParentMeeting.school_id == school_id, ParentMeeting.is_active.is_(True),
        )
    )
    meeting = result.scalar_one_or_none()
    if not meeting:
        from src.core.exceptions import NotFound
        raise NotFound("Parent Meeting")

    for field in ("meeting_date", "meeting_type", "agenda", "discussion_notes", "remarks", "follow_up_required", "next_meeting_date", "status"):
        if field in data and data[field] is not None:
            setattr(meeting, field, data[field])

    await db.commit()
    await db.refresh(meeting)
    return {
        "id": meeting.id,
        "type": meeting.meeting_type,
        "date": meeting.meeting_date,
        "notes": meeting.discussion_notes,
        "status": meeting.status,
        "agenda": meeting.agenda,
        "remarks": meeting.remarks,
        "follow_up_required": meeting.follow_up_required,
        "next_meeting_date": meeting.next_meeting_date,
    }


async def delete_parent_meeting(
    db: AsyncSession, school_id: UUID, student_id: UUID, meeting_id: UUID
) -> None:
    """Soft-delete a parent meeting."""
    from src.models.meeting import ParentMeeting

    result = await db.execute(
        select(ParentMeeting).where(
            ParentMeeting.id == meeting_id, ParentMeeting.student_id == student_id,
            ParentMeeting.school_id == school_id, ParentMeeting.is_active.is_(True),
        )
    )
    meeting = result.scalar_one_or_none()
    if not meeting:
        from src.core.exceptions import NotFound
        raise NotFound("Parent Meeting")

    meeting.is_active = False
    await db.commit()


async def get_activities(
    db: AsyncSession, school_id: UUID, student_id: UUID
) -> dict:
    """Get activities and awards for a student."""
    from src.models.activity import Activity, Award

    result = await db.execute(
        select(Student).where(
            Student.id == student_id, Student.school_id == school_id, Student.is_active.is_(True)
        )
    )
    if not result.scalar_one_or_none():
        raise StudentNotFound(str(student_id))

    activities_result = await db.execute(
        select(Activity).where(
            Activity.student_id == student_id, Activity.school_id == school_id, Activity.is_active.is_(True)
        ).order_by(Activity.start_date.desc())
    )
    extra_curricular = [
        {
            "id": a.id,
            "name": a.name,
            "activity_type": a.activity_type,
            "description": a.description,
            "role": a.role,
            "start_date": a.start_date,
            "end_date": a.end_date,
            "achievement": a.achievement,
            "since": str(a.start_date.year) if a.start_date else None,
            "status": a.status,
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
            "name": a.title,
            "title": a.title,
            "category": a.category,
            "year": str(a.awarded_date.year) if a.awarded_date else None,
            "awarded_date": a.awarded_date,
            "awarded_by": a.awarded_by,
            "level": a.level,
            "description": a.description,
        }
        for a in awards_result.scalars().all()
    ]

    return {"extra_curricular": extra_curricular, "awards": awards}


async def create_award(
    db: AsyncSession, school_id: UUID, student_id: UUID, data: dict, user_id: UUID
) -> dict:
    """Create an award for a student."""
    from src.models.activity import Award

    # Validate student
    result = await db.execute(
        select(Student).where(Student.id == student_id, Student.school_id == school_id, Student.is_active.is_(True))
    )
    if not result.scalar_one_or_none():
        raise StudentNotFound(str(student_id))

    # Get current academic year
    ay_result = await db.execute(
        select(AcademicYear).where(AcademicYear.school_id == school_id, AcademicYear.is_current.is_(True))
    )
    ay = ay_result.scalar_one_or_none()

    award = Award(
        school_id=school_id,
        student_id=student_id,
        academic_year_id=ay.id if ay else None,
        title=data["title"],
        category=data.get("category"),
        description=data.get("description"),
        awarded_date=data.get("awarded_date"),
        awarded_by=data.get("awarded_by"),
        level=data.get("level"),
        certificate_url=data.get("certificate_url"),
        recorded_by=await _resolve_staff_id(db, user_id, school_id),
        created_by=user_id,
    )
    db.add(award)
    await db.commit()
    await db.refresh(award)

    return {
        "id": award.id,
        "title": award.title,
        "category": award.category,
        "description": award.description,
        "awarded_date": award.awarded_date,
        "awarded_by": award.awarded_by,
        "level": award.level,
    }


async def update_award(
    db: AsyncSession, school_id: UUID, student_id: UUID, award_id: UUID, data: dict
) -> dict:
    """Update an award."""
    from src.models.activity import Award

    result = await db.execute(
        select(Award).where(
            Award.id == award_id, Award.student_id == student_id,
            Award.school_id == school_id, Award.is_active.is_(True),
        )
    )
    award = result.scalar_one_or_none()
    if not award:
        from src.core.exceptions import NotFound
        raise NotFound("Award")

    for field in ("title", "category", "description", "awarded_date", "awarded_by", "level", "certificate_url"):
        if field in data and data[field] is not None:
            setattr(award, field, data[field])

    await db.commit()
    await db.refresh(award)
    return {
        "id": award.id,
        "title": award.title,
        "category": award.category,
        "description": award.description,
        "awarded_date": award.awarded_date,
        "awarded_by": award.awarded_by,
        "level": award.level,
    }


async def delete_award(
    db: AsyncSession, school_id: UUID, student_id: UUID, award_id: UUID
) -> None:
    """Soft-delete an award."""
    from src.models.activity import Award

    result = await db.execute(
        select(Award).where(
            Award.id == award_id, Award.student_id == student_id,
            Award.school_id == school_id, Award.is_active.is_(True),
        )
    )
    award = result.scalar_one_or_none()
    if not award:
        from src.core.exceptions import NotFound
        raise NotFound("Award")

    award.is_active = False
    await db.commit()


async def create_activity(
    db: AsyncSession, school_id: UUID, student_id: UUID, data: dict, user_id: UUID
) -> dict:
    """Create an activity for a student."""
    from src.models.activity import Activity

    result = await db.execute(
        select(Student).where(Student.id == student_id, Student.school_id == school_id, Student.is_active.is_(True))
    )
    if not result.scalar_one_or_none():
        raise StudentNotFound(str(student_id))

    ay_result = await db.execute(
        select(AcademicYear).where(AcademicYear.school_id == school_id, AcademicYear.is_current.is_(True))
    )
    ay = ay_result.scalar_one_or_none()

    # Resolve staff_id from user
    staff_id = await _resolve_staff_id(db, user_id, school_id)

    activity = Activity(
        school_id=school_id,
        student_id=student_id,
        academic_year_id=ay.id if ay else None,
        name=data["name"],
        activity_type=data["activity_type"],
        description=data.get("description"),
        role=data.get("role"),
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        achievement=data.get("achievement"),
        recorded_by=staff_id,
        status="Active",
        created_by=user_id,
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)

    return {
        "id": activity.id,
        "name": activity.name,
        "activity_type": activity.activity_type,
        "description": activity.description,
        "role": activity.role,
        "start_date": activity.start_date,
        "end_date": activity.end_date,
        "achievement": activity.achievement,
        "status": activity.status,
    }


async def update_activity(
    db: AsyncSession, school_id: UUID, student_id: UUID, activity_id: UUID, data: dict
) -> dict:
    """Update an activity."""
    from src.models.activity import Activity

    result = await db.execute(
        select(Activity).where(
            Activity.id == activity_id, Activity.student_id == student_id,
            Activity.school_id == school_id, Activity.is_active.is_(True),
        )
    )
    activity = result.scalar_one_or_none()
    if not activity:
        from src.core.exceptions import NotFound
        raise NotFound("Activity")

    for field in ("name", "activity_type", "description", "role", "start_date", "end_date", "achievement"):
        if field in data and data[field] is not None:
            setattr(activity, field, data[field])

    await db.commit()
    await db.refresh(activity)
    return {
        "id": activity.id,
        "name": activity.name,
        "activity_type": activity.activity_type,
        "description": activity.description,
        "role": activity.role,
        "start_date": activity.start_date,
        "end_date": activity.end_date,
        "achievement": activity.achievement,
        "status": activity.status,
    }


async def delete_activity(
    db: AsyncSession, school_id: UUID, student_id: UUID, activity_id: UUID
) -> None:
    """Soft-delete an activity."""
    from src.models.activity import Activity

    result = await db.execute(
        select(Activity).where(
            Activity.id == activity_id, Activity.student_id == student_id,
            Activity.school_id == school_id, Activity.is_active.is_(True),
        )
    )
    activity = result.scalar_one_or_none()
    if not activity:
        from src.core.exceptions import NotFound
        raise NotFound("Activity")

    activity.is_active = False
    await db.commit()


async def get_fee_history(
    db: AsyncSession, school_id: UUID, student_id: UUID
) -> dict:
    """Get fee history for a student - actual payment transactions."""
    result = await db.execute(
        select(Student).where(
            Student.id == student_id, Student.school_id == school_id, Student.is_active.is_(True)
        )
    )
    if not result.scalar_one_or_none():
        raise StudentNotFound(str(student_id))

    # Get all fee records for this student
    from src.models.fee import FeeRecord, FeePayment
    records_result = await db.execute(
        select(FeeRecord).where(
            FeeRecord.school_id == school_id,
            FeeRecord.student_id == student_id,
            FeeRecord.is_active.is_(True),
        )
    )
    records = records_result.scalars().all()
    record_ids = [r.id for r in records]

    total_fees = sum(float(r.total_amount or 0) for r in records)
    total_paid = sum(float(r.paid or 0) for r in records)

    # Get all payments across all fee records
    payments = []
    if record_ids:
        payments_result = await db.execute(
            select(FeePayment).where(
                FeePayment.fee_record_id.in_(record_ids),
                FeePayment.is_active.is_(True),
            ).order_by(FeePayment.payment_date.desc())
        )
        for p in payments_result.scalars().all():
            fee_record = next((r for r in records if r.id == p.fee_record_id), None)
            payments.append({
                "id": p.id,
                "amount": float(p.amount),
                "payment_date": p.payment_date,
                "method": p.payment_method,
                "reference": p.reference,
                "status": "Paid",
            })

    return {
        "summary": {"total_fees": total_fees, "total_paid": total_paid, "total_due": total_fees - total_paid},
        "fee_structure": [{"component": r.fee_type, "amount": float(r.total_amount), "concession": float(r.concession_amount or 0), "original_amount": float(r.total_amount) + float(r.concession_amount or 0), "frequency": r.fee_category, "status": r.status, "paid": float(r.paid or 0), "pending": float(r.pending or 0)} for r in records],
        "payments": payments,
    }


async def get_disciplinary_records(
    db: AsyncSession, school_id: UUID, student_id: UUID
) -> dict:
    """Get disciplinary records for a student."""
    from src.models.activity import DisciplinaryRecord

    result = await db.execute(
        select(Student).where(
            Student.id == student_id, Student.school_id == school_id, Student.is_active.is_(True)
        )
    )
    if not result.scalar_one_or_none():
        raise StudentNotFound(str(student_id))

    records_result = await db.execute(
        select(DisciplinaryRecord).where(
            DisciplinaryRecord.student_id == student_id,
            DisciplinaryRecord.school_id == school_id,
            DisciplinaryRecord.is_active.is_(True),
        ).order_by(DisciplinaryRecord.incident_date.desc())
    )
    records = [
        {
            "id": r.id,
            "incident_date": r.incident_date,
            "category": r.category,
            "severity": r.severity,
            "description": r.description,
            "action_taken": r.action_taken,
            "parent_notified": r.parent_notified,
            "status": r.status,
        }
        for r in records_result.scalars().all()
    ]
    status = "Clean" if not records else "Has Records"
    return {"records": records, "status": status}


async def create_disciplinary_record(
    db: AsyncSession, school_id: UUID, student_id: UUID, data: dict, user_id: UUID
) -> dict:
    """Create a disciplinary record for a student."""
    from src.models.activity import DisciplinaryRecord

    result = await db.execute(
        select(Student).where(Student.id == student_id, Student.school_id == school_id, Student.is_active.is_(True))
    )
    if not result.scalar_one_or_none():
        raise StudentNotFound(str(student_id))

    ay_result = await db.execute(
        select(AcademicYear).where(AcademicYear.school_id == school_id, AcademicYear.is_current.is_(True))
    )
    ay = ay_result.scalar_one_or_none()

    # Resolve staff_id from user
    staff_id = await _resolve_staff_id(db, user_id, school_id)

    record = DisciplinaryRecord(
        school_id=school_id,
        student_id=student_id,
        academic_year_id=ay.id if ay else None,
        incident_date=data["incident_date"],
        category=data["category"],
        severity=data["severity"],
        description=data["description"],
        action_taken=data.get("action_taken"),
        reported_by=staff_id,
        parent_notified=data.get("parent_notified", False),
        status=data.get("status", "Open"),
        created_by=user_id,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return {
        "id": record.id,
        "incident_date": record.incident_date,
        "category": record.category,
        "severity": record.severity,
        "description": record.description,
        "action_taken": record.action_taken,
        "parent_notified": record.parent_notified,
        "status": record.status,
    }


async def update_disciplinary_record(
    db: AsyncSession, school_id: UUID, student_id: UUID, record_id: UUID, data: dict
) -> dict:
    """Update a disciplinary record."""
    from src.models.activity import DisciplinaryRecord

    result = await db.execute(
        select(DisciplinaryRecord).where(
            DisciplinaryRecord.id == record_id, DisciplinaryRecord.student_id == student_id,
            DisciplinaryRecord.school_id == school_id, DisciplinaryRecord.is_active.is_(True),
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        from src.core.exceptions import NotFound
        raise NotFound("Disciplinary Record")

    for field in ("incident_date", "category", "severity", "description", "action_taken", "parent_notified", "status"):
        if field in data and data[field] is not None:
            setattr(record, field, data[field])

    await db.commit()
    await db.refresh(record)
    return {
        "id": record.id,
        "incident_date": record.incident_date,
        "category": record.category,
        "severity": record.severity,
        "description": record.description,
        "action_taken": record.action_taken,
        "parent_notified": record.parent_notified,
        "status": record.status,
    }


async def delete_disciplinary_record(
    db: AsyncSession, school_id: UUID, student_id: UUID, record_id: UUID
) -> None:
    """Soft-delete a disciplinary record."""
    from src.models.activity import DisciplinaryRecord

    result = await db.execute(
        select(DisciplinaryRecord).where(
            DisciplinaryRecord.id == record_id, DisciplinaryRecord.student_id == student_id,
            DisciplinaryRecord.school_id == school_id, DisciplinaryRecord.is_active.is_(True),
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        from src.core.exceptions import NotFound
        raise NotFound("Disciplinary Record")

    record.is_active = False
    await db.commit()


# ---------------------------------------------------------------------------
# Export CSV
# ---------------------------------------------------------------------------


async def export_students_csv(
    db: AsyncSession,
    school_id: UUID,
    class_name: str | None = None,
    section: str | None = None,
    status: str | None = None,
) -> str:
    """Export students as CSV string."""
    query = select(Student).where(
        Student.school_id == school_id,
        Student.is_active.is_(True),
    )
    if status:
        query = query.where(Student.status == status)

    result = await db.execute(query.order_by(Student.full_name))
    students = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Admission Number",
        "Full Name",
        "Email",
        "Phone",
        "Gender",
        "Date of Birth",
        "Admission Date",
        "Status",
        "Blood Group",
        "Address",
    ])
    for s in students:
        writer.writerow([
            s.admission_number,
            s.full_name,
            s.email or "",
            s.phone or "",
            s.gender or "",
            str(s.date_of_birth) if s.date_of_birth else "",
            str(s.admission_date) if s.admission_date else "",
            s.status,
            s.blood_group or "",
            s.address_line1 or "",
        ])

    return output.getvalue()


# ---------------------------------------------------------------------------
# Bulk import
# ---------------------------------------------------------------------------


async def bulk_import_students(
    db: AsyncSession,
    school_id: UUID,
    csv_content: str,
    created_by: UUID,
) -> dict:
    """Bulk import students from CSV content."""
    reader = csv.DictReader(io.StringIO(csv_content))
    imported = 0
    skipped = 0
    errors: list[dict] = []

    for row_num, row in enumerate(reader, start=2):
        roll = row.get("roll_number", "").strip()
        full_name = row.get("full_name", "").strip()

        if not roll or not full_name:
            errors.append({"row": row_num, "error": "Missing roll_number or full_name"})
            skipped += 1
            continue

        # Check duplicate
        existing = await db.execute(
            select(Student).where(
                Student.school_id == school_id,
                Student.admission_number == roll,
            )
        )
        if existing.scalar_one_or_none():
            errors.append({"row": row_num, "error": f"Duplicate roll number {roll}"})
            skipped += 1
            continue

        name_parts = full_name.split(" ", 1)
        student = Student(
            school_id=school_id,
            admission_number=roll,
            first_name=name_parts[0],
            last_name=name_parts[1] if len(name_parts) > 1 else None,
            full_name=full_name,
            email=row.get("email", "").strip() or None,
            phone=row.get("phone", "").strip() or None,
            gender=row.get("gender", "").strip() or None,
            status="Active",
            created_by=created_by,
        )
        db.add(student)
        imported += 1

    await db.commit()
    return {"imported": imported, "skipped": skipped, "errors": errors}


# ---------------------------------------------------------------------------
# Student Attendance Calendar
# ---------------------------------------------------------------------------


async def get_student_attendance(
    db: AsyncSession, school_id: UUID, student_id: UUID, month: int, year: int
) -> dict:
    """Get attendance records for a student for a given month/year."""
    from calendar import monthrange

    start_date = date(year, month, 1)
    _, last_day = monthrange(year, month)
    end_date = date(year, month, last_day)

    result = await db.execute(
        select(AttendanceRecord.id, AttendanceSession.date, AttendanceRecord.status)
        .select_from(AttendanceRecord)
        .join(AttendanceSession, AttendanceRecord.attendance_session_id == AttendanceSession.id)
        .where(
            AttendanceRecord.student_id == student_id,
            AttendanceSession.school_id == school_id,
            AttendanceSession.date >= start_date,
            AttendanceSession.date <= end_date,
            AttendanceRecord.is_active.is_(True),
            AttendanceSession.is_active.is_(True),
        )
    )
    rows = result.all()

    records = []
    for row in rows:
        records.append({
            "date": row.date.isoformat() if row.date else None,
            "status": row.status,
        })

    return {"month": month, "year": year, "records": records}
