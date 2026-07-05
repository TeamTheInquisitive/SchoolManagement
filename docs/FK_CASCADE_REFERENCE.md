# Foreign Key & Cascade Delete Reference

**Last Updated: 2026-07-04**

## Overview

- **Total tables:** 46
- **FKs with `ondelete="CASCADE"`:** 6
- **FKs with RESTRICT (default):** All others
- **Primary delete strategy:** Soft-delete (`is_active=False`)
- **Hard delete:** Only timetable module + superadmin school deletion

---

## FKs WITH `ondelete="CASCADE"` (DB auto-deletes child)

| Child Table | FK Column | Parent Table | Parent Delete Strategy |
|-------------|-----------|--------------|------------------------|
| staff_subjects | staff_id | staff | Soft |
| exam_results | exam_id | exams | Soft |
| grade_scales | grade_system_id | grade_systems | Soft |
| notification_recipients | notification_id | notifications | Soft |
| attendance_records | attendance_session_id | attendance_sessions | Soft |
| assignment_submissions | assignment_id | assignments | Soft |

**ORM-level cascades (via `relationship(..., cascade="all, delete-orphan")`):**
- `Staff.subjects` → StaffSubject
- `AttendanceSession.records` → AttendanceRecord

---

## FKs WITHOUT cascade (RESTRICT) — Grouped by Parent

### schools (Hard delete: superadmin only)

| Child Table | FK Column |
|-------------|-----------|
| users | school_id |
| academic_years | school_id |
| settings | school_id |
| enum_configs | school_id |
| classes | school_id |
| sections | school_id |
| subjects | school_id |
| students | school_id |
| parents | school_id |
| staff | school_id |
| vehicles | school_id |
| drivers | school_id |
| helpers | school_id |
| routes | school_id |
| library_books | school_id |
| subscriptions | school_id |
| subscription_payments | school_id |
| *(+ all BaseModel tables via SchoolMixin)* | school_id |

---

### academic_years (Soft delete, blocked if `is_current=True`)

| Child Table | FK Column |
|-------------|-----------|
| class_sections | academic_year_id |
| class_subjects | academic_year_id |
| student_enrollments | academic_year_id |
| student_mentors | academic_year_id |
| class_assignments | academic_year_id |
| staff_subjects | academic_year_id |
| period_configs | academic_year_id |
| timetable_slots | academic_year_id |
| attendance_sessions | academic_year_id |
| exams | academic_year_id |
| grade_systems | academic_year_id |
| leave_policies | academic_year_id |
| leave_applications | academic_year_id |
| leave_balances | academic_year_id |
| fee_structures | academic_year_id |
| fee_records | academic_year_id |
| fee_reminders | academic_year_id |
| salary_structures | academic_year_id |
| payslips | academic_year_id |
| salary_advances | academic_year_id |
| salary_revisions | academic_year_id |
| assignments | academic_year_id |
| student_transport | academic_year_id |
| route_assignments | academic_year_id |
| activities | academic_year_id |
| awards | academic_year_id |
| disciplinary_records | academic_year_id |
| parent_meetings | academic_year_id |
| adhoc_classes | academic_year_id |

---

### classes (Soft delete)

| Child Table | FK Column |
|-------------|-----------|
| class_sections | class_id |
| class_subjects | class_id |
| fee_structures | class_id |

---

### sections (Soft delete)

| Child Table | FK Column |
|-------------|-----------|
| class_sections | section_id |

---

### class_sections (Soft delete, blocked if students enrolled)

| Child Table | FK Column |
|-------------|-----------|
| student_enrollments | class_section_id |
| class_assignments | class_section_id |
| timetable_slots | class_section_id |
| attendance_sessions | class_section_id |
| exams | class_section_id |
| assignments | class_section_id |
| fee_structures | class_section_id |
| adhoc_classes | class_section_id |

---

### subjects (Soft delete)

| Child Table | FK Column |
|-------------|-----------|
| class_subjects | subject_id |
| staff_subjects | subject_id |
| class_assignments | subject_id |
| timetable_slots | subject_id |
| attendance_sessions | subject_id |
| exams | subject_id |
| assignments | subject_id |
| adhoc_classes | subject_id |

---

### students (Soft delete)

| Child Table | FK Column |
|-------------|-----------|
| users | student_id |
| student_enrollments | student_id |
| student_parents | student_id |
| student_mentors | student_id |
| attendance_records | student_id |
| exam_results | student_id |
| assignment_submissions | student_id |
| fee_records | student_id |
| student_transport | student_id |
| activities | student_id |
| awards | student_id |
| disciplinary_records | student_id |
| parent_meetings | student_id |

---

### parents (Soft delete)

| Child Table | FK Column |
|-------------|-----------|
| users | parent_id |
| student_parents | parent_id |
| parent_meetings | parent_id |

---

### staff (Soft delete)

| Child Table | FK Column | Notes |
|-------------|-----------|-------|
| users | staff_id | |
| staff_subjects | staff_id | Has CASCADE |
| class_assignments | staff_id | |
| student_mentors | staff_id | |
| timetable_slots | staff_id | |
| attendance_sessions | submitted_by | |
| exams | examiner_id | |
| leave_applications | staff_id | |
| leave_applications | substitute_teacher_id | |
| leave_balances | staff_id | |
| salary_structures | staff_id | |
| payslips | staff_id | |
| salary_advances | staff_id | |
| salary_revisions | staff_id | |
| assignments | staff_id | |
| assignment_submissions | graded_by | |
| activities | recorded_by | |
| awards | recorded_by | |
| disciplinary_records | reported_by | |
| parent_meetings | conducted_by | |
| adhoc_classes | staff_id | |
| adhoc_classes | original_staff_id | |

---

### users (Soft delete)

| Child Table | FK Column |
|-------------|-----------|
| staff | user_id |
| leave_applications | approved_by |
| leave_applications | rejected_by |
| fee_payments | recorded_by |
| fee_reminders | sent_by |
| fee_penalties | applied_by |
| payslips | generated_by |
| salary_advances | approved_by |
| salary_advances | rejected_by |
| salary_revisions | approved_by |
| library_issues | borrower_id |
| notifications | created_by_user_id |
| notification_recipients | user_id |

---

### routes (Soft delete)

| Child Table | FK Column |
|-------------|-----------|
| route_assignments | route_id |
| student_transport | route_id |

---

### vehicles (Soft delete)

| Child Table | FK Column |
|-------------|-----------|
| route_assignments | vehicle_id |

---

### drivers (Soft delete)

| Child Table | FK Column |
|-------------|-----------|
| route_assignments | driver_id |

---

### helpers (Soft delete)

| Child Table | FK Column |
|-------------|-----------|
| route_assignments | helper_id |

---

### fee_structures (Soft delete)

| Child Table | FK Column |
|-------------|-----------|
| fee_records | fee_structure_id |

---

### fee_records (Soft delete)

| Child Table | FK Column |
|-------------|-----------|
| fee_payments | fee_record_id |
| fee_penalties | fee_record_id |

---

### library_books (Soft delete)

| Child Table | FK Column |
|-------------|-----------|
| library_issues | book_id |

---

### subscriptions (Platform-level, no user-facing delete)

| Child Table | FK Column |
|-------------|-----------|
| subscription_payments | subscription_id |

---

### period_configs (Hard delete)

| Child Table | FK Column |
|-------------|-----------|
| timetable_slots | period_config_id |

---

## Delete Strategies by Table

### Hard Delete (rows physically removed)

| Table | Context | Prerequisite |
|-------|---------|--------------|
| timetable_slots | Admin deletes slot or resets class timetable | Leaf table, safe |
| period_configs | Admin deletes a period | Must delete timetable_slots for that period first |
| All tables | Superadmin hard-deletes a school | Manual ordered deletion (leaf → root) |

### Soft Delete (normal operations)

All other tables use `is_active=False`, `deleted_at=now()`, `deleted_by=user_id`.

---

## Circular FK References

| Table A | Column | Table B | Column | Resolution |
|---------|--------|---------|--------|------------|
| users | staff_id | staff | user_id | `use_alter=True`, NULLed before hard-delete |
| users | student_id | students | — | `use_alter=True`, NULLed before hard-delete |
| users | parent_id | parents | — | `use_alter=True`, NULLed before hard-delete |

---

## UUID Columns WITHOUT FK Constraints

| Table | Column | Logically References | Reason |
|-------|--------|---------------------|--------|
| staff | primary_subject_id | subjects.id | Oversight (could add FK) |
| BaseModel (all) | created_by | users.id | Audit field, avoids circular deps |
| BaseModel (all) | updated_by | users.id | Audit field, avoids circular deps |
| SoftDeleteMixin (all) | deleted_by | users.id | Avoids blocking user deletion |
| attendance_sessions | cancelled_by | users.id | Same pattern as audit fields |

---

## Superadmin Hard-Delete Order

When a school is permanently deleted, tables are deleted in this order (leaf-first):

```
1.  notification_recipients
2.  attendance_records
3.  assignment_submissions
4.  exam_results
5.  grade_scales
6.  fee_payments
7.  fee_penalties
8.  fee_reminders
9.  library_issues
10. student_transport
11. route_assignments
12. student_parents
13. student_mentors
14. student_enrollments
15. timetable_slots
16. adhoc_classes
17. staff_subjects
18. class_assignments
19. parent_meetings
20. activities
21. awards
22. disciplinary_records
23. leave_applications
24. leave_balances
25. payslips
26. salary_advances
27. salary_revisions
28. salary_structures
29. notifications
30. attendance_sessions
31. assignments
32. exams
33. fee_records
34. fee_structures
35. grade_systems
36. leave_policies
37. period_configs
38. library_books
39. subscription_payments
40. subscriptions
41. class_subjects
42. class_sections
43. subjects
44. sections
45. classes
46. routes
47. vehicles
48. drivers
49. helpers
50. users          (after NULLing staff_id, student_id, parent_id)
51. parents
52. students
53. staff          (after NULLing user_id)
54. enum_configs
55. settings
56. academic_years
57. schools        (finally)
```

---

## Key Implications

1. **You cannot hard-delete any parent with RESTRICT children** without deleting children first or soft-deleting instead.
2. **Soft-delete never triggers FK violations** because the row remains in the table.
3. **The 6 CASCADE FKs only matter** if you somehow hard-delete the parent (which the app normally doesn't do for those parents).
4. **Switching academic years is safe** because the current year is never deleted (blocked by validation).
5. **The superadmin hard-delete is the only nuclear option** and handles the full dependency chain manually in a single transaction.
