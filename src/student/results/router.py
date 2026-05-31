from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from src.auth.dependencies import SchoolDep, StudentUser
from src.core.dependencies import PaginationDep, SessionDep
from src.student.results import service
from src.student.results.schemas import (
    DownloadReportResponse,
    ExamDetailResponse,
    ExamResultsListResponse,
    LeaderboardResponse,
    ResultsOverviewResponse,
)

router = APIRouter(prefix="/student/results", tags=["Student Results"])


@router.get("", response_model=ResultsOverviewResponse)
async def get_results_overview(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
    academic_year: str | None = Query(default=None),
) -> ResultsOverviewResponse:
    """Get overall results summary with performance trend, subject comparison, and radar."""
    result = await service.get_results_overview(db, school.id, user, academic_year)
    return ResultsOverviewResponse(**result)


@router.get("/exams", response_model=ExamResultsListResponse)
async def get_exams_with_results(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
    pagination: PaginationDep,
    exam_type: str | None = Query(default=None),
    academic_year: str | None = Query(default=None),
) -> ExamResultsListResponse:
    """List all exams with results."""
    result = await service.get_exams_with_results(
        db, school.id, user, pagination, exam_type, academic_year
    )
    return ExamResultsListResponse(**result)


@router.get("/download-report", response_model=DownloadReportResponse)
async def download_report(
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
    academic_year: str | None = Query(default=None),
    exam_id: uuid.UUID | None = Query(default=None),
) -> DownloadReportResponse:
    """Download consolidated results report."""
    result = await service.get_download_report(db, school.id, user, academic_year, exam_id)
    return DownloadReportResponse(**result)


@router.get("/exam/{exam_id}", response_model=ExamDetailResponse)
async def get_exam_result_detail(
    exam_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
) -> ExamDetailResponse:
    """Get detailed result for a specific exam."""
    result = await service.get_exam_result_detail(db, school.id, user, exam_id)
    return ExamDetailResponse(**result)


@router.get("/exam/{exam_id}/leaderboard", response_model=LeaderboardResponse)
async def get_exam_leaderboard(
    exam_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: StudentUser,
    subject: str | None = Query(default=None),
) -> LeaderboardResponse:
    """Get leaderboard for a specific exam."""
    result = await service.get_exam_leaderboard(db, school.id, user, exam_id, subject)
    return LeaderboardResponse(**result)
