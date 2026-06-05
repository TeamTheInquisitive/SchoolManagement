from __future__ import annotations

import os
import time
import uuid

from fastapi import APIRouter, HTTPException, UploadFile, File
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
from src.models.core import School

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
    updated_fields = await service.update_settings(db, school.id, update_data, user.id)
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
        db, school.id, update_data, user.id
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
    return await service.create_academic_year(db, school.id, data, user.id)


@router.put("/academic-years/{year_id}")
async def update_academic_year_by_id(
    year_id: str,
    data: dict,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Update an academic year."""
    return await service.update_academic_year_by_id(db, school.id, year_id, data, user.id)


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


@router.put("/academic-year", response_model=AcademicYearUpdateResponse)
async def update_academic_year(
    data: AcademicYearUpdateRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> AcademicYearUpdateResponse:
    """Update academic year config."""
    update_data = data.model_dump(exclude_none=True, mode="json")
    result = await service.update_academic_year(db, school.id, update_data, user.id)
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
    result = await service.update_enum_values(db, school.id, category, values, user.id)
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
    created = await service.bulk_create_classes(db, school.id, data.classes, user.id)
    return ClassesBulkResponse(
        created=created,
        message=f"{created} classes created",
        metadata={},
    )


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
    created = await service.bulk_create_sections(db, school.id, data.sections, user.id, data.class_id)
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
    created = await service.bulk_create_subjects(db, school.id, subjects, user.id)
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
    return await service.update_subject(db, school.id, subject_id, data, user.id)


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
        db, school.id, class_id, data.get("subject_ids", []), user.id
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
    return await service.create_fee_structure(db, school.id, data, user.id)


@router.put("/fee-structures/{structure_id}")
async def update_fee_structure(
    structure_id: str,
    data: dict,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> dict:
    """Update a fee structure."""
    return await service.update_fee_structure(db, school.id, structure_id, data, user.id)


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
    return await service.update_id_generation_config(db, school.id, data, user.id)


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
