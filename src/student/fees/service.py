from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFound
from src.core.pagination import PaginationParams, paginate
from src.models.academic import ClassSection
from src.models.core import AcademicYear, School, User
from src.models.fee import FeePayment, FeeRecord, FeeReminder, FeeStructure
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


async def _get_academic_year_by_name(
    db: AsyncSession, school_id: uuid.UUID, name: str | None
) -> AcademicYear:
    """Get academic year by name or return current."""
    if name:
        result = await db.execute(
            select(AcademicYear).where(
                AcademicYear.school_id == school_id,
                AcademicYear.name == name,
                AcademicYear.is_active.is_(True),
            )
        )
        ay = result.scalar_one_or_none()
        if ay:
            return ay
    return await _get_current_academic_year(db, school_id)


async def _get_student_from_user(
    db: AsyncSession, user: User, school_id: uuid.UUID
) -> Student:
    """Get the student record from the authenticated user."""
    if not user.student_id:
        raise NotFound("Student profile")
    result = await db.execute(
        select(Student).where(
            Student.id == user.student_id,
            Student.school_id == school_id,
            Student.is_active.is_(True),
        )
    )
    student = result.scalar_one_or_none()
    if not student:
        raise NotFound("Student profile")
    return student


async def _get_student_class_section(
    db: AsyncSession, student_id: uuid.UUID, school_id: uuid.UUID
) -> str:
    """Get formatted class-section string for a student."""
    result = await db.execute(
        select(StudentEnrollment)
        .where(
            StudentEnrollment.student_id == student_id,
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.is_active.is_(True),
        )
        .order_by(StudentEnrollment.created_at.desc())
        .limit(1)
    )
    enrollment = result.scalar_one_or_none()
    if not enrollment:
        return ""
    cs = enrollment.class_section
    if cs:
        cls = cs.class_
        sec = cs.section
        cls_name = cls.name if cls else ""
        sec_name = sec.name if sec else ""
        return f"{cls_name}-{sec_name}" if sec_name else cls_name
    return ""


async def _get_student_enrollment(
    db: AsyncSession, student_id: uuid.UUID, school_id: uuid.UUID, academic_year_id: uuid.UUID
) -> StudentEnrollment | None:
    """Get student enrollment for a specific academic year."""
    result = await db.execute(
        select(StudentEnrollment).where(
            StudentEnrollment.student_id == student_id,
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.academic_year_id == academic_year_id,
            StudentEnrollment.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


async def get_fee_summary(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    academic_year: str | None = None,
) -> dict:
    """Get fee summary with current dues and recent payment history."""
    student = await _get_student_from_user(db, user, school_id)
    ay = await _get_academic_year_by_name(db, school_id, academic_year)

    # Get all fee records for this student
    result = await db.execute(
        select(FeeRecord).where(
            FeeRecord.school_id == school_id,
            FeeRecord.academic_year_id == ay.id,
            FeeRecord.student_id == student.id,
            FeeRecord.is_active.is_(True),
        )
    )
    records = result.scalars().all()

    total_fees = Decimal("0")
    paid = Decimal("0")
    due = Decimal("0")
    overdue = Decimal("0")
    late_fines = Decimal("0")

    today = date.today()
    current_dues = []

    for record in records:
        total_fees += record.total_amount
        paid += record.paid
        late_fines += record.total_late_fee

        if record.pending > 0:
            if record.due_date < today:
                overdue += record.pending
            else:
                due += record.pending

            current_dues.append({
                "id": record.id,
                "fee_type": record.fee_type,
                "fee_category": record.fee_category,
                "amount": record.pending,
                "due_date": record.due_date,
                "status": "Overdue" if record.due_date < today else "Pending",
            })

    # Recent payments (last 5)
    payments_result = await db.execute(
        select(FeePayment)
        .join(FeeRecord, FeePayment.fee_record_id == FeeRecord.id)
        .where(
            FeeRecord.school_id == school_id,
            FeeRecord.academic_year_id == ay.id,
            FeeRecord.student_id == student.id,
            FeePayment.is_active.is_(True),
        )
        .order_by(FeePayment.payment_date.desc())
        .limit(5)
    )
    payments = payments_result.scalars().all()

    recent_payments = []
    for payment in payments:
        fee_record = payment.fee_record
        receipt_id = f"RCP-{payment.payment_date.year}-{str(payment.id)[:5].upper()}"
        recent_payments.append({
            "id": payment.id,
            "fee_type": fee_record.fee_type if fee_record else "",
            "fee_category": fee_record.fee_category if fee_record else "academic",
            "amount": payment.amount,
            "currency": "INR",
            "paid_date": payment.payment_date,
            "method": payment.payment_method,
            "receipt_id": receipt_id,
            "status": "Paid",
        })

    return {
        "academic_year": ay.name,
        "summary": {
            "total_fees": total_fees,
            "paid": paid,
            "due": due,
            "overdue": overdue,
            "late_fines": late_fines,
            "currency": "INR",
        },
        "current_dues": current_dues,
        "recent_payments": recent_payments,
        "metadata": {},
    }


async def get_fee_structure(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    academic_year: str | None = None,
) -> dict:
    """Get fee structure breakdown for the student's class."""
    student = await _get_student_from_user(db, user, school_id)
    ay = await _get_academic_year_by_name(db, school_id, academic_year)

    # Get student's enrollment to find class_section
    enrollment = await _get_student_enrollment(db, student.id, school_id, ay.id)

    # Query fee structures for the student's class section (or all)
    query = select(FeeStructure).where(
        FeeStructure.school_id == school_id,
        FeeStructure.academic_year_id == ay.id,
        FeeStructure.is_active.is_(True),
    )

    if enrollment and enrollment.class_section_id:
        query = query.where(
            (FeeStructure.class_section_id == enrollment.class_section_id)
            | (FeeStructure.class_section_id.is_(None))
        )
    else:
        query = query.where(FeeStructure.class_section_id.is_(None))

    result = await db.execute(query)
    structures = result.scalars().all()

    components = []
    total_annual = Decimal("0")

    frequency_multiplier = {
        "Monthly": 12,
        "Quarterly": 4,
        "Semi-Annually": 2,
        "Annually": 1,
        "One-Time": 1,
    }

    for structure in structures:
        components.append({
            "id": structure.id,
            "fee_component": structure.fee_type,
            "fee_category": structure.fee_category,
            "amount": structure.amount,
            "currency": "INR",
            "frequency": structure.frequency,
            "metadata": structure.metadata_ or {},
        })
        multiplier = frequency_multiplier.get(structure.frequency, 1)
        total_annual += structure.amount * multiplier

    return {
        "academic_year": ay.name,
        "components": components,
        "total_annual_fee": total_annual,
        "currency": "INR",
        "metadata": {},
    }


async def get_fee_dues(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    pagination: PaginationParams,
    academic_year: str | None = None,
) -> dict:
    """Get list of current fee dues."""
    student = await _get_student_from_user(db, user, school_id)
    ay = await _get_academic_year_by_name(db, school_id, academic_year)

    query = select(FeeRecord).where(
        FeeRecord.school_id == school_id,
        FeeRecord.academic_year_id == ay.id,
        FeeRecord.student_id == student.id,
        FeeRecord.is_active.is_(True),
    )

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.order_by(FeeRecord.due_date.asc())
    query = query.offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    records = result.scalars().all()

    today = date.today()
    total_due = Decimal("0")
    items = []

    for record in records:
        is_overdue = record.due_date < today and record.pending > 0
        days_overdue = (today - record.due_date).days if is_overdue else None
        days_until_due = (record.due_date - today).days if not is_overdue and record.pending > 0 else None

        if record.pending > 0:
            total_due += record.pending

        item = {
            "id": record.id,
            "fee_type": record.fee_type,
            "fee_category": record.fee_category,
            "description": record.description,
            "amount": record.total_amount,
            "total_amount": record.total_amount,
            "paid_amount": record.paid,
            "balance": record.pending,
            "currency": "INR",
            "due_date": record.due_date,
            "status": record.status,
            "is_overdue": is_overdue,
            "days_until_due": days_until_due,
            "days_overdue": days_overdue,
            "metadata": record.metadata_ or {},
        }

        if record.status == "Paid":
            # Find the payment for receipt URL
            if record.payments:
                last_payment = record.payments[-1]
                item["receipt_url"] = f"/api/v1/student/fees/receipt/{last_payment.id}/"
        elif record.pending > 0:
            item["pay_now_url"] = f"/api/v1/student/fees/pay/{record.id}/"

        items.append(item)

    paginated = paginate(items, total, pagination)
    paginated["total_due"] = total_due
    paginated["currency"] = "INR"
    return paginated


async def get_payment_history(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    pagination: PaginationParams,
    academic_year: str | None = None,
) -> dict:
    """Get payment history for the student."""
    student = await _get_student_from_user(db, user, school_id)
    ay = await _get_academic_year_by_name(db, school_id, academic_year)

    query = (
        select(FeePayment)
        .join(FeeRecord, FeePayment.fee_record_id == FeeRecord.id)
        .where(
            FeeRecord.school_id == school_id,
            FeeRecord.academic_year_id == ay.id,
            FeeRecord.student_id == student.id,
            FeePayment.is_active.is_(True),
        )
    )

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.order_by(FeePayment.payment_date.desc())
    query = query.offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    payments = result.scalars().all()

    items = []
    for payment in payments:
        fee_record = payment.fee_record
        receipt_id = f"RCP-{payment.payment_date.year}-{str(payment.id)[:5].upper()}"
        items.append({
            "id": payment.id,
            "fee_type": fee_record.fee_type if fee_record else "",
            "fee_category": fee_record.fee_category if fee_record else "academic",
            "description": fee_record.description if fee_record else None,
            "amount": payment.amount,
            "currency": "INR",
            "paid_date": payment.payment_date,
            "method": payment.payment_method,
            "transaction_id": payment.reference,
            "receipt_id": receipt_id,
            "receipt_url": f"/api/v1/student/fees/receipt/{payment.id}/",
            "status": "Paid",
            "metadata": payment.metadata_ or {},
        })

    paginated = paginate(items, total, pagination)
    paginated["metadata"] = {}
    return paginated


async def get_receipt(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    payment_id: uuid.UUID,
) -> dict:
    """Get payment receipt details."""
    student = await _get_student_from_user(db, user, school_id)

    # Get payment
    result = await db.execute(
        select(FeePayment)
        .join(FeeRecord, FeePayment.fee_record_id == FeeRecord.id)
        .where(
            FeePayment.id == payment_id,
            FeeRecord.school_id == school_id,
            FeeRecord.student_id == student.id,
            FeePayment.is_active.is_(True),
        )
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise NotFound("Payment receipt", str(payment_id))

    fee_record = payment.fee_record

    # Get school info
    school_result = await db.execute(select(School).where(School.id == school_id))
    school = school_result.scalar_one_or_none()

    class_section = await _get_student_class_section(db, student.id, school_id)
    receipt_id = f"RCP-{payment.payment_date.year}-{str(payment.id)[:5].upper()}"

    school_address = ""
    if school:
        parts = [p for p in [school.address_line1, school.city, school.state, school.pincode] if p]
        school_address = ", ".join(parts)

    return {
        "payment_id": payment.id,
        "receipt_id": receipt_id,
        "student_name": student.full_name,
        "roll_number": student.admission_number,
        "class_section": class_section,
        "fee_type": fee_record.fee_type if fee_record else "",
        "description": fee_record.description if fee_record else None,
        "amount": payment.amount,
        "currency": "INR",
        "paid_date": payment.payment_date,
        "method": payment.payment_method,
        "transaction_id": payment.reference,
        "school_name": school.name if school else "",
        "school_address": school_address,
        "download_url": f"/api/v1/student/fees/receipt/{payment.id}/download/",
        "content_type": "application/pdf",
        "generated_at": payment.created_at,
        "metadata": {},
    }


async def get_reminders(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
) -> dict:
    """Get fee reminders sent by admin relevant to this student."""
    student = await _get_student_from_user(db, user, school_id)
    ay = await _get_current_academic_year(db, school_id)

    # Get student's class info for filtering
    enrollment = await _get_student_enrollment(db, student.id, school_id, ay.id)
    class_name = None
    section_name = None
    if enrollment and enrollment.class_section:
        cs = enrollment.class_section
        if cs.class_:
            class_name = cs.class_.name
        if cs.section:
            section_name = cs.section.name

    # Get reminders targeting All, or the student's class/section, or Overdue
    query = select(FeeReminder).where(
        FeeReminder.school_id == school_id,
        FeeReminder.academic_year_id == ay.id,
        FeeReminder.is_active.is_(True),
    )

    result = await db.execute(query.order_by(FeeReminder.sent_at.desc()).limit(20))
    reminders = result.scalars().all()

    # Filter reminders relevant to this student
    items = []
    for reminder in reminders:
        target = reminder.target_group.lower()
        if target == "all":
            pass  # include
        elif target == "class" and reminder.class_name:
            if reminder.class_name != class_name:
                continue
        elif target == "section" and reminder.class_name and reminder.section:
            if reminder.class_name != class_name or reminder.section != section_name:
                continue
        elif target == "overdue":
            # Check if student has overdue fees
            overdue_result = await db.execute(
                select(func.count()).where(
                    FeeRecord.school_id == school_id,
                    FeeRecord.student_id == student.id,
                    FeeRecord.is_active.is_(True),
                    FeeRecord.due_date < date.today(),
                    FeeRecord.pending > 0,
                )
            )
            if (overdue_result.scalar() or 0) == 0:
                continue

        items.append({
            "id": reminder.id,
            "message": reminder.message,
            "sent_at": reminder.sent_at,
            "send_via": reminder.send_via,
            "target_group": reminder.target_group,
        })

    return {
        "count": len(items),
        "results": items,
    }
