from __future__ import annotations

import csv
import io
from datetime import date
from uuid import UUID

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
from src.models.fee import FeeRecord, FeeStructure


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
        for item in items:
            item["password_changed"] = pw_changed_map.get(item["id"], False)

    # Compute summary
    active_count = sum(1 for i in items if i["status"] == "Active")
    inactive_count = len(items) - active_count

    paginated = paginate(items, total, pagination)
    paginated["summary"] = {
        "total": total,
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
        status="Active",
        created_by=created_by,
    )
    db.add(student)
    await db.flush()

    # Create user account if not already exists (rollnumber@schoolcode.com)
    from src.models.core import School
    school_result = await db.execute(select(School).where(School.id == school_id))
    school_obj = school_result.scalar_one()
    user_email = data.get("email") or f"{roll_number}@{school_obj.code}.com"
    existing_user = await db.execute(
        select(User).where(User.school_id == school_id, User.email == user_email)
    )
    if not existing_user.scalar_one_or_none():
        user = User(
            school_id=school_id,
            email=user_email,
            password_hash=hash_password(user_email),
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
                due = date.today() + timedelta(days=30)
                concession_amount = float(concessions.get(str(fs.id), 0))
                total = float(fs.amount)
                net_amount = max(0, total - concession_amount)
                fee_record = FeeRecord(
                    school_id=school_id,
                    academic_year_id=current_ay2.id,
                    student_id=student.id,
                    fee_structure_id=fs.id,
                    fee_type=fs.fee_type,
                    fee_category=fs.fee_category,
                    total_amount=net_amount,
                    paid=0,
                    pending=net_amount,
                    due_date=due,
                    status="Pending",
                    is_active=True,
                    description=f"Auto-generated ({fs.frequency}){f' | Concession: ₹{concession_amount:.0f}' if concession_amount > 0 else ''}",
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

    return {
        "id": student.id,
        "roll_number": student.admission_number,
        "full_name": student.full_name,
        "email": student.email,
        "phone": student.phone,
        "class_name": class_name_val,
        "section": section_val,
        "status": student.status,
        "type": None,
        "gender": student.gender,
        "date_of_birth": student.date_of_birth,
        "admission_date": student.admission_date,
        "address": student.address_line1,
        "city": student.city,
        "state": student.state,
        "pincode": student.pincode,
        "parent": parent_info,
        "medical": {
            "blood_group": student.blood_group,
            "religion": student.religion,
            "conditions": student.medical_conditions or "None reported",
            "allergies": student.allergies.split(",") if student.allergies else [],
        },
        "mentor": mentor_info,
        "stats": {
            "attendance_percentage": None,
            "average_grade": None,
            "assignments_submitted": None,
            "assignments_total": None,
            "fee_due": None,
            "class_rank": None,
            "class_strength": None,
        },
        "behavior": {
            "overall_rating": None,
            "discipline_score": None,
            "punctuality_score": None,
        },
        "created_at": student.created_at,
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

    # Update name parts if full_name changed
    if "full_name" in data and data["full_name"]:
        name_parts = data["full_name"].split(" ", 1)
        student.first_name = name_parts[0]
        student.last_name = name_parts[1] if len(name_parts) > 1 else None

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

    await db.commit()
    await db.refresh(student)
    return student


# ---------------------------------------------------------------------------
# Sub-resource endpoints (stubs returning appropriate structures)
# ---------------------------------------------------------------------------


async def get_exam_results(
    db: AsyncSession, school_id: UUID, student_id: UUID, academic_year: str | None = None
) -> dict:
    """Get student exam results."""
    # Validate student exists
    result = await db.execute(
        select(Student).where(
            Student.id == student_id, Student.school_id == school_id, Student.is_active.is_(True)
        )
    )
    if not result.scalar_one_or_none():
        raise StudentNotFound(str(student_id))

    return {"exams": [], "trend": []}


async def get_parent_meetings(
    db: AsyncSession, school_id: UUID, student_id: UUID
) -> dict:
    """Get parent meeting history for a student."""
    result = await db.execute(
        select(Student).where(
            Student.id == student_id, Student.school_id == school_id, Student.is_active.is_(True)
        )
    )
    if not result.scalar_one_or_none():
        raise StudentNotFound(str(student_id))

    return {"total_meetings": 0, "attended": 0, "meetings": []}


async def get_activities(
    db: AsyncSession, school_id: UUID, student_id: UUID
) -> dict:
    """Get activities and awards for a student."""
    result = await db.execute(
        select(Student).where(
            Student.id == student_id, Student.school_id == school_id, Student.is_active.is_(True)
        )
    )
    if not result.scalar_one_or_none():
        raise StudentNotFound(str(student_id))

    return {"extra_curricular": [], "awards": []}


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
        "fee_structure": [{"component": r.fee_type, "amount": float(r.total_amount), "frequency": r.fee_category} for r in records],
        "payments": payments,
    }


async def get_disciplinary_records(
    db: AsyncSession, school_id: UUID, student_id: UUID
) -> dict:
    """Get disciplinary records for a student."""
    result = await db.execute(
        select(Student).where(
            Student.id == student_id, Student.school_id == school_id, Student.is_active.is_(True)
        )
    )
    if not result.scalar_one_or_none():
        raise StudentNotFound(str(student_id))

    return {"records": [], "status": "Clean"}


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
