from __future__ import annotations

from fastapi import APIRouter

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
from src.core.dependencies import SessionDep

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
