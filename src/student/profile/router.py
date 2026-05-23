from __future__ import annotations

from fastapi import APIRouter

from src.auth.dependencies import SchoolDep, StudentUser
from src.core.dependencies import SessionDep
from src.student.profile import service
from src.student.profile.schemas import (
    MentorDetailResponse,
    StudentProfileResponse,
    UpdateProfileRequest,
    UpdateProfileResponse,
)

router = APIRouter(prefix="/student/profile", tags=["Student Profile"])


@router.get("/", response_model=StudentProfileResponse)
async def get_profile(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
) -> StudentProfileResponse:
    """Get own full profile (personal, parent, medical, transport, mentor)."""
    result = await service.get_profile(db, school.id, user)
    return StudentProfileResponse(**result)


@router.put("/", response_model=UpdateProfileResponse)
async def update_profile(
    data: UpdateProfileRequest,
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
) -> UpdateProfileResponse:
    """Update editable fields only (phone, address, emergency contact)."""
    result = await service.update_profile(db, school.id, user, data.model_dump(exclude_none=True))
    return UpdateProfileResponse(**result)


@router.get("/mentor/", response_model=MentorDetailResponse)
async def get_mentor(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
) -> MentorDetailResponse:
    """Get assigned mentor details."""
    result = await service.get_mentor(db, school.id, user)
    return MentorDetailResponse(**result)
