from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AppException, NotFound
from src.core.pagination import PaginationParams, paginate
from src.models.academic import Class, ClassSection, Section
from src.models.core import AcademicYear, School, User
from src.models.fee import FeePenalty, FeePayment, FeeRecord, FeeReminder, FeeStructure
from src.models.student import Student, StudentEnrollment


async def _get_current_academic_year(
    db: AsyncSession, school_id: uuid.UUID
) -> AcademicYear:
    """Get the current academic year for the school."""
    result = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
            AcademicYear.is_active.is_(True),
        )
    )
    ay = result.scalar_one_or_none()
    if not ay:
        raise NotFound("Current academic year")
    return ay


async def _get_student_class_info(
    db: AsyncSession, student: Student, school_id: uuid.UUID
) -> tuple[str, str]:
    """Get student's current class and section names."""
    result = await db.execute(
        select(StudentEnrollment)
        .where(
            StudentEnrollment.student_id == student.id,
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.is_active.is_(True),
        )
        .order_by(StudentEnrollment.created_at.desc())
        .limit(1)
    )
    enrollment = result.scalar_one_or_none()
    if not enrollment:
        return ("", "")

    cs = enrollment.class_section
    if cs:
        cls = cs.class_
        sec = cs.section
        return (cls.name if cls else "", sec.name if sec else "")
    return ("", "")


def _compute_overdue_days(due_date: date) -> int:
    """Compute number of overdue days from due date."""
    today = date.today()
    if today > due_date:
        return (today - due_date).days
    return 0


async def list_fee_records(
    db: AsyncSession,
    school_id: uuid.UUID,
    pagination: PaginationParams,
    search: str | None = None,
    class_name: str | None = None,
    section: str | None = None,
    status: str | None = None,
    fee_type: str | None = None,
    fee_category: str | None = None,
    due_from: date | None = None,
    due_to: date | None = None,
) -> dict:
    """List fee records with filters, pagination, and summary KPIs."""
    ay = await _get_current_academic_year(db, school_id)

    query = (
        select(FeeRecord)
        .where(
            FeeRecord.school_id == school_id,
            FeeRecord.academic_year_id == ay.id,
        )
    )

    # Apply filters
    if status:
        status_map = {
            "paid": "Paid",
            "partial": "Partial",
            "pending": "Pending",
            "overdue": "Overdue",
            "draft": "Draft",
        }
        mapped_status = status_map.get(status.lower(), status)
        query = query.where(FeeRecord.status == mapped_status)
        if mapped_status == "Draft":
            query = query.where(FeeRecord.is_active.is_(False))
        else:
            query = query.where(FeeRecord.is_active.is_(True))
    else:
        query = query.where(FeeRecord.is_active.is_(True))

    if fee_type:
        query = query.where(FeeRecord.fee_type == fee_type)

    if fee_category:
        query = query.where(FeeRecord.fee_category == fee_category)

    if due_from:
        query = query.where(FeeRecord.due_date >= due_from)

    if due_to:
        query = query.where(FeeRecord.due_date <= due_to)

    if search or class_name or section:
        query = query.join(Student, FeeRecord.student_id == Student.id)
        if search:
            query = query.where(Student.full_name.ilike(f"%{search}%"))
        if class_name or section:
            query = query.join(
                StudentEnrollment,
                and_(
                    StudentEnrollment.student_id == Student.id,
                    StudentEnrollment.school_id == school_id,
                    StudentEnrollment.is_active.is_(True),
                ),
            ).join(
                ClassSection,
                StudentEnrollment.class_section_id == ClassSection.id,
            ).join(Class, ClassSection.class_id == Class.id)
            if class_name:
                query = query.where(Class.name == class_name)
            if section:
                query = query.join(
                    Section, ClassSection.section_id == Section.id
                ).where(Section.name == section)

    # Fetch all records (pagination applied after grouping by student)
    query = query.order_by(FeeRecord.student_id)
    result = await db.execute(query)
    records = result.scalars().all()

    # Build results - group by student
    student_map = {}
    for record in records:
        student = record.student
        sid = record.student_id
        if sid not in student_map:
            cls_name, sec_name = await _get_student_class_info(db, student, school_id)
            student_map[sid] = {
                "student_id": sid,
                "student_name": student.full_name if student else "",
                "roll_number": student.admission_number if student else None,
                "class_name": cls_name,
                "section": sec_name,
                "total_amount": Decimal("0"),
                "total_paid": Decimal("0"),
                "total_pending": Decimal("0"),
                "total_late_fine": Decimal("0"),
                "components_count": 0,
                "has_overdue": False,
                "all_paid": True,
            }
        entry = student_map[sid]
        entry["total_amount"] += record.total_amount or Decimal("0")
        entry["total_paid"] += record.paid or Decimal("0")
        entry["total_pending"] += record.pending or Decimal("0")
        entry["total_late_fine"] += record.total_late_fee or Decimal("0")
        entry["components_count"] += 1
        if record.status == "Overdue":
            entry["has_overdue"] = True
        if record.status != "Paid":
            entry["all_paid"] = False

    items = []
    for entry in student_map.values():
        if entry["all_paid"]:
            status = "Paid"
        elif entry["has_overdue"]:
            status = "Overdue"
        elif entry["total_paid"] > 0:
            status = "Partial"
        else:
            status = "Pending"
        items.append({
            "student_id": entry["student_id"],
            "student_name": entry["student_name"],
            "roll_number": entry["roll_number"],
            "class_name": entry["class_name"],
            "section": entry["section"],
            "total_amount": entry["total_amount"],
            "total_paid": entry["total_paid"],
            "total_pending": entry["total_pending"],
            "total_late_fine": entry["total_late_fine"],
            "status": status,
            "components_count": entry["components_count"],
        })

    # Summary KPIs (across all matching records, not just current page)
    summary_query = select(
        func.coalesce(func.sum(FeeRecord.total_amount), 0).label("total_fees"),
        func.coalesce(func.sum(FeeRecord.paid), 0).label("collected"),
        func.coalesce(func.sum(FeeRecord.pending), 0).label("pending_sum"),
        func.coalesce(func.sum(FeeRecord.total_late_fee), 0).label("late_fines_total"),
        func.sum(case((FeeRecord.status == "Overdue", 1), else_=0)).label("overdue_count"),
    ).where(
        FeeRecord.school_id == school_id,
        FeeRecord.academic_year_id == ay.id,
        FeeRecord.is_active.is_(True),
    )
    summary_result = await db.execute(summary_query)
    summary_row = summary_result.one()

    total_fees = summary_row.total_fees or Decimal("0")
    collected = summary_row.collected or Decimal("0")
    pending_sum = summary_row.pending_sum or Decimal("0")
    late_fines_total = summary_row.late_fines_total or Decimal("0")
    overdue_count = summary_row.overdue_count or 0
    collection_rate = (
        round(float(collected) / float(total_fees) * 100, 1)
        if total_fees > 0
        else 0.0
    )

    # Paginate grouped results
    total_students = len(items)
    start = pagination.offset
    end = start + pagination.page_size
    paginated_items = items[start:end]
    paginated = paginate(paginated_items, total_students, pagination)
    paginated["summary"] = {
        "total_fees": total_fees,
        "collected": collected,
        "pending": pending_sum,
        "overdue_count": overdue_count,
        "late_fines_total": late_fines_total,
        "collection_rate": collection_rate,
    }
    return paginated


async def get_fee_record_detail(
    db: AsyncSession,
    school_id: uuid.UUID,
    fee_id: uuid.UUID,
) -> dict:
    """Get a single fee record with payment and fine history."""
    result = await db.execute(
        select(FeeRecord).where(
            FeeRecord.id == fee_id,
            FeeRecord.school_id == school_id,
            FeeRecord.is_active.is_(True),
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise NotFound("Fee record", str(fee_id))

    student = record.student
    cls_name, sec_name = await _get_student_class_info(db, student, school_id)
    overdue_days = _compute_overdue_days(record.due_date)

    # Payment history — explicit query to guarantee fresh data
    payments_result = await db.execute(
        select(FeePayment).where(
            FeePayment.fee_record_id == fee_id,
            FeePayment.is_active.is_(True),
        ).order_by(FeePayment.payment_date.asc())
    )
    payments = payments_result.scalars().all()

    payment_history = []
    for payment in payments:
        recorder_name = None
        if payment.recorder:
            recorder_name = payment.recorder.email
        payment_history.append({
            "id": payment.id,
            "amount": payment.amount,
            "payment_date": payment.payment_date,
            "method": payment.payment_method,
            "reference": payment.reference,
            "recorded_by": recorder_name,
        })

    # Fine history — explicit query to guarantee fresh data
    penalties_result = await db.execute(
        select(FeePenalty).where(
            FeePenalty.fee_record_id == fee_id,
            FeePenalty.is_active.is_(True),
        ).order_by(FeePenalty.applied_on.asc())
    )
    penalties = penalties_result.scalars().all()

    fine_history = []
    for penalty in penalties:
        applier_name = penalty.applier.email if penalty.applier else None
        fine_history.append({
            "id": penalty.id,
            "penalty_type": penalty.penalty_type,
            "amount": penalty.amount,
            "applied_on": penalty.applied_on,
            "applied_by": applier_name,
        })

    return {
        "id": record.id,
        "student_id": record.student_id,
        "student_name": student.full_name if student else "",
        "class_name": cls_name,
        "section": sec_name,
        "fee_type": record.fee_type,
        "fee_category": record.fee_category,
        "total_amount": record.total_amount,
        "concession_amount": float(record.concession_amount or 0),
        "paid": record.paid,
        "pending": record.pending,
        "late_fine": record.total_late_fee,
        "due_date": record.due_date,
        "status": record.status,
        "overdue_days": overdue_days,
        "payment_history": payment_history,
        "fine_history": fine_history,
        "is_active": record.is_active,
        "metadata": record.metadata_ or {},
    }


async def create_fee_record(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    data: dict,
) -> dict:
    """Create a fee record (assign fee to a student)."""
    ay = await _get_current_academic_year(db, school_id)

    student_id = data["student_id"]
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

    total_amount = Decimal(str(data["total_amount"]))
    record = FeeRecord(
        school_id=school_id,
        academic_year_id=ay.id,
        student_id=student_id,
        fee_type=data["fee_type"],
        fee_category=data.get("fee_category", "academic"),
        total_amount=total_amount,
        paid=Decimal("0"),
        pending=total_amount,
        total_late_fee=Decimal("0"),
        due_date=data["due_date"],
        status="Pending",
        description=data.get("description"),
        created_by=user.id,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    cls_name, sec_name = await _get_student_class_info(db, student, school_id)

    return {
        "id": record.id,
        "student_id": record.student_id,
        "student_name": student.full_name,
        "class_name": cls_name,
        "section": sec_name,
        "fee_type": record.fee_type,
        "fee_category": record.fee_category,
        "total_amount": record.total_amount,
        "concession_amount": float(record.concession_amount or 0),
        "paid": record.paid,
        "pending": record.pending,
        "late_fine": record.total_late_fee,
        "due_date": record.due_date,
        "status": record.status,
        "created_at": record.created_at,
        "metadata": record.metadata_ or {},
    }


async def update_fee_record(
    db: AsyncSession,
    school_id: uuid.UUID,
    fee_id: uuid.UUID,
    data: dict,
) -> dict:
    """Update a fee record — used to activate draft records created on student admission."""
    result = await db.execute(
        select(FeeRecord).where(FeeRecord.id == fee_id, FeeRecord.school_id == school_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise NotFound("Fee record")

    for k, v in data.items():
        if k == "is_active" and v is True and record.status == "Draft":
            record.status = "Pending"
            record.is_active = True
            if record.total_amount:
                record.pending = record.total_amount - record.paid
        elif k == "total_amount":
            setattr(record, k, v)
            record.pending = v - record.paid
        elif hasattr(record, k):
            setattr(record, k, v)

    await db.commit()
    await db.refresh(record)

    student = record.student
    cls_name, sec_name = await _get_student_class_info(db, student, school_id)

    return {
        "id": record.id,
        "student_id": record.student_id,
        "student_name": student.full_name if student else "",
        "class_name": cls_name,
        "section": sec_name,
        "fee_type": record.fee_type,
        "fee_category": record.fee_category,
        "total_amount": record.total_amount,
        "concession_amount": float(record.concession_amount or 0),
        "paid": record.paid,
        "pending": record.pending,
        "due_date": record.due_date,
        "status": record.status,
        "is_active": record.is_active,
    }


async def generate_due_fees(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    data: dict,
) -> dict:
    """Bulk generate due fees for selected students or all enrolled students in a class/section."""
    ay = await _get_current_academic_year(db, school_id)

    # If academic_year specified, find it
    if data.get("academic_year"):
        result = await db.execute(
            select(AcademicYear).where(
                AcademicYear.school_id == school_id,
                AcademicYear.name == data["academic_year"],
                AcademicYear.is_active.is_(True),
            )
        )
        found_ay = result.scalar_one_or_none()
        if found_ay:
            ay = found_ay

    fee_type = data["fee_type"]
    amount = Decimal(str(data["amount"]))
    due_date = data["due_date"]
    fee_category = data.get("fee_category", "academic")

    # Mode 1: student_ids provided directly (from selection)
    if data.get("student_ids"):
        student_ids = [uuid.UUID(sid) if isinstance(sid, str) else sid for sid in data["student_ids"]]
        generated = 0
        skipped = 0
        created_records = []

        for student_id in student_ids:
            existing = await db.execute(
                select(FeeRecord).where(
                    FeeRecord.school_id == school_id,
                    FeeRecord.academic_year_id == ay.id,
                    FeeRecord.student_id == student_id,
                    FeeRecord.fee_type == fee_type,
                    FeeRecord.due_date == due_date,
                    FeeRecord.is_active.is_(True),
                )
            )
            if existing.scalar_one_or_none():
                skipped += 1
                continue

            record = FeeRecord(
                school_id=school_id,
                academic_year_id=ay.id,
                student_id=student_id,
                fee_type=fee_type,
                fee_category=fee_category,
                total_amount=amount,
                paid=Decimal("0"),
                pending=amount,
                total_late_fee=Decimal("0"),
                due_date=due_date,
                status="Pending",
                description=data.get("term"),
                created_by=user.id,
            )
            db.add(record)
            created_records.append(record)
            generated += 1

        await db.commit()

        records_output = []
        for record in created_records:
            await db.refresh(record)
            student = record.student
            records_output.append({
                "id": record.id,
                "student_id": record.student_id,
                "student_name": student.full_name if student else "",
            })

        return {
            "generated": generated,
            "skipped": skipped,
            "message": f"Generated {generated} fee record(s), skipped {skipped} duplicate(s)",
            "records": records_output,
        }

    # Mode 2: class_name/section provided (legacy bulk by class)
    class_name = data.get("class_name")
    section_name = data.get("section")
    if not class_name:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Either student_ids or class_name is required")

    class_query = select(Class).where(
        Class.school_id == school_id,
        Class.name == class_name,
        Class.is_active.is_(True),
    )
    cls_result = await db.execute(class_query)
    cls = cls_result.scalar_one_or_none()
    if not cls:
        raise NotFound("Class", class_name)

    # Get class sections
    cs_query = select(ClassSection).where(
        ClassSection.school_id == school_id,
        ClassSection.class_id == cls.id,
        ClassSection.is_active.is_(True),
    )
    if section_name:
        cs_query = cs_query.join(Section, ClassSection.section_id == Section.id).where(
            Section.name == section_name
        )
    cs_result = await db.execute(cs_query)
    class_sections = cs_result.scalars().all()

    if not class_sections:
        raise NotFound("Class section", f"{class_name}-{section_name or 'All'}")

    cs_ids = [cs.id for cs in class_sections]

    # Get enrolled students
    enrollment_query = select(StudentEnrollment).where(
        StudentEnrollment.school_id == school_id,
        StudentEnrollment.academic_year_id == ay.id,
        StudentEnrollment.class_section_id.in_(cs_ids),
        StudentEnrollment.is_active.is_(True),
    )
    enrollment_result = await db.execute(enrollment_query)
    enrollments = enrollment_result.scalars().all()

    generated = 0
    skipped = 0
    created_records: list[FeeRecord] = []
    for enrollment in enrollments:
        student_id = enrollment.student_id

        # Check if already exists for this student/fee_type/due_date
        existing = await db.execute(
            select(FeeRecord).where(
                FeeRecord.school_id == school_id,
                FeeRecord.academic_year_id == ay.id,
                FeeRecord.student_id == student_id,
                FeeRecord.fee_type == fee_type,
                FeeRecord.due_date == due_date,
                FeeRecord.is_active.is_(True),
            )
        )
        if existing.scalar_one_or_none():
            skipped += 1
            continue

        record = FeeRecord(
            school_id=school_id,
            academic_year_id=ay.id,
            student_id=student_id,
            fee_type=fee_type,
            fee_category=fee_category,
            total_amount=amount,
            paid=Decimal("0"),
            pending=amount,
            total_late_fee=Decimal("0"),
            due_date=due_date,
            status="Pending",
            description=data.get("term"),
            created_by=user.id,
        )
        db.add(record)
        created_records.append(record)
        generated += 1

    await db.commit()

    # Build records list with student names
    records_output = []
    for record in created_records:
        await db.refresh(record)
        student = record.student
        student_name = student.full_name if student else ""
        records_output.append({
            "id": record.id,
            "student_id": record.student_id,
            "student_name": student_name,
            "fee_type": record.fee_type,
            "total_amount": record.total_amount,
        "concession_amount": float(record.concession_amount or 0),
            "due_date": record.due_date,
            "status": record.status,
        })

    class_section_label = f"{class_name}-{section_name}" if section_name else class_name
    return {
        "generated": generated,
        "fee_type": fee_type,
        "amount": amount,
        "due_date": due_date,
        "class_section": class_section_label,
        "skipped": skipped,
        "message": f"Due fee of ₹{amount:,.0f} generated for {generated} students in Class {class_section_label}.",
        "records": records_output,
    }


async def record_payment(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    fee_id: uuid.UUID,
    data: dict,
) -> dict:
    """Record a payment (partial or full) against a fee record."""
    result = await db.execute(
        select(FeeRecord).where(
            FeeRecord.id == fee_id,
            FeeRecord.school_id == school_id,
            FeeRecord.is_active.is_(True),
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise NotFound("Fee record", str(fee_id))

    payment_amount = Decimal(str(data["amount"]))
    current_pending = record.pending

    if payment_amount > current_pending:
        raise AppException(
            status_code=400,
            error=f"Payment amount (₹{payment_amount:,.0f}) exceeds pending amount (₹{current_pending:,.0f})",
            code="PAYMENT_EXCEEDS_PENDING",
        )

    previously_paid = record.paid

    # Create payment record
    payment = FeePayment(
        school_id=school_id,
        fee_record_id=fee_id,
        amount=payment_amount,
        payment_date=date.today(),
        payment_method=data["payment_method"],
        reference=data.get("reference"),
        recorded_by=user.id,
        created_by=user.id,
    )
    # Add payment via the relationship to ensure ORM consistency
    record.payments.append(payment)

    # Update fee record
    new_paid = (record.paid or Decimal("0")) + payment_amount
    new_pending = (record.pending or Decimal("0")) - payment_amount
    record.paid = new_paid
    record.pending = new_pending

    if new_pending <= 0:
        record.status = "Paid"
    else:
        record.status = "Partial"

    # Flush to ensure INSERT and UPDATE are sent to the database
    await db.flush()
    await db.commit()
    await db.refresh(record)
    await db.refresh(payment)

    student = record.student
    student_name = student.full_name if student else ""

    status_msg = "Fee fully paid." if record.status == "Paid" else f"Remaining: ₹{record.pending:,.0f}."

    return {
        "id": payment.id,
        "fee_id": record.id,
        "student_name": student_name,
        "fee_type": record.fee_type,
        "total_amount": record.total_amount,
        "concession_amount": float(record.concession_amount or 0),
        "previously_paid": previously_paid,
        "payment_recorded": payment_amount,
        "total_paid_now": record.paid,
        "pending_now": record.pending,
        "status": record.status.lower(),
        "payment_date": payment.payment_date,
        "payment_method": payment.payment_method,
        "reference": payment.reference,
        "recorded_by": user.email,
        "message": f"Payment of ₹{payment_amount:,.0f} recorded. {status_msg}",
    }


async def bulk_record_payment(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    student_id: uuid.UUID,
    data: dict,
) -> dict:
    """Record a bulk payment that distributes across multiple pending fee components for a student.

    The total amount is distributed across pending fee records in order of due date (oldest first).
    """
    ay = await _get_current_academic_year(db, school_id)

    # Verify student exists
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

    # Get all pending fee records for this student, ordered by due date (oldest first)
    records_result = await db.execute(
        select(FeeRecord)
        .where(
            FeeRecord.school_id == school_id,
            FeeRecord.academic_year_id == ay.id,
            FeeRecord.student_id == student_id,
            FeeRecord.is_active.is_(True),
            FeeRecord.status.in_(["Pending", "Partial", "Overdue"]),
        )
        .order_by(FeeRecord.due_date.asc())
    )
    pending_records = records_result.scalars().all()

    if not pending_records:
        raise AppException(
            status_code=400,
            error="No pending fee records found for this student",
            code="NO_PENDING_FEES",
        )

    total_payment = Decimal(str(data["amount"]))
    payment_method = data["payment_method"]
    reference = data.get("reference")

    # Calculate total pending across all records
    total_pending_all = sum(r.pending for r in pending_records)
    if total_payment > total_pending_all:
        raise AppException(
            status_code=400,
            error=f"Payment amount ({total_payment:,.0f}) exceeds total pending ({total_pending_all:,.0f})",
            code="PAYMENT_EXCEEDS_TOTAL_PENDING",
        )

    # Distribute payment across records
    remaining = total_payment
    components = []

    for record in pending_records:
        if remaining <= 0:
            break

        component_pending = record.pending
        pay_for_this = min(remaining, component_pending)

        # Create payment record
        payment = FeePayment(
            school_id=school_id,
            fee_record_id=record.id,
            amount=pay_for_this,
            payment_date=date.today(),
            payment_method=payment_method,
            reference=reference,
            recorded_by=user.id,
            created_by=user.id,
        )
        record.payments.append(payment)

        # Update fee record
        pending_before = record.pending
        record.paid = (record.paid or Decimal("0")) + pay_for_this
        record.pending = (record.pending or Decimal("0")) - pay_for_this

        if record.pending <= 0:
            record.status = "Paid"
        else:
            record.status = "Partial"

        components.append({
            "fee_id": record.id,
            "fee_type": record.fee_type,
            "amount_paid": pay_for_this,
            "pending_before": pending_before,
            "pending_after": record.pending,
            "status": record.status,
        })

        remaining -= pay_for_this

    await db.flush()
    await db.commit()

    return {
        "student_id": student_id,
        "student_name": student.full_name,
        "total_amount_paid": total_payment,
        "payment_method": payment_method,
        "components_paid": len(components),
        "components": components,
        "message": f"Payment of {total_payment:,.0f} recorded across {len(components)} fee component(s).",
    }


async def apply_late_fee(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    fee_id: uuid.UUID,
    data: dict,
) -> dict:
    """Apply a late fee/penalty to a fee record."""
    result = await db.execute(
        select(FeeRecord).where(
            FeeRecord.id == fee_id,
            FeeRecord.school_id == school_id,
            FeeRecord.is_active.is_(True),
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise NotFound("Fee record", str(fee_id))

    penalty_type = data["penalty_type"]
    now = datetime.now(timezone.utc)

    if penalty_type == "fixed":
        raw_amount = data.get("amount")
        if not raw_amount:
            raise AppException(
                status_code=400,
                error="Amount is required for fixed penalty type",
                code="MISSING_AMOUNT",
            )
        penalty_amount = Decimal(str(raw_amount))
        percentage = None
    else:
        raw_percentage = data.get("percentage")
        if not raw_percentage:
            raise AppException(
                status_code=400,
                error="Percentage is required for percentage penalty type",
                code="MISSING_PERCENTAGE",
            )
        percentage = Decimal(str(raw_percentage))
        penalty_amount = (record.pending * percentage) / Decimal("100")

    # Create penalty record
    penalty = FeePenalty(
        school_id=school_id,
        fee_record_id=fee_id,
        penalty_type=penalty_type,
        amount=penalty_amount,
        percentage=percentage,
        applied_on=now,
        applied_by=user.id,
        created_by=user.id,
    )
    db.add(penalty)

    # Update fee record totals
    record.total_late_fee = (record.total_late_fee or Decimal("0")) + penalty_amount
    record.pending = (record.pending or Decimal("0")) + penalty_amount

    # Update status to Overdue if past due date
    if record.due_date < date.today() and record.status not in ("Paid",):
        record.status = "Overdue"

    await db.commit()
    await db.refresh(record)
    await db.refresh(penalty)

    student = record.student
    overdue_days = _compute_overdue_days(record.due_date)

    return {
        "id": penalty.id,
        "fee_id": record.id,
        "student_name": student.full_name if student else "",
        "pending_amount": record.pending,
        "overdue_days": overdue_days,
        "penalty_type": penalty_type,
        "penalty_applied": penalty_amount,
        "total_late_fine_now": record.total_late_fee,
        "new_pending_with_fine": record.pending,
        "applied_on": now.date(),
        "applied_by": user.email,
        "message": f"Late fee of ₹{penalty_amount:,.0f} applied.",
    }


async def bulk_apply_late_fees(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    data: dict,
) -> dict:
    """Bulk apply late fees to all overdue records."""
    ay = await _get_current_academic_year(db, school_id)

    query = select(FeeRecord).where(
        FeeRecord.school_id == school_id,
        FeeRecord.academic_year_id == ay.id,
        FeeRecord.is_active.is_(True),
        FeeRecord.status.in_(["Overdue", "Pending", "Partial"]),
        FeeRecord.due_date < date.today(),
    )

    # Filter by class if specified
    if data.get("class_name"):
        query = query.join(Student, FeeRecord.student_id == Student.id).join(
            StudentEnrollment,
            and_(
                StudentEnrollment.student_id == Student.id,
                StudentEnrollment.school_id == school_id,
                StudentEnrollment.is_active.is_(True),
            ),
        ).join(
            ClassSection,
            StudentEnrollment.class_section_id == ClassSection.id,
        ).join(Class, ClassSection.class_id == Class.id).where(
            Class.name == data["class_name"]
        )
        if data.get("section"):
            query = query.join(
                Section, ClassSection.section_id == Section.id
            ).where(Section.name == data["section"])

    result = await db.execute(query)
    records = result.scalars().all()

    penalty_type = data["penalty_type"]
    now = datetime.now(timezone.utc)
    applied_records = []
    total_fines = Decimal("0")

    # Validate required fields upfront
    if penalty_type == "fixed":
        raw_amount = data.get("amount")
        if not raw_amount:
            raise AppException(
                status_code=400,
                error="Amount is required for fixed penalty type",
                code="MISSING_AMOUNT",
            )
        fixed_amount = Decimal(str(raw_amount))
    else:
        raw_percentage = data.get("percentage")
        if not raw_percentage:
            raise AppException(
                status_code=400,
                error="Percentage is required for percentage penalty type",
                code="MISSING_PERCENTAGE",
            )
        pct_value = Decimal(str(raw_percentage))

    for record in records:
        if penalty_type == "fixed":
            penalty_amount = fixed_amount
            percentage = None
        else:
            percentage = pct_value
            penalty_amount = (record.pending * percentage) / Decimal("100")

        penalty = FeePenalty(
            school_id=school_id,
            fee_record_id=record.id,
            penalty_type=penalty_type,
            amount=penalty_amount,
            percentage=percentage,
            applied_on=now,
            applied_by=user.id,
            created_by=user.id,
        )
        db.add(penalty)

        record.total_late_fee = (record.total_late_fee or Decimal("0")) + penalty_amount
        record.pending = (record.pending or Decimal("0")) + penalty_amount
        record.status = "Overdue"

        student = record.student
        applied_records.append({
            "fee_id": record.id,
            "student_name": student.full_name if student else "",
            "fine_applied": penalty_amount,
        })
        total_fines += penalty_amount

    await db.commit()

    return {
        "applied_to": len(applied_records),
        "total_fines_applied": total_fines,
        "records": applied_records,
        "message": f"Late fee applied to {len(applied_records)} overdue records.",
    }


async def send_reminder(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    data: dict,
) -> dict:
    """Send fee payment reminders."""
    ay = await _get_current_academic_year(db, school_id)
    now = datetime.now(timezone.utc)

    # Count target students
    query = select(FeeRecord).where(
        FeeRecord.school_id == school_id,
        FeeRecord.academic_year_id == ay.id,
        FeeRecord.is_active.is_(True),
    )

    target_group = data["target_group"]
    if target_group.lower() == "selected" and data.get("student_ids"):
        query = query.where(FeeRecord.student_id.in_(data["student_ids"]))
    elif target_group.lower() == "overdue":
        query = query.where(
            FeeRecord.status.in_(["Overdue", "Pending", "Partial"]),
            FeeRecord.due_date < date.today(),
        )

    if data.get("class_name"):
        query = query.join(Student, FeeRecord.student_id == Student.id).join(
            StudentEnrollment,
            and_(
                StudentEnrollment.student_id == Student.id,
                StudentEnrollment.school_id == school_id,
                StudentEnrollment.is_active.is_(True),
            ),
        ).join(
            ClassSection,
            StudentEnrollment.class_section_id == ClassSection.id,
        ).join(Class, ClassSection.class_id == Class.id).where(
            Class.name == data["class_name"]
        )
        if data.get("section"):
            query = query.join(
                Section, ClassSection.section_id == Section.id
            ).where(Section.name == data["section"])

    # Get distinct student count
    count_result = await db.execute(
        select(func.count(func.distinct(FeeRecord.student_id))).select_from(
            query.subquery()
        )
    )
    sent_count = count_result.scalar() or 0

    # Create reminder record
    reminder = FeeReminder(
        school_id=school_id,
        academic_year_id=ay.id,
        target_group=target_group,
        class_name=data.get("class_name"),
        section=data.get("section"),
        message=data["message"],
        send_via=data["send_via"],
        sent_to_count=sent_count,
        sent_by=user.id,
        sent_at=now,
        created_by=user.id,
    )
    db.add(reminder)
    await db.commit()

    return {
        "sent_to": sent_count,
        "target_group": target_group,
        "send_via": data["send_via"],
        "message": f"Reminder sent to {sent_count} recipients",
    }


async def get_fee_receipt(
    db: AsyncSession,
    school_id: uuid.UUID,
    fee_id: uuid.UUID,
) -> dict:
    """Generate a payment receipt for a specific fee record."""
    result = await db.execute(
        select(FeeRecord).where(
            FeeRecord.id == fee_id,
            FeeRecord.school_id == school_id,
            FeeRecord.is_active.is_(True),
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise NotFound("Fee record", str(fee_id))

    # Get school info
    school_result = await db.execute(select(School).where(School.id == school_id))
    school = school_result.scalar_one_or_none()

    student = record.student
    cls_name, sec_name = await _get_student_class_info(db, student, school_id)
    ay = record.academic_year

    # Build payments list
    payments = []
    for payment in record.payments:
        if not payment.is_active:
            continue
        payments.append({
            "amount": payment.amount,
            "payment_date": payment.payment_date,
            "method": payment.payment_method,
            "reference": payment.reference,
        })

    receipt_number = f"RCP-{date.today().year}-{str(record.id)[:5].upper()}"
    school_address = ""
    if school:
        parts = [p for p in [school.address_line1, school.city, school.state, school.pincode] if p]
        school_address = ", ".join(parts)

    return {
        "receipt_number": receipt_number,
        "generated_on": date.today(),
        "school_name": school.name if school else "",
        "school_address": school_address,
        "student_name": student.full_name if student else "",
        "student_id": record.student_id,
        "roll_number": student.admission_number if student else None,
        "class_section": f"{cls_name}-{sec_name}" if sec_name else cls_name,
        "fee_type": record.fee_type,
        "academic_year": ay.name if ay else "",
        "total_amount": record.total_amount,
        "concession_amount": float(record.concession_amount or 0),
        "total_paid": record.paid,
        "pending": record.pending,
        "late_fine": record.total_late_fee,
        "status": record.status.lower(),
        "payments": payments,
        "download_url": f"/api/v1/admin/fees/receipts/{receipt_number}/download/",
        "metadata": record.metadata_ or {},
    }


async def get_student_fee_records(
    db: AsyncSession,
    school_id: uuid.UUID,
    student_id: uuid.UUID,
    academic_year: str | None = None,
    status: str | None = None,
) -> dict:
    """Get all fee records for a specific student with summary."""
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

    # Get academic year
    if academic_year:
        ay_result = await db.execute(
            select(AcademicYear).where(
                AcademicYear.school_id == school_id,
                AcademicYear.name == academic_year,
                AcademicYear.is_active.is_(True),
            )
        )
        ay = ay_result.scalar_one_or_none()
        if not ay:
            raise NotFound("Academic year", academic_year)
    else:
        ay = await _get_current_academic_year(db, school_id)

    query = select(FeeRecord).where(
        FeeRecord.school_id == school_id,
        FeeRecord.academic_year_id == ay.id,
        FeeRecord.student_id == student_id,
        FeeRecord.is_active.is_(True),
    )

    if status:
        status_map = {
            "paid": "Paid",
            "partial": "Partial",
            "pending": "Pending",
            "overdue": "Overdue",
        }
        mapped_status = status_map.get(status.lower(), status)
        query = query.where(FeeRecord.status == mapped_status)

    result = await db.execute(query.order_by(FeeRecord.due_date.desc()))
    records = result.scalars().all()

    cls_name, sec_name = await _get_student_class_info(db, student, school_id)

    items = []
    total_fees = Decimal("0")
    total_paid = Decimal("0")
    total_pending = Decimal("0")
    total_fines = Decimal("0")

    for record in records:
        items.append({
            "id": record.id,
            "fee_type": record.fee_type,
            "fee_category": record.fee_category,
            "total_amount": record.total_amount,
        "concession_amount": float(record.concession_amount or 0),
            "paid": record.paid,
            "pending": record.pending,
            "late_fine": record.total_late_fee,
            "due_date": record.due_date,
            "status": record.status.lower(),
        })
        total_fees += record.total_amount
        total_paid += record.paid
        total_pending += record.pending
        total_fines += record.total_late_fee

    return {
        "student_id": student_id,
        "student_name": student.full_name,
        "class_section": f"{cls_name}-{sec_name}" if sec_name else cls_name,
        "academic_year": ay.name,
        "summary": {
            "total_fees": total_fees,
            "total_paid": total_paid,
            "total_pending": total_pending,
            "total_fines": total_fines,
        },
        "records": items,
    }


async def get_student_consolidated_receipt(
    db: AsyncSession,
    school_id: uuid.UUID,
    student_id: uuid.UUID,
    academic_year: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> dict:
    """Generate a consolidated payment receipt for a student."""
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

    # Get academic year
    if academic_year:
        ay_result = await db.execute(
            select(AcademicYear).where(
                AcademicYear.school_id == school_id,
                AcademicYear.name == academic_year,
                AcademicYear.is_active.is_(True),
            )
        )
        ay = ay_result.scalar_one_or_none()
        if not ay:
            raise NotFound("Academic year", academic_year)
    else:
        ay = await _get_current_academic_year(db, school_id)

    # Get school info
    school_result = await db.execute(select(School).where(School.id == school_id))
    school = school_result.scalar_one_or_none()

    cls_name, sec_name = await _get_student_class_info(db, student, school_id)

    # Get all fee records for this student
    records_query = select(FeeRecord).where(
        FeeRecord.school_id == school_id,
        FeeRecord.academic_year_id == ay.id,
        FeeRecord.student_id == student_id,
        FeeRecord.is_active.is_(True),
    )
    records_result = await db.execute(records_query)
    fee_records = records_result.scalars().all()

    # Get all payments
    fee_record_ids = [r.id for r in fee_records]
    payments_query = select(FeePayment).where(
        FeePayment.school_id == school_id,
        FeePayment.fee_record_id.in_(fee_record_ids) if fee_record_ids else FeePayment.id.is_(None),
        FeePayment.is_active.is_(True),
    )
    if from_date:
        payments_query = payments_query.where(FeePayment.payment_date >= from_date)
    if to_date:
        payments_query = payments_query.where(FeePayment.payment_date <= to_date)

    payments_query = payments_query.order_by(FeePayment.payment_date.asc())
    payments_result = await db.execute(payments_query)
    payments = payments_result.scalars().all()

    # Build summary
    total_fees_assigned = sum(r.total_amount for r in fee_records)
    total_paid = sum(r.paid for r in fee_records)
    total_pending = sum(r.pending for r in fee_records)
    total_fines = sum(r.total_late_fee for r in fee_records)

    # Build payments list
    payment_items = []
    for payment in payments:
        # Find fee record for this payment to get fee_type
        fee_record = next((r for r in fee_records if r.id == payment.fee_record_id), None)
        payment_items.append({
            "fee_type": fee_record.fee_type if fee_record else "",
            "amount": payment.amount,
            "payment_date": payment.payment_date,
            "method": payment.payment_method,
            "reference": payment.reference,
        })

    receipt_number = f"RCP-CONS-{date.today().year}-{str(student_id)[:5].upper()}"
    school_address = ""
    if school:
        parts = [p for p in [school.address_line1, school.city, school.state, school.pincode] if p]
        school_address = ", ".join(parts)

    period_start = from_date or ay.start_date
    period_end = to_date or date.today()

    return {
        "receipt_number": receipt_number,
        "generated_on": date.today(),
        "school_name": school.name if school else "",
        "school_address": school_address,
        "student_name": student.full_name,
        "student_id": student_id,
        "roll_number": student.admission_number,
        "class_section": f"{cls_name}-{sec_name}" if sec_name else cls_name,
        "academic_year": ay.name,
        "period": f"{period_start} to {period_end}",
        "fee_summary": {
            "total_fees_assigned": total_fees_assigned,
            "total_paid": total_paid,
            "total_pending": total_pending,
            "total_fines": total_fines,
        },
        "payments": payment_items,
        "total_payments_count": len(payment_items),
        "total_amount_paid": sum(p.amount for p in payments),
        "download_url": f"/api/v1/admin/fees/receipts/{receipt_number}/download/",
        "metadata": {},
    }


async def export_fee_records(
    db: AsyncSession,
    school_id: uuid.UUID,
    class_name: str | None = None,
    status: str | None = None,
) -> list[dict]:
    """Export fee records as a list of dicts (for CSV generation)."""
    ay = await _get_current_academic_year(db, school_id)

    query = select(FeeRecord).where(
        FeeRecord.school_id == school_id,
        FeeRecord.academic_year_id == ay.id,
        FeeRecord.is_active.is_(True),
    )

    if status:
        status_map = {
            "paid": "Paid",
            "partial": "Partial",
            "pending": "Pending",
            "overdue": "Overdue",
        }
        mapped_status = status_map.get(status.lower(), status)
        query = query.where(FeeRecord.status == mapped_status)

    if class_name:
        query = query.join(Student, FeeRecord.student_id == Student.id).join(
            StudentEnrollment,
            and_(
                StudentEnrollment.student_id == Student.id,
                StudentEnrollment.school_id == school_id,
                StudentEnrollment.is_active.is_(True),
            ),
        ).join(
            ClassSection,
            StudentEnrollment.class_section_id == ClassSection.id,
        ).join(Class, ClassSection.class_id == Class.id).where(
            Class.name == class_name
        )

    result = await db.execute(query.order_by(FeeRecord.due_date.desc()))
    records = result.scalars().all()

    rows = []
    for record in records:
        student = record.student
        cls_name, sec_name = await _get_student_class_info(db, student, school_id)
        rows.append({
            "student_name": student.full_name if student else "",
            "class": cls_name,
            "section": sec_name,
            "fee_type": record.fee_type,
            "fee_category": record.fee_category,
            "total_amount": str(record.total_amount),
            "paid": str(record.paid),
            "pending": str(record.pending),
            "late_fine": str(record.total_late_fee),
            "due_date": str(record.due_date),
            "status": record.status,
        })

    return rows
