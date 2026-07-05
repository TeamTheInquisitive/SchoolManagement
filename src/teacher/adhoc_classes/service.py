from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFound
from src.core.pagination import PaginationParams, paginate
from src.models.academic import Class, ClassSection, Section, Subject
from src.models.adhoc_class import AdhocClass
from src.models.core import AcademicYear, User


async def _get_current_academic_year(db: AsyncSession, school_id: uuid.UUID) -> AcademicYear:
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
        result = await db.execute(
            select(AcademicYear)
            .where(
                AcademicYear.school_id == school_id,
                AcademicYear.is_active.is_(True),
            )
            .order_by(AcademicYear.start_date.desc())
            .limit(1)
        )
        ay = result.scalar_one_or_none()
    return ay


async def _resolve_class_section(
    db: AsyncSession, school_id: uuid.UUID, class_name: str, section: str
) -> ClassSection | None:
    """Resolve class_name + section to a ClassSection."""
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
    """Resolve subject name to Subject model."""
    result = await db.execute(
        select(Subject).where(
            Subject.school_id == school_id,
            Subject.name == subject_name,
            Subject.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


async def _build_response(adhoc: AdhocClass, db: AsyncSession) -> dict:
    """Build response dict for an AdhocClass."""
    # Get class name + section
    cs_result = await db.execute(
        select(Class.name, Section.name)
        .select_from(ClassSection)
        .join(Class, ClassSection.class_id == Class.id)
        .join(Section, ClassSection.section_id == Section.id)
        .where(ClassSection.id == adhoc.class_section_id)
    )
    cs_row = cs_result.one_or_none()
    class_name = cs_row[0] if cs_row else ""
    section_name = cs_row[1] if cs_row else ""

    # Get subject name
    subj_result = await db.execute(
        select(Subject.name).where(Subject.id == adhoc.subject_id)
    )
    subject_name = subj_result.scalar_one_or_none() or ""

    return {
        "id": adhoc.id,
        "staff_id": adhoc.staff_id,
        "class_name": class_name,
        "section": section_name,
        "subject": subject_name,
        "date": adhoc.date,
        "start_time": adhoc.start_time,
        "end_time": adhoc.end_time,
        "duration_minutes": adhoc.duration_minutes,
        "type": adhoc.type,
        "reason": adhoc.reason,
        "original_staff_id": adhoc.original_staff_id,
        "topic": adhoc.topic,
        "notes": adhoc.notes,
        "description": adhoc.description,
        "student_count": adhoc.student_count,
        "status": adhoc.status,
        "created_at": adhoc.created_at,
    }


async def list_adhoc_classes(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    pagination: PaginationParams,
    status: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> dict:
    """List adhoc classes for the teacher."""
    staff_id = user.staff_id

    base_filter = and_(
        AdhocClass.school_id == school_id,
        AdhocClass.staff_id == staff_id,
        AdhocClass.is_active.is_(True),
    )

    filters = [base_filter]
    if status:
        filters.append(AdhocClass.status == status)
    if from_date:
        filters.append(AdhocClass.date >= from_date)
    if to_date:
        filters.append(AdhocClass.date <= to_date)

    # Count
    count_query = select(func.count(AdhocClass.id)).where(*filters)
    total = (await db.execute(count_query)).scalar() or 0

    # Results
    query = (
        select(AdhocClass)
        .where(*filters)
        .order_by(AdhocClass.date.desc(), AdhocClass.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    )
    result = await db.execute(query)
    records = result.scalars().all()

    items = []
    for record in records:
        items.append(await _build_response(record, db))

    return paginate(items, total, pagination)


async def create_adhoc_class(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    data: dict,
) -> dict:
    """Create a new adhoc class."""
    staff_id = user.staff_id
    ay = await _get_current_academic_year(db, school_id)

    # Resolve class section
    cs = await _resolve_class_section(db, school_id, data["class_name"], data["section"])
    if not cs:
        raise NotFound("ClassSection", f"{data['class_name']}-{data['section']}")

    # Resolve subject
    subject = await _resolve_subject(db, school_id, data["subject"])
    if not subject:
        raise NotFound("Subject", data["subject"])

    adhoc = AdhocClass(
        school_id=school_id,
        academic_year_id=ay.id if ay else None,
        staff_id=staff_id,
        class_section_id=cs.id,
        subject_id=subject.id,
        date=data["date"],
        start_time=data.get("start_time"),
        end_time=data.get("end_time"),
        duration_minutes=data.get("duration_minutes"),
        type=data["type"],
        reason=data.get("reason"),
        original_staff_id=data.get("original_staff_id"),
        topic=data.get("topic"),
        notes=data.get("notes"),
        description=data.get("description"),
        student_count=data.get("student_count", 0),
        status="Scheduled",
    )
    db.add(adhoc)
    await db.commit()
    await db.refresh(adhoc)
    return await _build_response(adhoc, db)


async def update_adhoc_class(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    adhoc_id: uuid.UUID,
    data: dict,
) -> dict:
    """Update an adhoc class (mark done, add notes, student_count)."""
    staff_id = user.staff_id

    result = await db.execute(
        select(AdhocClass).where(
            AdhocClass.id == adhoc_id,
            AdhocClass.school_id == school_id,
            AdhocClass.staff_id == staff_id,
            AdhocClass.is_active.is_(True),
        )
    )
    adhoc = result.scalar_one_or_none()
    if not adhoc:
        raise NotFound("AdhocClass", str(adhoc_id))

    update_data = {k: v for k, v in data.items() if v is not None}
    for key, value in update_data.items():
        setattr(adhoc, key, value)

    await db.commit()
    await db.refresh(adhoc)
    return await _build_response(adhoc, db)


async def delete_adhoc_class(
    db: AsyncSession,
    school_id: uuid.UUID,
    user: User,
    adhoc_id: uuid.UUID,
) -> dict:
    """Soft-delete (cancel) an adhoc class."""
    staff_id = user.staff_id

    result = await db.execute(
        select(AdhocClass).where(
            AdhocClass.id == adhoc_id,
            AdhocClass.school_id == school_id,
            AdhocClass.staff_id == staff_id,
            AdhocClass.is_active.is_(True),
        )
    )
    adhoc = result.scalar_one_or_none()
    if not adhoc:
        raise NotFound("AdhocClass", str(adhoc_id))

    adhoc.status = "Cancelled"
    adhoc.is_active = False
    await db.commit()

    return {
        "id": adhoc.id,
        "status": "Cancelled",
        "message": "Adhoc class cancelled successfully.",
    }
