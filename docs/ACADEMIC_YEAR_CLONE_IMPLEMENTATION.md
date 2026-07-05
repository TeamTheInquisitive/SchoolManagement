# Academic Year Clone — Complete Implementation Plan

**Created: 2026-07-04**

---

## Table of Contents

1. [Overview](#1-overview)
2. [Backend — File Structure](#2-backend--file-structure)
3. [Backend — Pydantic Schemas](#3-backend--pydantic-schemas)
4. [Backend — Router Endpoints](#4-backend--router-endpoints)
5. [Backend — Service: Preview Function](#5-backend--service-preview-function)
6. [Backend — Service: Clone Orchestrator](#6-backend--service-clone-orchestrator)
7. [Backend — Service: Per-Module Clone Functions](#7-backend--service-per-module-clone-functions)
8. [Backend — ID Mapping Strategy](#8-backend--id-mapping-strategy)
9. [Backend — Dependency Resolution](#9-backend--dependency-resolution)
10. [Backend — Error Handling](#10-backend--error-handling)
11. [Backend — Transaction Management](#11-backend--transaction-management)
12. [Frontend — File Structure](#12-frontend--file-structure)
13. [Frontend — API Config & Hooks](#13-frontend--api-config--hooks)
14. [Frontend — Component: CloneYearModal](#14-frontend--component-cloneyearmodal)
15. [Frontend — Integration with AcademicYearTab](#15-frontend--integration-with-academicyeartab)
16. [Frontend — Post-Clone UI](#16-frontend--post-clone-ui)
17. [Testing Scenarios](#17-testing-scenarios)
18. [Edge Cases](#18-edge-cases)

---

## 1. Overview

### Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/admin/settings/academic-years/{source_year_id}/clone-preview` | Get record counts per module from source year |
| POST | `/admin/settings/academic-years/{target_year_id}/initialize-from/{source_year_id}` | Execute clone |

### Module → Table Mapping

| Module Key | Tables | Phase |
|------------|--------|-------|
| `academic_structure` | class_sections, class_subjects | 1 |
| `teacher_assignments` | staff_subjects, class_assignments | 2 (needs academic_structure) |
| `timetable` | period_configs, timetable_slots | 2 (needs academic_structure) |
| `fee_structure` | fee_structures | 2 (needs academic_structure) |
| `leave_policies` | leave_policies | 1 |
| `grading_system` | grade_systems, grade_scales | 1 |
| `transport` | route_assignments, student_transport | 1 |
| `payroll` | salary_structures | 1 |
| `mentoring` | student_mentors | 1 |

---

## 2. Backend — File Structure

### Files to Create

```
src/admin/settings/clone_service.py    (~450 lines)  — All clone logic
src/admin/settings/clone_schemas.py    (~120 lines)  — Request/response schemas
```

### Files to Modify

```
src/admin/settings/router.py           — Add 2 new endpoints (~30 lines added)
```

---

## 3. Backend — Pydantic Schemas

### File: `src/admin/settings/clone_schemas.py`

```python
from __future__ import annotations

import uuid
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
    status: str = "completed"  # completed | not_requested | skipped_dependency
    details: dict[str, TableResult] = {}


class CloneResponse(BaseModel):
    message: str
    source_year: str
    target_year: str
    results: dict[str, ModuleResult]
    total_records_cloned: int
    warnings: list[str] = []
```

---

## 4. Backend — Router Endpoints

### File: `src/admin/settings/router.py` (add these 2 endpoints)

```python
from src.admin.settings.clone_schemas import CloneRequest, ClonePreviewResponse, CloneResponse
from src.admin.settings import clone_service


@router.get("/academic-years/{source_year_id}/clone-preview")
async def get_clone_preview(
    source_year_id: str,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> ClonePreviewResponse:
    """Get record counts per module for clone preview."""
    return await clone_service.get_clone_preview(db, school.id, uuid.UUID(source_year_id))


@router.post("/academic-years/{target_year_id}/initialize-from/{source_year_id}", status_code=201)
async def initialize_from_year(
    target_year_id: str,
    source_year_id: str,
    data: CloneRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> CloneResponse:
    """Clone data from source academic year to target."""
    return await clone_service.execute_clone(
        db=db,
        school_id=school.id,
        target_year_id=uuid.UUID(target_year_id),
        source_year_id=uuid.UUID(source_year_id),
        modules=data.modules,
    )
```

---

## 5. Backend — Service: Preview Function

### File: `src/admin/settings/clone_service.py`

```python
async def get_clone_preview(
    db: AsyncSession,
    school_id: uuid.UUID,
    source_year_id: uuid.UUID,
) -> ClonePreviewResponse:
```

**Algorithm:**

1. Validate source_year_id exists for this school and is_active
2. For each module, count records in source year:

```python
# academic_structure
class_sections_count = COUNT(*) FROM class_sections 
    WHERE school_id = :school_id AND academic_year_id = :source AND is_active = True

class_subjects_count = COUNT(*) FROM class_subjects
    WHERE school_id = :school_id AND academic_year_id = :source AND is_active = True

# teacher_assignments
staff_subjects_count = COUNT(*) FROM staff_subjects ss
    JOIN staff s ON ss.staff_id = s.id
    WHERE ss.school_id = :school_id AND ss.academic_year_id = :source 
    AND ss.is_active = True AND s.is_active = True AND s.status = 'Active'

class_assignments_count = COUNT(*) FROM class_assignments ca
    JOIN staff s ON ca.staff_id = s.id
    WHERE ca.school_id = :school_id AND ca.academic_year_id = :source
    AND ca.is_active = True AND ca.status = 'Active' 
    AND s.is_active = True AND s.status = 'Active'

# timetable
period_configs_count = COUNT(*) FROM period_configs
    WHERE school_id = :school_id AND academic_year_id = :source AND is_active = True

timetable_slots_count = COUNT(*) FROM timetable_slots ts
    WHERE ts.school_id = :school_id AND ts.academic_year_id = :source AND ts.is_active = True

# fee_structure
fee_structures_count = COUNT(*) FROM fee_structures
    WHERE school_id = :school_id AND academic_year_id = :source AND is_active = True

# leave_policies
leave_policies_count = COUNT(*) FROM leave_policies
    WHERE school_id = :school_id AND academic_year_id = :source AND is_active = True

# grading_system
grade_systems_count = COUNT(*) FROM grade_systems
    WHERE school_id = :school_id AND academic_year_id = :source AND is_active = True

grade_scales_count = COUNT(*) FROM grade_scales gs
    JOIN grade_systems gsys ON gs.grade_system_id = gsys.id
    WHERE gsys.school_id = :school_id AND gsys.academic_year_id = :source
    AND gs.is_active = True AND gsys.is_active = True

# transport
route_assignments_count = COUNT(*) FROM route_assignments ra
    JOIN vehicles v ON ra.vehicle_id = v.id
    JOIN drivers d ON ra.driver_id = d.id
    WHERE ra.school_id = :school_id AND ra.academic_year_id = :source
    AND ra.is_active = True AND ra.status = 'Active'
    AND v.is_active = True AND d.is_active = True

student_transport_count = COUNT(*) FROM student_transport st
    JOIN students s ON st.student_id = s.id
    JOIN routes r ON st.route_id = r.id
    WHERE st.school_id = :school_id AND st.academic_year_id = :source
    AND st.is_active = True AND s.is_active = True AND s.status = 'Active'
    AND r.is_active = True

# payroll
salary_structures_count = COUNT(*) FROM salary_structures ss
    JOIN staff s ON ss.staff_id = s.id
    WHERE ss.school_id = :school_id AND ss.academic_year_id = :source
    AND ss.is_active = True AND s.is_active = True AND s.status = 'Active'

# mentoring
student_mentors_count = COUNT(*) FROM student_mentors sm
    JOIN staff s ON sm.staff_id = s.id
    JOIN students st ON sm.student_id = st.id
    WHERE sm.school_id = :school_id AND sm.academic_year_id = :source
    AND sm.is_active = True AND s.is_active = True AND s.status = 'Active'
    AND st.is_active = True AND st.status = 'Active'
```

3. Return response:

```python
return ClonePreviewResponse(
    source_year_id=str(source_year_id),
    source_year_name=source_year.name,
    modules={
        "academic_structure": ModulePreview(
            label="Academic Structure",
            description="Class-section combinations, subject-class mappings",
            count=class_sections_count + class_subjects_count,
            default_enabled=True,
        ),
        "teacher_assignments": ModulePreview(
            label="Teacher Assignments",
            description="Teacher subject qualifications, class-section-subject allocations",
            count=staff_subjects_count + class_assignments_count,
            default_enabled=True,
        ),
        "timetable": ModulePreview(
            label="Timetable",
            description="Period/bell schedule config, full weekly timetable grid",
            count=period_configs_count + timetable_slots_count,
            default_enabled=True,
        ),
        "fee_structure": ModulePreview(
            label="Fee Structure",
            description="Fee types, amounts, frequencies per class",
            count=fee_structures_count,
            default_enabled=True,
        ),
        "leave_policies": ModulePreview(
            label="Leave Policies",
            description="Leave types, limits, rules, carry-forward settings",
            count=leave_policies_count,
            default_enabled=True,
        ),
        "grading_system": ModulePreview(
            label="Grading System",
            description="Grade scheme (A+, A, B+...), percentage ranges, grade points",
            count=grade_systems_count + grade_scales_count,
            default_enabled=True,
        ),
        "transport": ModulePreview(
            label="Transport",
            description="Route-vehicle-driver assignments, student pickup/drop points",
            count=route_assignments_count + student_transport_count,
            default_enabled=True,
        ),
        "payroll": ModulePreview(
            label="Payroll",
            description="Salary structures (basic, HRA, DA, deductions) for all active staff",
            count=salary_structures_count,
            default_enabled=False,
        ),
        "mentoring": ModulePreview(
            label="Mentoring",
            description="Student-teacher mentor assignments",
            count=student_mentors_count,
            default_enabled=False,
        ),
    },
    total_records=sum_of_all_counts,
)
```

---

## 6. Backend — Service: Clone Orchestrator

```python
async def execute_clone(
    db: AsyncSession,
    school_id: uuid.UUID,
    target_year_id: uuid.UUID,
    source_year_id: uuid.UUID,
    modules: CloneModules,
) -> CloneResponse:
```

**Algorithm:**

```
1. VALIDATE:
   a. source_year exists, is_active, belongs to school_id
   b. target_year exists, is_active, belongs to school_id
   c. source_year_id != target_year_id
   d. target_year is NOT the current year (prevent overwriting live data)

2. CHECK DEPENDENCIES:
   If modules.teacher_assignments or modules.timetable or modules.fee_structure:
       If NOT modules.academic_structure:
           Check if class_sections already exist in target_year
           If not → return error MISSING_DEPENDENCY

3. INITIALIZE:
   results = {}
   warnings = []
   id_map = {
       "class_sections": {},    # old_id → new_id
       "period_configs": {},    # old_id → new_id
       "grade_systems": {},     # old_id → new_id
   }

4. PHASE 1 — Independent modules (no cross-module dependencies):
   if modules.academic_structure:
       results["academic_structure"] = await _clone_academic_structure(...)
       # Populates id_map["class_sections"]
   
   if modules.leave_policies:
       results["leave_policies"] = await _clone_leave_policies(...)
   
   if modules.grading_system:
       results["grading_system"] = await _clone_grading_system(...)
       # Populates id_map["grade_systems"]
   
   if modules.transport:
       results["transport"] = await _clone_transport(...)
   
   if modules.payroll:
       results["payroll"] = await _clone_payroll(...)
   
   if modules.mentoring:
       results["mentoring"] = await _clone_mentoring(...)

5. PHASE 2 — Dependent modules:
   # Resolve class_section mapping (either from Phase 1 clone or pre-existing)
   if not id_map["class_sections"]:
       id_map["class_sections"] = await _build_class_section_map(db, school_id, source_year_id, target_year_id)
   
   if not id_map["period_configs"] and modules.timetable:
       # period_configs cloned in timetable module itself (Phase 2a)
       pass

   if modules.teacher_assignments:
       results["teacher_assignments"] = await _clone_teacher_assignments(...)
   
   if modules.timetable:
       results["timetable"] = await _clone_timetable(...)
       # Populates id_map["period_configs"] internally
   
   if modules.fee_structure:
       results["fee_structure"] = await _clone_fee_structure(...)

6. MARK non-requested modules:
   for module_key not in results:
       results[module_key] = ModuleResult(status="not_requested")

7. COMMIT transaction

8. RETURN CloneResponse(...)
```

---

## 7. Backend — Service: Per-Module Clone Functions

### 7.1 `_clone_academic_structure`

```python
async def _clone_academic_structure(
    db: AsyncSession,
    school_id: uuid.UUID,
    source_year_id: uuid.UUID,
    target_year_id: uuid.UUID,
    id_map: dict,
    warnings: list[str],
) -> ModuleResult:
```

#### Step A: Clone class_sections

**Source query:**
```sql
SELECT id, class_id, section_id
FROM class_sections
WHERE school_id = :school_id
  AND academic_year_id = :source_year_id
  AND is_active = True
```

**For each row:**
```python
# Check if already exists in target
existing = SELECT id FROM class_sections
    WHERE school_id = :school_id
      AND class_id = :class_id
      AND section_id = :section_id
      AND academic_year_id = :target_year_id

if existing:
    id_map["class_sections"][old_id] = existing.id
    skipped += 1
    continue

# Check parent entities still active
class_active = SELECT is_active FROM classes WHERE id = :class_id
section_active = SELECT is_active FROM sections WHERE id = :section_id

if not class_active or not section_active:
    skipped += 1
    warnings.append(f"class_section skipped: class or section inactive")
    continue

# Create new
new_cs = ClassSection(
    id=uuid.uuid4(),
    school_id=school_id,
    class_id=row.class_id,
    section_id=row.section_id,
    academic_year_id=target_year_id,
)
db.add(new_cs)
id_map["class_sections"][old_id] = new_cs.id
cloned += 1
```

**Columns copied:** class_id, section_id
**Columns NOT copied:** id (new UUID), academic_year_id (target), metadata_, timestamps, audit

#### Step B: Clone class_subjects

**Source query:**
```sql
SELECT id, class_id, subject_id
FROM class_subjects
WHERE school_id = :school_id
  AND academic_year_id = :source_year_id
  AND is_active = True
```

**For each row:**
```python
# Check duplicate
existing = SELECT id FROM class_subjects
    WHERE school_id = :school_id
      AND class_id = :class_id
      AND subject_id = :subject_id
      AND academic_year_id = :target_year_id

if existing:
    skipped += 1
    continue

# Check subject still active
subject_active = SELECT is_active FROM subjects WHERE id = :subject_id
if not subject_active:
    skipped += 1
    continue

new_csub = ClassSubject(
    id=uuid.uuid4(),
    school_id=school_id,
    class_id=row.class_id,
    subject_id=row.subject_id,
    academic_year_id=target_year_id,
)
db.add(new_csub)
cloned += 1
```

**Columns copied:** class_id, subject_id
**Columns NOT copied:** id, academic_year_id, metadata_, timestamps, audit

---

### 7.2 `_clone_teacher_assignments`

```python
async def _clone_teacher_assignments(
    db: AsyncSession,
    school_id: uuid.UUID,
    source_year_id: uuid.UUID,
    target_year_id: uuid.UUID,
    id_map: dict,
    warnings: list[str],
) -> ModuleResult:
```

#### Step A: Clone staff_subjects

**Source query:**
```sql
SELECT ss.id, ss.staff_id, ss.subject_id, ss.is_primary
FROM staff_subjects ss
JOIN staff s ON ss.staff_id = s.id
WHERE ss.school_id = :school_id
  AND ss.academic_year_id = :source_year_id
  AND ss.is_active = True
  AND s.is_active = True
  AND s.status = 'Active'
```

**For each row:**
```python
# Check duplicate
existing = SELECT id FROM staff_subjects
    WHERE school_id = :school_id
      AND staff_id = :staff_id
      AND subject_id = :subject_id
      AND academic_year_id = :target_year_id

if existing:
    skipped += 1
    continue

# Check subject still active
subject_active = SELECT is_active FROM subjects WHERE id = :subject_id
if not subject_active:
    skipped += 1
    continue

new_ss = StaffSubject(
    id=uuid.uuid4(),
    school_id=school_id,
    staff_id=row.staff_id,
    subject_id=row.subject_id,
    academic_year_id=target_year_id,
    is_primary=row.is_primary,
)
db.add(new_ss)
cloned += 1
```

**Columns copied:** staff_id, subject_id, is_primary
**Columns NOT copied:** id, academic_year_id, metadata_, timestamps, audit

#### Step B: Clone class_assignments

**Source query:**
```sql
SELECT ca.id, ca.staff_id, ca.class_section_id, ca.subject_id,
       ca.is_class_teacher, ca.periods_per_week
FROM class_assignments ca
JOIN staff s ON ca.staff_id = s.id
WHERE ca.school_id = :school_id
  AND ca.academic_year_id = :source_year_id
  AND ca.is_active = True
  AND ca.status = 'Active'
  AND s.is_active = True
  AND s.status = 'Active'
```

**For each row:**
```python
# Resolve new class_section_id
new_cs_id = id_map["class_sections"].get(row.class_section_id)
if not new_cs_id:
    skipped += 1
    warnings.append(f"class_assignment skipped: class_section {row.class_section_id} not found in target year")
    continue

# Check duplicate
existing = SELECT id FROM class_assignments
    WHERE school_id = :school_id
      AND staff_id = :staff_id
      AND class_section_id = :new_cs_id
      AND subject_id = :subject_id
      AND academic_year_id = :target_year_id

if existing:
    skipped += 1
    continue

new_ca = ClassAssignment(
    id=uuid.uuid4(),
    school_id=school_id,
    staff_id=row.staff_id,
    class_section_id=new_cs_id,        # ← MAPPED
    subject_id=row.subject_id,
    academic_year_id=target_year_id,
    is_class_teacher=row.is_class_teacher,
    periods_per_week=row.periods_per_week,
    status="Active",
    end_date=None,
    end_reason=None,
)
db.add(new_ca)
cloned += 1
```

**Columns copied:** staff_id, subject_id, is_class_teacher, periods_per_week
**Columns resolved via ID map:** class_section_id
**Columns reset:** status="Active", end_date=None, end_reason=None
**Columns NOT copied:** id, academic_year_id, metadata_, timestamps, audit

---

### 7.3 `_clone_timetable`

```python
async def _clone_timetable(
    db: AsyncSession,
    school_id: uuid.UUID,
    source_year_id: uuid.UUID,
    target_year_id: uuid.UUID,
    id_map: dict,
    warnings: list[str],
) -> ModuleResult:
```

#### Step A: Clone period_configs

**Source query:**
```sql
SELECT id, name, start_time, end_time, duration_minutes, is_break, sort_order
FROM period_configs
WHERE school_id = :school_id
  AND academic_year_id = :source_year_id
  AND is_active = True
ORDER BY sort_order
```

**For each row:**
```python
# Check duplicate (by start_time which is unique per year)
existing = SELECT id FROM period_configs
    WHERE school_id = :school_id
      AND academic_year_id = :target_year_id
      AND start_time = :start_time

if existing:
    id_map["period_configs"][old_id] = existing.id
    skipped += 1
    continue

new_pc = PeriodConfig(
    id=uuid.uuid4(),
    school_id=school_id,
    academic_year_id=target_year_id,
    name=row.name,
    start_time=row.start_time,
    end_time=row.end_time,
    duration_minutes=row.duration_minutes,
    is_break=row.is_break,
    sort_order=row.sort_order,
)
db.add(new_pc)
id_map["period_configs"][old_id] = new_pc.id
cloned += 1
```

**Columns copied:** name, start_time, end_time, duration_minutes, is_break, sort_order
**Columns NOT copied:** id, academic_year_id, metadata_, timestamps, audit

#### Step B: Clone timetable_slots

**Source query:**
```sql
SELECT ts.id, ts.class_section_id, ts.period_config_id, ts.day_of_week,
       ts.subject_id, ts.staff_id, ts.slot_type
FROM timetable_slots ts
WHERE ts.school_id = :school_id
  AND ts.academic_year_id = :source_year_id
  AND ts.is_active = True
```

**For each row:**
```python
# Resolve FKs
new_cs_id = id_map["class_sections"].get(row.class_section_id)
new_pc_id = id_map["period_configs"].get(row.period_config_id)

if not new_cs_id or not new_pc_id:
    skipped += 1
    continue

# Resolve staff_id (set to NULL if staff inactive)
resolved_staff_id = row.staff_id
if row.staff_id:
    staff_active = SELECT is_active, status FROM staff WHERE id = :staff_id
    if not staff_active or staff_active.status != 'Active':
        resolved_staff_id = None
        warnings.append(f"timetable slot: staff cleared (inactive)")

# Check duplicate
existing = SELECT id FROM timetable_slots
    WHERE school_id = :school_id
      AND academic_year_id = :target_year_id
      AND class_section_id = :new_cs_id
      AND period_config_id = :new_pc_id
      AND day_of_week = :day_of_week

if existing:
    skipped += 1
    continue

new_slot = TimetableSlot(
    id=uuid.uuid4(),
    school_id=school_id,
    academic_year_id=target_year_id,
    class_section_id=new_cs_id,         # ← MAPPED
    period_config_id=new_pc_id,         # ← MAPPED
    day_of_week=row.day_of_week,
    subject_id=row.subject_id,
    staff_id=resolved_staff_id,
    slot_type=row.slot_type,
)
db.add(new_slot)
cloned += 1
```

**Columns copied:** day_of_week, subject_id, staff_id (if active), slot_type
**Columns resolved via ID map:** class_section_id, period_config_id
**Columns NOT copied:** id, academic_year_id, metadata_, timestamps, audit

---

### 7.4 `_clone_fee_structure`

```python
async def _clone_fee_structure(
    db: AsyncSession,
    school_id: uuid.UUID,
    source_year_id: uuid.UUID,
    target_year_id: uuid.UUID,
    id_map: dict,
    warnings: list[str],
) -> ModuleResult:
```

**Source query:**
```sql
SELECT id, class_id, class_section_id, fee_type, fee_category, amount, frequency
FROM fee_structures
WHERE school_id = :school_id
  AND academic_year_id = :source_year_id
  AND is_active = True
```

**For each row:**
```python
# Resolve class_section_id if set
resolved_cs_id = None
if row.class_section_id:
    resolved_cs_id = id_map["class_sections"].get(row.class_section_id)
    if not resolved_cs_id:
        skipped += 1
        warnings.append(f"fee_structure skipped: class_section not in target year")
        continue

# Check duplicate
existing = SELECT id FROM fee_structures
    WHERE school_id = :school_id
      AND academic_year_id = :target_year_id
      AND class_section_id = :resolved_cs_id
      AND fee_type = :fee_type

if existing:
    skipped += 1
    continue

new_fs = FeeStructure(
    id=uuid.uuid4(),
    school_id=school_id,
    academic_year_id=target_year_id,
    class_id=row.class_id,
    class_section_id=resolved_cs_id,    # ← MAPPED (or NULL)
    fee_type=row.fee_type,
    fee_category=row.fee_category,
    amount=row.amount,
    frequency=row.frequency,
)
db.add(new_fs)
cloned += 1
```

**Columns copied:** class_id, fee_type, fee_category, amount, frequency
**Columns resolved via ID map:** class_section_id
**Columns NOT copied:** id, academic_year_id, metadata_, timestamps, audit

---

### 7.5 `_clone_leave_policies`

**Source query:**
```sql
SELECT leave_type, display_name, code, total_per_year, carry_forward,
       max_carry_forward, max_consecutive_days, requires_approval,
       half_day_allowed, medical_certificate_required_after_days,
       advance_notice_days, applicable_to, members
FROM leave_policies
WHERE school_id = :school_id
  AND academic_year_id = :source_year_id
  AND is_active = True
```

**For each row:**
```python
# Check duplicate
existing = SELECT id FROM leave_policies
    WHERE school_id = :school_id
      AND academic_year_id = :target_year_id
      AND leave_type = :leave_type
      AND applicable_to = :applicable_to

if existing:
    skipped += 1
    continue

new_lp = LeavePolicy(
    id=uuid.uuid4(),
    school_id=school_id,
    academic_year_id=target_year_id,
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
db.add(new_lp)
cloned += 1
```

**Columns copied:** ALL content columns (leave_type, display_name, code, total_per_year, carry_forward, max_carry_forward, max_consecutive_days, requires_approval, half_day_allowed, medical_certificate_required_after_days, advance_notice_days, applicable_to, members)
**Columns NOT copied:** id, academic_year_id, metadata_, timestamps, audit

---

### 7.6 `_clone_grading_system`

#### Step A: Clone grade_systems

**Source query:**
```sql
SELECT id, name, is_default
FROM grade_systems
WHERE school_id = :school_id
  AND academic_year_id = :source_year_id
  AND is_active = True
```

**For each row:**
```python
existing = SELECT id FROM grade_systems
    WHERE school_id = :school_id
      AND academic_year_id = :target_year_id
      AND name = :name

if existing:
    id_map["grade_systems"][old_id] = existing.id
    skipped += 1
    continue

new_gs = GradeSystem(
    id=uuid.uuid4(),
    school_id=school_id,
    academic_year_id=target_year_id,
    name=row.name,
    is_default=row.is_default,
)
db.add(new_gs)
id_map["grade_systems"][old_id] = new_gs.id
cloned += 1
```

#### Step B: Clone grade_scales

**Source query:**
```sql
SELECT grade_system_id, grade, min_percentage, max_percentage,
       grade_point, description, sort_order
FROM grade_scales
WHERE school_id = :school_id
  AND is_active = True
  AND grade_system_id IN (... source grade_system ids ...)
```

**For each row:**
```python
new_gs_id = id_map["grade_systems"].get(row.grade_system_id)
if not new_gs_id:
    skipped += 1
    continue

# Check duplicate
existing = SELECT id FROM grade_scales
    WHERE school_id = :school_id
      AND grade_system_id = :new_gs_id
      AND grade = :grade

if existing:
    skipped += 1
    continue

new_scale = GradeScale(
    id=uuid.uuid4(),
    school_id=school_id,
    grade_system_id=new_gs_id,          # ← MAPPED
    grade=row.grade,
    min_percentage=row.min_percentage,
    max_percentage=row.max_percentage,
    grade_point=row.grade_point,
    description=row.description,
    sort_order=row.sort_order,
)
db.add(new_scale)
cloned += 1
```

**Columns copied:** grade, min_percentage, max_percentage, grade_point, description, sort_order
**Columns resolved via ID map:** grade_system_id
**Columns NOT copied:** id, metadata_, timestamps, audit

---

### 7.7 `_clone_transport`

#### Step A: Clone route_assignments

**Source query:**
```sql
SELECT ra.id, ra.route_id, ra.vehicle_id, ra.driver_id, ra.helper_id
FROM route_assignments ra
JOIN vehicles v ON ra.vehicle_id = v.id
JOIN drivers d ON ra.driver_id = d.id
WHERE ra.school_id = :school_id
  AND ra.academic_year_id = :source_year_id
  AND ra.is_active = True
  AND ra.status = 'Active'
  AND v.is_active = True AND v.status = 'Operational'
  AND d.is_active = True
```

**For each row:**
```python
# Check duplicate
existing = SELECT id FROM route_assignments
    WHERE school_id = :school_id
      AND vehicle_id = :vehicle_id
      AND academic_year_id = :target_year_id
      AND is_active = True

if existing:
    skipped += 1
    continue

# Verify route still active
route_active = SELECT is_active, status FROM routes WHERE id = :route_id
if not route_active or route_active.status != 'Active':
    skipped += 1
    continue

# Verify helper still active (if set)
resolved_helper_id = row.helper_id
if row.helper_id:
    helper_active = SELECT is_active FROM helpers WHERE id = :helper_id
    if not helper_active:
        resolved_helper_id = None

new_ra = RouteAssignment(
    id=uuid.uuid4(),
    school_id=school_id,
    route_id=row.route_id,
    vehicle_id=row.vehicle_id,
    driver_id=row.driver_id,
    helper_id=resolved_helper_id,
    academic_year_id=target_year_id,
    status="Active",
)
db.add(new_ra)
cloned += 1
```

**Columns copied:** route_id, vehicle_id, driver_id, helper_id (if active)
**Columns reset:** status="Active"
**Columns NOT copied:** id, academic_year_id, metadata_, timestamps, audit

#### Step B: Clone student_transport

**Source query:**
```sql
SELECT st.student_id, st.route_id, st.pickup_point, st.drop_point
FROM student_transport st
JOIN students s ON st.student_id = s.id
JOIN routes r ON st.route_id = r.id
WHERE st.school_id = :school_id
  AND st.academic_year_id = :source_year_id
  AND st.is_active = True
  AND s.is_active = True AND s.status = 'Active'
  AND r.is_active = True AND r.status = 'Active'
```

**For each row:**
```python
# Check duplicate
existing = SELECT id FROM student_transport
    WHERE school_id = :school_id
      AND student_id = :student_id
      AND academic_year_id = :target_year_id

if existing:
    skipped += 1
    continue

new_st = StudentTransport(
    id=uuid.uuid4(),
    school_id=school_id,
    student_id=row.student_id,
    route_id=row.route_id,
    academic_year_id=target_year_id,
    pickup_point=row.pickup_point,
    drop_point=row.drop_point,
)
db.add(new_st)
cloned += 1
```

**Columns copied:** student_id, route_id, pickup_point, drop_point
**Columns NOT copied:** id, academic_year_id, metadata_, timestamps, audit

---

### 7.8 `_clone_payroll`

**Source query:**
```sql
SELECT ss.staff_id, ss.basic_salary, ss.hra, ss.da, ss.transport_allowance,
       ss.medical_allowance, ss.other_allowances, ss.pf_deduction,
       ss.professional_tax, ss.tds, ss.other_deductions, ss.net_salary
FROM salary_structures ss
JOIN staff s ON ss.staff_id = s.id
WHERE ss.school_id = :school_id
  AND ss.academic_year_id = :source_year_id
  AND ss.is_active = True
  AND s.is_active = True AND s.status = 'Active'
```

**For each row:**
```python
# Check duplicate (unique on school_id + staff_id)
existing = SELECT id FROM salary_structures
    WHERE school_id = :school_id
      AND staff_id = :staff_id
      AND academic_year_id = :target_year_id

if existing:
    skipped += 1
    continue

new_ss = SalaryStructure(
    id=uuid.uuid4(),
    school_id=school_id,
    staff_id=row.staff_id,
    academic_year_id=target_year_id,
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
    effective_from=target_year.start_date,  # ← New year's start
)
db.add(new_ss)
cloned += 1
```

**Columns copied:** staff_id, basic_salary, hra, da, transport_allowance, medical_allowance, other_allowances, pf_deduction, professional_tax, tds, other_deductions, net_salary
**Columns reset:** effective_from = target year's start_date
**Columns NOT copied:** id, academic_year_id, metadata_, timestamps, audit

---

### 7.9 `_clone_mentoring`

**Source query:**
```sql
SELECT sm.student_id, sm.staff_id, sm.notes
FROM student_mentors sm
JOIN staff s ON sm.staff_id = s.id
JOIN students st ON sm.student_id = st.id
WHERE sm.school_id = :school_id
  AND sm.academic_year_id = :source_year_id
  AND sm.is_active = True
  AND s.is_active = True AND s.status = 'Active'
  AND st.is_active = True AND st.status = 'Active'
```

**For each row:**
```python
# Check duplicate
existing = SELECT id FROM student_mentors
    WHERE school_id = :school_id
      AND academic_year_id = :target_year_id
      AND student_id = :student_id

if existing:
    skipped += 1
    continue

new_sm = StudentMentor(
    id=uuid.uuid4(),
    school_id=school_id,
    academic_year_id=target_year_id,
    student_id=row.student_id,
    staff_id=row.staff_id,
    assigned_date=date.today(),
    notes=row.notes,
)
db.add(new_sm)
cloned += 1
```

**Columns copied:** student_id, staff_id, notes
**Columns reset:** assigned_date = today
**Columns NOT copied:** id, academic_year_id, metadata_, timestamps, audit

---

## 8. Backend — ID Mapping Strategy

The `id_map` dict tracks old→new UUID mappings for parent tables whose IDs are referenced by child tables:

```python
id_map = {
    "class_sections": {},    # Used by: class_assignments, timetable_slots, fee_structures
    "period_configs": {},    # Used by: timetable_slots
    "grade_systems": {},     # Used by: grade_scales
}
```

### How mapping is built:

1. **During clone:** When a new row is created, store `id_map[table][old_id] = new_id`
2. **When skipping (already exists):** Query the existing row's ID and store it in the map
3. **Pre-existing data:** If Phase 2 needs class_sections but Phase 1 didn't clone them (already existed), call `_build_class_section_map()`:

```python
async def _build_class_section_map(
    db: AsyncSession,
    school_id: uuid.UUID,
    source_year_id: uuid.UUID,
    target_year_id: uuid.UUID,
) -> dict[uuid.UUID, uuid.UUID]:
    """Build mapping from source class_section IDs to target class_section IDs.
    
    Matches by (class_id, section_id) since those are the logical identity.
    """
    source_rows = SELECT id, class_id, section_id FROM class_sections
        WHERE school_id = :school_id AND academic_year_id = :source_year_id AND is_active = True
    
    target_rows = SELECT id, class_id, section_id FROM class_sections
        WHERE school_id = :school_id AND academic_year_id = :target_year_id AND is_active = True
    
    # Index target by (class_id, section_id) → id
    target_index = {(r.class_id, r.section_id): r.id for r in target_rows}
    
    # Map source id → target id
    mapping = {}
    for src in source_rows:
        target_id = target_index.get((src.class_id, src.section_id))
        if target_id:
            mapping[src.id] = target_id
    
    return mapping
```

---

## 9. Backend — Dependency Resolution

### Dependency Rules

| Module | Depends On | What it needs |
|--------|-----------|---------------|
| teacher_assignments | academic_structure | class_section_id mapping |
| timetable | academic_structure | class_section_id mapping |
| fee_structure | academic_structure | class_section_id mapping |
| grading_system (grade_scales) | grading_system (grade_systems) | Internal — handled within same function |
| timetable (slots) | timetable (period_configs) | Internal — handled within same function |

### Resolution Strategy

```python
# Before Phase 2, check if dependencies are met
if modules.teacher_assignments or modules.timetable or modules.fee_structure:
    if not id_map.get("class_sections"):
        # Check if target year already has class_sections (from a prior clone or manual setup)
        target_cs_count = COUNT(*) FROM class_sections
            WHERE school_id = :school_id AND academic_year_id = :target_year_id AND is_active = True
        
        if target_cs_count == 0:
            # Cannot proceed — need academic_structure
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Cannot clone Teacher Assignments / Timetable / Fee Structure without Academic Structure. Either enable Academic Structure module or set up class-sections for the target year first.",
                    "code": "MISSING_DEPENDENCY",
                    "required_modules": ["academic_structure"],
                }
            )
        else:
            # Build mapping from existing data
            id_map["class_sections"] = await _build_class_section_map(...)
```

---

## 10. Backend — Error Handling

### HTTP Status Codes

| Status | When |
|--------|------|
| 200 | Preview successful |
| 201 | Clone successful |
| 400 | Validation failure (same year, missing dependency, etc.) |
| 404 | Source or target year not found |
| 409 | Target year already has data and force not set |

### Error Response Format

```python
from src.core.exceptions import AppException

class CloneError(AppException):
    def __init__(self, message: str, code: str, details: dict = None):
        super().__init__(status_code=400, error=message, code=code)
        self.details = details
```

### Specific Error Cases

```python
# 1. Source year not found
if not source_year:
    raise NotFound("Academic Year", str(source_year_id))

# 2. Target year not found
if not target_year:
    raise NotFound("Academic Year", str(target_year_id))

# 3. Same year
if source_year_id == target_year_id:
    raise CloneError(
        "Source and target academic years must be different",
        code="SAME_YEAR",
    )

# 4. Target is current year
if target_year.is_current:
    raise CloneError(
        "Cannot initialize the current academic year. Set a different year as current first.",
        code="TARGET_IS_CURRENT",
    )

# 5. Source has no data at all
if all_counts_zero:
    raise CloneError(
        f"Source year '{source_year.name}' has no data to clone",
        code="SOURCE_EMPTY",
    )

# 6. Missing dependency (described in Section 9)

# 7. Source year belongs to different school (shouldn't happen with proper auth, but defense)
if source_year.school_id != school_id:
    raise NotFound("Academic Year", str(source_year_id))
```

---

## 11. Backend — Transaction Management

```python
async def execute_clone(...) -> CloneResponse:
    # All clone operations happen within the existing session
    # The session is managed by the dependency injection (SessionDep)
    # We do NOT commit until everything succeeds
    
    try:
        # ... all clone logic ...
        
        # Single commit at the end
        await db.commit()
        
        return CloneResponse(...)
    
    except Exception as e:
        # Rollback happens automatically via session context manager
        await db.rollback()
        raise
```

**Key points:**
- SQLAlchemy async session auto-rolls-back on exception
- We call `db.add()` for all new objects but don't `await db.flush()` between modules (batch insert)
- Exception in any module rolls back ALL modules (atomic)
- If we need IDs for mapping before commit, use `await db.flush()` after each Phase

**Flush strategy:**
```python
# Phase 1: clone independent modules, flush to get IDs for mapping
# ... clone class_sections ...
await db.flush()  # Now id_map["class_sections"] has real IDs

# Phase 2: clone dependent modules using the map
# ... clone class_assignments, timetable_slots, fee_structures ...

# Final commit
await db.commit()
```

---

## 12. Frontend — File Structure

### Files to Modify

```
src/pages/settings/SettingsPage.jsx     — Add "Initialize" button + modal trigger in AcademicYearTab
src/services/settingsService.js         — Add 2 new React Query hooks
src/config/api.js                       — Add 2 new endpoint URLs
```

### Components (all inline in SettingsPage.jsx or extracted)

```
AcademicYearTab                         — Existing, add "Initialize" button per year card
CloneYearModal                          — New component (~200 lines)
```

---

## 13. Frontend — API Config & Hooks

### File: `src/config/api.js` — Add to settings object:

```javascript
// Add these to the settings section:
clonePreview: (yearId) => `/admin/settings/academic-years/${yearId}/clone-preview`,
cloneInitialize: (targetId, sourceId) => `/admin/settings/academic-years/${targetId}/initialize-from/${sourceId}`,
```

### File: `src/services/settingsService.js` — Add these hooks:

```javascript
export const useClonePreview = (sourceYearId) =>
  useQuery({
    queryKey: ['settings', 'clone-preview', sourceYearId],
    queryFn: () => api.get(EP.clonePreview(sourceYearId)).then(r => r.data),
    enabled: !!sourceYearId,
  });

export const useInitializeFromYear = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ targetYearId, sourceYearId, modules }) =>
      api.post(EP.cloneInitialize(targetYearId, sourceYearId), { modules }).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['settings', 'academic-year'] });
      qc.invalidateQueries({ queryKey: ['settings', 'academic-years'] });
      qc.invalidateQueries({ queryKey: ['settings', 'class-sections'] });
      qc.invalidateQueries({ queryKey: ['settings', 'subjects'] });
      qc.invalidateQueries({ queryKey: ['settings', 'class-subjects'] });
      qc.invalidateQueries({ queryKey: ['settings', 'fee-structures'] });
      qc.invalidateQueries({ queryKey: ['timetable'] });
      qc.invalidateQueries({ queryKey: ['teachers'] });
    },
  });
};
```

---

## 14. Frontend — Component: CloneYearModal

### Props

```javascript
function CloneYearModal({ open, onClose, targetYear, allYears }) {
```

### State Variables

```javascript
const [sourceYearId, setSourceYearId] = useState(null);   // Selected source year
const [modules, setModules] = useState({                  // Checkbox states
  academic_structure: true,
  teacher_assignments: true,
  timetable: true,
  fee_structure: true,
  leave_policies: true,
  grading_system: true,
  transport: true,
  payroll: false,
  mentoring: false,
});
```

### Data Fetching

```javascript
const { data: preview, isLoading: previewLoading } = useClonePreview(sourceYearId);
const cloneMutation = useInitializeFromYear();
```

### Event Handlers

```javascript
const toggleModule = (key) => {
  setModules(prev => ({ ...prev, [key]: !prev[key] }));
};

const handleClone = () => {
  cloneMutation.mutate(
    { targetYearId: targetYear.id, sourceYearId, modules },
    {
      onSuccess: (data) => {
        toast.success(`Initialized ${data.total_records_cloned} records from ${data.source_year}`);
        onClose();
      },
      onError: (err) => {
        const msg = err.response?.data?.error || 'Clone failed';
        toast.error(msg);
      },
    }
  );
};

const totalSelected = preview
  ? Object.entries(modules)
      .filter(([_, enabled]) => enabled)
      .reduce((sum, [key]) => sum + (preview.modules[key]?.count || 0), 0)
  : 0;
```

### JSX Structure

```jsx
<Modal open={open} onClose={onClose} title={`Initialize ${targetYear.name}`} size="lg">
  {/* Source Year Selector */}
  <div className="mb-6">
    <label className="block text-sm font-medium text-slate-700 mb-2">Copy from</label>
    <select
      value={sourceYearId || ''}
      onChange={(e) => setSourceYearId(e.target.value || null)}
      className="input-field"
    >
      <option value="">Select source year...</option>
      {allYears
        .filter(y => y.id !== targetYear.id)
        .map(y => (
          <option key={y.id} value={y.id}>{y.name} ({y.start_date} → {y.end_date})</option>
        ))}
    </select>
  </div>

  {/* Module Table */}
  {sourceYearId && (
    <>
      {previewLoading ? (
        <div className="space-y-3">
          {[1,2,3,4,5].map(i => <Skeleton key={i} className="h-12 w-full" />)}
        </div>
      ) : preview ? (
        <>
          <table className="w-full text-sm border border-slate-200 rounded-lg overflow-hidden">
            <thead className="bg-slate-50">
              <tr>
                <th className="w-10 px-3 py-2.5"></th>
                <th className="text-left px-3 py-2.5 font-semibold text-slate-700">Module</th>
                <th className="text-left px-3 py-2.5 font-semibold text-slate-700">What will be copied</th>
                <th className="text-right px-3 py-2.5 font-semibold text-slate-700">Records</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(preview.modules).map(([key, mod]) => (
                <tr key={key} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="px-3 py-3">
                    <input
                      type="checkbox"
                      checked={modules[key] ?? false}
                      onChange={() => toggleModule(key)}
                      className="rounded border-slate-300"
                    />
                  </td>
                  <td className="px-3 py-3 font-medium text-slate-900">{mod.label}</td>
                  <td className="px-3 py-3 text-slate-500 text-xs">{mod.description}</td>
                  <td className="px-3 py-3 text-right font-mono text-slate-700">{mod.count}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Info banner */}
          <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-xs text-blue-700">
              Inactive staff, students, and out-of-service vehicles are automatically excluded.
              All copied data can be modified after initialization.
            </p>
          </div>
        </>
      ) : null}
    </>
  )}

  {/* Footer */}
  <div className="flex items-center justify-between mt-6 pt-4 border-t border-slate-100">
    <p className="text-sm text-slate-500">
      {totalSelected > 0 ? `≈ ${totalSelected} records will be copied` : 'Select modules to copy'}
    </p>
    <div className="flex gap-3">
      <Button variant="ghost" onClick={onClose}>Cancel</Button>
      <Button
        onClick={handleClone}
        loading={cloneMutation.isPending}
        disabled={!sourceYearId || totalSelected === 0}
      >
        Initialize ({totalSelected})
      </Button>
    </div>
  </div>
</Modal>
```

---

## 15. Frontend — Integration with AcademicYearTab

### Changes to existing `AcademicYearTab` component:

Add state:
```javascript
const [cloneTarget, setCloneTarget] = useState(null);  // Year being initialized
```

Add button on each year card (after "Set Current" button, for non-current years):

```jsx
{!year.is_current && (
  <button
    onClick={() => setCloneTarget(year)}
    className="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
  >
    Initialize
  </button>
)}
```

Add modal at the bottom of the component:

```jsx
{cloneTarget && (
  <CloneYearModal
    open={!!cloneTarget}
    onClose={() => setCloneTarget(null)}
    targetYear={cloneTarget}
    allYears={years}
  />
)}
```

---

## 16. Frontend — Post-Clone UI

### Success Toast
```
"Initialized 588 records from 2025-2026"
```

### Query Invalidation (triggers refetch)
After successful clone, these queries are invalidated:
- `academic-year` — refreshes current year display
- `academic-years` — refreshes the list
- `class-sections` — shows the new class-sections
- `subjects` — still same (masters not cloned)
- `class-subjects` — shows new mappings
- `fee-structures` — shows new structures
- `timetable` — shows new timetable
- `teachers` — shows new assignments

### Visual Indicator on Year Card (optional enhancement)
After clone, the year card could show:
```
2026-2027  (Apr 2026 → Mar 2027)
✓ Initialized from 2025-2026 — 588 records
```

This can be stored in the academic_year's `metadata` JSON field during clone:
```python
target_year.metadata_ = {
    **(target_year.metadata_ or {}),
    "initialized_from": source_year.name,
    "initialized_at": datetime.now(timezone.utc).isoformat(),
    "records_cloned": total_cloned,
}
```

---

## 17. Testing Scenarios

### Manual Testing Checklist

| # | Scenario | Expected |
|---|----------|----------|
| 1 | Click "Initialize" on empty year, select source, all modules checked | Clone succeeds, counts match preview |
| 2 | Click "Initialize" twice on same target | Second time skips all (0 cloned, all skipped) |
| 3 | Clone with only "Academic Structure" checked | Only class_sections + class_subjects created |
| 4 | Clone "Teacher Assignments" WITHOUT "Academic Structure" when target has no class_sections | Error: MISSING_DEPENDENCY |
| 5 | Clone "Teacher Assignments" WITHOUT "Academic Structure" when target already has class_sections | Succeeds using existing class_sections |
| 6 | Source year has inactive staff | Those staff's assignments NOT cloned, warning shown |
| 7 | Source year has out-of-service vehicle | Route assignment NOT cloned, warning shown |
| 8 | Source year has deleted subject | class_subjects referencing it NOT cloned |
| 9 | Source year has 0 records for a module | That module shows count=0 in preview, clones 0 |
| 10 | Select target == source year | Error: SAME_YEAR |
| 11 | Select current year as target | Error: TARGET_IS_CURRENT |
| 12 | Clone "Payroll" | salary_structures created with effective_from = target year start_date |
| 13 | Clone "Transport" with students | Both route_assignments and student_transport cloned |
| 14 | After clone, navigate to Timetable page | Timetable shows for new year |
| 15 | After clone, check Fee Structures tab | Fee structures show for new year |

### Data Verification Queries (run after clone)

```sql
-- Verify class_sections cloned
SELECT COUNT(*) FROM class_sections WHERE academic_year_id = '<target>' AND school_id = '<school>';

-- Verify no duplicate class_sections
SELECT class_id, section_id, COUNT(*) as cnt 
FROM class_sections 
WHERE academic_year_id = '<target>' AND school_id = '<school>' AND is_active = 1
GROUP BY class_id, section_id HAVING cnt > 1;

-- Verify timetable slots point to valid period_configs
SELECT ts.id FROM timetable_slots ts
LEFT JOIN period_configs pc ON ts.period_config_id = pc.id
WHERE ts.academic_year_id = '<target>' AND pc.id IS NULL;

-- Verify no inactive staff in cloned assignments
SELECT ca.id FROM class_assignments ca
JOIN staff s ON ca.staff_id = s.id
WHERE ca.academic_year_id = '<target>' AND (s.is_active = 0 OR s.status != 'Active');
```

---

## 18. Edge Cases

| # | Edge Case | Handling |
|---|-----------|----------|
| 1 | School has no academic years | "Initialize" button not shown (no source to pick) |
| 2 | School has only 1 academic year | No other year to clone from — dropdown empty, button disabled |
| 3 | Source year has class_sections but classes table has since been soft-deleted | Skip those class_sections, add warning |
| 4 | Staff member has both is_active=True but status="Resigned" | Excluded (we check BOTH is_active AND status='Active') |
| 5 | Vehicle is_active=True but status="Maintenance" | For route_assignments: excluded (check status='Operational') |
| 6 | fee_structures with class_section_id=NULL (school-wide fees) | Clone directly, no mapping needed |
| 7 | Timetable slot has staff_id pointing to inactive teacher | Clone the slot but set staff_id=NULL (with warning) |
| 8 | grade_systems with is_default=True exists in BOTH source and target | Skip source one, use existing target default |
| 9 | student_transport has route that was deleted | Skip that row (JOIN ensures only active routes) |
| 10 | Large school: 500+ timetable slots | Still single transaction, should complete in <3s |
| 11 | Network timeout during clone | Transaction rolls back entirely — safe to retry |
| 12 | User navigates away during clone | Clone completes server-side regardless; user sees result on next visit |
| 13 | Two admins clone to same target simultaneously | First one succeeds; second skips all (idempotent checks) |
| 14 | salary_structures unique constraint (school_id, staff_id) | Migration added academic_year_id to this — no conflict across years |
| 15 | leave_policies with members JSON (specific staff IDs) | Copied as-is — if a member left, policy still applies to remaining |

---

## Estimated Line Counts

| File | Lines |
|------|-------|
| `src/admin/settings/clone_schemas.py` | ~80 |
| `src/admin/settings/clone_service.py` | ~500 |
| `src/admin/settings/router.py` (additions) | ~25 |
| Frontend: `CloneYearModal` in SettingsPage.jsx | ~180 |
| Frontend: `settingsService.js` (additions) | ~20 |
| Frontend: `api.js` (additions) | ~2 |
| **Total new code** | **~807 lines** |
