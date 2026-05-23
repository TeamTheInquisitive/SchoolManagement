from __future__ import annotations

import uuid

from fastapi import APIRouter, File, Form, Query, UploadFile
from fastapi.responses import StreamingResponse

from src.auth.dependencies import SchoolDep, TeacherUser
from src.core.dependencies import PaginationDep, SessionDep
from src.teacher.grades import service
from src.teacher.grades.schemas import (
    ExamsForGradingResponse,
    GradeReportResponse,
    GradesListResponse,
    ImportGradesResponse,
    LeaderboardResponse,
    SubmitGradesRequest,
    SubmitGradesResponse,
    UpdateGradesRequest,
    UpdateGradesResponse,
)

router = APIRouter(prefix="/teacher/grades", tags=["Teacher Grades"])


@router.get("/", response_model=GradesListResponse)
async def get_grades(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    pagination: PaginationDep,
    class_id: uuid.UUID | None = Query(default=None),
    exam_id: uuid.UUID | None = Query(default=None),
) -> GradesListResponse:
    """Get grades for a class + exam with KPI stats."""
    result = await service.get_grades(db, school.id, user, pagination, class_id, exam_id)
    return GradesListResponse(**result)


@router.post("/", response_model=SubmitGradesResponse, status_code=201)
async def submit_grades(
    data: SubmitGradesRequest,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> SubmitGradesResponse:
    """Submit grades bulk for a class and exam."""
    result = await service.submit_grades(db, school.id, user, data)
    return SubmitGradesResponse(**result)


@router.put("/", response_model=UpdateGradesResponse)
async def update_grades(
    data: UpdateGradesRequest,
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
) -> UpdateGradesResponse:
    """Update existing grades for a class and exam."""
    result = await service.update_grades(db, school.id, user, data)
    return UpdateGradesResponse(**result)


@router.get("/exams/", response_model=ExamsForGradingResponse)
async def get_exams_for_grading(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    class_id: uuid.UUID | None = Query(default=None),
    academic_year: str | None = Query(default=None),
) -> ExamsForGradingResponse:
    """List available exams for grading."""
    result = await service.get_exams_for_grading(db, school.id, user, class_id, academic_year)
    return ExamsForGradingResponse(**result)


@router.get("/report/", response_model=GradeReportResponse)
async def get_report(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    class_id: uuid.UUID | None = Query(default=None),
    exam_id: uuid.UUID | None = Query(default=None),
) -> GradeReportResponse:
    """Get exam report with marks + grade distribution."""
    result = await service.get_report(db, school.id, user, class_id, exam_id)
    return GradeReportResponse(**result)


@router.get("/leaderboard/", response_model=LeaderboardResponse)
async def get_leaderboard(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    class_id: uuid.UUID | None = Query(default=None),
    exam_id: uuid.UUID | None = Query(default=None),
    limit: int = Query(default=20, le=100),
) -> LeaderboardResponse:
    """Get ranked leaderboard for an exam."""
    result = await service.get_leaderboard(db, school.id, user, class_id, exam_id, limit)
    return LeaderboardResponse(**result)


@router.post("/import/", response_model=ImportGradesResponse)
async def import_grades(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    file: UploadFile = File(...),
    class_id: uuid.UUID = Form(...),
    exam_id: uuid.UUID = Form(...),
) -> ImportGradesResponse:
    """Import grades from CSV."""
    content = await file.read()
    file_content = content.decode("utf-8")
    result = await service.import_grades(db, school.id, user, class_id, exam_id, file_content)
    return ImportGradesResponse(**result)


@router.get("/export/")
async def export_grades(
    db: SessionDep,
    school: SchoolDep,
    user: TeacherUser,
    class_id: uuid.UUID | None = Query(default=None),
    exam_id: uuid.UUID | None = Query(default=None),
    format: str = Query(default="csv"),
) -> StreamingResponse:
    """Export grades as CSV/PDF."""
    csv_content = await service.export_grades(db, school.id, user, class_id, exam_id)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=grades_{exam_id}.csv"
        },
    )
