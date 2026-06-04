from __future__ import annotations

import csv
import io
import uuid
from datetime import date

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.admin.teachers.exceptions import (
    DuplicateAssignment,
    SubjectNotQualified,
    TeacherNotFound,
    WorkloadExceeded,
)
from src.core.exceptions import ConflictError, NotFound
from src.core.pagination import PaginationParams, paginate
from src.core.security import hash_password
from src.models.academic import ClassSection, Subject
from src.models.core import AcademicYear, User
from src.models.staff import ClassAssignment, Staff, StaffSubject
from src.models.payroll import SalaryStructure


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_teacher_response(staff: Staff) -> dict:
    """Transform a Staff ORM object into the teacher response format."""
    subjects = []
    primary_subject = None
    for ss in (staff.subjects or []):
        if ss.subject:
            subjects.append(ss.subject.name)
            if ss.is_primary:
                primary_subject = ss.subject.name

    active_assignments = [
        a for a in (staff.class_assignments or [])
        if a.status == "Active" and a.is_active
    ]

    class_assignments = []
    total_periods = 0
    is_class_teacher_of = []

    for a in active_assignments:
        class_name = ""
        section = ""
        if a.class_section:
            if a.class_section.class_:
                class_name = a.class_section.class_.name
            if a.class_section.section:
                section = a.class_section.section.name

        subject_name = a.subject.name if a.subject else ""
        periods = a.periods_per_week or 0
        total_periods += periods

        class_assignments.append({
            "id": a.id,
            "class_name": class_name,
            "section": section,
            "subject": subject_name,
            "is_class_teacher": a.is_class_teacher,
            "periods_per_week": a.periods_per_week,
            "status": a.status,
        })

        if a.is_class_teacher:
            is_class_teacher_of.append(f"{class_name}-{section}")

    return {
        "id": staff.id,
        "employee_id": staff.employee_id,
        "user": {
            "full_name": staff.full_name,
            "email": staff.email,
            "phone": staff.phone,
        },
        "subjects": subjects,
        "primary_subject": primary_subject,
        "qualification": staff.qualification,
        "joining_date": staff.joining_date,
        "workload_hours": total_periods,
        "max_workload_hours": staff.max_workload_hours,
        "class_assignments": class_assignments,
        "total_periods_per_week": total_periods,
        "classes_count": len(active_assignments),
        "is_class_teacher_of": is_class_teacher_of,
        "status": staff.status,
        "is_active": staff.is_active,
        "left_date": staff.left_date,
        "left_reason": staff.left_reason,
        "created_at": staff.created_at,
    }


async def _get_current_academic_year(
    db: AsyncSession, school_id: uuid.UUID
) -> AcademicYear | None:
    """Get the current academic year for a school."""
    result = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
            AcademicYear.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


async def _resolve_class_section(
    db: AsyncSession,
    school_id: uuid.UUID,
    class_name: str,
    section: str,
) -> ClassSection | None:
    """Resolve a class_name + section string to a ClassSection record."""
    from src.models.academic import Class, Section

    result = await db.execute(
        select(ClassSection)
        .join(Class, ClassSection.class_id == Class.id)
        .join(Section, ClassSection.section_id == Section.id)
        .where(
            ClassSection.school_id == school_id,
            ClassSection.is_active.is_(True),
            Class.name == class_name,
            Section.name == section,
        )
    )
    return result.scalar_one_or_none()


async def _resolve_subject(
    db: AsyncSession, school_id: uuid.UUID, subject_name: str
) -> Subject | None:
    """Resolve a subject name to a Subject record."""
    result = await db.execute(
        select(Subject).where(
            Subject.school_id == school_id,
            Subject.name == subject_name,
            Subject.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------


async def list_teachers(
    db: AsyncSession,
    school_id: uuid.UUID,
    pagination: PaginationParams,
    search: str | None = None,
    subject: str | None = None,
    class_name: str | None = None,
    section: str | None = None,
    status: str | None = None,
    include_inactive: bool = False,
) -> dict:
    """List teachers (staff with is_teacher=True)."""
    query = select(Staff).where(
        Staff.school_id == school_id,
        Staff.is_teacher.is_(True),
        Staff.is_active.is_(True),
    )

    if not include_inactive:
        query = query.where(Staff.status == "Active")
    elif status:
        query = query.where(Staff.status == status)

    if search:
        search_filter = f"%{search}%"
        query = query.where(
            or_(
                Staff.full_name.ilike(search_filter),
                Staff.email.ilike(search_filter),
                Staff.employee_id.ilike(search_filter),
            )
        )

    if subject:
        query = query.where(
            Staff.id.in_(
                select(StaffSubject.staff_id)
                .join(Subject, StaffSubject.subject_id == Subject.id)
                .where(Subject.name == subject)
            )
        )

    if class_name or section:
        from src.models.academic import Class, Section as SectionModel

        cs_query = select(ClassAssignment.staff_id).join(
            ClassSection, ClassAssignment.class_section_id == ClassSection.id
        )
        if class_name:
            cs_query = cs_query.join(Class, ClassSection.class_id == Class.id).where(
                Class.name == class_name
            )
        if section:
            cs_query = cs_query.join(
                SectionModel, ClassSection.section_id == SectionModel.id
            ).where(SectionModel.name == section)

        cs_query = cs_query.where(ClassAssignment.status == "Active")
        query = query.where(Staff.id.in_(cs_query))

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Fetch page with relationships
    query = query.order_by(Staff.full_name).offset(pagination.offset).limit(pagination.page_size)
    query = query.options(
        selectinload(Staff.subjects).selectinload(StaffSubject.subject),
        selectinload(Staff.class_assignments).selectinload(ClassAssignment.class_section),
        selectinload(Staff.class_assignments).selectinload(ClassAssignment.subject),
    )
    result = await db.execute(query)
    teachers = result.scalars().unique().all()

    results = [_build_teacher_response(t) for t in teachers]

    # Lookup password_changed for all teachers
    staff_ids = [t.id for t in teachers]
    if staff_ids:
        from src.models.core import User
        user_result = await db.execute(
            select(User.email, User.password_changed).where(
                User.school_id == school_id, User.email.in_([t.email for t in teachers])
            )
        )
        pw_map = {row.email: row.password_changed for row in user_result}
        for r in results:
            r["password_changed"] = pw_map.get(r["user"]["email"], False)

    return paginate(results, total, pagination)


async def create_teacher(
    db: AsyncSession,
    school_id: uuid.UUID,
    data: dict,
    created_by: uuid.UUID,
) -> dict:
    """Create a teacher (staff + is_teacher=True + user account + subjects)."""
    employee_id = data["employee_id"]
    email = data["email"]
    full_name = data["full_name"]
    subject_names = data.pop("subjects", [])
    primary_subject_name = data.pop("primary_subject", None)

    # Check duplicate employee_id
    existing = await db.execute(
        select(Staff).where(
            Staff.school_id == school_id,
            Staff.employee_id == employee_id,
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError(
            f"Staff with employee ID {employee_id} already exists",
            {"employee_id": employee_id},
        )

    # Check duplicate email
    existing_email = await db.execute(
        select(Staff).where(
            Staff.school_id == school_id,
            Staff.email == email,
            Staff.is_active.is_(True),
        )
    )
    if existing_email.scalar_one_or_none():
        raise ConflictError(
            f"Staff with email {email} already exists",
            {"email": email},
        )

    # Resolve primary subject
    primary_subject_id = None
    if primary_subject_name:
        subj = await _resolve_subject(db, school_id, primary_subject_name)
        if subj:
            primary_subject_id = subj.id

    # Determine first/last name from full_name
    name_parts = full_name.split(" ", 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else None

    # Create staff record
    staff = Staff(
        school_id=school_id,
        employee_id=employee_id,
        first_name=first_name,
        last_name=last_name,
        full_name=full_name,
        email=email,
        phone=data.get("phone"),
        is_teacher=True,
        qualification=data.get("qualification"),
        joining_date=data.get("joining_date"),
        max_workload_hours=data.get("max_workload_hours"),
        department=data.get("department", "Teaching"),
        designation=data.get("designation"),
        gender=data.get("gender"),
        employment_type=data.get("employment_type"),
        primary_subject_id=primary_subject_id,
        status="Active",
        created_by=created_by,
    )
    db.add(staff)
    await db.flush()

    # Link subjects
    for subj_name in subject_names:
        subj = await _resolve_subject(db, school_id, subj_name)
        if subj:
            is_primary = subj_name == primary_subject_name
            staff_subject = StaffSubject(
                school_id=school_id,
                staff_id=staff.id,
                subject_id=subj.id,
                is_primary=is_primary,
                created_by=created_by,
            )
            db.add(staff_subject)

    # Create user account for the teacher (password = email)
    user = User(
        school_id=school_id,
        email=email,
        password_hash=hash_password(email),
        full_name=full_name,
        role="teacher",
        phone=data.get("phone"),
        created_by=created_by,
    )
    db.add(user)
    await db.flush()

    # Link user to staff
    staff.user_id = user.id

    # Create salary structure from submitted salary fields
    ay_result = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
        )
    )
    current_ay = ay_result.scalar_one_or_none()
    if current_ay:
        from decimal import Decimal
        basic = Decimal(str(data.get("basic_salary") or 0))
        hra_val = Decimal(str(data.get("hra") or 0))
        da_val = Decimal(str(data.get("da") or 0))
        ta_val = Decimal(str(data.get("ta") or 0))
        other_allow = Decimal(str(data.get("other_allowances") or 0))
        pf_val = Decimal(str(data.get("pf_deduction") or 0))
        tax_val = Decimal(str(data.get("tax_deduction") or 0))
        other_ded = Decimal(str(data.get("other_deductions") or 0))
        net = basic + hra_val + da_val + ta_val + other_allow - pf_val - tax_val - other_ded
        has_salary = basic > 0
        salary_structure = SalaryStructure(
            school_id=school_id,
            staff_id=staff.id,
            academic_year_id=current_ay.id,
            basic_salary=basic,
            hra=hra_val,
            da=da_val,
            transport_allowance=ta_val,
            other_allowances={"other_allowances": float(other_allow)},
            pf_deduction=pf_val,
            tds=tax_val,
            other_deductions={"other_deductions": float(other_ded)},
            net_salary=net,
            effective_from=data.get("joining_date") or date.today(),
            is_active=has_salary,
            created_by=created_by,
        )
        db.add(salary_structure)

    # Save bank details to staff record
    if data.get("bank_name"):
        staff.bank_name = data["bank_name"]
    if data.get("account_number"):
        staff.bank_account_number = data["account_number"]
    if data.get("ifsc_code"):
        staff.bank_ifsc = data["ifsc_code"]
    if data.get("pan_number"):
        staff.pan_number = data["pan_number"]

    await db.commit()
    await db.refresh(staff)

    return _build_teacher_response(staff)


async def get_teacher(
    db: AsyncSession,
    school_id: uuid.UUID,
    teacher_id: uuid.UUID,
) -> dict:
    """Get a single teacher's full profile."""
    query = (
        select(Staff)
        .where(
            Staff.id == teacher_id,
            Staff.school_id == school_id,
            Staff.is_teacher.is_(True),
            Staff.is_active.is_(True),
        )
        .options(
            selectinload(Staff.subjects).selectinload(StaffSubject.subject),
            selectinload(Staff.class_assignments).selectinload(ClassAssignment.class_section),
            selectinload(Staff.class_assignments).selectinload(ClassAssignment.subject),
        )
    )
    result = await db.execute(query)
    staff = result.scalar_one_or_none()
    if not staff:
        raise TeacherNotFound(str(teacher_id))

    return _build_teacher_response(staff)


async def update_teacher(
    db: AsyncSession,
    school_id: uuid.UUID,
    teacher_id: uuid.UUID,
    data: dict,
    updated_by: uuid.UUID,
) -> dict:
    """Update a teacher's details."""
    result = await db.execute(
        select(Staff)
        .where(
            Staff.id == teacher_id,
            Staff.school_id == school_id,
            Staff.is_teacher.is_(True),
            Staff.is_active.is_(True),
        )
        .options(
            selectinload(Staff.subjects).selectinload(StaffSubject.subject),
            selectinload(Staff.class_assignments).selectinload(ClassAssignment.class_section),
            selectinload(Staff.class_assignments).selectinload(ClassAssignment.subject),
        )
    )
    staff = result.scalar_one_or_none()
    if not staff:
        raise TeacherNotFound(str(teacher_id))

    # Handle subject changes
    subject_names = data.pop("subjects", None)
    primary_subject_name = data.pop("primary_subject", None)

    # Update simple fields
    field_map = {
        "full_name": "full_name",
        "email": "email",
        "phone": "phone",
        "qualification": "qualification",
        "max_workload_hours": "max_workload_hours",
        "department": "department",
        "designation": "designation",
        "gender": "gender",
        "employment_type": "employment_type",
    }

    for req_field, model_field in field_map.items():
        if req_field in data and data[req_field] is not None:
            setattr(staff, model_field, data[req_field])

    # Update full_name parts
    if "full_name" in data and data["full_name"]:
        name_parts = data["full_name"].split(" ", 1)
        staff.first_name = name_parts[0]
        staff.last_name = name_parts[1] if len(name_parts) > 1 else None

    # Update subjects if provided
    if subject_names is not None:
        # Remove existing
        for ss in list(staff.subjects):
            await db.delete(ss)

        # Add new
        for subj_name in subject_names:
            subj = await _resolve_subject(db, school_id, subj_name)
            if subj:
                is_primary = subj_name == primary_subject_name
                staff_subject = StaffSubject(
                    school_id=school_id,
                    staff_id=staff.id,
                    subject_id=subj.id,
                    is_primary=is_primary,
                    created_by=updated_by,
                )
                db.add(staff_subject)

    # Update primary subject
    if primary_subject_name:
        subj = await _resolve_subject(db, school_id, primary_subject_name)
        if subj:
            staff.primary_subject_id = subj.id

    staff.updated_by = updated_by
    await db.commit()
    await db.refresh(staff)

    return _build_teacher_response(staff)


async def delete_teacher(
    db: AsyncSession,
    school_id: uuid.UUID,
    teacher_id: uuid.UUID,
    deleted_by: uuid.UUID,
    reason: str | None = None,
    left_date_val: date | None = None,
) -> Staff:
    """Soft-delete a teacher (set Inactive, preserve history)."""
    result = await db.execute(
        select(Staff).where(
            Staff.id == teacher_id,
            Staff.school_id == school_id,
            Staff.is_teacher.is_(True),
            Staff.is_active.is_(True),
        )
    )
    staff = result.scalar_one_or_none()
    if not staff:
        raise TeacherNotFound(str(teacher_id))

    staff.status = "Inactive"
    staff.left_date = left_date_val or date.today()
    staff.left_reason = reason
    staff.updated_by = deleted_by
    await db.commit()
    await db.refresh(staff)
    return staff


# ---------------------------------------------------------------------------
# Assignments
# ---------------------------------------------------------------------------


async def assign_class(
    db: AsyncSession,
    school_id: uuid.UUID,
    teacher_id: uuid.UUID,
    data: dict,
    created_by: uuid.UUID,
) -> ClassAssignment:
    """Assign a class-section-subject to a teacher."""
    # Get teacher
    result = await db.execute(
        select(Staff)
        .where(
            Staff.id == teacher_id,
            Staff.school_id == school_id,
            Staff.is_teacher.is_(True),
            Staff.is_active.is_(True),
        )
        .options(selectinload(Staff.subjects).selectinload(StaffSubject.subject))
    )
    staff = result.scalar_one_or_none()
    if not staff:
        raise TeacherNotFound(str(teacher_id))

    class_name = data["class_name"]
    section = data["section"]
    subject_name = data["subject"]
    is_class_teacher = data.get("is_class_teacher", False)
    periods_per_week = data.get("periods_per_week")

    # Resolve class_section
    class_section = await _resolve_class_section(db, school_id, class_name, section)
    if not class_section:
        raise NotFound("ClassSection", f"{class_name}-{section}")

    # Resolve subject
    subject = await _resolve_subject(db, school_id, subject_name)
    if not subject:
        raise NotFound("Subject", subject_name)

    # Validate teacher is qualified
    qualified_subjects = [ss.subject.name for ss in staff.subjects if ss.subject]
    if subject_name not in qualified_subjects:
        raise SubjectNotQualified(subject_name, qualified_subjects)

    # Get current academic year
    academic_year = await _get_current_academic_year(db, school_id)
    if not academic_year:
        raise NotFound("AcademicYear", "current")

    # Check duplicate
    existing = await db.execute(
        select(ClassAssignment).where(
            ClassAssignment.school_id == school_id,
            ClassAssignment.staff_id == teacher_id,
            ClassAssignment.class_section_id == class_section.id,
            ClassAssignment.subject_id == subject.id,
            ClassAssignment.academic_year_id == academic_year.id,
            ClassAssignment.status == "Active",
            ClassAssignment.is_active.is_(True),
        )
    )
    if existing.scalar_one_or_none():
        raise DuplicateAssignment(f"{class_name}-{section}", subject_name)

    # Check workload
    if staff.max_workload_hours and periods_per_week:
        current_load_result = await db.execute(
            select(func.coalesce(func.sum(ClassAssignment.periods_per_week), 0)).where(
                ClassAssignment.staff_id == teacher_id,
                ClassAssignment.academic_year_id == academic_year.id,
                ClassAssignment.status == "Active",
                ClassAssignment.is_active.is_(True),
            )
        )
        current_load = current_load_result.scalar() or 0
        if current_load + periods_per_week > staff.max_workload_hours:
            raise WorkloadExceeded(int(current_load), periods_per_week, staff.max_workload_hours)

    # Create assignment
    assignment = ClassAssignment(
        school_id=school_id,
        staff_id=teacher_id,
        class_section_id=class_section.id,
        subject_id=subject.id,
        academic_year_id=academic_year.id,
        is_class_teacher=is_class_teacher,
        periods_per_week=periods_per_week,
        status="Active",
        created_by=created_by,
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment, attribute_names=["class_section", "subject"])
    return assignment


async def bulk_assign(
    db: AsyncSession,
    school_id: uuid.UUID,
    teacher_id: uuid.UUID,
    assignments_data: list[dict],
    created_by: uuid.UUID,
) -> dict:
    """Assign multiple class-section-subject combos at once."""
    assigned = 0
    skipped = 0
    created_assignments = []

    for item in assignments_data:
        try:
            assignment = await assign_class(db, school_id, teacher_id, item, created_by)
            assigned += 1

            class_name = ""
            section_name = ""
            if assignment.class_section:
                if assignment.class_section.class_:
                    class_name = assignment.class_section.class_.name
                if assignment.class_section.section:
                    section_name = assignment.class_section.section.name

            created_assignments.append({
                "id": assignment.id,
                "class_name": class_name,
                "section": section_name,
                "subject": assignment.subject.name if assignment.subject else "",
                "is_class_teacher": assignment.is_class_teacher,
                "periods_per_week": assignment.periods_per_week,
            })
        except (DuplicateAssignment, WorkloadExceeded, SubjectNotQualified):
            skipped += 1

    # Calculate totals
    academic_year = await _get_current_academic_year(db, school_id)
    total_periods = 0
    if academic_year:
        load_result = await db.execute(
            select(func.coalesce(func.sum(ClassAssignment.periods_per_week), 0)).where(
                ClassAssignment.staff_id == teacher_id,
                ClassAssignment.academic_year_id == academic_year.id,
                ClassAssignment.status == "Active",
                ClassAssignment.is_active.is_(True),
            )
        )
        total_periods = int(load_result.scalar() or 0)

    return {
        "assigned": assigned,
        "skipped": skipped,
        "assignments": created_assignments,
        "total_periods_per_week": total_periods,
        "workload_hours": total_periods,
    }


async def get_assignments(
    db: AsyncSession,
    school_id: uuid.UUID,
    teacher_id: uuid.UUID,
    subject_filter: str | None = None,
    class_filter: str | None = None,
) -> dict:
    """Get all class assignments for a teacher."""
    result = await db.execute(
        select(Staff).where(
            Staff.id == teacher_id,
            Staff.school_id == school_id,
            Staff.is_teacher.is_(True),
            Staff.is_active.is_(True),
        )
    )
    staff = result.scalar_one_or_none()
    if not staff:
        raise TeacherNotFound(str(teacher_id))

    query = (
        select(ClassAssignment)
        .where(
            ClassAssignment.staff_id == teacher_id,
            ClassAssignment.school_id == school_id,
            ClassAssignment.status == "Active",
            ClassAssignment.is_active.is_(True),
        )
        .options(
            selectinload(ClassAssignment.class_section),
            selectinload(ClassAssignment.subject),
        )
    )

    if subject_filter:
        query = query.join(Subject, ClassAssignment.subject_id == Subject.id).where(
            Subject.name == subject_filter
        )

    if class_filter:
        from src.models.academic import Class

        query = query.join(
            ClassSection, ClassAssignment.class_section_id == ClassSection.id
        ).join(Class, ClassSection.class_id == Class.id).where(Class.name == class_filter)

    result = await db.execute(query)
    assignments = result.scalars().unique().all()

    total_periods = 0
    assignment_list = []
    for a in assignments:
        class_name = ""
        section = ""
        if a.class_section:
            if a.class_section.class_:
                class_name = a.class_section.class_.name
            if a.class_section.section:
                section = a.class_section.section.name

        periods = a.periods_per_week or 0
        total_periods += periods

        assignment_list.append({
            "id": a.id,
            "class_name": class_name,
            "section": section,
            "subject": a.subject.name if a.subject else "",
            "is_class_teacher": a.is_class_teacher,
            "periods_per_week": a.periods_per_week,
            "status": a.status,
        })

    return {
        "teacher_id": staff.id,
        "teacher_name": staff.full_name,
        "total_assignments": len(assignment_list),
        "total_periods_per_week": total_periods,
        "assignments": assignment_list,
    }


async def remove_assignment(
    db: AsyncSession,
    school_id: uuid.UUID,
    teacher_id: uuid.UUID,
    assignment_id: uuid.UUID,
    updated_by: uuid.UUID,
    reason: str | None = None,
    end_date_val: date | None = None,
) -> dict:
    """Soft-remove a class assignment."""
    result = await db.execute(
        select(ClassAssignment)
        .where(
            ClassAssignment.id == assignment_id,
            ClassAssignment.staff_id == teacher_id,
            ClassAssignment.school_id == school_id,
            ClassAssignment.is_active.is_(True),
        )
        .options(
            selectinload(ClassAssignment.class_section),
            selectinload(ClassAssignment.subject),
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise NotFound("ClassAssignment", str(assignment_id))

    assignment.status = "Inactive"
    assignment.end_date = end_date_val or date.today()
    assignment.end_reason = reason
    assignment.updated_by = updated_by
    await db.commit()
    await db.refresh(assignment)

    class_name = ""
    section = ""
    if assignment.class_section:
        if assignment.class_section.class_:
            class_name = assignment.class_section.class_.name
        if assignment.class_section.section:
            section = assignment.class_section.section.name

    return {
        "id": assignment.id,
        "class_name": class_name,
        "section": section,
        "subject": assignment.subject.name if assignment.subject else "",
        "status": assignment.status,
        "end_date": assignment.end_date,
        "reason": assignment.end_reason,
        "message": "Assignment removed. Historical records preserved.",
    }


# ---------------------------------------------------------------------------
# Teachers by class
# ---------------------------------------------------------------------------


async def get_teachers_by_class(
    db: AsyncSession,
    school_id: uuid.UUID,
    class_name: str,
    section: str,
) -> dict:
    """Get all teachers assigned to a specific class/section."""
    class_section = await _resolve_class_section(db, school_id, class_name, section)
    if not class_section:
        raise NotFound("ClassSection", f"{class_name}-{section}")

    academic_year = await _get_current_academic_year(db, school_id)
    if not academic_year:
        return {"class_name": class_name, "section": section, "teachers": []}

    result = await db.execute(
        select(ClassAssignment)
        .where(
            ClassAssignment.school_id == school_id,
            ClassAssignment.class_section_id == class_section.id,
            ClassAssignment.academic_year_id == academic_year.id,
            ClassAssignment.status == "Active",
            ClassAssignment.is_active.is_(True),
        )
        .options(
            selectinload(ClassAssignment.staff),
            selectinload(ClassAssignment.subject),
        )
    )
    assignments = result.scalars().all()

    teachers = []
    for a in assignments:
        teachers.append({
            "teacher_id": a.staff.id if a.staff else None,
            "teacher_name": a.staff.full_name if a.staff else "",
            "subject": a.subject.name if a.subject else "",
            "is_class_teacher": a.is_class_teacher,
            "periods_per_week": a.periods_per_week,
        })

    return {
        "class_name": class_name,
        "section": section,
        "teachers": teachers,
    }


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------


async def get_teacher_history(
    db: AsyncSession,
    school_id: uuid.UUID,
    teacher_id: uuid.UUID,
    academic_year_name: str | None = None,
) -> dict:
    """Get historical records for a teacher."""
    result = await db.execute(
        select(Staff)
        .where(
            Staff.id == teacher_id,
            Staff.school_id == school_id,
            Staff.is_teacher.is_(True),
        )
        .options(selectinload(Staff.subjects).selectinload(StaffSubject.subject))
    )
    staff = result.scalar_one_or_none()
    if not staff:
        raise TeacherNotFound(str(teacher_id))

    # Get all assignments (active + inactive)
    query = (
        select(ClassAssignment)
        .where(
            ClassAssignment.staff_id == teacher_id,
            ClassAssignment.school_id == school_id,
        )
        .options(
            selectinload(ClassAssignment.class_section),
            selectinload(ClassAssignment.subject),
            selectinload(ClassAssignment.academic_year),
        )
        .order_by(ClassAssignment.created_at.desc())
    )

    if academic_year_name:
        query = query.join(
            AcademicYear, ClassAssignment.academic_year_id == AcademicYear.id
        ).where(AcademicYear.name == academic_year_name)

    result = await db.execute(query)
    assignments = result.scalars().unique().all()

    # Group by academic year
    history_by_year: dict[str, list] = {}
    for a in assignments:
        year_name = a.academic_year.name if a.academic_year else "Unknown"
        class_name = ""
        section = ""
        if a.class_section:
            if a.class_section.class_:
                class_name = a.class_section.class_.name
            if a.class_section.section:
                section = a.class_section.section.name

        entry = {
            "class_name": class_name,
            "section": section,
            "subject": a.subject.name if a.subject else "",
            "is_class_teacher": a.is_class_teacher,
            "periods_per_week": a.periods_per_week,
            "status": a.status,
        }
        history_by_year.setdefault(year_name, []).append(entry)

    assignment_history = [
        {"academic_year": year, "assignments": assigns}
        for year, assigns in history_by_year.items()
    ]

    subjects_taught = list({ss.subject.name for ss in staff.subjects if ss.subject})

    return {
        "teacher_id": staff.id,
        "employee_id": staff.employee_id,
        "full_name": staff.full_name,
        "status": staff.status,
        "joining_date": staff.joining_date,
        "left_date": staff.left_date,
        "reason": staff.left_reason,
        "subjects_taught": subjects_taught,
        "assignment_history": assignment_history,
    }


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------


async def export_teachers_csv(
    db: AsyncSession,
    school_id: uuid.UUID,
) -> str:
    """Export teachers as CSV."""
    query = (
        select(Staff)
        .where(
            Staff.school_id == school_id,
            Staff.is_teacher.is_(True),
            Staff.is_active.is_(True),
        )
        .options(selectinload(Staff.subjects).selectinload(StaffSubject.subject))
        .order_by(Staff.full_name)
    )
    result = await db.execute(query)
    teachers = result.scalars().unique().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Employee ID",
        "Full Name",
        "Email",
        "Phone",
        "Subjects",
        "Qualification",
        "Joining Date",
        "Max Workload Hours",
        "Status",
    ])

    for t in teachers:
        subjects = ", ".join(ss.subject.name for ss in t.subjects if ss.subject)
        writer.writerow([
            t.employee_id,
            t.full_name,
            t.email,
            t.phone or "",
            subjects,
            t.qualification or "",
            str(t.joining_date) if t.joining_date else "",
            t.max_workload_hours or "",
            t.status,
        ])

    return output.getvalue()
