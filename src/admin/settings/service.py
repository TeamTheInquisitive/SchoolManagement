from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.academic import Class, Section, Subject
from src.models.core import AcademicYear, EnumConfig, School, Settings


# ---------------------------------------------------------------------------
# Settings (generic key-value)
# ---------------------------------------------------------------------------


async def get_all_settings(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get all settings grouped by category, plus school profile and academic year."""
    # Fetch settings rows
    result = await db.execute(
        select(Settings).where(
            Settings.school_id == school_id, Settings.is_active.is_(True)
        )
    )
    settings_rows = result.scalars().all()

    # Group by category
    grouped: dict = {}
    for row in settings_rows:
        grouped.setdefault(row.category, {})[row.key] = row.value

    # Fetch school profile
    school_result = await db.execute(select(School).where(School.id == school_id))
    school = school_result.scalar_one_or_none()

    school_profile = {}
    if school:
        school_profile = {
            "school_name": school.name,
            "school_code": school.code,
            "logo_url": school.logo_url,
            "address": school.address_line1,
            "city": school.city,
            "state": school.state,
            "pin_code": school.pincode,
            "phone": school.phone,
            "email": school.email,
            "website": school.website,
            "principal_name": school.principal_name,
            "established_year": school.established_year,
            "board": school.board_affiliation,
            "metadata": {},
        }

    # Fetch academic year
    ay_result = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
            AcademicYear.is_active.is_(True),
        )
    )
    current_ay = ay_result.scalar_one_or_none()

    academic_year = {}
    if current_ay:
        terms_value = grouped.get("academic", {}).get("terms", [])
        academic_year = {
            "current": current_ay.name,
            "start_date": str(current_ay.start_date),
            "end_date": str(current_ay.end_date),
            "terms": terms_value if isinstance(terms_value, list) else [],
        }

    # Fetch classes
    classes_result = await db.execute(
        select(Class)
        .where(Class.school_id == school_id, Class.is_active.is_(True))
        .order_by(Class.sort_order)
    )
    classes = [c.name for c in classes_result.scalars().all()]

    # Fetch sections
    sections_result = await db.execute(
        select(Section)
        .where(Section.school_id == school_id, Section.is_active.is_(True))
        .order_by(Section.sort_order)
    )
    sections = [s.name for s in sections_result.scalars().all()]

    return {
        "school_profile": school_profile,
        "academic_year": academic_year,
        "classes": classes,
        "sections": sections,
        "working_days": grouped.get("general", {}).get("working_days", []),
        "fine_rules": grouped.get("fees", {}).get("fine_rules", {}),
        "notification_channels": grouped.get("notifications", {}).get("channels", []),
        "metadata": {},
    }


async def update_settings(
    db: AsyncSession, school_id: uuid.UUID, data: dict, updated_by: uuid.UUID
) -> list[str]:
    """Update settings by category/key. Returns list of updated fields."""
    updated_fields: list[str] = []

    category_key_map = {
        "fine_rules": ("fees", "fine_rules"),
        "working_days": ("general", "working_days"),
        "notification_channels": ("notifications", "channels"),
    }

    for field_name, value in data.items():
        if value is None:
            continue
        mapping = category_key_map.get(field_name)
        if not mapping:
            continue

        category, key = mapping

        result = await db.execute(
            select(Settings).where(
                Settings.school_id == school_id,
                Settings.category == category,
                Settings.key == key,
                Settings.is_active.is_(True),
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.value = value
            existing.updated_by = updated_by
        else:
            new_setting = Settings(
                school_id=school_id,
                category=category,
                key=key,
                value=value,
                created_by=updated_by,
            )
            db.add(new_setting)

        updated_fields.append(field_name)

    if updated_fields:
        await db.commit()

    return updated_fields


# ---------------------------------------------------------------------------
# School Profile
# ---------------------------------------------------------------------------


async def get_school_profile(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get school profile."""
    result = await db.execute(select(School).where(School.id == school_id))
    school = result.scalar_one_or_none()

    if not school:
        return {}

    return {
        "school_name": school.name,
        "school_code": school.code,
        "logo_url": school.logo_url,
        "address": school.address_line1,
        "city": school.city,
        "state": school.state,
        "pin_code": school.pincode,
        "phone": school.phone,
        "email": school.email,
        "website": school.website,
        "principal_name": school.principal_name,
        "established_year": school.established_year,
        "board": school.board_affiliation,
        "metadata": {},
    }


async def update_school_profile(
    db: AsyncSession, school_id: uuid.UUID, data: dict, updated_by: uuid.UUID
) -> tuple[str, list[str]]:
    """Update school profile. Returns (school_name, updated_fields)."""
    result = await db.execute(select(School).where(School.id == school_id))
    school = result.scalar_one_or_none()

    if not school:
        return "", []

    updated_fields: list[str] = []
    field_map = {
        "school_name": "name",
        "logo_url": "logo_url",
        "address": "address_line1",
        "city": "city",
        "state": "state",
        "pin_code": "pincode",
        "phone": "phone",
        "email": "email",
        "website": "website",
        "principal_name": "principal_name",
        "established_year": "established_year",
        "board": "board_affiliation",
    }

    for req_field, model_field in field_map.items():
        if req_field in data and data[req_field] is not None:
            setattr(school, model_field, data[req_field])
            updated_fields.append(req_field)

    if updated_fields:
        school.updated_by = updated_by
        await db.commit()
        await db.refresh(school)

    return school.name, updated_fields


# ---------------------------------------------------------------------------
# Academic Year
# ---------------------------------------------------------------------------


async def get_academic_year(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get current academic year configuration."""
    # Current year
    result = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
            AcademicYear.is_active.is_(True),
        )
    )
    current_ay = result.scalar_one_or_none()

    # Terms from settings
    terms_result = await db.execute(
        select(Settings).where(
            Settings.school_id == school_id,
            Settings.category == "academic",
            Settings.key == "terms",
            Settings.is_active.is_(True),
        )
    )
    terms_setting = terms_result.scalar_one_or_none()
    terms = terms_setting.value if terms_setting and isinstance(terms_setting.value, list) else []

    # Previous years
    prev_result = await db.execute(
        select(AcademicYear)
        .where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(False),
            AcademicYear.is_active.is_(True),
        )
        .order_by(AcademicYear.start_date.desc())
    )
    previous_years = [ay.name for ay in prev_result.scalars().all()]

    return {
        "current": current_ay.name if current_ay else None,
        "start_date": current_ay.start_date if current_ay else None,
        "end_date": current_ay.end_date if current_ay else None,
        "terms": terms,
        "previous_years": previous_years,
        "metadata": {},
    }


async def update_academic_year(
    db: AsyncSession, school_id: uuid.UUID, data: dict, updated_by: uuid.UUID
) -> dict:
    """Update academic year configuration."""
    current_name = data.get("current")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    terms = data.get("terms")

    # Update or create academic year record
    if current_name:
        result = await db.execute(
            select(AcademicYear).where(
                AcademicYear.school_id == school_id,
                AcademicYear.name == current_name,
                AcademicYear.is_active.is_(True),
            )
        )
        ay = result.scalar_one_or_none()

        if ay:
            if start_date:
                ay.start_date = start_date
            if end_date:
                ay.end_date = end_date
            ay.is_current = True
            ay.updated_by = updated_by
        else:
            # Create new academic year
            if start_date and end_date:
                # Unset previous current
                prev_result = await db.execute(
                    select(AcademicYear).where(
                        AcademicYear.school_id == school_id,
                        AcademicYear.is_current.is_(True),
                    )
                )
                for prev_ay in prev_result.scalars().all():
                    prev_ay.is_current = False

                new_ay = AcademicYear(
                    school_id=school_id,
                    name=current_name,
                    start_date=start_date,
                    end_date=end_date,
                    is_current=True,
                    created_by=updated_by,
                )
                db.add(new_ay)

    # Store terms in settings
    terms_count = 0
    if terms is not None:
        terms_data = [t if isinstance(t, dict) else t.model_dump(mode="json") for t in terms]
        terms_count = len(terms_data)

        result = await db.execute(
            select(Settings).where(
                Settings.school_id == school_id,
                Settings.category == "academic",
                Settings.key == "terms",
                Settings.is_active.is_(True),
            )
        )
        terms_setting = result.scalar_one_or_none()

        if terms_setting:
            terms_setting.value = terms_data
            terms_setting.updated_by = updated_by
        else:
            new_setting = Settings(
                school_id=school_id,
                category="academic",
                key="terms",
                value=terms_data,
                created_by=updated_by,
            )
            db.add(new_setting)

    await db.commit()

    return {
        "message": "Academic year configuration updated",
        "current": current_name,
        "terms_count": terms_count,
        "metadata": {},
    }


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


async def get_enum_values(
    db: AsyncSession, school_id: uuid.UUID, category: str
) -> dict:
    """Get enum values for a category."""
    result = await db.execute(
        select(EnumConfig)
        .where(
            EnumConfig.school_id == school_id,
            EnumConfig.category == category,
            EnumConfig.is_active.is_(True),
        )
        .order_by(EnumConfig.sort_order)
    )
    rows = result.scalars().all()

    values = [
        {
            "id": str(row.id),
            "code": row.value,
            "label": row.label,
            "is_active": row.is_active,
        }
        for row in rows
    ]

    return {
        "category": category,
        "values": values,
        "metadata": {},
    }


async def update_enum_values(
    db: AsyncSession,
    school_id: uuid.UUID,
    category: str,
    values: list[dict],
    updated_by: uuid.UUID,
) -> dict:
    """Add or update enum values for a category."""
    added = 0
    updated = 0
    added_codes: list[str] = []
    updated_codes: list[str] = []

    for item in values:
        code = item["code"]
        label = item["label"]
        is_active = item.get("is_active", True)

        result = await db.execute(
            select(EnumConfig).where(
                EnumConfig.school_id == school_id,
                EnumConfig.category == category,
                EnumConfig.value == code,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.label = label
            existing.is_active = is_active
            existing.updated_by = updated_by
            updated += 1
            updated_codes.append(code)
        else:
            new_enum = EnumConfig(
                school_id=school_id,
                category=category,
                value=code,
                label=label,
                is_active=is_active,
                sort_order=0,
                created_by=updated_by,
            )
            db.add(new_enum)
            added += 1
            added_codes.append(code)

    await db.commit()

    parts = []
    if added_codes:
        parts.append(f"Added: {', '.join(added_codes)}.")
    if updated_codes:
        parts.append(f"Updated: {', '.join(updated_codes)}.")

    message = f"{category.replace('_', ' ').title()} updated. {' '.join(parts)}"

    return {
        "category": category,
        "added": added,
        "updated": updated,
        "message": message,
        "metadata": {},
    }


# ---------------------------------------------------------------------------
# Bulk: Classes
# ---------------------------------------------------------------------------


async def bulk_create_classes(
    db: AsyncSession,
    school_id: uuid.UUID,
    class_names: list[str],
    created_by: uuid.UUID,
) -> int:
    """Bulk create classes. Skips already existing ones. Returns created count."""
    created = 0
    for idx, name in enumerate(class_names):
        result = await db.execute(
            select(Class).where(
                Class.school_id == school_id,
                Class.name == name,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            continue

        new_class = Class(
            school_id=school_id,
            name=name,
            display_name=f"Class {name}",
            sort_order=idx + 1,
            created_by=created_by,
        )
        db.add(new_class)
        created += 1

    if created:
        await db.commit()

    return created


# ---------------------------------------------------------------------------
# Bulk: Sections
# ---------------------------------------------------------------------------


async def bulk_create_sections(
    db: AsyncSession,
    school_id: uuid.UUID,
    section_names: list[str],
    created_by: uuid.UUID,
) -> int:
    """Bulk create sections. Skips already existing ones. Returns created count."""
    created = 0
    for idx, name in enumerate(section_names):
        result = await db.execute(
            select(Section).where(
                Section.school_id == school_id,
                Section.name == name,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            continue

        new_section = Section(
            school_id=school_id,
            name=name,
            sort_order=idx + 1,
            created_by=created_by,
        )
        db.add(new_section)
        created += 1

    if created:
        await db.commit()

    return created


# ---------------------------------------------------------------------------
# Bulk: Subjects
# ---------------------------------------------------------------------------


async def bulk_create_subjects(
    db: AsyncSession,
    school_id: uuid.UUID,
    subjects: list[dict],
    created_by: uuid.UUID,
) -> int:
    """Bulk create subjects. Skips already existing ones. Returns created count."""
    created = 0
    for item in subjects:
        name = item["name"]
        code = item.get("code")

        # Check if subject with same name exists
        result = await db.execute(
            select(Subject).where(
                Subject.school_id == school_id,
                Subject.name == name,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            continue

        new_subject = Subject(
            school_id=school_id,
            name=name,
            code=code,
            created_by=created_by,
        )
        db.add(new_subject)
        created += 1

    if created:
        await db.commit()

    return created


# ---------------------------------------------------------------------------
# Class Sections Lookup
# ---------------------------------------------------------------------------


async def list_class_sections(db: AsyncSession, school_id: uuid.UUID) -> list[dict]:
    """List all class-section combinations with UUIDs."""
    from src.models.academic import ClassSection

    result = await db.execute(
        select(ClassSection).where(ClassSection.school_id == school_id)
    )
    sections = result.scalars().all()
    return [
        {
            "id": str(cs.id),
            "class_name": cs.class_.name if cs.class_ else "",
            "section": cs.section.name if cs.section else "",
        }
        for cs in sections
    ]


async def list_subjects(db: AsyncSession, school_id: uuid.UUID) -> list[dict]:
    """List all subjects for dropdowns."""
    from src.models.academic import Subject

    result = await db.execute(
        select(Subject).where(Subject.school_id == school_id, Subject.is_active.is_(True))
    )
    subjects = result.scalars().all()
    return [
        {"id": str(s.id), "name": s.name, "code": s.code}
        for s in subjects
    ]
