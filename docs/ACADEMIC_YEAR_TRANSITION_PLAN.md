# Academic Year Transition — Clone/Copy Feature Plan

**Created: 2026-07-04**

---

## 1. Business Context

When a school moves from one academic year (e.g., 2025-2026) to the next (2026-2027), administrators need to carry forward structural/configuration data rather than recreating it manually. This feature provides a one-click "clone from previous year" capability.

### User Flow

1. Admin creates a new academic year in Settings → Academic Year tab
2. Admin clicks "Initialize from Previous Year" (or during creation, selects "Copy from: 2025-2026")
3. System clones applicable data, admin reviews and adjusts
4. Admin sets the new year as "Current" when ready to go live

---

## 2. What Gets Cloned — Admin-Facing Module View

The admin sees **high-level feature modules** (not raw table names). The backend handles all dependent tables internally per module.

---

### Admin Clone UI — Modal Layout

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  Initialize 2026-2027 from 2025-2026                                             │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  Select modules to copy:                                                         │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │    │ Module                │ What will be copied                     │ Count│  │
│  ├────┼───────────────────────┼─────────────────────────────────────────┼──────┤  │
│  │ ☑  │ Academic Structure    │ Class-section combinations,             │  24  │  │
│  │    │                       │ subject-class mappings                  │ +96  │  │
│  ├────┼───────────────────────┼─────────────────────────────────────────┼──────┤  │
│  │ ☑  │ Teacher Assignments   │ Teacher subject qualifications,         │  45  │  │
│  │    │                       │ class-section-subject allocations       │ +72  │  │
│  ├────┼───────────────────────┼─────────────────────────────────────────┼──────┤  │
│  │ ☑  │ Timetable             │ Period/bell schedule config,            │   8  │  │
│  │    │                       │ full weekly timetable grid              │+288  │  │
│  ├────┼───────────────────────┼─────────────────────────────────────────┼──────┤  │
│  │ ☑  │ Fee Structure         │ Fee types, amounts, frequencies         │  48  │  │
│  │    │                       │ per class                               │      │  │
│  ├────┼───────────────────────┼─────────────────────────────────────────┼──────┤  │
│  │ ☑  │ Leave Policies        │ Leave types, limits, rules,             │   5  │  │
│  │    │                       │ carry-forward settings                  │      │  │
│  ├────┼───────────────────────┼─────────────────────────────────────────┼──────┤  │
│  │ ☑  │ Grading System        │ Grade scheme (A+, A, B+...),            │   1  │  │
│  │    │                       │ percentage ranges, grade points         │  +8  │  │
│  ├────┼───────────────────────┼─────────────────────────────────────────┼──────┤  │
│  │ ☑  │ Transport             │ Route-vehicle-driver assignments,       │   6  │  │
│  │    │                       │ student pickup/drop points              │+180  │  │
│  ├────┼───────────────────────┼─────────────────────────────────────────┼──────┤  │
│  │ ☐  │ Payroll               │ Salary structures (basic, HRA, DA,     │  35  │  │
│  │    │                       │ deductions) for all active staff        │      │  │
│  ├────┼───────────────────────┼─────────────────────────────────────────┼──────┤  │
│  │ ☐  │ Mentoring             │ Student-teacher mentor assignments      │ 120  │  │
│  └────┴───────────────────────┴─────────────────────────────────────────┴──────┘  │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │ ⓘ  Inactive staff, inactive students, and out-of-service vehicles are   │    │
│  │     automatically excluded from cloning.                                 │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │ ⓘ  All copied data can be modified after initialization.                │    │
│  │     Fee amounts, timetable slots, and teacher assignments are starting  │    │
│  │     points — review and adjust before setting this year as current.     │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
│                     [ Cancel ]              [ Initialize (≈ 588 records) ]        │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

### Module → Backend Table Mapping (internal, not shown to admin)

| Admin Module | Backend Tables Cloned | Dependency |
|--------------|----------------------|------------|
| **Academic Structure** | `class_sections`, `class_subjects` | None (Phase 1) |
| **Teacher Assignments** | `staff_subjects`, `class_assignments` | class_sections must exist |
| **Timetable** | `period_configs`, `timetable_slots` | class_sections + period_configs |
| **Fee Structure** | `fee_structures` | class_sections (for class_section_id resolution) |
| **Leave Policies** | `leave_policies` | None (Phase 1) |
| **Grading System** | `grade_systems`, `grade_scales` | None (Phase 1) |
| **Transport** | `route_assignments`, `student_transport` | None (Phase 1) |
| **Payroll** | `salary_structures` | None (Phase 1) |
| **Mentoring** | `student_mentors` | None (Phase 1) |

**Key point:** The backend resolves dependencies automatically. If admin selects "Timetable" but NOT "Academic Structure", the backend checks if class_sections already exist for the target year. If not, it returns an error:

```json
{
  "error": "Cannot clone Timetable — Academic Structure must be cloned first (no class_sections found for 2026-2027)",
  "code": "MISSING_DEPENDENCY",
  "required_modules": ["academic_structure"]
}
```

---

### Module Default States

| Module | Default | Reason |
|--------|---------|--------|
| Academic Structure | ☑ ON | Almost always needed |
| Teacher Assignments | ☑ ON | Usually same teachers continue |
| Timetable | ☑ ON | Starting point, admin tweaks |
| Fee Structure | ☑ ON | Amounts carry forward (admin adjusts for hikes) |
| Leave Policies | ☑ ON | Policies rarely change |
| Grading System | ☑ ON | Usually identical year to year |
| Transport | ☑ ON | Routes/vehicles/drivers usually continue |
| Payroll | ☐ OFF | Admin may want to apply hikes first |
| Mentoring | ☐ OFF | Often changes with promotions |

---

### What is NOT cloned (never shown in UI, handled implicitly)

| Data Type | Reason | How it's created in new year |
|-----------|--------|------------------------------|
| Student enrollments | Students get promoted, not flat-copied | Separate "Bulk Promote" feature |
| Attendance | Starts fresh | Recorded daily by teachers |
| Exams & results | New schedule each year | Created by admin |
| Assignments & submissions | New work each year | Created by teachers |
| Fee records & payments | Generated from structures | "Generate Due Fees" button |
| Leave balances | Allocated from policies | "Allocate Balances" action |
| Payslips | Generated monthly | "Run Payroll" action |
| Salary advances | Per-request | Staff applies individually |
| Notifications | Transient | Created as needed |

---

### SPECIAL HANDLING

| Item | Behavior |
|------|----------|
| leave_balances | NOT cloned — instead, **re-allocated** from leave_policies (total_per_year + carry_forward from previous year's remaining) |

---

## 3. Clone Logic — Detailed Per Table

### 3.1 class_sections

```
Source: class_sections WHERE school_id = X AND academic_year_id = OLD_YEAR AND is_active = True
Action: For each row, create new row with:
  - Same class_id, section_id
  - academic_year_id = NEW_YEAR
  - New UUID
  - Skip if (school_id, class_id, section_id, academic_year_id) already exists
```

**Why clone instead of reuse:** The same class_section combo for a different year is a different entity (different students enrolled, different timetable).

### 3.2 class_subjects

```
Source: class_subjects WHERE school_id = X AND academic_year_id = OLD_YEAR AND is_active = True
Action: For each row, create new row with:
  - Same class_id, subject_id
  - academic_year_id = NEW_YEAR
  - New UUID
  - Skip duplicates
```

### 3.3 staff_subjects

```
Source: staff_subjects WHERE school_id = X AND academic_year_id = OLD_YEAR AND is_active = True
Action: For each row, create new row with:
  - Same staff_id, subject_id, is_primary
  - academic_year_id = NEW_YEAR
  - New UUID
  - Only clone if staff.is_active = True (skip departed staff)
  - Skip duplicates
```

### 3.4 class_assignments

```
Source: class_assignments WHERE school_id = X AND academic_year_id = OLD_YEAR 
        AND is_active = True AND status = 'Active'
Action: For each row:
  - Resolve new class_section_id (find the cloned class_section for same class+section in NEW_YEAR)
  - Same staff_id, subject_id, is_class_teacher, periods_per_week
  - academic_year_id = NEW_YEAR
  - status = 'Active', end_date = None, end_reason = None
  - Only clone if staff.is_active = True
  - Skip duplicates
```

**Dependency:** Requires class_sections to be cloned first.

### 3.5 fee_structures

```
Source: fee_structures WHERE school_id = X AND academic_year_id = OLD_YEAR AND is_active = True
Action: For each row, create new row with:
  - Same class_id, fee_type, fee_category, amount, frequency
  - Resolve class_section_id to new year's equivalent (if set)
  - academic_year_id = NEW_YEAR
  - New UUID
  - Skip duplicates
```

**Admin note:** Amounts are copied as-is. Admin should review and adjust fee amounts for the new year (e.g., annual hike).

### 3.6 leave_policies

```
Source: leave_policies WHERE school_id = X AND academic_year_id = OLD_YEAR AND is_active = True
Action: For each row, create new row with:
  - Same leave_type, display_name, code, total_per_year, carry_forward, 
    max_carry_forward, max_consecutive_days, requires_approval, half_day_allowed,
    medical_certificate_required_after_days, advance_notice_days, applicable_to, members
  - academic_year_id = NEW_YEAR
  - New UUID
  - Skip duplicates
```

### 3.7 period_configs

```
Source: period_configs WHERE school_id = X AND academic_year_id = OLD_YEAR AND is_active = True
Action: For each row, create new row with:
  - Same name, start_time, end_time, duration_minutes, is_break, sort_order
  - academic_year_id = NEW_YEAR
  - New UUID
  - Skip duplicates (based on school_id + academic_year_id + start_time)
```

### 3.8 timetable_slots

```
Source: timetable_slots WHERE school_id = X AND academic_year_id = OLD_YEAR AND is_active = True
Action: For each row:
  - Resolve new class_section_id (cloned equivalent in NEW_YEAR)
  - Resolve new period_config_id (cloned equivalent in NEW_YEAR, matched by start_time)
  - Same day_of_week, subject_id, staff_id, slot_type
  - academic_year_id = NEW_YEAR
  - Only if staff.is_active = True (else leave staff_id as NULL)
  - Skip duplicates
```

**Dependency:** Requires class_sections and period_configs to be cloned first.

### 3.9 grade_systems + grade_scales

```
Source: grade_systems WHERE school_id = X AND academic_year_id = OLD_YEAR AND is_active = True
Action: For each grade_system:
  - Clone the system: same name, is_default
  - academic_year_id = NEW_YEAR
  - Then clone all grade_scales for that system:
    - Same grade, min_percentage, max_percentage, grade_point, description, sort_order
    - grade_system_id = new system's ID
  - Skip duplicates
```

### 3.10 route_assignments

```
Source: route_assignments WHERE school_id = X AND academic_year_id = OLD_YEAR 
        AND is_active = True AND status = 'Active'
Action: For each row, create new row with:
  - Same route_id, vehicle_id, driver_id, helper_id
  - academic_year_id = NEW_YEAR
  - status = 'Active'
  - Only if vehicle.is_active AND driver.is_active (skip decommissioned)
  - Skip duplicates
```

### 3.11 student_transport (Optional — admin selectable)

```
Source: student_transport WHERE school_id = X AND academic_year_id = OLD_YEAR AND is_active = True
Action: For each row, create new row with:
  - Same student_id, route_id, pickup_point, drop_point
  - academic_year_id = NEW_YEAR
  - New UUID
  - Only if student.is_active AND route.is_active
  - Skip duplicates (based on school_id + student_id + academic_year_id)
```

**Note:** Optional because students may change routes, graduate, or drop transport. Admin should review after clone. Best used when most students continue with the same pickup/drop points.

### 3.12 salary_structures (Optional — admin selectable)

```
Source: salary_structures WHERE school_id = X AND academic_year_id = OLD_YEAR AND is_active = True
Action: For each row, create new row with:
  - Same staff_id, basic_salary, hra, da, transport_allowance, medical_allowance,
    other_allowances, pf_deduction, professional_tax, tds, other_deductions, net_salary
  - academic_year_id = NEW_YEAR
  - effective_from = new year's start_date
  - New UUID
  - Only if staff.is_active (skip departed staff)
  - Skip duplicates (based on school_id + staff_id unique constraint)
```

**Note:** Amounts are copied as-is from previous year. Admin should then use salary revisions to apply hikes/increments for the new year. This gives a starting baseline rather than building from scratch.

### 3.13 student_mentors (Optional — admin selectable)

```
Source: student_mentors WHERE school_id = X AND academic_year_id = OLD_YEAR AND is_active = True
Action: For each row:
  - Same student_id, staff_id
  - academic_year_id = NEW_YEAR
  - assigned_date = today
  - Only if staff.is_active AND student.is_active
  - Skip duplicates
```

**Note:** Optional because mentor assignments often change. UI should present as a checkbox: "☐ Also copy mentor assignments"

---

## 4. Clone Order (respecting dependencies)

```
Phase 1 — Independent (can run in parallel):
  ├── class_sections
  ├── class_subjects
  ├── staff_subjects
  ├── leave_policies
  ├── period_configs
  ├── grade_systems + grade_scales
  ├── route_assignments
  └── salary_structures

Phase 2 — Depends on Phase 1:
  ├── class_assignments (needs class_sections)
  ├── fee_structures (needs class_sections)
  └── timetable_slots (needs class_sections + period_configs)

Phase 3 — Optional, depends on Phase 1:
  ├── student_transport (needs routes to be valid)
  └── student_mentors (needs class_sections for enrollment context)
```

---

## 5. API Design

### Endpoint

```
POST /admin/settings/academic-years/{new_year_id}/initialize-from/{source_year_id}
```

### Request Body

Admin sends high-level module keys. Backend resolves which tables to clone per module.

```json
{
  "modules": {
    "academic_structure": true,
    "teacher_assignments": true,
    "timetable": true,
    "fee_structure": true,
    "leave_policies": true,
    "grading_system": true,
    "transport": true,
    "payroll": false,
    "mentoring": false
  },
  "options": {}
  // Note: inactive staff, students, and vehicles are ALWAYS excluded.
  // No option to include them — this is a hard rule, not configurable.
}
```

**Module → Tables resolved by backend:**

| Module Key | Tables Cloned |
|------------|---------------|
| `academic_structure` | class_sections, class_subjects |
| `teacher_assignments` | staff_subjects, class_assignments |
| `timetable` | period_configs, timetable_slots |
| `fee_structure` | fee_structures |
| `leave_policies` | leave_policies |
| `grading_system` | grade_systems, grade_scales |
| `transport` | route_assignments, student_transport |
| `payroll` | salary_structures |
| `mentoring` | student_mentors |

### Response

```json
{
  "message": "Academic year 2026-2027 initialized from 2025-2026",
  "source_year": "2025-2026",
  "target_year": "2026-2027",
  "results": {
    "academic_structure": {
      "cloned": 120,
      "skipped": 0,
      "details": {
        "class_sections": { "cloned": 24, "skipped": 0 },
        "class_subjects": { "cloned": 96, "skipped": 0 }
      }
    },
    "teacher_assignments": {
      "cloned": 117,
      "skipped": 3,
      "details": {
        "staff_subjects": { "cloned": 45, "skipped": 3, "skipped_reason": "inactive staff" },
        "class_assignments": { "cloned": 72, "skipped": 0 }
      }
    },
    "timetable": {
      "cloned": 296,
      "skipped": 12,
      "details": {
        "period_configs": { "cloned": 8, "skipped": 0 },
        "timetable_slots": { "cloned": 288, "skipped": 12 }
      }
    },
    "fee_structure": {
      "cloned": 48,
      "skipped": 0,
      "details": { "fee_structures": { "cloned": 48, "skipped": 0 } }
    },
    "leave_policies": {
      "cloned": 5,
      "skipped": 0,
      "details": { "leave_policies": { "cloned": 5, "skipped": 0 } }
    },
    "grading_system": {
      "cloned": 9,
      "skipped": 0,
      "details": {
        "grade_systems": { "cloned": 1, "skipped": 0 },
        "grade_scales": { "cloned": 8, "skipped": 0 }
      }
    },
    "transport": {
      "cloned": 186,
      "skipped": 1,
      "details": {
        "route_assignments": { "cloned": 6, "skipped": 1 },
        "student_transport": { "cloned": 180, "skipped": 0 }
      }
    },
    "payroll": { "status": "not_requested" },
    "mentoring": { "status": "not_requested" }
  },
  "total_records_cloned": 781,
  "warnings": [
    "3 teacher assignments skipped: staff EMP012, EMP018, EMP031 are inactive",
    "1 route assignment skipped: vehicle BUS-003 is out of service"
  ]
}
```

### Validation Rules

- Target year must exist and NOT be the current year (to prevent accidental overwrite of live data)
- Source year must exist and have data
- Target year should be empty (or endpoint should support `force: true` to re-clone)
- If target already has data for a module, skip that module (or warn and require `force`)

### Error Cases

```json
// Target already has data
{
  "error": "Target year 2026-2027 already has 24 class_sections. Use force:true to overwrite or delete existing data first.",
  "code": "TARGET_NOT_EMPTY"
}

// Source has no data
{
  "error": "Source year 2024-2025 has no class_sections to clone",
  "code": "SOURCE_EMPTY"
}

// Same year
{
  "error": "Source and target academic years must be different",
  "code": "SAME_YEAR"
}
```

---

## 6. Frontend UX

### Trigger Point: Academic Year Card

After creating the year, show an "Initialize" button on the academic year card:

```
┌─────────────────────────────────────────────────────────────┐
│ 2026-2027  (Apr 2026 → Mar 2027)          [ Set Current ]  │
│ Status: Empty — no data configured                          │
│                                                             │
│ [ Initialize from Previous Year ]  [ Edit ]  [ Delete ]    │
└─────────────────────────────────────────────────────────────┘
```

### Clone Modal

Clicking "Initialize from Previous Year" opens the module selection modal shown in **Section 2** above (the table-based UI with Module, Description, and Count columns).

The modal flow:
1. Admin selects source year from dropdown
2. Backend fetches counts per module from the source year (preview API call)
3. Admin checks/unchecks modules and sets options
4. Admin clicks "Initialize" → backend clones all selected modules + dependencies
5. Success toast with summary

### Preview API (for count column in the modal)

```
GET /admin/settings/academic-years/{source_year_id}/clone-preview
```

Response:
```json
{
  "source_year": "2025-2026",
  "modules": {
    "academic_structure": { "label": "Academic Structure", "description": "Class-section combinations, subject-class mappings", "count": 120 },
    "teacher_assignments": { "label": "Teacher Assignments", "description": "Teacher subject qualifications, class-section-subject allocations", "count": 117 },
    "timetable": { "label": "Timetable", "description": "Period/bell schedule config, full weekly timetable grid", "count": 296 },
    "fee_structure": { "label": "Fee Structure", "description": "Fee types, amounts, frequencies per class", "count": 48 },
    "leave_policies": { "label": "Leave Policies", "description": "Leave types, limits, rules, carry-forward settings", "count": 5 },
    "grading_system": { "label": "Grading System", "description": "Grade scheme (A+, A, B+...), percentage ranges, grade points", "count": 9 },
    "transport": { "label": "Transport", "description": "Route-vehicle-driver assignments, student pickup/drop points", "count": 186 },
    "payroll": { "label": "Payroll", "description": "Salary structures (basic, HRA, DA, deductions) for all active staff", "count": 35 },
    "mentoring": { "label": "Mentoring", "description": "Student-teacher mentor assignments", "count": 120 }
  }
}
```

### Post-Initialize Success State

```
┌─────────────────────────────────────────────────────────────┐
│ 2026-2027  (Apr 2026 → Mar 2027)          [ Set Current ]  │
│ ✓ Initialized from 2025-2026 on Jul 04, 2026               │
│   120 structures · 117 teacher mappings · 296 timetable     │
│                                                             │
│ [ Review Structure ]  [ Edit ]  [ Delete ]                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Backend Implementation Plan

### File Structure

```
src/admin/settings/
├── service.py          (add clone functions)
├── router.py           (add endpoint)
└── schemas.py          (add request/response schemas)
```

### Service Function Skeleton

```python
async def initialize_academic_year(
    db: AsyncSession,
    school_id: uuid.UUID,
    target_year_id: uuid.UUID,
    source_year_id: uuid.UUID,
    modules: dict[str, bool],
    options: dict,
    created_by: uuid.UUID,
) -> dict:
    """Clone selected data from source academic year to target."""
    
    # 1. Validate source and target exist
    # 2. Validate target is not current
    # 3. Check target is empty (or force mode)
    # 4. Build ID mapping: old_class_section_id → new_class_section_id
    # 5. Execute clones in dependency order
    # 6. Return summary with counts and warnings
```

### Key Implementation Details

1. **ID Mapping:** When cloning class_sections, maintain a `{old_id: new_id}` dict. Downstream clones (class_assignments, timetable_slots, fee_structures) use this to resolve the new FK values.

2. **Idempotency:** Use `ON DUPLICATE KEY` / skip logic so running the clone twice doesn't create duplicates.

3. **Transaction:** Entire clone runs in a single transaction. If any step fails, everything rolls back.

4. **Performance:** For schools with ~300 timetable slots, this is ~500 INSERTs total. Should complete in < 2 seconds. No need for background jobs.

5. **Audit trail:** All cloned records get `created_by` set to the admin who triggered the clone.

---

## 8. Leave Balance Allocation (Separate but Related)

After cloning leave_policies, admin needs to **allocate balances** for all staff. This is already an existing endpoint:

```
POST /admin/leaves/allocate
```

This should be called after the academic year is set as current. It creates `leave_balances` for each staff member based on:
- `total_per_year` from leave_policies
- `carry_forward` amount from previous year's remaining balance (if policy allows)

This is NOT part of the clone — it's a separate action triggered when the year goes live.

---

## 9. Student Promotion (Separate Feature)

Student enrollment in the new year is handled by a separate "Promotion" feature:

```
POST /admin/students/bulk-promote
```

This moves students from Class 9-A (old year) → Class 10-A (new year), creating new `student_enrollments` records. It's intentionally separate from the year clone because:
- Not all students pass / get promoted
- Some students change sections
- New admissions happen independently
- Promotion requires result/attendance thresholds

---

## 10. Migration Checklist for Existing Schools

For schools already running on the platform (data exists without proper year scoping on the 3 newly-added tables):

1. Run the Alembic migration (adds `academic_year_id` to staff_subjects, salary_advances, route_assignments)
2. Migration backfills with current academic year
3. No clone needed — existing data is already associated with the current year
4. Clone feature is used starting from the NEXT year transition

---

## 11. Edge Cases

| Scenario | Handling |
|----------|----------|
| Source year has 0 records for a module | Skip that module, report "0 cloned" |
| Staff member left between years | Skip their assignments (skip_inactive_staff) |
| Subject was deleted | Skip mappings referencing it |
| Class was deleted | Skip class_sections referencing it |
| Vehicle decommissioned | Skip route_assignment |
| Target year already has partial data | Skip existing, clone only new. Report what was skipped |
| Admin runs clone twice | Idempotent — duplicates are skipped |
| Clone then delete source year | Cloned data is independent (new UUIDs, new year FK) — safe |
| School has no previous year | Button disabled / error message |

---

## 12. Future Enhancements

1. **Selective clone per class:** "Only copy timetable for Class 10, not Class 9"
2. **Diff view:** Show what changed between years after clone + manual edits
3. **Auto-promote + clone in one flow:** Wizard that does year creation → clone → promotion → balance allocation
4. **Template years:** Clone from a "template" year rather than the immediately previous one
5. **Undo clone:** Bulk-delete all records created by a specific clone operation (tracked via metadata JSON field)

---

## 13. Estimated Effort

| Task | Effort |
|------|--------|
| Backend: clone service function + helpers | 2-3 days |
| Backend: API endpoint + validation + schemas | 0.5 day |
| Backend: unit tests | 1 day |
| Frontend: Initialize modal UI | 1-2 days |
| Frontend: source year preview (counts) | 0.5 day |
| Frontend: post-clone success state | 0.5 day |
| Integration testing | 1 day |
| **Total** | **~7-8 days** |
