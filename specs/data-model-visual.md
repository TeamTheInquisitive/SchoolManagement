# Data Model - Visual Reference

**58 Tables** | **Last Updated: 2026-06-06**

## Entity Relationship Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   School    │────▶│    Users      │────▶│   Staff     │
│             │     │ (role-based)  │     │ (teachers)  │
└─────────────┘     └──────────────┘     └─────────────┘
       │                    │                    │
       │              ┌─────┴─────┐              │
       │              │  Student  │              │
       │              └───────────┘              │
       │                    │                    │
       ▼                    ▼                    ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ AcademicYear│     │ Enrollment   │     │ClassAssign  │
│ Classes     │     │ FeeRecords   │     │SalaryStruct │
│ Sections    │     │ Attendance   │     │Payslips     │
│ Subjects    │     │ ExamResults  │     │LeaveBalance │
└─────────────┘     └──────────────┘     └─────────────┘
```

## Core Tables

### School & Auth
```
schools ──┐
           ├── users (email, role: admin/teacher/student/parent)
           ├── academic_years (name, start_date, end_date, is_current)
           └── settings (category, key, value)
```

### Academic Structure
```
classes ─── class_sections ─── sections
                │
                ├── class_subjects ─── subjects
                │
                └── student_enrollments ─── students
```

### Students
```
students
├── student_enrollments (class_section + academic_year)
├── student_parents ─── parents
├── student_mentors ─── staff
├── fee_records ─── fee_payments
├── attendance_records
├── exam_results
├── activities
├── awards
├── disciplinary_records
└── parent_meetings
```

### Staff & Teachers
```
staff (is_teacher=true for teachers)
├── staff_subjects ─── subjects (with is_primary)
├── class_assignments (class_section + subject + is_class_teacher)
├── salary_structures (components: basic, hra, da, ta, pf, tds)
├── payslips (monthly: components + paid_amount + status)
├── leave_balances (per leave_type per academic_year)
└── leave_applications
```

### Fee Management
```
fee_structures (template: type, amount, frequency, class/section)
    │
    └── fee_records (per student: total, paid, pending, status)
            │
            └── fee_payments (transactions: amount, date, method)
                    │
                    └── fee_penalties (late fees)
```

### Examinations
```
grade_systems ─── grade_scales (A+=90-100, A=80-89, etc.)

exams (name, type, class_section, subject, date, marks)
    │
    └── exam_results (student, marks_obtained, grade, rank)
```

### Attendance
```
attendance_sessions (class_section + date + totals)
    │
    └── attendance_records (student + status: Present/Absent/Late)
```

### Leave Management
```
leave_policies (type, days/year, applicable_to, display_name)
    │
    ├── leave_balances (staff + type + allocated/used/pending)
    │
    └── leave_applications (staff + dates + status + approval)
```

### Timetable
```
period_configs (name, start_time, end_time, is_break)
    │
    └── timetable_slots (class_section + period + day + subject + staff)
```

### Transport
```
vehicles ─── route_assignments ─── routes
drivers ─┘                              │
helpers ─┘                              └── student_transport
```

## Table Details (58 tables)

| Table | Key Fields |
|-------|-----------|
| academic_years | name, start_date, end_date, is_current |
| activities | student_id, activity_type, name, role, start_date, achievement |
| adhoc_classes | staff_id, class_section_id, date, type, reason |
| assignment_submissions | assignment_id, student_id, status, marks, feedback |
| assignments | class_section_id, subject_id, staff_id, title, due_date, max_marks |
| attendance_records | session_id, student_id, status (Present/Absent/Late) |
| attendance_sessions | class_section_id, date, submitted_by, totals |
| awards | student_id, title, category, awarded_date, level |
| class_assignments | staff_id, class_section_id, subject_id, is_class_teacher, periods/week |
| class_sections | class_id, section_id, academic_year_id |
| class_subjects | class_id, subject_id |
| classes | name, display_name, sort_order, max_periods |
| disciplinary_records | student_id, incident_date, category, severity, action_taken, status |
| drivers | full_name, license_number, license_type, status |
| enum_configs | category, value, label |
| exam_results | exam_id, student_id, marks_obtained, grade, rank |
| exams | name, exam_type, class_section_id, subject_id, date, total_marks |
| fee_payments | fee_record_id, amount, payment_date, method, reference |
| fee_penalties | fee_record_id, amount, applied_on |
| fee_records | student_id, fee_type, total_amount, paid, pending, status |
| fee_reminders | target_group, message, sent_to_count |
| fee_structures | fee_type, amount, frequency, class_id, class_section_id |
| grade_scales | grade, min_percentage, max_percentage, grade_point |
| grade_systems | name, is_default |
| helpers | full_name, phone, status |
| leave_applications | staff_id, leave_type, from_date, to_date, days, status |
| leave_balances | staff_id, leave_type, total_allocated, used, pending |
| leave_policies | leave_type, display_name, total_per_year, applicable_to, members |
| library_books | title, author, isbn, total_copies, available_copies |
| library_issues | book_id, borrower_id, issue_date, due_date, status |
| notification_recipients | notification_id, user_id, is_read |
| notifications | title, message, type, target_type |
| parent_meetings | student_id, meeting_date, conducted_by, agenda, status |
| parents | full_name, relation, email, phone, occupation |
| payslips | staff_id, month, year, basic+components, net_salary, paid_amount, status |
| period_configs | name, start_time, end_time, is_break |
| platform_settings | key, value |
| route_assignments | route_id, vehicle_id, driver_id, helper_id |
| routes | name, area, shift, stops, distance_km |
| salary_advances | staff_id, amount, reason, status |
| salary_revisions | staff_id, previous_basic, new_basic, effective_date |
| salary_structures | staff_id, basic, hra, da, ta, pf, tds, net_salary |
| schools | name, code, phone, email, subscription_status |
| sections | name, sort_order |
| settings | category, key, value |
| staff | employee_id, full_name, department, is_teacher, salary, bank details |
| staff_subjects | staff_id, subject_id, is_primary |
| student_enrollments | student_id, class_section_id, roll_number |
| student_mentors | student_id, staff_id |
| student_parents | student_id, parent_id |
| student_transport | student_id, route_id, pickup/drop |
| students | admission_number, full_name, gender, status, metadata |
| subjects | name, code |
| subscription_payments | subscription_id, amount, status |
| subscriptions | school_id, plan_type, amount, start/end_date |
| timetable_slots | class_section_id, period_config_id, day, subject_id, staff_id |
| users | email, password_hash, role, password_changed |
| vehicles | vehicle_number, type, capacity, status |
