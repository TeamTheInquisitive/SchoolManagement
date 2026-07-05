from __future__ import annotations

from pydantic import BaseModel


class CloneModules(BaseModel):
    academic_structure: bool = True
    teacher_assignments: bool = True
    timetable: bool = True
    fee_structure: bool = True
    leave_policies: bool = True
    grading_system: bool = True
    transport: bool = True
    payroll: bool = False
    mentoring: bool = False


class CloneRequest(BaseModel):
    modules: CloneModules = CloneModules()


class ModulePreview(BaseModel):
    label: str
    description: str
    count: int
    default_enabled: bool = True


class ClonePreviewResponse(BaseModel):
    source_year_id: str
    source_year_name: str
    modules: dict[str, ModulePreview]
    total_records: int


class TableResult(BaseModel):
    cloned: int = 0
    skipped: int = 0
    skipped_reasons: list[str] = []


class ModuleResult(BaseModel):
    cloned: int = 0
    skipped: int = 0
    status: str = "completed"
    details: dict[str, TableResult] = {}


class CloneResponse(BaseModel):
    message: str
    source_year: str
    target_year: str
    results: dict[str, ModuleResult]
    total_records_cloned: int
    warnings: list[str] = []
