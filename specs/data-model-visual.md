# Data Model Visual Relationships

## School Management System — 46 Tables across 16 Modules

---

## Overview Diagram (High-Level Module Dependencies)

```
                            ┌──────────────┐
                            │   schools    │  (ROOT)
                            └──────┬───────┘
           ┌───────────┬──────────┼──────────┬───────────┬────────────┐
           ▼           ▼          ▼          ▼           ▼            ▼
      [Academic]   [Students]  [Staff]  [Transport]  [Library]  [Subscriptions]
           │           │          │
           ▼           ▼          ▼
      [Timetable] [Attendance] [Leaves]
           │           │          │
           ▼           ▼          ▼
       [Exams]    [Activities] [Payroll]
           │
           ▼
      [Assignments]
```

---

## Module: Core

```
[schools]                          ← ROOT TABLE (no FK)

[platform_settings]                ← STANDALONE (no FK)

[users]
  |--FK--> [schools.id]            (CASCADE)
  |--FK--> [staff.id]
  |--FK--> [students.id]
  |--FK--> [parents.id]

[academic_years]  (BaseModel)
  |--FK--> [schools.id]            (CASCADE)

[settings]  (BaseModel)
  |--FK--> [schools.id]            (CASCADE)

[enum_configs]  (BaseModel)
  |--FK--> [schools.id]            (CASCADE)
```

---

## Module: Academic

```
[classes]
  |--FK--> [schools.id]            (CASCADE)

[sections]
  |--FK--> [schools.id]            (CASCADE)

[class_sections]
  |--FK--> [classes.id]            (CASCADE)
  |--FK--> [sections.id]           (CASCADE)
  |--FK--> [academic_years.id]     (CASCADE)

[subjects]
  |--FK--> [schools.id]            (CASCADE)

[class_subjects]
  |--FK--> [classes.id]            (CASCADE)
  |--FK--> [subjects.id]           (CASCADE)
  |--FK--> [academic_years.id]     (CASCADE)
```

---

## Module: Students

```
[students]
  |--FK--> [schools.id]            (CASCADE)

[student_enrollments]
  |--FK--> [students.id]           (CASCADE)
  |--FK--> [class_sections.id]     (CASCADE)
  |--FK--> [academic_years.id]     (CASCADE)

[parents]
  |--FK--> [schools.id]            (CASCADE)

[student_parents]
  |--FK--> [students.id]           (CASCADE)
  |--FK--> [parents.id]            (CASCADE)

[student_mentors]
  |--FK--> [students.id]           (CASCADE)
  |--FK--> [staff.id]              (CASCADE)
  |--FK--> [academic_years.id]     (CASCADE)
```

---

## Module: Staff

```
[staff]
  |--FK--> [schools.id]            (CASCADE)
  |--FK--> [users.id]              (CASCADE)

[staff_subjects]
  |--FK--> [staff.id]              (CASCADE)
  |--FK--> [subjects.id]           (CASCADE)

[class_assignments]
  |--FK--> [staff.id]              (CASCADE)
  |--FK--> [class_sections.id]     (CASCADE)
  |--FK--> [subjects.id]           (CASCADE)
  |--FK--> [academic_years.id]     (CASCADE)
```

---

## Module: Timetable

```
[period_configs]
  |--FK--> [academic_years.id]     (CASCADE)

[timetable_slots]
  |--FK--> [academic_years.id]     (CASCADE)
  |--FK--> [class_sections.id]     (CASCADE)
  |--FK--> [period_configs.id]     (CASCADE)
  |--FK--> [subjects.id]           (CASCADE)
  |--FK--> [staff.id]              (CASCADE)
```

---

## Module: Attendance

```
[attendance_sessions]
  |--FK--> [academic_years.id]     (CASCADE)
  |--FK--> [class_sections.id]     (CASCADE)
  |--FK--> [subjects.id]           (CASCADE)
  |--FK--> [staff.id]              (CASCADE)

[attendance_records]
  |--FK--> [attendance_sessions.id] (CASCADE)
  |--FK--> [students.id]            (CASCADE)
```

---

## Module: Exams

```
[exams]
  |--FK--> [academic_years.id]     (CASCADE)
  |--FK--> [class_sections.id]     (CASCADE)
  |--FK--> [subjects.id]           (CASCADE)
  |--FK--> [staff.id]              (CASCADE)

[exam_results]
  |--FK--> [exams.id]              (CASCADE)
  |--FK--> [students.id]           (CASCADE)

[grade_systems]
  |--FK--> [academic_years.id]     (CASCADE)

[grade_scales]
  |--FK--> [grade_systems.id]      (CASCADE)
```

---

## Module: Leaves

```
[leave_policies]
  |--FK--> [academic_years.id]     (CASCADE)

[leave_applications]
  |--FK--> [academic_years.id]     (CASCADE)
  |--FK--> [staff.id]              (CASCADE)
  |--FK--> [users.id]              (CASCADE)

[leave_balances]
  |--FK--> [academic_years.id]     (CASCADE)
  |--FK--> [staff.id]              (CASCADE)
```

---

## Module: Fees

```
[fee_structures]
  |--FK--> [academic_years.id]     (CASCADE)
  |--FK--> [classes.id]            (CASCADE)
  |--FK--> [class_sections.id]     (CASCADE)

[fee_records]
  |--FK--> [academic_years.id]     (CASCADE)
  |--FK--> [students.id]           (CASCADE)
  |--FK--> [fee_structures.id]     (CASCADE)

[fee_payments]
  |--FK--> [fee_records.id]        (CASCADE)
  |--FK--> [users.id]              (CASCADE)

[fee_reminders]
  |--FK--> [academic_years.id]     (CASCADE)
  |--FK--> [users.id]              (CASCADE)

[fee_penalties]
  |--FK--> [fee_records.id]        (CASCADE)
  |--FK--> [users.id]              (CASCADE)
```

---

## Module: Payroll

```
[salary_structures]
  |--FK--> [staff.id]              (CASCADE)
  |--FK--> [academic_years.id]     (CASCADE)

[payslips]
  |--FK--> [staff.id]              (CASCADE)
  |--FK--> [academic_years.id]     (CASCADE)
  |--FK--> [users.id]              (CASCADE)

[salary_advances]
  |--FK--> [staff.id]              (CASCADE)
  |--FK--> [users.id]              (CASCADE)

[salary_revisions]
  |--FK--> [staff.id]              (CASCADE)
  |--FK--> [academic_years.id]     (CASCADE)
  |--FK--> [users.id]              (CASCADE)
```

---

## Module: Assignments

```
[assignments]
  |--FK--> [academic_years.id]     (CASCADE)
  |--FK--> [class_sections.id]     (CASCADE)
  |--FK--> [subjects.id]           (CASCADE)
  |--FK--> [staff.id]              (CASCADE)

[assignment_submissions]
  |--FK--> [assignments.id]        (CASCADE)
  |--FK--> [students.id]           (CASCADE)
  |--FK--> [staff.id]              (CASCADE)
```

---

## Module: Transport

```
[vehicles]
  |--FK--> [schools.id]            (CASCADE)

[drivers]
  |--FK--> [schools.id]            (CASCADE)

[helpers]
  |--FK--> [schools.id]            (CASCADE)

[routes]
  |--FK--> [schools.id]            (CASCADE)

[route_assignments]
  |--FK--> [routes.id]             (CASCADE)
  |--FK--> [vehicles.id]           (CASCADE)
  |--FK--> [drivers.id]            (CASCADE)
  |--FK--> [helpers.id]            (CASCADE)

[student_transport]
  |--FK--> [students.id]           (CASCADE)
  |--FK--> [routes.id]             (CASCADE)
  |--FK--> [academic_years.id]     (CASCADE)
```

---

## Module: Library

```
[library_books]
  |--FK--> [schools.id]            (CASCADE)

[library_issues]
  |--FK--> [library_books.id]      (CASCADE)
  |--FK--> [users.id]              (CASCADE)
```

---

## Module: Notifications

```
[notifications]
  |--FK--> [users.id]              (CASCADE)

[notification_recipients]
  |--FK--> [notifications.id]      (CASCADE)
  |--FK--> [users.id]              (CASCADE)
```

---

## Module: Activities

```
[activities]
  |--FK--> [academic_years.id]     (CASCADE)
  |--FK--> [students.id]           (CASCADE)
  |--FK--> [staff.id]              (CASCADE)

[awards]
  |--FK--> [academic_years.id]     (CASCADE)
  |--FK--> [students.id]           (CASCADE)
  |--FK--> [staff.id]              (CASCADE)

[disciplinary_records]
  |--FK--> [academic_years.id]     (CASCADE)
  |--FK--> [students.id]           (CASCADE)
  |--FK--> [staff.id]              (CASCADE)
```

---

## Module: Meetings

```
[parent_meetings]
  |--FK--> [academic_years.id]     (CASCADE)
  |--FK--> [students.id]           (CASCADE)
  |--FK--> [staff.id]              (CASCADE)
  |--FK--> [parents.id]            (CASCADE)
```

---

## Module: Adhoc

```
[adhoc_classes]
  |--FK--> [academic_years.id]     (CASCADE)
  |--FK--> [staff.id]              (CASCADE)
  |--FK--> [class_sections.id]     (CASCADE)
  |--FK--> [subjects.id]           (CASCADE)
```

---

## Module: Subscriptions

```
[subscriptions]
  |--FK--> [schools.id]            (CASCADE)

[subscription_payments]
  |--FK--> [subscriptions.id]      (CASCADE)
  |--FK--> [schools.id]            (CASCADE)
```

---

## Cascade Delete Summary

All foreign keys use **CASCADE on delete** to ensure referential integrity.
Deleting a school cascades through the entire tree of dependent records.

### Key Cascade Chains:

```
schools ──CASCADE──> classes ──CASCADE──> class_sections ──CASCADE──> timetable_slots
                                               |
                                               ├──CASCADE──> student_enrollments
                                               ├──CASCADE──> attendance_sessions ──CASCADE──> attendance_records
                                               ├──CASCADE──> exams ──CASCADE──> exam_results
                                               └──CASCADE──> assignments ──CASCADE──> assignment_submissions

schools ──CASCADE──> students ──CASCADE──> student_enrollments
                         |
                         ├──CASCADE──> student_parents
                         ├──CASCADE──> exam_results
                         ├──CASCADE──> attendance_records
                         ├──CASCADE──> fee_records ──CASCADE──> fee_payments
                         │                              └──CASCADE──> fee_penalties
                         └──CASCADE──> student_transport

schools ──CASCADE──> staff ──CASCADE──> staff_subjects
                       |
                       ├──CASCADE──> class_assignments
                       ├──CASCADE──> salary_structures
                       ├──CASCADE──> payslips
                       ├──CASCADE──> leave_applications
                       └──CASCADE──> leave_balances

schools ──CASCADE──> academic_years ──CASCADE──> grade_systems ──CASCADE──> grade_scales
                           |
                           ├──CASCADE──> period_configs
                           ├──CASCADE──> leave_policies
                           └──CASCADE──> fee_structures ──CASCADE──> fee_records
```

---

## Table Count by Module

| Module         | Tables |
|----------------|--------|
| Core           | 6      |
| Academic       | 5      |
| Students       | 5      |
| Staff          | 3      |
| Timetable      | 2      |
| Attendance     | 2      |
| Exams          | 4      |
| Leaves         | 3      |
| Fees           | 5      |
| Payroll        | 4      |
| Assignments    | 2      |
| Transport      | 6      |
| Library        | 2      |
| Notifications  | 2      |
| Activities     | 3      |
| Meetings       | 1      |
| Adhoc          | 1      |
| Subscriptions  | 2      |
| **Total**      | **46** |
