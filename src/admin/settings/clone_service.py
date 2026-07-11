from __future__ import annotations

import uuid
from datetime import date

from fastapi import HTTPException
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.admin.settings.clone_schemas import (
    CloneModules,
    ClonePreviewResponse,
    CloneResponse,
    ModulePreview,
    ModuleResult,
    TableResult,
)
from src.models.academic import Class, ClassSection, ClassSubject, Section, Subject
from src.models.core import AcademicYear
from src.models.examination import GradeScale, GradeSystem
from src.models.fee import FeeStructure
from src.models.leave import LeavePolicy
from src.models.payroll import SalaryStructure
from src.models.staff import ClassAssignment, Staff, StaffSubject
from src.models.student import Student, StudentMentor
from src.models.timetable import PeriodConfig, TimetableSlot
from src.models.transport import (
    Driver,
    Helper,
    Route,
    RouteAssignment,
    StudentTransport,
    Vehicle,
)


# ---------------------------------------------------------------------------
# Preview
# ---------------------------------------------------------------------------


async def get_clone_preview(
    db: AsyncSession,
    school_id: uuid.UUID,
    source_year_id: uuid.UUID,
) -> dict:
    source_year = await _get_year(db, school_id, source_year_id)

    counts = {}

    # academic_structure
    cs_count = await _count(db, ClassSection, school_id, source_year_id)
    csub_count = await _count(db, ClassSubject, school_id, source_year_id)
    counts["academic_structure"] = cs_count + csub_count

    # teacher_assignments
    ss_count = await _count_with_active_staff(db, StaffSubject, school_id, source_year_id)
    ca_count = await _count_with_active_staff(db, ClassAssignment, school_id, source_year_id, status_filter="Active")
    counts["teacher_assignments"] = ss_count + ca_count

    # timetable
    pc_count = await _count(db, PeriodConfig, school_id, source_year_id)
    ts_count = await _count(db, TimetableSlot, school_id, source_year_id)
    counts["timetable"] = pc_count + ts_count

    # fee_structure
    counts["fee_structure"] = await _count(db, FeeStructure, school_id, source_year_id)

    # leave_policies
    counts["leave_policies"] = await _count(db, LeavePolicy, school_id, source_year_id)

    # grading_system
    gs_count = await _count(db, GradeSystem, school_id, source_year_id)
    gsc_count = await _count_grade_scales(db, school_id, source_year_id)
    counts["grading_system"] = gs_count + gsc_count

    # transport
    ra_count = await _count_active_route_assignments(db, school_id, source_year_id)
    st_count = await _count_active_student_transport(db, school_id, source_year_id)
    counts["transport"] = ra_count + st_count

    # payroll
    counts["payroll"] = await _count_with_active_staff(db, SalaryStructure, school_id, source_year_id)

    # mentoring
    counts["mentoring"] = await _count_active_mentors(db, school_id, source_year_id)

    modules = {
        "academic_structure": ModulePreview(
            label="Academic Structure",
            description="Class-section combinations, subject-class mappings",
            count=counts["academic_structure"],
        ),
        "teacher_assignments": ModulePreview(
            label="Teacher Assignments",
            description="Teacher subject qualifications, class-section-subject allocations",
            count=counts["teacher_assignments"],
        ),
        "timetable": ModulePreview(
            label="Timetable",
            description="Period/bell schedule config, full weekly timetable grid",
            count=counts["timetable"],
        ),
        "fee_structure": ModulePreview(
            label="Fee Structure",
            description="Fee types, amounts, frequencies per class",
            count=counts["fee_structure"],
        ),
        "leave_policies": ModulePreview(
            label="Leave Policies",
            description="Leave types, limits, rules, carry-forward settings",
            count=counts["leave_policies"],
        ),
        "grading_system": ModulePreview(
            label="Grading System",
            description="Grade scheme (A+, A, B+...), percentage ranges, grade points",
            count=counts["grading_system"],
        ),
        "transport": ModulePreview(
            label="Transport",
            description="Route-vehicle-driver assignments, student pickup/drop points",
            count=counts["transport"],
        ),
        "payroll": ModulePreview(
            label="Payroll",
            description="Salary structures (basic, HRA, DA, deductions) for all active staff",
            count=counts["payroll"],
            default_enabled=False,
        ),
        "mentoring": ModulePreview(
            label="Mentoring",
            description="Student-teacher mentor assignments",
            count=counts["mentoring"],
            default_enabled=False,
        ),
    }

    return ClonePreviewResponse(
        source_year_id=str(source_year_id),
        source_year_name=source_year.name,
        modules=modules,
        total_records=sum(counts.values()),
    ).model_dump()


# ---------------------------------------------------------------------------
# Execute Clone
# ---------------------------------------------------------------------------


async def execute_clone(
    db: AsyncSession,
    school_id: uuid.UUID,
    target_year_id: uuid.UUID,
    source_year_id: uuid.UUID,
    modules: CloneModules,
) -> dict:
    # Validate
    source_year = await _get_year(db, school_id, source_year_id)
    target_year = await _get_year(db, school_id, target_year_id)

    if source_year_id == target_year_id:
        raise HTTPException(status_code=400, detail="Source and target academic years must be different")

    if target_year.is_current:
        raise HTTPException(status_code=400, detail="Cannot initialize the current academic year. Set a different year as current first.")

    # State
    id_map = {"class_sections": {}, "period_configs": {}, "grade_systems": {}}
    warnings: list[str] = []
    results: dict[str, ModuleResult] = {}

    # Phase 1: Independent modules (flush between each to avoid autoflush surprises)
    if modules.academic_structure:
        results["academic_structure"] = await _clone_academic_structure(
            db, school_id, source_year_id, target_year_id, id_map, warnings
        )
        await db.flush()

    if modules.leave_policies:
        results["leave_policies"] = await _clone_leave_policies(
            db, school_id, source_year_id, target_year_id, warnings
        )
        await db.flush()

    if modules.grading_system:
        results["grading_system"] = await _clone_grading_system(
            db, school_id, source_year_id, target_year_id, id_map, warnings
        )
        await db.flush()

    if modules.transport:
        results["transport"] = await _clone_transport(
            db, school_id, source_year_id, target_year_id, warnings
        )
        await db.flush()

    if modules.payroll:
        results["payroll"] = await _clone_payroll(
            db, school_id, source_year_id, target_year_id, target_year.start_date, warnings
        )
        await db.flush()

    if modules.mentoring:
        results["mentoring"] = await _clone_mentoring(
            db, school_id, source_year_id, target_year_id, warnings
        )

    # Phase 2: Dependent modules (need class_section mapping)
    needs_cs_map = modules.teacher_assignments or modules.timetable or modules.fee_structure
    if needs_cs_map and not id_map["class_sections"]:
        id_map["class_sections"] = await _build_class_section_map(
            db, school_id, source_year_id, target_year_id
        )
        if not id_map["class_sections"]:
            dep_error = "Academic Structure must be cloned first (no class-sections found for target year)"
            if modules.teacher_assignments:
                results["teacher_assignments"] = ModuleResult(status="skipped_dependency")
            if modules.timetable:
                results["timetable"] = ModuleResult(status="skipped_dependency")
            if modules.fee_structure:
                results["fee_structure"] = ModuleResult(status="skipped_dependency")
            warnings.append(dep_error)
            needs_cs_map = False

    if needs_cs_map:
        if modules.teacher_assignments:
            results["teacher_assignments"] = await _clone_teacher_assignments(
                db, school_id, source_year_id, target_year_id, id_map, warnings
            )
            await db.flush()

        if modules.timetable:
            results["timetable"] = await _clone_timetable(
                db, school_id, source_year_id, target_year_id, id_map, warnings
            )
            await db.flush()

        if modules.fee_structure:
            results["fee_structure"] = await _clone_fee_structure(
                db, school_id, source_year_id, target_year_id, id_map, warnings
            )
            await db.flush()

    # Mark non-requested
    all_keys = [
        "academic_structure", "teacher_assignments", "timetable", "fee_structure",
        "leave_policies", "grading_system", "transport", "payroll", "mentoring",
    ]
    for key in all_keys:
        if key not in results:
            results[key] = ModuleResult(status="not_requested")

    # Store initialization metadata on target year
    total_cloned = sum(r.cloned for r in results.values())
    target_year.metadata_ = {
        **(target_year.metadata_ or {}),
        "initialized_from": source_year.name,
        "initialized_from_id": str(source_year_id),
        "records_cloned": total_cloned,
    }

    await db.commit()

    return CloneResponse(
        message=f"Academic year {target_year.name} initialized from {source_year.name}",
        source_year=source_year.name,
        target_year=target_year.name,
        results=results,
        total_records_cloned=total_cloned,
        warnings=warnings,
    ).model_dump()


# ---------------------------------------------------------------------------
# Module Clone Functions
# ---------------------------------------------------------------------------


async def _clone_academic_structure(
    db: AsyncSession, school_id: uuid.UUID,
    source_id: uuid.UUID, target_id: uuid.UUID,
    id_map: dict, warnings: list[str],
) -> ModuleResult:
    cs_result = await _clone_class_sections(db, school_id, source_id, target_id, id_map, warnings)
    csub_result = await _clone_class_subjects(db, school_id, source_id, target_id, warnings)
    return ModuleResult(
        cloned=cs_result.cloned + csub_result.cloned,
        skipped=cs_result.skipped + csub_result.skipped,
        details={"class_sections": cs_result, "class_subjects": csub_result},
    )


async def _clone_class_sections(
    db: AsyncSession, school_id: uuid.UUID,
    source_id: uuid.UUID, target_id: uuid.UUID,
    id_map: dict, warnings: list[str],
) -> TableResult:
    result = await db.execute(
        select(ClassSection).where(
            ClassSection.school_id == school_id,
            ClassSection.academic_year_id == source_id,
            ClassSection.is_active.is_(True),
        )
    )
    rows = result.scalars().all()
    cloned = skipped = 0

    for row in rows:
        existing = await db.execute(
            select(ClassSection.id).where(
                ClassSection.school_id == school_id,
                ClassSection.class_id == row.class_id,
                ClassSection.section_id == row.section_id,
                ClassSection.academic_year_id == target_id,
            )
        )
        ex = existing.scalar_one_or_none()
        if ex:
            id_map["class_sections"][row.id] = ex
            skipped += 1
            continue

        new = ClassSection(
            school_id=school_id,
            class_id=row.class_id,
            section_id=row.section_id,
            academic_year_id=target_id,
        )
        db.add(new)
        await db.flush()
        id_map["class_sections"][row.id] = new.id
        cloned += 1

    return TableResult(cloned=cloned, skipped=skipped)


async def _clone_class_subjects(
    db: AsyncSession, school_id: uuid.UUID,
    source_id: uuid.UUID, target_id: uuid.UUID,
    warnings: list[str],
) -> TableResult:
    result = await db.execute(
        select(ClassSubject).where(
            ClassSubject.school_id == school_id,
            ClassSubject.academic_year_id == source_id,
            ClassSubject.is_active.is_(True),
        )
    )
    rows = result.scalars().all()
    cloned = skipped = 0

    for row in rows:
        existing = await db.execute(
            select(ClassSubject.id).where(
                ClassSubject.school_id == school_id,
                ClassSubject.class_id == row.class_id,
                ClassSubject.subject_id == row.subject_id,
                ClassSubject.academic_year_id == target_id,
            )
        )
        if existing.scalar_one_or_none():
            skipped += 1
            continue

        new = ClassSubject(
            school_id=school_id,
            class_id=row.class_id,
            subject_id=row.subject_id,
            academic_year_id=target_id,
        )
        db.add(new)
        cloned += 1

    return TableResult(cloned=cloned, skipped=skipped)


async def _clone_teacher_assignments(
    db: AsyncSession, school_id: uuid.UUID,
    source_id: uuid.UUID, target_id: uuid.UUID,
    id_map: dict, warnings: list[str],
) -> ModuleResult:
    ss_result = await _clone_staff_subjects(db, school_id, source_id, target_id, warnings)
    ca_result = await _clone_class_assignments(db, school_id, source_id, target_id, id_map, warnings)
    return ModuleResult(
        cloned=ss_result.cloned + ca_result.cloned,
        skipped=ss_result.skipped + ca_result.skipped,
        details={"staff_subjects": ss_result, "class_assignments": ca_result},
    )


async def _clone_staff_subjects(
    db: AsyncSession, school_id: uuid.UUID,
    source_id: uuid.UUID, target_id: uuid.UUID,
    warnings: list[str],
) -> TableResult:
    result = await db.execute(
        select(StaffSubject)
        .join(Staff, StaffSubject.staff_id == Staff.id)
        .where(
            StaffSubject.school_id == school_id,
            StaffSubject.academic_year_id == source_id,
            StaffSubject.is_active.is_(True),
            Staff.is_active.is_(True),
            Staff.status == "Active",
        )
    )
    rows = result.scalars().all()
    cloned = skipped = 0

    for row in rows:
        existing = await db.execute(
            select(StaffSubject.id).where(
                StaffSubject.school_id == school_id,
                StaffSubject.staff_id == row.staff_id,
                StaffSubject.subject_id == row.subject_id,
                StaffSubject.academic_year_id == target_id,
            )
        )
        if existing.scalar_one_or_none():
            skipped += 1
            continue

        new = StaffSubject(
            school_id=school_id,
            staff_id=row.staff_id,
            subject_id=row.subject_id,
            academic_year_id=target_id,
            is_primary=row.is_primary,
        )
        db.add(new)
        cloned += 1

    return TableResult(cloned=cloned, skipped=skipped)


async def _clone_class_assignments(
    db: AsyncSession, school_id: uuid.UUID,
    source_id: uuid.UUID, target_id: uuid.UUID,
    id_map: dict, warnings: list[str],
) -> TableResult:
    result = await db.execute(
        select(ClassAssignment)
        .join(Staff, ClassAssignment.staff_id == Staff.id)
        .where(
            ClassAssignment.school_id == school_id,
            ClassAssignment.academic_year_id == source_id,
            ClassAssignment.is_active.is_(True),
            ClassAssignment.status == "Active",
            Staff.is_active.is_(True),
            Staff.status == "Active",
        )
    )
    rows = result.scalars().all()
    cloned = skipped = 0
    skipped_reasons = []

    for row in rows:
        new_cs_id = id_map["class_sections"].get(row.class_section_id)
        if not new_cs_id:
            skipped += 1
            continue

        existing = await db.execute(
            select(ClassAssignment.id).where(
                ClassAssignment.school_id == school_id,
                ClassAssignment.staff_id == row.staff_id,
                ClassAssignment.class_section_id == new_cs_id,
                ClassAssignment.subject_id == row.subject_id,
                ClassAssignment.academic_year_id == target_id,
            )
        )
        if existing.scalar_one_or_none():
            skipped += 1
            continue

        new = ClassAssignment(
            school_id=school_id,
            staff_id=row.staff_id,
            class_section_id=new_cs_id,
            subject_id=row.subject_id,
            academic_year_id=target_id,
            is_class_teacher=row.is_class_teacher,
            periods_per_week=row.periods_per_week,
            status="Active",
        )
        db.add(new)
        cloned += 1

    return TableResult(cloned=cloned, skipped=skipped, skipped_reasons=skipped_reasons)


async def _clone_timetable(
    db: AsyncSession, school_id: uuid.UUID,
    source_id: uuid.UUID, target_id: uuid.UUID,
    id_map: dict, warnings: list[str],
) -> ModuleResult:
    pc_result = await _clone_period_configs(db, school_id, source_id, target_id, id_map, warnings)
    await db.flush()
    ts_result = await _clone_timetable_slots(db, school_id, source_id, target_id, id_map, warnings)
    return ModuleResult(
        cloned=pc_result.cloned + ts_result.cloned,
        skipped=pc_result.skipped + ts_result.skipped,
        details={"period_configs": pc_result, "timetable_slots": ts_result},
    )


async def _clone_period_configs(
    db: AsyncSession, school_id: uuid.UUID,
    source_id: uuid.UUID, target_id: uuid.UUID,
    id_map: dict, warnings: list[str],
) -> TableResult:
    result = await db.execute(
        select(PeriodConfig).where(
            PeriodConfig.school_id == school_id,
            PeriodConfig.academic_year_id == source_id,
            PeriodConfig.is_active.is_(True),
        ).order_by(PeriodConfig.sort_order)
    )
    rows = result.scalars().all()
    cloned = skipped = 0

    for row in rows:
        existing = await db.execute(
            select(PeriodConfig.id).where(
                PeriodConfig.school_id == school_id,
                PeriodConfig.academic_year_id == target_id,
                PeriodConfig.start_time == row.start_time,
            )
        )
        ex = existing.scalar_one_or_none()
        if ex:
            id_map["period_configs"][row.id] = ex
            skipped += 1
            continue

        new = PeriodConfig(
            school_id=school_id,
            academic_year_id=target_id,
            name=row.name,
            start_time=row.start_time,
            end_time=row.end_time,
            duration_minutes=row.duration_minutes,
            is_break=row.is_break,
            sort_order=row.sort_order,
        )
        db.add(new)
        await db.flush()
        id_map["period_configs"][row.id] = new.id
        cloned += 1

    return TableResult(cloned=cloned, skipped=skipped)


async def _clone_timetable_slots(
    db: AsyncSession, school_id: uuid.UUID,
    source_id: uuid.UUID, target_id: uuid.UUID,
    id_map: dict, warnings: list[str],
) -> TableResult:
    result = await db.execute(
        select(TimetableSlot).where(
            TimetableSlot.school_id == school_id,
            TimetableSlot.academic_year_id == source_id,
            TimetableSlot.is_active.is_(True),
        )
    )
    rows = result.scalars().all()
    cloned = skipped = 0

    for row in rows:
        new_cs_id = id_map["class_sections"].get(row.class_section_id)
        new_pc_id = id_map["period_configs"].get(row.period_config_id)
        if not new_cs_id or not new_pc_id:
            skipped += 1
            continue

        existing = await db.execute(
            select(TimetableSlot.id).where(
                TimetableSlot.school_id == school_id,
                TimetableSlot.academic_year_id == target_id,
                TimetableSlot.class_section_id == new_cs_id,
                TimetableSlot.period_config_id == new_pc_id,
                TimetableSlot.day_of_week == row.day_of_week,
            )
        )
        if existing.scalar_one_or_none():
            skipped += 1
            continue

        # Clear staff if inactive
        staff_id = row.staff_id
        if staff_id:
            staff_check = await db.execute(
                select(Staff.is_active, Staff.status).where(Staff.id == staff_id)
            )
            staff_row = staff_check.one_or_none()
            if not staff_row or not staff_row.is_active or staff_row.status != "Active":
                staff_id = None

        new = TimetableSlot(
            school_id=school_id,
            academic_year_id=target_id,
            class_section_id=new_cs_id,
            period_config_id=new_pc_id,
            day_of_week=row.day_of_week,
            subject_id=row.subject_id,
            staff_id=staff_id,
            slot_type=row.slot_type,
        )
        db.add(new)
        cloned += 1

    return TableResult(cloned=cloned, skipped=skipped)


async def _clone_fee_structure(
    db: AsyncSession, school_id: uuid.UUID,
    source_id: uuid.UUID, target_id: uuid.UUID,
    id_map: dict, warnings: list[str],
) -> ModuleResult:
    result = await db.execute(
        select(FeeStructure).where(
            FeeStructure.school_id == school_id,
            FeeStructure.academic_year_id == source_id,
            FeeStructure.is_active.is_(True),
        )
    )
    rows = result.scalars().all()
    cloned = skipped = 0

    for row in rows:
        resolved_cs_id = None
        if row.class_section_id:
            resolved_cs_id = id_map["class_sections"].get(row.class_section_id)
            if not resolved_cs_id:
                skipped += 1
                continue

        existing = await db.execute(
            select(FeeStructure.id).where(
                FeeStructure.school_id == school_id,
                FeeStructure.academic_year_id == target_id,
                FeeStructure.class_section_id == resolved_cs_id,
                FeeStructure.fee_type == row.fee_type,
            )
        )
        if existing.scalar_one_or_none():
            skipped += 1
            continue

        new = FeeStructure(
            school_id=school_id,
            academic_year_id=target_id,
            class_id=row.class_id,
            class_section_id=resolved_cs_id,
            fee_type=row.fee_type,
            fee_category=row.fee_category,
            amount=row.amount,
            frequency=row.frequency,
        )
        db.add(new)
        cloned += 1

    return ModuleResult(
        cloned=cloned, skipped=skipped,
        details={"fee_structures": TableResult(cloned=cloned, skipped=skipped)},
    )


async def _clone_leave_policies(
    db: AsyncSession, school_id: uuid.UUID,
    source_id: uuid.UUID, target_id: uuid.UUID,
    warnings: list[str],
) -> ModuleResult:
    result = await db.execute(
        select(LeavePolicy).where(
            LeavePolicy.school_id == school_id,
            LeavePolicy.academic_year_id == source_id,
            LeavePolicy.is_active.is_(True),
        )
    )
    rows = result.scalars().all()
    cloned = skipped = 0

    for row in rows:
        existing = await db.execute(
            select(LeavePolicy.id).where(
                LeavePolicy.school_id == school_id,
                LeavePolicy.academic_year_id == target_id,
                LeavePolicy.leave_type == row.leave_type,
                LeavePolicy.applicable_to == row.applicable_to,
            )
        )
        if existing.scalar_one_or_none():
            skipped += 1
            continue

        new = LeavePolicy(
            school_id=school_id,
            academic_year_id=target_id,
            leave_type=row.leave_type,
            display_name=row.display_name,
            code=row.code,
            total_per_year=row.total_per_year,
            carry_forward=row.carry_forward,
            max_carry_forward=row.max_carry_forward,
            max_consecutive_days=row.max_consecutive_days,
            requires_approval=row.requires_approval,
            half_day_allowed=row.half_day_allowed,
            medical_certificate_required_after_days=row.medical_certificate_required_after_days,
            advance_notice_days=row.advance_notice_days,
            applicable_to=row.applicable_to,
            members=row.members,
        )
        db.add(new)
        cloned += 1

    return ModuleResult(
        cloned=cloned, skipped=skipped,
        details={"leave_policies": TableResult(cloned=cloned, skipped=skipped)},
    )


async def _clone_grading_system(
    db: AsyncSession, school_id: uuid.UUID,
    source_id: uuid.UUID, target_id: uuid.UUID,
    id_map: dict, warnings: list[str],
) -> ModuleResult:
    # Clone grade_systems
    result = await db.execute(
        select(GradeSystem).where(
            GradeSystem.school_id == school_id,
            GradeSystem.academic_year_id == source_id,
            GradeSystem.is_active.is_(True),
        )
    )
    systems = result.scalars().all()
    sys_cloned = sys_skipped = 0

    for row in systems:
        # Unique constraint is (school_id, name) — school-wide, not per year, no is_active
        existing = await db.execute(
            select(GradeSystem.id).where(
                GradeSystem.school_id == school_id,
                GradeSystem.name == row.name,
            )
        )
        ex = existing.scalar_one_or_none()
        if ex:
            id_map["grade_systems"][row.id] = ex
            sys_skipped += 1
            continue

        new = GradeSystem(
            school_id=school_id,
            academic_year_id=target_id,
            name=row.name,
            is_default=row.is_default,
        )
        db.add(new)
        await db.flush()
        id_map["grade_systems"][row.id] = new.id
        sys_cloned += 1

    # Clone grade_scales
    source_system_ids = [s.id for s in systems]
    scale_cloned = scale_skipped = 0

    if source_system_ids:
        scale_result = await db.execute(
            select(GradeScale).where(
                GradeScale.school_id == school_id,
                GradeScale.grade_system_id.in_(source_system_ids),
                GradeScale.is_active.is_(True),
            )
        )
        scales = scale_result.scalars().all()

        for row in scales:
            new_gs_id = id_map["grade_systems"].get(row.grade_system_id)
            if not new_gs_id:
                scale_skipped += 1
                continue

            existing = await db.execute(
                select(GradeScale.id).where(
                    GradeScale.school_id == school_id,
                    GradeScale.grade_system_id == new_gs_id,
                    GradeScale.grade == row.grade,
                )
            )
            if existing.scalar_one_or_none():
                scale_skipped += 1
                continue

            new = GradeScale(
                school_id=school_id,
                grade_system_id=new_gs_id,
                grade=row.grade,
                min_percentage=row.min_percentage,
                max_percentage=row.max_percentage,
                grade_point=row.grade_point,
                description=row.description,
                sort_order=row.sort_order,
            )
            db.add(new)
            scale_cloned += 1

    return ModuleResult(
        cloned=sys_cloned + scale_cloned,
        skipped=sys_skipped + scale_skipped,
        details={
            "grade_systems": TableResult(cloned=sys_cloned, skipped=sys_skipped),
            "grade_scales": TableResult(cloned=scale_cloned, skipped=scale_skipped),
        },
    )


async def _clone_transport(
    db: AsyncSession, school_id: uuid.UUID,
    source_id: uuid.UUID, target_id: uuid.UUID,
    warnings: list[str],
) -> ModuleResult:
    ra_result = await _clone_route_assignments(db, school_id, source_id, target_id, warnings)
    await db.flush()
    st_result = await _clone_student_transport(db, school_id, source_id, target_id, warnings)
    return ModuleResult(
        cloned=ra_result.cloned + st_result.cloned,
        skipped=ra_result.skipped + st_result.skipped,
        details={"route_assignments": ra_result, "student_transport": st_result},
    )


async def _clone_route_assignments(
    db: AsyncSession, school_id: uuid.UUID,
    source_id: uuid.UUID, target_id: uuid.UUID,
    warnings: list[str],
) -> TableResult:
    result = await db.execute(
        select(RouteAssignment)
        .join(Vehicle, RouteAssignment.vehicle_id == Vehicle.id)
        .join(Driver, RouteAssignment.driver_id == Driver.id)
        .where(
            RouteAssignment.school_id == school_id,
            RouteAssignment.academic_year_id == source_id,
            RouteAssignment.is_active.is_(True),
            RouteAssignment.status == "Active",
            Vehicle.is_active.is_(True),
            Vehicle.status == "Operational",
            Driver.is_active.is_(True),
        )
    )
    rows = result.scalars().all()
    cloned = skipped = 0

    for row in rows:
        # DB constraint is (school_id, vehicle_id, is_active) — one active assignment per vehicle
        existing = await db.execute(
            select(RouteAssignment.id).where(
                RouteAssignment.school_id == school_id,
                RouteAssignment.vehicle_id == row.vehicle_id,
                RouteAssignment.is_active.is_(True),
            )
        )
        if existing.scalar_one_or_none():
            skipped += 1
            continue

        # Verify helper if set
        helper_id = row.helper_id
        if helper_id:
            h_check = await db.execute(select(Helper.is_active).where(Helper.id == helper_id))
            if not (h_check.scalar_one_or_none()):
                helper_id = None

        new = RouteAssignment(
            school_id=school_id,
            route_id=row.route_id,
            vehicle_id=row.vehicle_id,
            driver_id=row.driver_id,
            helper_id=helper_id,
            academic_year_id=target_id,
            status="Active",
        )
        db.add(new)
        cloned += 1

    return TableResult(cloned=cloned, skipped=skipped)


async def _clone_student_transport(
    db: AsyncSession, school_id: uuid.UUID,
    source_id: uuid.UUID, target_id: uuid.UUID,
    warnings: list[str],
) -> TableResult:
    result = await db.execute(
        select(StudentTransport)
        .join(Student, StudentTransport.student_id == Student.id)
        .join(Route, StudentTransport.route_id == Route.id)
        .where(
            StudentTransport.school_id == school_id,
            StudentTransport.academic_year_id == source_id,
            StudentTransport.is_active.is_(True),
            Student.is_active.is_(True),
            Student.status == "Active",
            Route.is_active.is_(True),
            Route.status == "Active",
        )
    )
    rows = result.scalars().all()
    cloned = skipped = 0

    for row in rows:
        existing = await db.execute(
            select(StudentTransport.id).where(
                StudentTransport.school_id == school_id,
                StudentTransport.student_id == row.student_id,
                StudentTransport.academic_year_id == target_id,
            )
        )
        if existing.scalar_one_or_none():
            skipped += 1
            continue

        new = StudentTransport(
            school_id=school_id,
            student_id=row.student_id,
            route_id=row.route_id,
            academic_year_id=target_id,
            pickup_point=row.pickup_point,
            drop_point=row.drop_point,
        )
        db.add(new)
        cloned += 1

    return TableResult(cloned=cloned, skipped=skipped)


async def _clone_payroll(
    db: AsyncSession, school_id: uuid.UUID,
    source_id: uuid.UUID, target_id: uuid.UUID,
    target_start_date: date,
    warnings: list[str],
) -> ModuleResult:
    result = await db.execute(
        select(SalaryStructure)
        .join(Staff, SalaryStructure.staff_id == Staff.id)
        .where(
            SalaryStructure.school_id == school_id,
            SalaryStructure.academic_year_id == source_id,
            SalaryStructure.is_active.is_(True),
            Staff.is_active.is_(True),
            Staff.status == "Active",
        )
    )
    rows = result.scalars().all()
    cloned = skipped = 0

    for row in rows:
        existing = await db.execute(
            select(SalaryStructure.id).where(
                SalaryStructure.school_id == school_id,
                SalaryStructure.staff_id == row.staff_id,
            )
        )
        if existing.scalar_one_or_none():
            skipped += 1
            continue

        new = SalaryStructure(
            school_id=school_id,
            staff_id=row.staff_id,
            academic_year_id=target_id,
            basic_salary=row.basic_salary,
            hra=row.hra,
            da=row.da,
            transport_allowance=row.transport_allowance,
            medical_allowance=row.medical_allowance,
            other_allowances=row.other_allowances,
            pf_deduction=row.pf_deduction,
            professional_tax=row.professional_tax,
            tds=row.tds,
            other_deductions=row.other_deductions,
            net_salary=row.net_salary,
            effective_from=target_start_date,
        )
        db.add(new)
        cloned += 1

    return ModuleResult(
        cloned=cloned, skipped=skipped,
        details={"salary_structures": TableResult(cloned=cloned, skipped=skipped)},
    )


async def _clone_mentoring(
    db: AsyncSession, school_id: uuid.UUID,
    source_id: uuid.UUID, target_id: uuid.UUID,
    warnings: list[str],
) -> ModuleResult:
    result = await db.execute(
        select(StudentMentor)
        .join(Staff, StudentMentor.staff_id == Staff.id)
        .join(Student, StudentMentor.student_id == Student.id)
        .where(
            StudentMentor.school_id == school_id,
            StudentMentor.academic_year_id == source_id,
            StudentMentor.is_active.is_(True),
            Staff.is_active.is_(True),
            Staff.status == "Active",
            Student.is_active.is_(True),
            Student.status == "Active",
        )
    )
    rows = result.scalars().all()
    cloned = skipped = 0

    for row in rows:
        existing = await db.execute(
            select(StudentMentor.id).where(
                StudentMentor.school_id == school_id,
                StudentMentor.academic_year_id == target_id,
                StudentMentor.student_id == row.student_id,
            )
        )
        if existing.scalar_one_or_none():
            skipped += 1
            continue

        new = StudentMentor(
            school_id=school_id,
            academic_year_id=target_id,
            student_id=row.student_id,
            staff_id=row.staff_id,
            assigned_date=date.today(),
            notes=row.notes,
        )
        db.add(new)
        cloned += 1

    return ModuleResult(
        cloned=cloned, skipped=skipped,
        details={"student_mentors": TableResult(cloned=cloned, skipped=skipped)},
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_year(db: AsyncSession, school_id: uuid.UUID, year_id: uuid.UUID) -> AcademicYear:
    result = await db.execute(
        select(AcademicYear).where(
            AcademicYear.id == year_id,
            AcademicYear.school_id == school_id,
            AcademicYear.is_active.is_(True),
        )
    )
    year = result.scalar_one_or_none()
    if not year:
        raise HTTPException(status_code=404, detail=f"Academic year not found")
    return year


async def _build_class_section_map(
    db: AsyncSession, school_id: uuid.UUID,
    source_id: uuid.UUID, target_id: uuid.UUID,
) -> dict[uuid.UUID, uuid.UUID]:
    source_result = await db.execute(
        select(ClassSection).where(
            ClassSection.school_id == school_id,
            ClassSection.academic_year_id == source_id,
            ClassSection.is_active.is_(True),
        )
    )
    source_rows = source_result.scalars().all()

    target_result = await db.execute(
        select(ClassSection).where(
            ClassSection.school_id == school_id,
            ClassSection.academic_year_id == target_id,
            ClassSection.is_active.is_(True),
        )
    )
    target_rows = target_result.scalars().all()

    target_index = {(r.class_id, r.section_id): r.id for r in target_rows}
    return {src.id: target_index[(src.class_id, src.section_id)]
            for src in source_rows
            if (src.class_id, src.section_id) in target_index}


async def _count(db: AsyncSession, model, school_id: uuid.UUID, year_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count(model.id)).where(
            model.school_id == school_id,
            model.academic_year_id == year_id,
            model.is_active.is_(True),
        )
    )
    return result.scalar() or 0


async def _count_with_active_staff(
    db: AsyncSession, model, school_id: uuid.UUID, year_id: uuid.UUID,
    status_filter: str | None = None,
) -> int:
    query = (
        select(func.count(model.id))
        .join(Staff, model.staff_id == Staff.id)
        .where(
            model.school_id == school_id,
            model.academic_year_id == year_id,
            model.is_active.is_(True),
            Staff.is_active.is_(True),
            Staff.status == "Active",
        )
    )
    if status_filter:
        query = query.where(model.status == status_filter)
    result = await db.execute(query)
    return result.scalar() or 0


async def _count_grade_scales(db: AsyncSession, school_id: uuid.UUID, year_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count(GradeScale.id))
        .join(GradeSystem, GradeScale.grade_system_id == GradeSystem.id)
        .where(
            GradeSystem.school_id == school_id,
            GradeSystem.academic_year_id == year_id,
            GradeScale.is_active.is_(True),
            GradeSystem.is_active.is_(True),
        )
    )
    return result.scalar() or 0


async def _count_active_route_assignments(db: AsyncSession, school_id: uuid.UUID, year_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count(RouteAssignment.id))
        .join(Vehicle, RouteAssignment.vehicle_id == Vehicle.id)
        .join(Driver, RouteAssignment.driver_id == Driver.id)
        .where(
            RouteAssignment.school_id == school_id,
            RouteAssignment.academic_year_id == year_id,
            RouteAssignment.is_active.is_(True),
            RouteAssignment.status == "Active",
            Vehicle.is_active.is_(True),
            Driver.is_active.is_(True),
        )
    )
    return result.scalar() or 0


async def _count_active_student_transport(db: AsyncSession, school_id: uuid.UUID, year_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count(StudentTransport.id))
        .join(Student, StudentTransport.student_id == Student.id)
        .join(Route, StudentTransport.route_id == Route.id)
        .where(
            StudentTransport.school_id == school_id,
            StudentTransport.academic_year_id == year_id,
            StudentTransport.is_active.is_(True),
            Student.is_active.is_(True),
            Student.status == "Active",
            Route.is_active.is_(True),
        )
    )
    return result.scalar() or 0


async def _count_active_mentors(db: AsyncSession, school_id: uuid.UUID, year_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count(StudentMentor.id))
        .join(Staff, StudentMentor.staff_id == Staff.id)
        .join(Student, StudentMentor.student_id == Student.id)
        .where(
            StudentMentor.school_id == school_id,
            StudentMentor.academic_year_id == year_id,
            StudentMentor.is_active.is_(True),
            Staff.is_active.is_(True),
            Staff.status == "Active",
            Student.is_active.is_(True),
            Student.status == "Active",
        )
    )
    return result.scalar() or 0
