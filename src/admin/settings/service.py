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

    # Validate: if both dates provided, end must be after start
    if start_date and end_date and end_date <= start_date:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

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


async def list_academic_years(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """List all academic years for a school."""
    result = await db.execute(
        select(AcademicYear)
        .where(AcademicYear.school_id == school_id, AcademicYear.is_active.is_(True))
        .order_by(AcademicYear.start_date.desc())
    )
    years = result.scalars().all()
    return {
        "academic_years": [
            {
                "id": str(ay.id),
                "name": ay.name,
                "start_date": str(ay.start_date),
                "end_date": str(ay.end_date),
                "is_current": ay.is_current,
            }
            for ay in years
        ]
    }


async def create_academic_year(
    db: AsyncSession, school_id: uuid.UUID, data: dict, created_by: uuid.UUID
) -> dict:
    """Create a new academic year."""
    from datetime import date as date_type

    name = data.get("name")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    set_current = data.get("is_current", False)

    if not name or not start_date or not end_date:
        from src.core.exceptions import ValidationError
        raise ValidationError("name, start_date, and end_date are required")

    if end_date <= start_date:
        from src.core.exceptions import ValidationError
        raise ValidationError("end_date must be after start_date")

    # Check duplicate
    existing = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == school_id, AcademicYear.name == name, AcademicYear.is_active.is_(True)
        )
    )
    if existing.scalar_one_or_none():
        from src.core.exceptions import ConflictError
        raise ConflictError(f"Academic year '{name}' already exists")

    if set_current:
        # Unset previous current
        prev = await db.execute(
            select(AcademicYear).where(AcademicYear.school_id == school_id, AcademicYear.is_current.is_(True))
        )
        for ay in prev.scalars().all():
            ay.is_current = False

    new_ay = AcademicYear(
        school_id=school_id,
        name=name,
        start_date=start_date,
        end_date=end_date,
        is_current=set_current,
        created_by=created_by,
    )
    db.add(new_ay)
    await db.commit()
    await db.refresh(new_ay)
    return {"id": str(new_ay.id), "name": new_ay.name, "start_date": str(new_ay.start_date), "end_date": str(new_ay.end_date), "is_current": new_ay.is_current}


async def update_academic_year_by_id(
    db: AsyncSession, school_id: uuid.UUID, year_id: str, data: dict, updated_by: uuid.UUID
) -> dict:
    """Update an academic year by ID."""
    # Validate name is not empty if provided
    if "name" in data and (not data["name"] or not str(data["name"]).strip()):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Academic year name must not be empty")

    result = await db.execute(
        select(AcademicYear).where(AcademicYear.id == year_id, AcademicYear.school_id == school_id, AcademicYear.is_active.is_(True))
    )
    ay = result.scalar_one_or_none()
    if not ay:
        from src.core.exceptions import NotFound
        raise NotFound("Academic Year", year_id)

    # Validate end_date > start_date considering both existing and new values
    new_start = data.get("start_date", ay.start_date)
    new_end = data.get("end_date", ay.end_date)
    if new_start and new_end and new_end <= new_start:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

    if "name" in data:
        ay.name = data["name"]
    if "start_date" in data:
        ay.start_date = data["start_date"]
    if "end_date" in data:
        ay.end_date = data["end_date"]
    ay.updated_by = updated_by
    await db.commit()
    return {"id": str(ay.id), "name": ay.name, "start_date": str(ay.start_date), "end_date": str(ay.end_date), "is_current": ay.is_current}


async def delete_academic_year(db: AsyncSession, school_id: uuid.UUID, year_id: str) -> dict:
    """Soft delete an academic year."""
    result = await db.execute(
        select(AcademicYear).where(AcademicYear.id == year_id, AcademicYear.school_id == school_id, AcademicYear.is_active.is_(True))
    )
    ay = result.scalar_one_or_none()
    if not ay:
        from src.core.exceptions import NotFound
        raise NotFound("Academic Year", year_id)
    if ay.is_current:
        from src.core.exceptions import ValidationError
        raise ValidationError("Cannot delete the current academic year")
    ay.is_active = False
    await db.commit()
    return {"message": f"Academic year '{ay.name}' deleted"}


async def set_current_academic_year(db: AsyncSession, school_id: uuid.UUID, year_id: str) -> dict:
    """Set an academic year as current."""
    result = await db.execute(
        select(AcademicYear).where(AcademicYear.id == year_id, AcademicYear.school_id == school_id, AcademicYear.is_active.is_(True))
    )
    ay = result.scalar_one_or_none()
    if not ay:
        from src.core.exceptions import NotFound
        raise NotFound("Academic Year", year_id)

    # Unset all others
    prev = await db.execute(
        select(AcademicYear).where(AcademicYear.school_id == school_id, AcademicYear.is_current.is_(True))
    )
    for prev_ay in prev.scalars().all():
        prev_ay.is_current = False

    ay.is_current = True
    await db.commit()
    return {"message": f"'{ay.name}' set as current academic year"}


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
    """Bulk create classes. Reactivates soft-deleted ones. Skips active duplicates."""
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
            if not existing.is_active:
                existing.is_active = True
                existing.deleted_at = None
                existing.deleted_by = None
                existing.updated_by = created_by
                created += 1
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
# Delete: Class
# ---------------------------------------------------------------------------


async def delete_class(
    db: AsyncSession, school_id: uuid.UUID, class_id: str, user_id: uuid.UUID
) -> dict:
    """Soft-delete a class and its associated class-section mappings."""
    from src.models.academic import ClassSection
    from datetime import datetime, timezone

    result = await db.execute(
        select(Class).where(
            Class.id == class_id, Class.school_id == school_id, Class.is_active.is_(True)
        )
    )
    cls = result.scalar_one_or_none()
    if not cls:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Class not found")

    now = datetime.now(timezone.utc)
    cls.is_active = False
    cls.deleted_by = user_id
    cls.deleted_at = now

    cs_result = await db.execute(
        select(ClassSection).where(
            ClassSection.school_id == school_id,
            ClassSection.class_id == cls.id,
            ClassSection.is_active.is_(True),
        )
    )
    for cs in cs_result.scalars().all():
        cs.is_active = False
        cs.deleted_by = user_id
        cs.deleted_at = now

    await db.commit()
    return {"message": f"Class '{cls.display_name or cls.name}' deleted"}


# ---------------------------------------------------------------------------
# Delete: Class-Section mapping
# ---------------------------------------------------------------------------


async def delete_class_section(
    db: AsyncSession, school_id: uuid.UUID, class_section_id: str, user_id: uuid.UUID
) -> dict:
    """Soft-delete a class-section mapping."""
    from src.models.academic import ClassSection
    from datetime import datetime, timezone

    result = await db.execute(
        select(ClassSection).where(
            ClassSection.id == class_section_id,
            ClassSection.school_id == school_id,
            ClassSection.is_active.is_(True),
        )
    )
    cs = result.scalar_one_or_none()
    if not cs:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Section not found")

    cs.is_active = False
    cs.deleted_by = user_id
    cs.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "Section removed from class"}


# ---------------------------------------------------------------------------
# Bulk: Sections
# ---------------------------------------------------------------------------


async def bulk_create_sections(
    db: AsyncSession,
    school_id: uuid.UUID,
    section_names: list[str],
    created_by: uuid.UUID,
    class_id: str | None = None,
) -> int:
    """Bulk create sections and optionally link to a class. Skips already existing ones."""
    from src.models.academic import ClassSection
    from src.models.core import AcademicYear

    created = 0
    section_ids = []

    for idx, name in enumerate(section_names):
        result = await db.execute(
            select(Section).where(
                Section.school_id == school_id,
                Section.name == name,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            if not existing.is_active:
                existing.is_active = True
                existing.deleted_at = None
                existing.deleted_by = None
                existing.updated_by = created_by
                created += 1
            section_ids.append(existing.id)
            continue

        new_section = Section(
            school_id=school_id,
            name=name,
            sort_order=idx + 1,
            created_by=created_by,
        )
        db.add(new_section)
        await db.flush()
        section_ids.append(new_section.id)
        created += 1

    # Link sections to class if class_id provided
    if class_id and section_ids:
        # Get current academic year
        ay_result = await db.execute(
            select(AcademicYear).where(AcademicYear.school_id == school_id, AcademicYear.is_current.is_(True))
        )
        academic_year = ay_result.scalar_one_or_none()
        ay_id = academic_year.id if academic_year else None

        for section_id in section_ids:
            # Check if mapping already exists
            existing_cs = await db.execute(
                select(ClassSection).where(
                    ClassSection.school_id == school_id,
                    ClassSection.class_id == class_id,
                    ClassSection.section_id == section_id,
                )
            )
            if existing_cs.scalar_one_or_none():
                continue
            cs = ClassSection(
                school_id=school_id,
                class_id=class_id,
                section_id=section_id,
                academic_year_id=ay_id,
                created_by=created_by,
            )
            db.add(cs)

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
    """Bulk create subjects. Reactivates soft-deleted ones. Skips active duplicates."""
    # Validate subject names are not empty
    for item in subjects:
        if not item.get("name") or not str(item["name"]).strip():
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Subject name must not be empty")

    created = 0
    for item in subjects:
        name = item["name"]
        code = item.get("code")

        result = await db.execute(
            select(Subject).where(
                Subject.school_id == school_id,
                Subject.name == name,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            if not existing.is_active:
                existing.is_active = True
                existing.deleted_at = None
                existing.deleted_by = None
                existing.updated_by = created_by
                if code:
                    existing.code = code
                created += 1
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


async def list_class_sections(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """List all classes grouped with their sections."""
    from src.models.academic import Class, Section, ClassSection

    # Get all classes for this school
    classes_result = await db.execute(
        select(Class).where(Class.school_id == school_id, Class.is_active.is_(True)).order_by(Class.sort_order)
    )
    classes = classes_result.scalars().all()

    # Get all class-section mappings
    cs_result = await db.execute(
        select(ClassSection).where(ClassSection.school_id == school_id, ClassSection.is_active.is_(True))
    )
    class_sections = cs_result.scalars().all()

    # Group sections by class_id
    sections_by_class = {}
    for cs in class_sections:
        if cs.class_id not in sections_by_class:
            sections_by_class[cs.class_id] = []
        sections_by_class[cs.class_id].append({
            "id": str(cs.id),
            "section_name": cs.section.name if cs.section else "",
        })

    return {
        "classes": [
            {
                "id": str(c.id),
                "name": c.name,
                "display_name": c.display_name,
                "sections": sections_by_class.get(c.id, []),
            }
            for c in classes
        ]
    }


async def list_subjects(db: AsyncSession, school_id: uuid.UUID) -> list[dict]:
    """List all subjects for dropdowns."""
    from src.models.academic import Subject

    result = await db.execute(
        select(Subject).where(Subject.school_id == school_id, Subject.is_active.is_(True))
    )
    subjects = result.scalars().all()
    return [
        {"id": str(s.id), "name": s.name, "code": s.code, "class_ids": s.metadata_.get("class_ids", [])}
        for s in subjects
    ]


async def update_subject(
    db: AsyncSession, school_id: uuid.UUID, subject_id: str, data: dict, user_id: uuid.UUID
) -> dict:
    """Update a subject's name and/or code."""
    from src.models.academic import Subject

    # Validate name is not empty if provided
    if "name" in data and (not data["name"] or not str(data["name"]).strip()):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Subject name must not be empty")

    result = await db.execute(
        select(Subject).where(
            Subject.id == subject_id, Subject.school_id == school_id, Subject.is_active.is_(True)
        )
    )
    subject = result.scalar_one_or_none()
    if not subject:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Subject not found")

    if "name" in data:
        subject.name = data["name"]
    if "code" in data:
        subject.code = data["code"]
    subject.updated_by = user_id
    await db.commit()
    await db.refresh(subject)
    return {"id": str(subject.id), "name": subject.name, "code": subject.code}


async def delete_subject(
    db: AsyncSession, school_id: uuid.UUID, subject_id: str, user_id: uuid.UUID
) -> None:
    """Soft-delete a subject."""
    from src.models.academic import Subject

    result = await db.execute(
        select(Subject).where(
            Subject.id == subject_id, Subject.school_id == school_id, Subject.is_active.is_(True)
        )
    )
    subject = result.scalar_one_or_none()
    if not subject:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Subject not found")

    subject.is_active = False
    subject.deleted_by = user_id
    from datetime import datetime, timezone
    subject.deleted_at = datetime.now(timezone.utc)
    await db.commit()


async def assign_classes_to_subject(
    db: AsyncSession, school_id: uuid.UUID, subject_id: str, class_ids: list[str]
) -> dict:
    """Assign classes to a subject via metadata."""
    from src.models.academic import Subject

    result = await db.execute(
        select(Subject).where(Subject.id == subject_id, Subject.school_id == school_id)
    )
    subject = result.scalar_one_or_none()
    if not subject:
        from src.core.exceptions import NotFound
        raise NotFound("Subject", subject_id)

    meta = dict(subject.metadata_) if subject.metadata_ else {}
    meta["class_ids"] = class_ids
    subject.metadata_ = meta
    await db.commit()
    return {"id": str(subject.id), "name": subject.name, "class_ids": class_ids}


# ---------------------------------------------------------------------------
# Class-Subject Mapping
# ---------------------------------------------------------------------------


async def get_class_subjects(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get subjects grouped by class for the current academic year."""
    from src.models.academic import Class, ClassSubject, Subject
    from src.models.core import AcademicYear

    ay_result = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
            AcademicYear.is_active.is_(True),
        )
    )
    current_ay = ay_result.scalar_one_or_none()
    if not current_ay:
        return {"academic_year": None, "classes": []}

    classes_result = await db.execute(
        select(Class)
        .where(Class.school_id == school_id, Class.is_active.is_(True))
        .order_by(Class.sort_order)
    )
    classes = classes_result.scalars().all()

    cs_result = await db.execute(
        select(ClassSubject).where(
            ClassSubject.school_id == school_id,
            ClassSubject.academic_year_id == current_ay.id,
            ClassSubject.is_active.is_(True),
        )
    )
    class_subjects = cs_result.scalars().all()

    subj_result = await db.execute(
        select(Subject).where(Subject.school_id == school_id, Subject.is_active.is_(True))
    )
    subjects_map = {s.id: s for s in subj_result.scalars().all()}

    subjects_by_class: dict = {}
    for cs in class_subjects:
        subjects_by_class.setdefault(cs.class_id, [])
        subj = subjects_map.get(cs.subject_id)
        if subj:
            subjects_by_class[cs.class_id].append(
                {"id": str(subj.id), "name": subj.name, "code": subj.code}
            )

    return {
        "academic_year": current_ay.name,
        "classes": [
            {
                "id": str(c.id),
                "name": c.name,
                "display_name": c.display_name or f"Class {c.name}",
                "subjects": subjects_by_class.get(c.id, []),
            }
            for c in classes
        ],
    }


async def update_class_subjects(
    db: AsyncSession,
    school_id: uuid.UUID,
    class_id: str,
    subject_ids: list[str],
    updated_by: uuid.UUID,
) -> dict:
    """Replace all subject assignments for a class in the current academic year."""
    from src.models.academic import ClassSubject
    from src.models.core import AcademicYear

    ay_result = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
            AcademicYear.is_active.is_(True),
        )
    )
    current_ay = ay_result.scalar_one_or_none()
    if not current_ay:
        return {"message": "No active academic year found"}

    existing_result = await db.execute(
        select(ClassSubject).where(
            ClassSubject.school_id == school_id,
            ClassSubject.class_id == class_id,
            ClassSubject.academic_year_id == current_ay.id,
            ClassSubject.is_active.is_(True),
        )
    )
    existing = existing_result.scalars().all()
    existing_subject_ids = {str(cs.subject_id) for cs in existing}

    new_subject_ids = set(subject_ids)

    # Delete removed
    for cs in existing:
        if str(cs.subject_id) not in new_subject_ids:
            await db.delete(cs)

    # Add new
    for sid in new_subject_ids - existing_subject_ids:
        db.add(ClassSubject(
            school_id=school_id,
            class_id=class_id,
            subject_id=sid,
            academic_year_id=current_ay.id,
            created_by=updated_by,
        ))

    await db.commit()
    return {"message": "Class subjects updated", "class_id": class_id, "subject_count": len(subject_ids)}


# ---------------------------------------------------------------------------
# Fee Structures
# ---------------------------------------------------------------------------


async def list_fee_structures(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """List all fee structures grouped by class, with section overrides."""
    from src.models.fee import FeeStructure
    from src.models.academic import Class, ClassSection

    # Get current academic year
    ay_result = await db.execute(
        select(AcademicYear).where(AcademicYear.school_id == school_id, AcademicYear.is_current.is_(True))
    )
    academic_year = ay_result.scalar_one_or_none()

    query = select(FeeStructure).where(
        FeeStructure.school_id == school_id, FeeStructure.is_active.is_(True)
    )
    if academic_year:
        query = query.where(FeeStructure.academic_year_id == academic_year.id)

    result = await db.execute(query)
    structures = result.scalars().all()

    # Get classes
    class_result = await db.execute(
        select(Class).where(Class.school_id == school_id, Class.is_active.is_(True)).order_by(Class.sort_order)
    )
    classes = class_result.scalars().all()

    # Get class_sections for section-specific display
    cs_result = await db.execute(
        select(ClassSection).where(ClassSection.school_id == school_id, ClassSection.is_active.is_(True))
    )
    class_sections = cs_result.scalars().all()

    def serialize_fs(fs):
        return {
            "id": str(fs.id),
            "fee_type": fs.fee_type,
            "fee_category": fs.fee_category,
            "amount": float(fs.amount),
            "frequency": fs.frequency,
            "class_id": str(fs.class_id) if fs.class_id else None,
            "class_section_id": str(fs.class_section_id) if fs.class_section_id else None,
        }

    return {
        "academic_year": academic_year.name if academic_year else None,
        "structures": [serialize_fs(fs) for fs in structures],
        "classes": [
            {"id": str(c.id), "name": c.name, "display_name": c.display_name}
            for c in classes
        ],
        "class_sections": [
            {"id": str(cs.id), "class_id": str(cs.class_id), "display_name": f"Class {cs.class_.name} - {cs.section.name}" if cs.section else f"Class {cs.class_.name}"}
            for cs in class_sections
        ],
    }


async def create_fee_structure(
    db: AsyncSession, school_id: uuid.UUID, data: dict, created_by: uuid.UUID
) -> dict:
    """Create a fee structure."""
    from src.models.fee import FeeStructure, FeeRecord
    from src.models.student import StudentEnrollment
    from src.models.academic import ClassSection
    from decimal import Decimal
    from datetime import date, timedelta

    ay_result = await db.execute(
        select(AcademicYear).where(AcademicYear.school_id == school_id, AcademicYear.is_current.is_(True))
    )
    academic_year = ay_result.scalar_one_or_none()
    if not academic_year:
        from src.core.exceptions import ValidationError
        raise ValidationError("No current academic year set")

    if not data.get("amount") or float(data["amount"]) <= 0:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Fee amount must be greater than zero")

    fs = FeeStructure(
        school_id=school_id,
        academic_year_id=academic_year.id,
        class_id=data.get("class_id") or None,
        class_section_id=data.get("class_section_id") or None,
        fee_type=data["fee_type"],
        fee_category=data.get("fee_category", "tuition"),
        amount=data["amount"],
        frequency=data.get("frequency", "monthly"),
        created_by=created_by,
    )
    db.add(fs)
    await db.flush()

    # Create FeeRecords for existing students in the applicable class/section
    enrollments = []

    if fs.class_section_id:
        # Specific section - query enrollments directly by class_section_id
        enrollment_result = await db.execute(
            select(StudentEnrollment).where(
                StudentEnrollment.school_id == school_id,
                StudentEnrollment.academic_year_id == academic_year.id,
                StudentEnrollment.class_section_id == fs.class_section_id,
                StudentEnrollment.status == "Active",
                StudentEnrollment.is_active.is_(True),
            )
        )
        enrollments = enrollment_result.scalars().all()
    elif fs.class_id:
        # Specific class - find all class_sections for this class in the current academic year
        cs_result = await db.execute(
            select(ClassSection.id).where(
                ClassSection.school_id == school_id,
                ClassSection.class_id == fs.class_id,
                ClassSection.academic_year_id == academic_year.id,
                ClassSection.is_active.is_(True),
            )
        )
        cs_ids = [row[0] for row in cs_result.all()]

        if cs_ids:
            enrollment_result = await db.execute(
                select(StudentEnrollment).where(
                    StudentEnrollment.school_id == school_id,
                    StudentEnrollment.academic_year_id == academic_year.id,
                    StudentEnrollment.class_section_id.in_(cs_ids),
                    StudentEnrollment.status == "Active",
                    StudentEnrollment.is_active.is_(True),
                )
            )
            enrollments = enrollment_result.scalars().all()
        else:
            # Fallback: class_sections may not have academic_year_id set or may
            # use is_active alone. Try without the academic_year filter.
            cs_result_fallback = await db.execute(
                select(ClassSection.id).where(
                    ClassSection.school_id == school_id,
                    ClassSection.class_id == fs.class_id,
                    ClassSection.is_active.is_(True),
                )
            )
            cs_ids_fallback = [row[0] for row in cs_result_fallback.all()]
            if cs_ids_fallback:
                enrollment_result = await db.execute(
                    select(StudentEnrollment).where(
                        StudentEnrollment.school_id == school_id,
                        StudentEnrollment.academic_year_id == academic_year.id,
                        StudentEnrollment.class_section_id.in_(cs_ids_fallback),
                        StudentEnrollment.status == "Active",
                        StudentEnrollment.is_active.is_(True),
                    )
                )
                enrollments = enrollment_result.scalars().all()
    else:
        # All classes - get all enrolled students for the current academic year
        enrollment_result = await db.execute(
            select(StudentEnrollment).where(
                StudentEnrollment.school_id == school_id,
                StudentEnrollment.academic_year_id == academic_year.id,
                StudentEnrollment.status == "Active",
                StudentEnrollment.is_active.is_(True),
            )
        )
        enrollments = enrollment_result.scalars().all()

    due_date = date.today() + timedelta(days=30)
    amount = Decimal(str(data["amount"]))

    for enrollment in enrollments:
        record = FeeRecord(
            school_id=school_id,
            academic_year_id=academic_year.id,
            student_id=enrollment.student_id,
            fee_structure_id=fs.id,
            fee_type=fs.fee_type,
            fee_category=fs.fee_category,
            total_amount=amount,
            concession_amount=Decimal("0"),
            paid=Decimal("0"),
            pending=amount,
            total_late_fee=Decimal("0"),
            due_date=due_date,
            status="Pending",
            description=f"Auto-generated from fee structure ({fs.frequency})",
            is_active=True,
            created_by=created_by,
        )
        db.add(record)

    records_created = len(enrollments)
    await db.commit()
    await db.refresh(fs)
    return {
        "id": str(fs.id),
        "fee_type": fs.fee_type,
        "fee_category": fs.fee_category,
        "amount": float(fs.amount),
        "frequency": fs.frequency,
        "records_created": records_created,
    }


async def update_fee_structure(
    db: AsyncSession, school_id: uuid.UUID, structure_id: str, data: dict, updated_by: uuid.UUID
) -> dict:
    """Update a fee structure."""
    from src.models.fee import FeeStructure

    result = await db.execute(
        select(FeeStructure).where(FeeStructure.id == structure_id, FeeStructure.school_id == school_id, FeeStructure.is_active.is_(True))
    )
    fs = result.scalar_one_or_none()
    if not fs:
        from src.core.exceptions import NotFound
        raise NotFound("Fee Structure", structure_id)

    if "fee_type" in data:
        fs.fee_type = data["fee_type"]
    if "amount" in data:
        fs.amount = data["amount"]
    if "frequency" in data:
        fs.frequency = data["frequency"]
    if "fee_category" in data:
        fs.fee_category = data["fee_category"]
    if "class_id" in data:
        fs.class_id = data["class_id"] or None
    if "class_section_id" in data:
        fs.class_section_id = data["class_section_id"] or None
    fs.updated_by = updated_by
    await db.commit()
    return {"id": str(fs.id), "fee_type": fs.fee_type, "amount": float(fs.amount), "frequency": fs.frequency}


async def delete_fee_structure(db: AsyncSession, school_id: uuid.UUID, structure_id: str) -> dict:
    """Soft delete a fee structure."""
    from src.models.fee import FeeStructure

    result = await db.execute(
        select(FeeStructure).where(FeeStructure.id == structure_id, FeeStructure.school_id == school_id, FeeStructure.is_active.is_(True))
    )
    fs = result.scalar_one_or_none()
    if not fs:
        from src.core.exceptions import NotFound
        raise NotFound("Fee Structure", structure_id)
    fs.is_active = False
    await db.commit()
    return {"message": "Fee structure deleted"}


# ---------------------------------------------------------------------------
# ID Auto-Generation
# ---------------------------------------------------------------------------

DEFAULT_ID_CONFIG = {
    "student": {"enabled": True, "pattern": "STU{YY}{SEQ:4}", "next_seq": 1},
    "teacher": {"enabled": True, "pattern": "TCH{YY}{SEQ:4}", "next_seq": 1},
    "staff": {"enabled": True, "pattern": "STF{YY}{SEQ:4}", "next_seq": 1},
}


async def get_id_generation_config(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get ID auto-generation config."""
    import re

    result = await db.execute(
        select(Settings).where(
            Settings.school_id == school_id,
            Settings.category == "id_generation",
            Settings.key == "config",
            Settings.is_active.is_(True),
        )
    )
    setting = result.scalar_one_or_none()
    config = setting.value if setting else DEFAULT_ID_CONFIG

    # Add preview for each entity type
    from datetime import datetime

    year = str(datetime.now().year)
    yy = year[-2:]
    for entity_type, cfg in config.items():
        pattern = cfg.get("pattern", "")
        preview = pattern.replace("{YY}", yy).replace("{YEAR}", yy)
        seq_match = re.search(r"\{SEQ(?::(\d+))?\}", preview)
        if seq_match:
            pad = int(seq_match.group(1)) if seq_match.group(1) else 1
            preview = preview[: seq_match.start()] + str(cfg.get("next_seq", 1)).zfill(pad) + preview[seq_match.end() :]
        cfg["preview"] = preview

    return config


async def update_id_generation_config(
    db: AsyncSession, school_id: uuid.UUID, data: dict, updated_by: uuid.UUID
) -> dict:
    """Update ID auto-generation config."""
    result = await db.execute(
        select(Settings).where(
            Settings.school_id == school_id,
            Settings.category == "id_generation",
            Settings.key == "config",
            Settings.is_active.is_(True),
        )
    )
    existing = result.scalar_one_or_none()

    # Merge: only update fields provided
    if existing:
        current = dict(existing.value)
        for entity_type, cfg in data.items():
            if entity_type in current:
                current[entity_type].update(cfg)
            else:
                current[entity_type] = cfg
        existing.value = current
        existing.updated_by = updated_by
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(existing, "value")
    else:
        merged = dict(DEFAULT_ID_CONFIG)
        for entity_type, cfg in data.items():
            if entity_type in merged:
                merged[entity_type].update(cfg)
            else:
                merged[entity_type] = cfg
        new_setting = Settings(
            school_id=school_id,
            category="id_generation",
            key="config",
            value=merged,
            created_by=updated_by,
        )
        db.add(new_setting)

    await db.commit()
    return {"message": "ID generation config updated"}


async def generate_next_id(
    db: AsyncSession, school_id: uuid.UUID, entity_type: str
) -> dict:
    """Generate the next ID for an entity type and increment sequence.

    Checks actual database records to ensure the counter is never behind
    what was imported via bulk operations.
    """
    import re
    from datetime import datetime
    from sqlalchemy import func

    result = await db.execute(
        select(Settings).where(
            Settings.school_id == school_id,
            Settings.category == "id_generation",
            Settings.key == "config",
            Settings.is_active.is_(True),
        )
    )
    setting = result.scalar_one_or_none()
    config = setting.value if setting else DEFAULT_ID_CONFIG

    cfg = config.get(entity_type)
    if not cfg or not cfg.get("enabled"):
        return {"enabled": False, "id": None}

    pattern = cfg["pattern"]
    seq = cfg.get("next_seq", 1)
    year = str(datetime.now().year)
    yy = year[-2:]

    # Build the prefix (everything before the sequence number)
    prefix_template = pattern.replace("{YY}", yy).replace("{YEAR}", yy)
    seq_match_pattern = re.search(r"\{SEQ(?::(\d+))?\}", prefix_template)
    prefix = prefix_template[: seq_match_pattern.start()] if seq_match_pattern else prefix_template
    pad = int(seq_match_pattern.group(1)) if seq_match_pattern and seq_match_pattern.group(1) else 1

    # Query actual max sequence from existing records to prevent duplicates
    actual_max_seq = await _get_max_seq_from_db(db, school_id, entity_type, prefix, len(prefix), pad)
    if actual_max_seq >= seq:
        seq = actual_max_seq + 1

    generated = prefix + str(seq).zfill(pad)

    # Increment sequence and persist
    cfg["next_seq"] = seq + 1
    config[entity_type] = cfg

    if setting:
        setting.value = config
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(setting, "value")
    else:
        new_setting = Settings(
            school_id=school_id,
            category="id_generation",
            key="config",
            value=config,
            created_by=school_id,
        )
        db.add(new_setting)

    await db.commit()
    return {"enabled": True, "id": generated}


async def _get_max_seq_from_db(
    db: AsyncSession, school_id: uuid.UUID, entity_type: str, prefix: str, prefix_len: int, pad: int
) -> int:
    """Query the actual max sequence number from the relevant table."""
    from sqlalchemy import func, cast, Integer

    if entity_type == "student":
        from src.models.student import Student
        result = await db.execute(
            select(func.max(Student.admission_number))
            .where(
                Student.school_id == school_id,
                Student.admission_number.like(f"{prefix}%"),
                Student.is_active.is_(True),
            )
        )
    elif entity_type == "teacher" or entity_type == "staff":
        from src.models.staff import Staff
        result = await db.execute(
            select(func.max(Staff.employee_id))
            .where(
                Staff.school_id == school_id,
                Staff.employee_id.like(f"{prefix}%"),
                Staff.is_active.is_(True),
            )
        )
    else:
        return 0

    max_id = result.scalar_one_or_none()
    if not max_id:
        return 0

    # Extract the numeric suffix after the prefix
    suffix = max_id[prefix_len:]
    try:
        return int(suffix)
    except (ValueError, TypeError):
        return 0
