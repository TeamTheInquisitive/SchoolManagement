from __future__ import annotations

import uuid

from fastapi import APIRouter, File, Query, UploadFile

from src.auth.dependencies import AdminUser, SchoolDep
from src.core.dependencies import PaginationDep, SessionDep
from src.admin.examinations import service
from src.admin.examinations.schemas import (
    AnalyticsResponse,
    BulkUploadResponse,
    EnterResultsRequest,
    EnterResultsResponse,
    ExamCancelResponse,
    ExamCreateResponse,
    ExamDetailResponse,
    ExamListResponse,
    ExamResultsResponse,
    ExamScheduleResponse,
    GenerateReportCardsRequest,
    GenerateReportCardsResponse,
    GradeSystemResponse,
    GradeSystemUpdateResponse,
    PublishResultsRequest,
    PublishResultsResponse,
    ReportCardResponse,
    CreateExamRequest,
    UpdateExamRequest,
    UpdateGradeSystemRequest,
    UpdateResultRequest,
    UpdateResultResponse,
)

router = APIRouter(prefix="/admin/examinations", tags=["Admin Examinations"])


@router.get("", response_model=ExamListResponse)
async def list_exams(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    pagination: PaginationDep,
    type: str | None = Query(default=None, alias="type"),
    class_name: str | None = Query(default=None),
    section: str | None = Query(default=None),
    subject: str | None = Query(default=None),
    status: str | None = Query(default=None),
    academic_year: str | None = Query(default=None),
) -> ExamListResponse:
    """List exams with filters."""
    result = await service.list_exams(
        db, school.id, pagination, type, class_name, section, subject, status, academic_year
    )
    return ExamListResponse(**result)


@router.post("", response_model=ExamCreateResponse, status_code=201)
async def create_exam(
    data: CreateExamRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> ExamCreateResponse:
    """Create a new exam."""
    result = await service.create_exam(db, school.id, user, data)
    return ExamCreateResponse(**result)


@router.get("/grade-system", response_model=GradeSystemResponse)
async def get_grade_system(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> GradeSystemResponse:
    """Get the active grade system."""
    result = await service.get_grade_system(db, school.id)
    return GradeSystemResponse(**result)


@router.put("/grade-system", response_model=GradeSystemUpdateResponse)
async def update_grade_system(
    data: UpdateGradeSystemRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> GradeSystemUpdateResponse:
    """Update the grade system."""
    result = await service.update_grade_system(db, school.id, user, data)
    return GradeSystemUpdateResponse(**result)


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    class_name: str | None = Query(default=None),
    section: str | None = Query(default=None),
    subject: str | None = Query(default=None),
    academic_year: str | None = Query(default=None),
    term: str | None = Query(default=None),
) -> AnalyticsResponse:
    """Get class/subject performance analytics."""
    result = await service.get_analytics(
        db, school.id, class_name, section, subject, academic_year, term
    )
    return AnalyticsResponse(**result)


@router.get("/report-card/{student_id}", response_model=ReportCardResponse)
async def get_report_card(
    student_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    academic_year: str | None = Query(default=None),
    term: str | None = Query(default=None),
) -> ReportCardResponse:
    """Generate report card data for a student."""
    result = await service.get_report_card(db, school.id, student_id, academic_year, term)
    return ReportCardResponse(**result)


@router.post("/report-card/generate", response_model=GenerateReportCardsResponse)
async def generate_report_cards(
    data: GenerateReportCardsRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> GenerateReportCardsResponse:
    """Batch generate report cards for a class."""
    result = await service.generate_report_cards(db, school.id, user, data)
    return GenerateReportCardsResponse(**result)


@router.get("/schedule", response_model=ExamScheduleResponse)
async def get_exam_schedule(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    class_name: str = Query(...),
    section: str = Query(...),
    academic_year: str | None = Query(default=None),
    term: str | None = Query(default=None),
) -> ExamScheduleResponse:
    """Get exam schedule for a class."""
    result = await service.get_exam_schedule(
        db, school.id, class_name, section, academic_year, term
    )
    return ExamScheduleResponse(**result)


@router.get("/{exam_id}", response_model=ExamDetailResponse)
async def get_exam_detail(
    exam_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> ExamDetailResponse:
    """Get full exam details with result summary."""
    result = await service.get_exam_detail(db, school.id, exam_id)
    return ExamDetailResponse(**result)


@router.put("/{exam_id}", response_model=ExamDetailResponse)
async def update_exam(
    exam_id: uuid.UUID,
    data: UpdateExamRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> ExamDetailResponse:
    """Update exam details."""
    result = await service.update_exam(db, school.id, user, exam_id, data)
    return ExamDetailResponse(**result)


@router.delete("/{exam_id}", response_model=ExamCancelResponse)
async def cancel_exam(
    exam_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> ExamCancelResponse:
    """Cancel (soft-delete) an exam. Only Draft/Scheduled allowed."""
    result = await service.cancel_exam(db, school.id, user, exam_id)
    return ExamCancelResponse(**result)


@router.get("/{exam_id}/results", response_model=ExamResultsResponse)
async def get_exam_results(
    exam_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> ExamResultsResponse:
    """Get all student results for an exam."""
    result = await service.get_exam_results(db, school.id, exam_id)
    return ExamResultsResponse(**result)


@router.post("/{exam_id}/results", response_model=EnterResultsResponse, status_code=201)
async def enter_results(
    exam_id: uuid.UUID,
    data: EnterResultsRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> EnterResultsResponse:
    """Enter results for students (bulk). Auto-computes grades and ranks."""
    result = await service.enter_results(db, school.id, user, exam_id, data)
    return EnterResultsResponse(**result)


@router.post("/{exam_id}/results/bulk-upload", response_model=BulkUploadResponse)
async def bulk_upload_results(
    exam_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    file: UploadFile = File(...),
) -> BulkUploadResponse:
    """Upload results via CSV file."""
    content = await file.read()
    file_content = content.decode("utf-8")
    result = await service.bulk_upload_results(db, school.id, user, exam_id, file_content)
    return BulkUploadResponse(**result)


@router.put("/{exam_id}/results/{result_id}", response_model=UpdateResultResponse)
async def update_result(
    exam_id: uuid.UUID,
    result_id: uuid.UUID,
    data: UpdateResultRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> UpdateResultResponse:
    """Update a single student's result."""
    result = await service.update_result(db, school.id, user, exam_id, result_id, data)
    return UpdateResultResponse(**result)


@router.post("/{exam_id}/publish", response_model=PublishResultsResponse)
async def publish_results(
    exam_id: uuid.UUID,
    data: PublishResultsRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> PublishResultsResponse:
    """Publish results for an exam."""
    result = await service.publish_results(db, school.id, user, exam_id, data)
    return PublishResultsResponse(**result)
