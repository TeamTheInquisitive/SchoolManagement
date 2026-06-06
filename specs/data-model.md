# Data Model Reference

**58 Tables | Last Updated: 2026-06-06**

## Base Model (inherited by all tables)
Every table includes: `id` (UUID PK), `metadata` (JSON), `created_at`, `updated_at`, `is_active`, `deleted_at`, `deleted_by`, `created_by`, `updated_by`, `school_id` (FK → schools).

## Tables by Module

### Core
- **schools**: name, code, logo_url, address, city, state, phone, email, board_affiliation, established_year, principal_name, subscription_status, trial_start_date, trial_end_date
- **users**: email, password_hash, password_changed, full_name, role (admin/teacher/student/parent), phone, staff_id, student_id, parent_id
- **academic_years**: name, start_date, end_date, is_current
- **settings**: category, key, value, description
- **platform_settings**: key (PK), value
- **enum_configs**: category, value, label, sort_order

### Academic Structure
- **classes**: name, display_name, sort_order, max_periods
- **sections**: name, sort_order
- **class_sections**: class_id, section_id, academic_year_id
- **subjects**: name, code, description
- **class_subjects**: class_id, subject_id, academic_year_id

### Students
- **students**: admission_number, first_name, last_name, full_name, email, phone, gender, date_of_birth, blood_group, religion, address, admission_date, status, metadata (student_type, token_advance, etc.)
- **student_enrollments**: student_id, class_section_id, academic_year_id, roll_number, enrollment_date, status
- **parents**: full_name, relation, email, phone, occupation, address
- **student_parents**: student_id, parent_id (join table)
- **student_mentors**: student_id, staff_id, academic_year_id
- **student_transport**: student_id, route_id, pickup/drop points

### Staff & Teachers
- **staff**: employee_id, full_name, email, phone, gender, date_of_birth, department, designation, employment_type, joining_date, qualification, is_teacher, primary_subject_id, max_workload_hours, salary, bank_name, bank_account_number, bank_ifsc, pan_number, emergency_contact_name/phone/relationship
- **staff_subjects**: staff_id, subject_id, is_primary
- **class_assignments**: staff_id, class_section_id, subject_id (nullable), academic_year_id, is_class_teacher, periods_per_week, status

### Salary & Payroll
- **salary_structures**: staff_id, academic_year_id, basic_salary, hra, da, transport_allowance, medical_allowance, other_allowances (JSON), pf_deduction, professional_tax, tds, other_deductions (JSON), net_salary, effective_from
- **payslips**: staff_id, month, year, basic_salary, hra, da, transport_allowance, total_allowances, total_deductions, net_salary, paid_amount, status (Unpaid/Partially Paid/Paid), paid_on, payment_method
- **salary_revisions**: staff_id, previous_basic, new_basic, effective_date, revision_type
- **salary_advances**: staff_id, amount, reason, recovery_months, status

### Fees
- **fee_structures**: academic_year_id, class_id, class_section_id, fee_type, fee_category, amount, frequency
- **fee_records**: student_id, academic_year_id, fee_structure_id, fee_type, fee_category, total_amount, paid, pending, total_late_fee, due_date, status (Pending/Partial/Paid/Overdue)
- **fee_payments**: fee_record_id, amount, payment_date, payment_method, reference, recorded_by
- **fee_penalties**: fee_record_id, penalty_type, amount, applied_on
- **fee_reminders**: target_group, message, send_via, sent_to_count

### Attendance
- **attendance_sessions**: class_section_id, academic_year_id, date, submitted_by (nullable FK→staff), submitted_at, status, total_present/absent/late
- **attendance_records**: attendance_session_id, student_id, status (Present/Absent/Late), remarks

### Examinations
- **exams**: name, exam_type, class_section_id, subject_id, academic_year_id, date, start_time, end_time, total_marks, passing_marks, status
- **exam_results**: exam_id, student_id, marks_obtained, grade, rank, is_pass
- **grade_systems**: academic_year_id, name, is_default
- **grade_scales**: grade_system_id, grade, min_percentage, max_percentage, grade_point, description (TEXT for class applicability JSON)

### Leaves
- **leave_policies**: academic_year_id, leave_type, display_name, code, total_per_year, carry_forward, requires_approval, half_day_allowed, applicable_to, members (JSON)
- **leave_balances**: staff_id, academic_year_id, leave_type, total_allocated, carried_forward, used, pending
- **leave_applications**: staff_id, academic_year_id, leave_type, from_date, to_date, days, status (Pending/Approved/Rejected/Cancelled)

### Activities & Records
- **activities**: student_id, academic_year_id, activity_type, name, description, role, start_date, end_date, achievement, status
- **awards**: student_id, academic_year_id, title, category, description, awarded_date, awarded_by, level
- **disciplinary_records**: student_id, academic_year_id, incident_date, category, severity, description, action_taken, parent_notified, status
- **parent_meetings**: student_id, academic_year_id, meeting_date, conducted_by, agenda, discussion_notes, action_items (JSON), status, meeting_type

### Timetable
- **period_configs**: academic_year_id, name, start_time, end_time, is_break, sort_order
- **timetable_slots**: class_section_id, academic_year_id, period_config_id, day_of_week, subject_id, staff_id

### Transport
- **vehicles**: vehicle_number, type, model, capacity, status
- **drivers**: full_name, license_number, license_type, status
- **helpers**: full_name, phone, status
- **routes**: name, area, shift, stops (JSON), distance_km
- **route_assignments**: route_id, vehicle_id, driver_id, helper_id, status

### Assignments
- **assignments**: class_section_id, subject_id, staff_id, title, description, due_date, max_marks, status
- **assignment_submissions**: assignment_id, student_id, status, marks, feedback, file_urls (JSON)

### Library
- **library_books**: title, author, isbn, category, total_copies, available_copies
- **library_issues**: book_id, borrower_id, issue_date, due_date, return_date, status

### Notifications
- **notifications**: title, message, type, target_type, recipients_count
- **notification_recipients**: notification_id, user_id, is_read

### Subscriptions (SuperAdmin)
- **subscriptions**: school_id, plan_type, amount, start_date, end_date
- **subscription_payments**: subscription_id, amount, payment_date, status
