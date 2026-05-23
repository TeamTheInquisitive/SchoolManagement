from __future__ import annotations

import uuid

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from src.auth.dependencies import SchoolDep, TeacherUser
from src.core.dependencies import PaginationDep, SessionDep
from src.teacher.assignments import service
from src.teacher.assignments.schemas import (
    AssignmentCreateResponse,
    AssignmentDeleteResponse,
    AssignmentDetailResponse,
    AssignmentListResponse,
    AssignmentUpdateResponse,
    CreateAssignmentRequest,
    GradeSubmissionRequest,
    GradeSubmissionResponse,
    SubmissionListResponse,
    UpdateAssignmentRequest,
)

router = APIRouter(prefix="/teacher/assignments", tags=["Teacher Assignments"])


@router.get("/", response_model=AssignmentListResponse)
async def list_assignments(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    pagination: PaginationDep,
    class_id: uuid.UUID | None = Query(default=None),
    status: str | None = Query(default=None),
    search: str | None = Query(default=None),
    academic_year: str | None = Query(default=None),
) -> AssignmentListResponse:
    """List teacher's assignments with filters and KPI summary."""
    result = await service.list_assignments(
        db, school.id, user, pagination, class_id, status, search, academic_year
    )
    return AssignmentListResponse(**result)


@router.post("/", response_model=AssignmentCreateResponse, status_code=201)
async def create_assignment(
    data: CreateAssignmentRequest,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> AssignmentCreateResponse:
    """Create a new assignment (auto-generates submissions for enrolled students)."""
    result = await service.create_assignment(db, school.id, user, data)
    return AssignmentCreateResponse(**result)


@router.get("/{assignment_id}/", response_model=AssignmentDetailResponse)
async def get_assignment(
    assignment_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> AssignmentDetailResponse:
    """Get assignment details with submission statistics."""
    result = await service.get_assignment_detail(db, school.id, user, assignment_id)
    return AssignmentDetailResponse(**result)


@router.put("/{assignment_id}/", response_model=AssignmentUpdateResponse)
async def update_assignment(
    assignment_id: uuid.UUID,
    data: UpdateAssignmentRequest,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> AssignmentUpdateResponse:
    """Update an existing assignment."""
    result = await service.update_assignment(db, school.id, user, assignment_id, data)
    return AssignmentUpdateResponse(**result)


@router.delete("/{assignment_id}/", response_model=AssignmentDeleteResponse)
async def delete_assignment(
    assignment_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> AssignmentDeleteResponse:
    """Soft-delete an assignment."""
    result = await service.delete_assignment(db, school.id, user, assignment_id)
    return AssignmentDeleteResponse(**result)


@router.get("/{assignment_id}/submissions/", response_model=SubmissionListResponse)
async def list_submissions(
    assignment_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    pagination: PaginationDep,
    status: str | None = Query(default=None),
) -> SubmissionListResponse:
    """List student submissions for a specific assignment."""
    result = await service.list_submissions(
        db, school.id, user, assignment_id, pagination, status
    )
    return SubmissionListResponse(**result)


@router.post(
    "/{assignment_id}/submissions/{submission_id}/grade/",
    response_model=GradeSubmissionResponse,
)
async def grade_submission(
    assignment_id: uuid.UUID,
    submission_id: uuid.UUID,
    data: GradeSubmissionRequest,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> GradeSubmissionResponse:
    """Grade a student submission."""
    result = await service.grade_submission(
        db, school.id, user, assignment_id, submission_id, data
    )
    return GradeSubmissionResponse(**result)


@router.get("/{assignment_id}/submissions/export/")
async def export_submissions(
    assignment_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> StreamingResponse:
    """Export all submissions for an assignment as CSV."""
    csv_content = await service.export_submissions_csv(
        db, school.id, user, assignment_id
    )
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=submissions_{assignment_id}.csv"
        },
    )
