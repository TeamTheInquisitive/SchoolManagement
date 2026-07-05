from __future__ import annotations

import os
import time
import uuid

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from sqlalchemy import select

from src.admin.settings import service
from src.admin.settings.schemas import (
    AcademicYearResponse,
    AcademicYearUpdateRequest,
    AcademicYearUpdateResponse,
    ClassesBulkRequest,
    ClassesBulkResponse,
    EnumCategoryResponse,
    EnumCategoryUpdateRequest,
    EnumCategoryUpdateResponse,
    SchoolProfileResponse,
    SchoolProfileUpdateRequest,
    SchoolProfileUpdateResponse,
    SectionsBulkRequest,
    SectionsBulkResponse,
    SettingsUpdateRequest,
    SettingsUpdateResponse,
    SubjectsBulkRequest,
    SubjectsBulkResponse,
)
from src.auth.dependencies import AdminUser, SchoolDep
from src.core.config import settings
from src.core.dependencies import SessionDep
from src.models.core import School, Settings

router = APIRouter(prefix="/admin/settings", tags=["Admin Settings"])


# ---------------------------------------------------------------------------
# GET / PUT all settings
# ---------------------------------------------------------------------------


@router.get("")
async def get_all_settings(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Get all settings grouped by category."""
    return await service.get_all_settings(db, school.id)


@router.put("", response_model=SettingsUpdateResponse)
async def update_settings(
    data: SettingsUpdateRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> SettingsUpdateResponse:
    """Update settings (partial update)."""
    update_data = data.model_dump(exclude_none=True)
    updated_fields = await service.update_settings(db, school.id, update_data)
    return SettingsUpdateResponse(
        message="Settings updated successfully",
        updated_fields=updated_fields,
        metadata={},
    )


# ---------------------------------------------------------------------------
# School Profile
# ---------------------------------------------------------------------------


@router.get("/school-profile", response_model=SchoolProfileResponse)
async def get_school_profile(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> SchoolProfileResponse:
    """Get school profile details."""
    profile = await service.get_school_profile(db, school.id)
    return SchoolProfileResponse(**profile)


@router.put("/school-profile", response_model=SchoolProfileUpdateResponse)
async def update_school_profile(
    data: SchoolProfileUpdateRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> SchoolProfileUpdateResponse:
    """Update school profile."""
    update_data = data.model_dump(exclude_none=True)
    school_name, updated_fields = await service.update_school_profile(
        db, school.id, update_data
    )
    return SchoolProfileUpdateResponse(
        message="School profile updated successfully",
        school_name=school_name,
        updated_fields=updated_fields,
        metadata={},
    )


# ---------------------------------------------------------------------------
# Academic Year
# ---------------------------------------------------------------------------


@router.get("/academic-year", response_model=AcademicYearResponse)
async def get_academic_year(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> AcademicYearResponse:
    """Get academic year configuration."""
    result = await service.get_academic_year(db, school.id)
    return AcademicYearResponse(**result)


@router.get("/academic-years")
async def list_academic_years(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """List all academic years."""
    return await service.list_academic_years(db, school.id)


@router.post("/academic-years", status_code=201)
async def create_academic_year(
    data: dict,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Create a new academic year."""
    return await service.create_academic_year(db, school.id, data)


@router.put("/academic-years/{year_id}")
async def update_academic_year_by_id(
    year_id: str,
    data: dict,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Update an academic year."""
    return await service.update_academic_year_by_id(db, school.id, year_id, data)


@router.delete("/academic-years/{year_id}")
async def delete_academic_year(
    year_id: str,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Delete an academic year."""
    return await service.delete_academic_year(db, school.id, year_id)


@router.post("/academic-years/{year_id}/set-current")
async def set_current_academic_year(
    year_id: str,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Set an academic year as current."""
    return await service.set_current_academic_year(db, school.id, year_id)


@router.get("/academic-years/{source_year_id}/clone-preview")
async def get_clone_preview(
    source_year_id: str,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Get record counts per module for clone preview."""
    from src.admin.settings import clone_service
    return await clone_service.get_clone_preview(db, school.id, uuid.UUID(source_year_id))


@router.post("/academic-years/{target_year_id}/initialize-from/{source_year_id}", status_code=201)
async def initialize_from_year(
    target_year_id: str,
    source_year_id: str,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    data: dict | None = None,
) -> dict:
    """Clone data from source academic year to target."""
    from src.admin.settings import clone_service
    from src.admin.settings.clone_schemas import CloneModules
    modules = CloneModules(**(data.get("modules", {}) if data else {}))
    return await clone_service.execute_clone(
        db=db,
        school_id=school.id,
        target_year_id=uuid.UUID(target_year_id),
        source_year_id=uuid.UUID(source_year_id),
        modules=modules,
    )


@router.put("/academic-year", response_model=AcademicYearUpdateResponse)
async def update_academic_year(
    data: AcademicYearUpdateRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> AcademicYearUpdateResponse:
    """Update academic year config."""
    update_data = data.model_dump(exclude_none=True, mode="json")
    result = await service.update_academic_year(db, school.id, update_data)
    return AcademicYearUpdateResponse(**result)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


@router.get("/enums/{category}", response_model=EnumCategoryResponse)
async def get_enum_values(
    category: str,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> EnumCategoryResponse:
    """Get enum values for a category."""
    result = await service.get_enum_values(db, school.id, category)
    return EnumCategoryResponse(**result)


@router.put("/enums/{category}", response_model=EnumCategoryUpdateResponse)
async def update_enum_values(
    category: str,
    data: EnumCategoryUpdateRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> EnumCategoryUpdateResponse:
    """Add or update enum values for a category."""
    values = [v.model_dump() for v in data.values]
    result = await service.update_enum_values(db, school.id, category, values)
    return EnumCategoryUpdateResponse(**result)


# ---------------------------------------------------------------------------
# Bulk: Classes
# ---------------------------------------------------------------------------


@router.post("/classes/bulk", response_model=ClassesBulkResponse, status_code=201)
async def bulk_create_classes(
    data: ClassesBulkRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> ClassesBulkResponse:
    """Bulk create classes."""
    created = await service.bulk_create_classes(db, school.id, data.classes)
    return ClassesBulkResponse(
        created=created,
        message=f"{created} classes created",
        metadata={},
    )


# ---------------------------------------------------------------------------
# Delete: Class
# ---------------------------------------------------------------------------


@router.delete("/classes/{class_id}")
async def delete_class(
    class_id: str,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Soft-delete a class and its associated class-section mappings."""
    return await service.delete_class(db, school.id, class_id, user.id)


# ---------------------------------------------------------------------------
# Delete: Class-Section (remove a section from a class)
# ---------------------------------------------------------------------------


@router.delete("/class-sections/{class_section_id}")
async def delete_class_section(
    class_section_id: str,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Soft-delete a class-section mapping."""
    return await service.delete_class_section(db, school.id, class_section_id, user.id)


# ---------------------------------------------------------------------------
# Bulk: Sections
# ---------------------------------------------------------------------------


@router.post("/sections/bulk", response_model=SectionsBulkResponse, status_code=201)
async def bulk_create_sections(
    data: SectionsBulkRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> SectionsBulkResponse:
    """Bulk create sections and optionally link to a class."""
    created = await service.bulk_create_sections(db, school.id, data.sections, data.class_id)
    return SectionsBulkResponse(
        created=created,
        message=f"{created} sections created",
        metadata={},
    )


# ---------------------------------------------------------------------------
# Bulk: Subjects
# ---------------------------------------------------------------------------


@router.post("/subjects/bulk", response_model=SubjectsBulkResponse, status_code=201)
async def bulk_create_subjects(
    data: SubjectsBulkRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> SubjectsBulkResponse:
    """Bulk create subjects."""
    subjects = [s.model_dump() for s in data.subjects]
    created = await service.bulk_create_subjects(db, school.id, subjects)
    return SubjectsBulkResponse(
        created=created,
        message=f"{created} subjects created",
        metadata={},
    )


# ---------------------------------------------------------------------------
# Class Sections Lookup
# ---------------------------------------------------------------------------


@router.get("/class-sections")
async def list_class_sections(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """List all classes grouped with their sections."""
    return await service.list_class_sections(db, school.id)


@router.get("/subjects")
async def list_subjects(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> list[dict]:
    """List all subjects for dropdowns."""
    return await service.list_subjects(db, school.id)


@router.put("/subjects/{subject_id}")
async def update_subject(
    subject_id: str,
    data: dict,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Update a subject's name and/or code."""
    return await service.update_subject(db, school.id, subject_id, data)


@router.delete("/subjects/{subject_id}")
async def delete_subject(
    subject_id: str,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Soft-delete a subject."""
    await service.delete_subject(db, school.id, subject_id, user.id)
    return {"message": "Subject deleted"}


@router.post("/upload-logo")
async def upload_school_logo(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    file: UploadFile = File(...),
) -> dict:
    """Upload or update the school logo."""
    # Validate file type
    allowed_types = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: png, jpg, jpeg, webp")

    # Validate file extension
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ("png", "jpg", "jpeg", "webp"):
        raise HTTPException(status_code=400, detail="Invalid file extension. Allowed: png, jpg, jpeg, webp")

    # Read file and validate size (2MB limit)
    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 2MB")

    # Ensure upload directory exists
    logos_dir = os.path.join(settings.UPLOAD_DIR, "logos")
    os.makedirs(logos_dir, exist_ok=True)

    # Save file
    filename = f"{school.id}_{int(time.time())}.{ext}"
    filepath = os.path.join(logos_dir, filename)
    with open(filepath, "wb") as f:
        f.write(contents)

    # Update school logo_url in database
    logo_url = f"/uploads/logos/{filename}"
    result = await db.execute(select(School).where(School.id == school.id))
    school_obj = result.scalar_one()
    school_obj.logo_url = logo_url
    await db.commit()

    return {"logo_url": logo_url}


@router.put("/subjects/{subject_id}/classes")
async def assign_classes_to_subject(
    subject_id: str,
    data: dict,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Assign classes to a subject."""
    return await service.assign_classes_to_subject(db, school.id, subject_id, data.get("class_ids", []))


# ---------------------------------------------------------------------------
# Class-Subject Mapping
# ---------------------------------------------------------------------------


@router.get("/class-subjects")
async def get_class_subjects(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Get subjects grouped by class for the current academic year."""
    return await service.get_class_subjects(db, school.id)


@router.put("/class-subjects/{class_id}")
async def update_class_subjects(
    class_id: str,
    data: dict,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Replace all subject assignments for a class in the current academic year."""
    return await service.update_class_subjects(
        db, school.id, class_id, data.get("subject_ids", [])
    )


# ---------------------------------------------------------------------------
# Fee Structures
# ---------------------------------------------------------------------------


@router.get("/fee-structures")
async def list_fee_structures(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """List all fee structures grouped by class."""
    return await service.list_fee_structures(db, school.id)


@router.post("/fee-structures", status_code=201)
async def create_fee_structure(
    data: dict,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Create a fee structure."""
    return await service.create_fee_structure(db, school.id, data)


@router.put("/fee-structures/{structure_id}")
async def update_fee_structure(
    structure_id: str,
    data: dict,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Update a fee structure."""
    return await service.update_fee_structure(db, school.id, structure_id, data)


@router.delete("/fee-structures/{structure_id}")
async def delete_fee_structure(
    structure_id: str,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Delete a fee structure."""
    return await service.delete_fee_structure(db, school.id, structure_id)


# ---------------------------------------------------------------------------
# ID Auto-Generation
# ---------------------------------------------------------------------------


@router.get("/check-prefix")
async def check_prefix_availability(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    prefix: str = Query(..., min_length=2, max_length=6),
) -> dict:
    """Check if an ID prefix is available (not used by another school)."""
    return await service.check_prefix_availability(db, prefix.upper(), school.id)


@router.get("/id-generation")
async def get_id_generation_config(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Get ID auto-generation config."""
    return await service.get_id_generation_config(db, school.id)


@router.put("/id-generation")
async def update_id_generation_config(
    data: dict,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Update ID auto-generation config."""
    return await service.update_id_generation_config(db, school.id, data)


# ---------------------------------------------------------------------------
# Holidays
# ---------------------------------------------------------------------------


@router.get("/holidays")
async def get_holidays(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Get holidays list for the current academic year."""
    from src.models.core import AcademicYear

    ay_result = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == school.id,
            AcademicYear.is_current.is_(True),
            AcademicYear.is_active.is_(True),
        )
    )
    ay = ay_result.scalar_one_or_none()
    ay_key = f"holidays_{ay.id}" if ay else "holidays"

    result = await db.execute(
        select(Settings).where(
            Settings.school_id == school.id,
            Settings.category == "school",
            Settings.key == ay_key,
            Settings.is_active.is_(True),
        )
    )
    row = result.scalar_one_or_none()
    if row:
        return {"holidays": row.value if row.value else [], "academic_year": ay.name if ay else None}

    return {"holidays": [], "academic_year": ay.name if ay else None}


@router.put("/holidays")
async def update_holidays(
    data: dict,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Update holidays list for the current academic year."""
    from src.models.core import AcademicYear

    ay_result = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == school.id,
            AcademicYear.is_current.is_(True),
            AcademicYear.is_active.is_(True),
        )
    )
    ay = ay_result.scalar_one_or_none()
    ay_key = f"holidays_{ay.id}" if ay else "holidays"

    holidays = data.get("holidays", [])
    result = await db.execute(
        select(Settings).where(
            Settings.school_id == school.id,
            Settings.category == "school",
            Settings.key == ay_key,
        )
    )
    row = result.scalar_one_or_none()
    if row:
        row.value = holidays
        row.is_active = True
    else:
        row = Settings(
            id=uuid.uuid4(),
            school_id=school.id,
            category="school",
            key=ay_key,
            value=holidays,
        )
        db.add(row)
    await db.commit()
    return {"holidays": holidays, "academic_year": ay.name if ay else None, "message": "Holidays updated successfully"}


@router.get("/next-id")
async def get_next_id(
    type: str,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Generate next ID for entity type."""
    if type not in ("student", "teacher", "staff"):
        raise HTTPException(status_code=400, detail="type must be student, teacher, or staff")
    return await service.generate_next_id(db, school.id, type)


@router.get("/attendance-config")
async def get_attendance_config(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Get attendance alert configuration."""
    from src.models.core import Settings
    result = await db.execute(
        select(Settings.value).where(
            Settings.school_id == school.id,
            Settings.category == "attendance",
            Settings.key == "config",
            Settings.is_active.is_(True),
        )
    )
    config = result.scalar_one_or_none()
    if not isinstance(config, dict):
        config = {"threshold": 75, "min_days": 30, "attendance_mode": "daily"}
    if "attendance_mode" not in config:
        config["attendance_mode"] = "daily"

    # Also include working_days from general settings
    wd_result = await db.execute(
        select(Settings.value).where(
            Settings.school_id == school.id,
            Settings.category == "general",
            Settings.key == "working_days",
            Settings.is_active.is_(True),
        )
    )
    working_days = wd_result.scalar_one_or_none()
    config["working_days"] = working_days if isinstance(working_days, list) else []

    return config


@router.put("/attendance-config")
async def update_attendance_config(
    data: dict,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Update attendance alert configuration. Body: { threshold: 75, min_days: 30, attendance_mode: "daily" }"""
    from src.models.core import Settings
    valid_modes = ("daily", "subject_wise", "twice_daily")
    attendance_mode = data.get("attendance_mode", "daily")
    if attendance_mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"attendance_mode must be one of: {', '.join(valid_modes)}")
    config = {
        "threshold": data.get("threshold", 75),
        "min_days": data.get("min_days", 30),
        "attendance_mode": attendance_mode,
    }
    result = await db.execute(
        select(Settings).where(
            Settings.school_id == school.id,
            Settings.category == "attendance",
            Settings.key == "config",
        )
    )
    row = result.scalar_one_or_none()
    if row:
        row.value = config
        row.is_active = True
    else:
        db.add(Settings(school_id=school.id, category="attendance", key="config", value=config))
    await db.commit()
    return {**config, "message": "Attendance config updated"}


# ---------------------------------------------------------------------------
# Class-Section Teacher Assignments
# ---------------------------------------------------------------------------


@router.get("/class-section-assignments", response_model=None)
async def get_class_section_assignments(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Get all class sections with their assigned class teacher and subject teachers."""
    return await service.get_class_section_assignments(db, school.id)


@router.put("/class-section-assignments/{class_section_id}", response_model=None)
async def update_class_section_assignments(
    class_section_id: uuid.UUID,
    data: dict,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Upsert class teacher and subject teacher assignments for a specific section."""
    class_teacher_id = data.get("class_teacher_id")
    if class_teacher_id is not None:
        class_teacher_id = uuid.UUID(class_teacher_id) if isinstance(class_teacher_id, str) else class_teacher_id

    subject_teachers = data.get("subject_teachers", [])

    try:
        return await service.update_class_section_assignments(
            db=db,
            school_id=school.id,
            class_section_id=class_section_id,
            class_teacher_id=class_teacher_id,
            subject_teachers=subject_teachers,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
