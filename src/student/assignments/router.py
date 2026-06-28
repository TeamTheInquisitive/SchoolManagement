from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, File, Form, Query, UploadFile

from src.auth.dependencies import SchoolDep, StudentUser
from src.core.dependencies import PaginationDep, SessionDep
from src.student.assignments import service
from src.student.assignments.schemas import (
    StudentAssignmentDetailResponse,
    StudentAssignmentListResponse,
    StudentSubmissionDetailResponse,
    SubmitAssignmentResponse,
)

router = APIRouter(prefix="/student/assignments", tags=["Student Assignments"])


@router.get("", response_model=StudentAssignmentListResponse)
async def list_assignments(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
    pagination: PaginationDep,
    status: str | None = Query(default=None),
    subject: str | None = Query(default=None),
    academic_year: str | None = Query(default=None),
) -> StudentAssignmentListResponse:
    """List student's assignments with summary and filtering."""
    result = await service.list_assignments(
        db, school.id, user, pagination, status, subject, academic_year
    )
    return StudentAssignmentListResponse(**result)


@router.get("/{assignment_id}", response_model=StudentAssignmentDetailResponse)
async def get_assignment_detail(
    assignment_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
) -> StudentAssignmentDetailResponse:
    """Get detailed assignment information."""
    result = await service.get_assignment_detail(db, school.id, user, assignment_id)
    return StudentAssignmentDetailResponse(**result)


@router.post(
    "/{assignment_id}/submit",
    response_model=SubmitAssignmentResponse,
    status_code=201,
)
async def submit_assignment(
    assignment_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
    comments: Annotated[str | None, Form()] = None,
    files: list[UploadFile] | None = File(default=None),
) -> SubmitAssignmentResponse:
    """Submit an assignment with optional comments and files."""
    result = await service.submit_assignment(
        db, school.id, user, assignment_id, comments, files
    )
    return SubmitAssignmentResponse(**result)


@router.get(
    "/{assignment_id}/submission",
    response_model=StudentSubmissionDetailResponse,
)
async def get_submission_detail(
    assignment_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
) -> StudentSubmissionDetailResponse:
    """View own submission details including grade and feedback."""
    result = await service.get_submission_detail(db, school.id, user, assignment_id)
    return StudentSubmissionDetailResponse(**result)
