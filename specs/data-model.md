# Data Model Reference

**46 Tables | Last Updated: 2026-06-21**

---

## Base Model (Abstract)

All tables marked with "(BaseModel)" inherit the following columns from `src/core/base_model.py`:

| Column | Type | Constraints | Default | Notes |
|--------|------|-------------|---------|-------|
| id | UUID (CHAR(36)) | PRIMARY KEY | uuid4 | |
| school_id | UUID (CHAR(36)) | NOT NULL, FK -> schools.id, INDEXED | | SchoolMixin |
| metadata | JSON | | {} | Column named `metadata_` in Python |
| created_at | DateTime | NOT NULL | func.now() | TimestampMixin |
| updated_at | DateTime | NOT NULL | func.now() | onupdate=func.now() |
| is_active | Boolean | INDEXED | True | SoftDeleteMixin |
| deleted_at | DateTime | NULLABLE | None | SoftDeleteMixin |
| deleted_by | UUID (CHAR(36)) | NULLABLE | None | SoftDeleteMixin |
| created_by | UUID (CHAR(36)) | NULLABLE | None | AuditMixin |
| updated_by | UUID (CHAR(36)) | NULLABLE | None | AuditMixin |

**Naming Convention** (for auto-generated constraint names):
- Index: `ix_<column_label>`
- Unique: `uq_<table>_<columns>`
- Check: `ck_<table>_<constraint_name>`
- FK: `fk_<table>_<column>_<referred_table>`
- PK: `pk_<table>`

---

## Core Module

### schools

Does NOT use BaseModel -- uses Base + TimestampMixin + SoftDeleteMixin + AuditMixin (no SchoolMixin).

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| id | UUID (CHAR(36)) | PRIMARY KEY | uuid4 |
| name | String(255) | NOT NULL | |
| code | String(50) | NOT NULL, UNIQUE | |
| logo_url | Text | NULLABLE | None |
| address_line1 | String(255) | NULLABLE | None |
| address_line2 | String(255) | NULLABLE | None |
| city | String(100) | NULLABLE | None |
| state | String(100) | NULLABLE | None |
| country | String(100) | NULLABLE | "India" |
| pincode | String(20) | NULLABLE | None |
| phone | String(20) | NULLABLE | None |
| email | String(255) | NULLABLE | None |
| website | String(255) | NULLABLE | None |
| board_affiliation | String(100) | NULLABLE | None |
| established_year | Integer | NULLABLE | None |
| principal_name | String(255) | NULLABLE | None |
| enrollment_date | Date | NULLABLE | None |
| subscription_status | String(20) | | "trial" (server_default) |
| trial_start_date | Date | NULLABLE | None |
| trial_end_date | Date | NULLABLE | None |
| metadata | JSON | | {} |
| created_at | DateTime | NOT NULL | func.now() |
| updated_at | DateTime | NOT NULL | func.now() |
| is_active | Boolean | | True |
| deleted_at | DateTime | NULLABLE | None |
| deleted_by | UUID | NULLABLE | None |
| created_by | UUID | NULLABLE | None |
| updated_by | UUID | NULLABLE | None |

Relationships: users (one-to-many), subscriptions (one-to-many)

---

### users

Does NOT use BaseModel -- uses Base + TimestampMixin + SoftDeleteMixin + AuditMixin (no SchoolMixin -- has explicit school_id).

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| id | UUID (CHAR(36)) | PRIMARY KEY | uuid4 |
| school_id | UUID (CHAR(36)) | NOT NULL, FK -> schools.id, INDEXED | |
| email | String(255) | NOT NULL | |
| password_hash | String(255) | NOT NULL | |
| password_changed | Boolean | | False |
| full_name | String(255) | NOT NULL | |
| role | String(20) | NOT NULL | | Values: admin, teacher, student, parent |
| phone | String(20) | NULLABLE | None |
| avatar_url | Text | NULLABLE | None |
| last_login_at | DateTime | NULLABLE | None |
| password_reset_token | String(255) | NULLABLE | None |
| password_reset_expires | DateTime | NULLABLE | None |
| is_locked | Boolean | | False |
| failed_login_attempts | Integer | | 0 |
| staff_id | UUID | NULLABLE, FK -> staff.id (use_alter) | None |
| student_id | UUID | NULLABLE, FK -> students.id (use_alter) | None |
| parent_id | UUID | NULLABLE, FK -> parents.id (use_alter) | None |
| metadata | JSON | | {} |
| created_at / updated_at / is_active / deleted_at / deleted_by / created_by / updated_by | (inherited) | | |

Unique Constraints: `uq_users_school_email` (school_id, email)

---

### academic_years (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| name | String(20) | NOT NULL | |
| start_date | Date | NOT NULL | |
| end_date | Date | NOT NULL | |
| is_current | Boolean | | False |

Unique: `uq_academic_years_school_name` (school_id, name)
Check: `chk_academic_years_dates` (end_date > start_date)

---

### settings (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| category | String(100) | NOT NULL | |
| key | String(100) | NOT NULL | |
| value | JSON | NOT NULL | |
| description | Text | NULLABLE | None |

Unique: `uq_settings_school_category_key` (school_id, category, key)

---

### enum_configs (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| category | String(100) | NOT NULL | |
| value | String(100) | NOT NULL | |
| label | String(255) | NOT NULL | |
| sort_order | Integer | | 0 |
| config | JSON | | {} |

Unique: `uq_enum_configs_school_cat_val` (school_id, category, value)

---

### platform_settings

Does NOT use BaseModel -- uses Base only. No school_id, no soft-delete, no audit.

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| key | String(100) | PRIMARY KEY | |
| value | String(500) | NOT NULL | |
| updated_at | DateTime | | func.now() (onupdate) |

---

## Academic Structure Module

### classes (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| name | String(50) | NOT NULL | |
| display_name | String(100) | NULLABLE | None |
| sort_order | Integer | | 0 |
| max_periods | Integer | NULLABLE | None |

Unique: `uq_classes_school_name` (school_id, name)

### sections (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| name | String(10) | NOT NULL | |
| sort_order | Integer | | 0 |

Unique: `uq_sections_school_name` (school_id, name)

### class_sections (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| class_id | UUID | NOT NULL, FK -> classes.id | |
| section_id | UUID | NOT NULL, FK -> sections.id | |
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |

Unique: `uq_class_sections_school_class_section_year` (school_id, class_id, section_id, academic_year_id)

### subjects (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| name | String(100) | NOT NULL | |
| code | String(20) | NULLABLE | None |
| description | Text | NULLABLE | None |

Unique: `uq_subjects_school_name` (school_id, name), `uq_subjects_school_code` (school_id, code)

### class_subjects (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| class_id | UUID | NOT NULL, FK -> classes.id | |
| subject_id | UUID | NOT NULL, FK -> subjects.id | |
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |

Unique: `uq_class_subjects` (school_id, class_id, subject_id, academic_year_id)

---

## Students Module

### students (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| admission_number | String(50) | NOT NULL | |
| first_name | String(100) | NOT NULL | |
| last_name | String(100) | NULLABLE | None |
| full_name | String(255) | NOT NULL | |
| email | String(255) | NULLABLE | None |
| phone | String(20) | NULLABLE | None |
| gender | String(10) | NULLABLE | None |
| date_of_birth | Date | NULLABLE | None |
| photo_url | Text | NULLABLE | None |
| blood_group | String(5) | NULLABLE | None |
| nationality | String(50) | NULLABLE | None |
| religion | String(50) | NULLABLE | None |
| caste | String(50) | NULLABLE | None |
| mother_tongue | String(50) | NULLABLE | None |
| medical_conditions | Text | NULLABLE | None |
| allergies | Text | NULLABLE | None |
| address_line1 | String(255) | NULLABLE | None |
| address_line2 | String(255) | NULLABLE | None |
| city | String(100) | NULLABLE | None |
| state | String(100) | NULLABLE | None |
| pincode | String(20) | NULLABLE | None |
| admission_date | Date | NULLABLE | None |
| left_date | Date | NULLABLE | None |
| left_reason | Text | NULLABLE | None |
| previous_school | String(255) | NULLABLE | None |
| transfer_certificate_number | String(100) | NULLABLE | None |
| status | String(20) | NOT NULL | "Active" |
| aadhar_number | String(20) | NULLABLE | None |

Unique: `uq_students_school_admission` (school_id, admission_number)
Indexes: `idx_students_name` (school_id, full_name), `idx_students_status` (school_id, status)

### student_enrollments (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| student_id | UUID | NOT NULL, FK -> students.id | |
| class_section_id | UUID | NOT NULL, FK -> class_sections.id | |
| roll_number | String(20) | NULLABLE | None |
| enrollment_date | Date | NULLABLE | None |
| status | String(20) | NOT NULL | "Active" |

Unique: `uq_student_enrollments_year` (school_id, academic_year_id, student_id)
Indexes: `idx_student_enrollments_class` (class_section_id, academic_year_id), `idx_student_enrollments_student` (student_id, academic_year_id)

### parents (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| first_name | String(100) | NOT NULL | |
| last_name | String(100) | NULLABLE | None |
| full_name | String(255) | NOT NULL | |
| relation | String(20) | NOT NULL | |
| email | String(255) | NULLABLE | None |
| phone | String(20) | NULLABLE | None |
| alternate_phone | String(20) | NULLABLE | None |
| occupation | String(100) | NULLABLE | None |
| annual_income | String(50) | NULLABLE | None |
| address_line1 | String(255) | NULLABLE | None |
| address_line2 | String(255) | NULLABLE | None |
| city | String(100) | NULLABLE | None |
| state | String(100) | NULLABLE | None |
| pincode | String(20) | NULLABLE | None |
| aadhar_number | String(20) | NULLABLE | None |
| is_primary_contact | Boolean | | False |

Indexes: `idx_parents_email` (school_id, email), `idx_parents_phone` (school_id, phone)

### student_parents (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| student_id | UUID | NOT NULL, FK -> students.id | |
| parent_id | UUID | NOT NULL, FK -> parents.id | |

Unique: `uq_student_parents` (school_id, student_id, parent_id)

### student_mentors (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| student_id | UUID | NOT NULL, FK -> students.id | |
| staff_id | UUID | NOT NULL, FK -> staff.id | |
| assigned_date | Date | NULLABLE | None |
| notes | Text | NULLABLE | None |

Unique: `uq_student_mentors_year` (school_id, academic_year_id, student_id)
Indexes: `idx_student_mentors_staff` (staff_id, academic_year_id)

---

## Staff Module

### staff (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| employee_id | String(50) | NOT NULL | |
| first_name | String(100) | NOT NULL | |
| last_name | String(100) | NULLABLE | None |
| full_name | String(255) | NOT NULL | |
| email | String(255) | NOT NULL | |
| phone | String(20) | NULLABLE | None |
| alternate_phone | String(20) | NULLABLE | None |
| gender | String(10) | NULLABLE | None |
| date_of_birth | Date | NULLABLE | None |
| photo_url | Text | NULLABLE | None |
| department | String(100) | NULLABLE | None |
| designation | String(100) | NULLABLE | None |
| employment_type | String(50) | NULLABLE | None |
| joining_date | Date | NULLABLE | None |
| left_date | Date | NULLABLE | None |
| left_reason | Text | NULLABLE | None |
| qualification | String(255) | NULLABLE | None |
| experience_years | Numeric(4,1) | NULLABLE | None |
| address_line1 | String(255) | NULLABLE | None |
| address_line2 | String(255) | NULLABLE | None |
| city | String(100) | NULLABLE | None |
| state | String(100) | NULLABLE | None |
| pincode | String(20) | NULLABLE | None |
| blood_group | String(5) | NULLABLE | None |
| emergency_contact_name | String(255) | NULLABLE | None |
| emergency_contact_phone | String(20) | NULLABLE | None |
| emergency_contact_relationship | String(50) | NULLABLE | None |
| bank_name | String(100) | NULLABLE | None |
| bank_account_number | String(50) | NULLABLE | None |
| bank_ifsc | String(20) | NULLABLE | None |
| pan_number | String(20) | NULLABLE | None |
| aadhar_number | String(20) | NULLABLE | None |
| is_teacher | Boolean | | False |
| primary_subject_id | UUID | NULLABLE | None |
| max_workload_hours | Integer | NULLABLE | None |
| salary | Numeric(10,2) | NULLABLE | None |
| status | String(20) | NOT NULL | "Active" |
| user_id | UUID | NULLABLE, FK -> users.id (use_alter) | None |

Unique: `uq_staff_school_employee_id` (school_id, employee_id), `uq_staff_school_email` (school_id, email)
Indexes: `idx_staff_is_teacher`, `idx_staff_department`, `idx_staff_name`, `idx_staff_status` (all prefixed with school_id)

### staff_subjects (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| staff_id | UUID | NOT NULL, FK -> staff.id (ondelete=CASCADE) | |
| subject_id | UUID | NOT NULL, FK -> subjects.id | |
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| is_primary | Boolean | | False |

Unique: `uq_staff_subjects_staff_subject_year` (school_id, staff_id, subject_id, academic_year_id)
Indexes: `idx_staff_subjects_year` (school_id, academic_year_id)

### class_assignments (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| staff_id | UUID | NOT NULL, FK -> staff.id | |
| class_section_id | UUID | NOT NULL, FK -> class_sections.id | |
| subject_id | UUID | NULLABLE, FK -> subjects.id | None |
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| is_class_teacher | Boolean | | False |
| periods_per_week | Integer | NULLABLE | None |
| status | String(20) | NOT NULL | "Active" |
| end_date | Date | NULLABLE | None |
| end_reason | Text | NULLABLE | None |

Unique: `uq_class_assignments_unique` (school_id, staff_id, class_section_id, subject_id, academic_year_id)

---

## Timetable Module (HARD DELETE -- no soft-delete in service layer)

### period_configs (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| name | String(50) | NULLABLE | None |
| start_time | Time | NOT NULL | |
| end_time | Time | NOT NULL | |
| duration_minutes | Integer | NULLABLE | None |
| is_break | Boolean | NOT NULL | False |
| sort_order | Integer | NOT NULL | 0 |

Unique: `uq_period_configs_unique` (school_id, academic_year_id, start_time)
Check: `chk_period_configs_time` (end_time > start_time)

### timetable_slots (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| class_section_id | UUID | NOT NULL, FK -> class_sections.id | |
| period_config_id | UUID | NOT NULL, FK -> period_configs.id | |
| day_of_week | String(10) | NOT NULL | |
| subject_id | UUID | NULLABLE, FK -> subjects.id | None |
| staff_id | UUID | NULLABLE, FK -> staff.id | None |
| slot_type | String(50) | NOT NULL | "Subject" |

Unique: `uq_timetable_slots_class` (school_id, academic_year_id, class_section_id, period_config_id, day_of_week)
Indexes: `idx_timetable_slots_teacher` (staff_id, academic_year_id, day_of_week), `idx_timetable_slots_class_day` (class_section_id, academic_year_id, day_of_week)

---

## Attendance Module

### attendance_sessions (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| class_section_id | UUID | NOT NULL, FK -> class_sections.id | |
| date | Date | NOT NULL | |
| subject_id | UUID | NULLABLE, FK -> subjects.id | None |
| period_number | Integer | NULLABLE | None |
| submitted_by | UUID | NULLABLE, FK -> staff.id | None |
| submitted_at | DateTime(tz) | NOT NULL | |
| status | String(20) | NOT NULL | "Submitted" |
| cancelled_at | DateTime(tz) | NULLABLE | None |
| cancelled_by | UUID | NULLABLE | None |
| total_present | Integer | NULLABLE | None |
| total_absent | Integer | NULLABLE | None |
| total_late | Integer | NULLABLE | None |

Unique: `uq_attendance_sessions_school_class_date_year_subject_period` (school_id, class_section_id, date, academic_year_id, subject_id, period_number)
Cascade: records (delete-orphan)

### attendance_records (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| attendance_session_id | UUID | NOT NULL, FK -> attendance_sessions.id (ondelete=CASCADE) | |
| student_id | UUID | NOT NULL, FK -> students.id | |
| status | String(10) | NOT NULL | | Values: Present, Absent, Late |
| remarks | Text | NULLABLE | None |

Unique: `uq_attendance_records_session_student` (school_id, attendance_session_id, student_id)

---

## Examination Module

### exams (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| name | String(255) | NOT NULL | |
| exam_type | String(50) | NOT NULL | |
| class_section_id | UUID | NOT NULL, FK -> class_sections.id | |
| subject_id | UUID | NOT NULL, FK -> subjects.id | |
| date | Date | NULLABLE | None |
| start_time | Time | NULLABLE | None |
| end_time | Time | NULLABLE | None |
| total_marks | Numeric(6,2) | NOT NULL | |
| passing_marks | Numeric(6,2) | NULLABLE | None |
| status | String(20) | NOT NULL | "Draft" |
| examiner_id | UUID | NULLABLE, FK -> staff.id | None |
| term | String(20) | NULLABLE | None |
| published_at | DateTime(tz) | NULLABLE | None |
| cancelled_at | DateTime(tz) | NULLABLE | None |

### exam_results (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| exam_id | UUID | NOT NULL, FK -> exams.id (ondelete=CASCADE) | |
| student_id | UUID | NOT NULL, FK -> students.id | |
| marks_obtained | Numeric(6,2) | NULLABLE | None |
| grade | String(10) | NULLABLE | None |
| rank | Integer | NULLABLE | None |
| attendance | String(10) | NOT NULL | "Present" |
| remarks | Text | NULLABLE | None |
| is_pass | Boolean | NULLABLE | None |

Unique: `uq_exam_results_school_exam_student` (school_id, exam_id, student_id)

### grade_systems (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| name | String(100) | NOT NULL | |
| is_default | Boolean | | False |

Unique: `uq_grade_systems_school_name` (school_id, name)

### grade_scales (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| grade_system_id | UUID | NOT NULL, FK -> grade_systems.id (ondelete=CASCADE) | |
| grade | String(10) | NOT NULL | |
| min_percentage | Numeric(5,2) | NOT NULL | |
| max_percentage | Numeric(5,2) | NOT NULL | |
| grade_point | Numeric(3,1) | NULLABLE | None |
| description | Text | NULLABLE | None |
| sort_order | Integer | | 0 |

Unique: `uq_grade_scales_system_grade` (school_id, grade_system_id, grade)

---

## Leave Module

### leave_policies (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| leave_type | String(50) | NOT NULL | |
| display_name | String(50) | NULLABLE | None |
| code | String(10) | NULLABLE | None |
| total_per_year | Integer | NOT NULL | |
| carry_forward | Boolean | | False |
| max_carry_forward | Integer | NULLABLE | None |
| max_consecutive_days | Integer | NULLABLE | None |
| requires_approval | Boolean | | True |
| half_day_allowed | Boolean | | False |
| medical_certificate_required_after_days | Integer | NULLABLE | None |
| advance_notice_days | Integer | NULLABLE | None |
| applicable_to | String(255) | NULLABLE | "all" |
| members | JSON | NULLABLE | None |

Unique: `uq_leave_policies_year_type` (school_id, academic_year_id, leave_type, applicable_to)

### leave_applications (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| staff_id | UUID | NOT NULL, FK -> staff.id | |
| leave_type | String(50) | NOT NULL | |
| from_date | Date | NOT NULL | |
| to_date | Date | NOT NULL | |
| days | Numeric(4,1) | NOT NULL | |
| is_half_day | Boolean | | False |
| reason | Text | NOT NULL | |
| status | String(20) | NOT NULL | "Pending" |
| applied_on | DateTime(tz) | NOT NULL | |
| approved_by | UUID | NULLABLE, FK -> users.id | None |
| approved_on | DateTime(tz) | NULLABLE | None |
| rejected_by | UUID | NULLABLE, FK -> users.id | None |
| rejected_on | DateTime(tz) | NULLABLE | None |
| remarks | Text | NULLABLE | None |
| substitute_teacher_id | UUID | NULLABLE, FK -> staff.id | None |
| cancelled_on | DateTime(tz) | NULLABLE | None |

### leave_balances (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| staff_id | UUID | NOT NULL, FK -> staff.id | |
| leave_type | String(50) | NOT NULL | |
| total_allocated | Integer | NOT NULL | |
| carried_forward | Integer | | 0 |
| used | Numeric(5,1) | | 0 |
| pending | Numeric(5,1) | | 0 |

Unique: `uq_leave_balances_staff_year_type` (school_id, staff_id, academic_year_id, leave_type)

---

## Fee Module

### fee_structures (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| class_id | UUID | NULLABLE, FK -> classes.id | None |
| class_section_id | UUID | NULLABLE, FK -> class_sections.id | None |
| fee_type | String(50) | NOT NULL | |
| fee_category | String(20) | NOT NULL | "academic" |
| amount | Numeric(10,2) | NOT NULL | |
| frequency | String(30) | NOT NULL | |

Unique: `uq_fee_structures_year_class_type` (school_id, academic_year_id, class_section_id, fee_type)

### fee_records (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| student_id | UUID | NOT NULL, FK -> students.id | |
| fee_structure_id | UUID | NULLABLE, FK -> fee_structures.id | None |
| fee_type | String(50) | NOT NULL | |
| fee_category | String(20) | NOT NULL | "academic" |
| total_amount | Numeric(10,2) | NOT NULL | |
| paid | Numeric(10,2) | NOT NULL | 0 |
| pending | Numeric(10,2) | NOT NULL | |
| total_late_fee | Numeric(10,2) | NOT NULL | 0 |
| due_date | Date | NOT NULL | |
| status | String(20) | NOT NULL | "Pending" |
| description | String(255) | NULLABLE | None |
| concession_amount | Numeric(10,2) | NOT NULL | 0 |

### fee_payments (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| fee_record_id | UUID | NOT NULL, FK -> fee_records.id | |
| amount | Numeric(10,2) | NOT NULL | |
| payment_date | Date | NOT NULL | |
| payment_method | String(50) | NOT NULL | |
| reference | String(100) | NULLABLE | None |
| recorded_by | UUID | NULLABLE, FK -> users.id | None |

### fee_reminders (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| target_group | String(20) | NOT NULL | |
| class_name | String(50) | NULLABLE | None |
| section | String(10) | NULLABLE | None |
| message | Text | NOT NULL | |
| send_via | String(20) | NOT NULL | |
| sent_to_count | Integer | | 0 |
| sent_by | UUID | NOT NULL, FK -> users.id | |
| sent_at | DateTime(tz) | NOT NULL | |

### fee_penalties (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| fee_record_id | UUID | NOT NULL, FK -> fee_records.id | |
| penalty_type | String(20) | NOT NULL | |
| amount | Numeric(10,2) | NOT NULL | |
| percentage | Numeric(5,2) | NULLABLE | None |
| applied_on | DateTime(tz) | NOT NULL | |
| applied_by | UUID | NOT NULL, FK -> users.id | |

---

## Payroll Module

### salary_structures (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| staff_id | UUID | NOT NULL, FK -> staff.id | |
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| basic_salary | Numeric(10,2) | NOT NULL | |
| hra | Numeric(10,2) | | 0 |
| da | Numeric(10,2) | | 0 |
| transport_allowance | Numeric(10,2) | | 0 |
| medical_allowance | Numeric(10,2) | | 0 |
| other_allowances | JSON | | {} |
| pf_deduction | Numeric(10,2) | | 0 |
| professional_tax | Numeric(10,2) | | 0 |
| tds | Numeric(10,2) | | 0 |
| other_deductions | JSON | | {} |
| net_salary | Numeric(10,2) | NOT NULL | |
| effective_from | Date | NOT NULL | |

Unique: `uq_salary_structures_active` (school_id, staff_id)

### payslips (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| staff_id | UUID | NOT NULL, FK -> staff.id | |
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| month | Integer | NOT NULL | |
| year | Integer | NOT NULL | |
| basic_salary | Numeric(10,2) | NOT NULL | |
| hra | Numeric(10,2) | | 0 |
| da | Numeric(10,2) | | 0 |
| transport_allowance | Numeric(10,2) | | 0 |
| total_allowances | Numeric(10,2) | NOT NULL | |
| total_deductions | Numeric(10,2) | NOT NULL | |
| net_salary | Numeric(10,2) | NOT NULL | |
| paid_amount | Numeric(10,2) | | 0 |
| working_days | Integer | | 26 |
| total_days | Integer | | 30 |
| status | String(20) | NOT NULL | "Generated" |
| paid_on | Date | NULLABLE | None |
| payment_method | String(50) | NULLABLE | None |
| reference | String(100) | NULLABLE | None |
| notes | Text | NULLABLE | None |
| payment_history | JSON | NULLABLE | None |
| generated_at | DateTime(tz) | NOT NULL | |
| generated_by | UUID | NULLABLE, FK -> users.id | None |

Unique: `uq_payslips_month` (school_id, staff_id, month, year)

### salary_advances (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| staff_id | UUID | NOT NULL, FK -> staff.id | |
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| amount | Numeric(10,2) | NOT NULL | |
| reason | Text | NULLABLE | None |
| recovery_months | Integer | NULLABLE | None |
| per_month_deduction | Numeric(10,2) | NULLABLE | None |
| status | String(20) | NOT NULL | "Pending" |
| applied_on | DateTime(tz) | NOT NULL | |
| approved_by | UUID | NULLABLE, FK -> users.id | None |
| approved_on | DateTime(tz) | NULLABLE | None |
| rejected_by | UUID | NULLABLE, FK -> users.id | None |
| remarks | Text | NULLABLE | None |
| disbursed_on | DateTime(tz) | NULLABLE | None |

Indexes: `idx_salary_advances_year` (school_id, academic_year_id)

### salary_revisions (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| staff_id | UUID | NOT NULL, FK -> staff.id | |
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| effective_date | Date | NOT NULL | |
| previous_basic | Numeric(10,2) | NOT NULL | |
| new_basic | Numeric(10,2) | NOT NULL | |
| revision_type | String(50) | NOT NULL | |
| percentage | Numeric(5,2) | NULLABLE | None |
| increment_amount | Numeric(10,2) | NULLABLE | None |
| approved_by | UUID | NULLABLE, FK -> users.id | None |
| approved_on | DateTime(tz) | NULLABLE | None |
| remarks | Text | NULLABLE | None |

---

## Assignment Module

### assignments (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| class_section_id | UUID | NOT NULL, FK -> class_sections.id | |
| subject_id | UUID | NOT NULL, FK -> subjects.id | |
| staff_id | UUID | NOT NULL, FK -> staff.id | |
| title | String(255) | NOT NULL | |
| description | Text | NULLABLE | None |
| due_date | Date | NOT NULL | |
| max_marks | Numeric(6,2) | NULLABLE | None |
| status | String(20) | NOT NULL | "Active" |
| assigned_date | Date | NOT NULL | |

### assignment_submissions (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| assignment_id | UUID | NOT NULL, FK -> assignments.id (ondelete=CASCADE) | |
| student_id | UUID | NOT NULL, FK -> students.id | |
| status | String(20) | NOT NULL | "Pending" |
| submitted_at | DateTime(tz) | NULLABLE | None |
| comments | Text | NULLABLE | None |
| file_urls | JSON | NULLABLE | [] |
| marks | Numeric(6,2) | NULLABLE | None |
| feedback | Text | NULLABLE | None |
| graded_at | DateTime(tz) | NULLABLE | None |
| graded_by | UUID | NULLABLE, FK -> staff.id | None |
| is_late | Boolean | | False |

Unique: `uq_assignment_submissions_school_assignment_student` (school_id, assignment_id, student_id)

---

## Transport Module

### vehicles (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| vehicle_number | String(50) | NOT NULL | |
| plate_number | String(50) | NULLABLE | None |
| type | String(50) | NOT NULL | |
| model | String(100) | NULLABLE | None |
| year | Integer | NULLABLE | None |
| fuel_type | String(20) | NULLABLE | None |
| capacity | Integer | NOT NULL | |
| occupied_seats | Integer | | 0 |
| status | String(20) | NOT NULL | "Operational" |
| next_service_date | Date | NULLABLE | None |
| insurance_expiry | Date | NULLABLE | None |
| fitness_expiry | Date | NULLABLE | None |

Unique: `uq_vehicles_school_vehicle_number_active` (school_id, vehicle_number, is_active)

### drivers (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| driver_id | String(50) | NOT NULL | |
| full_name | String(255) | NOT NULL | |
| phone | String(20) | NOT NULL | |
| email | String(255) | NULLABLE | None |
| license_number | String(50) | NOT NULL | |
| license_type | String(20) | NULLABLE | None |
| license_expiry | Date | NULLABLE | None |
| experience_years | Integer | NULLABLE | None |
| join_date | Date | NULLABLE | None |
| status | String(20) | NOT NULL | "Available" |
| emergency_contact_name | String(255) | NULLABLE | None |
| emergency_contact_phone | String(20) | NULLABLE | None |

Unique: `uq_drivers_school_driver_id` (school_id, driver_id)

### helpers (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| helper_id | String(50) | NOT NULL | |
| full_name | String(255) | NOT NULL | |
| phone | String(20) | NOT NULL | |
| join_date | Date | NULLABLE | None |
| status | String(20) | NOT NULL | "Available" |

Unique: `uq_helpers_school_helper_id` (school_id, helper_id)

### routes (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| route_code | String(20) | NOT NULL | |
| name | String(100) | NOT NULL | |
| area | String(100) | NULLABLE | None |
| shift | String(20) | NULLABLE | None |
| stops | JSON | | [] |
| distance_km | Float | NULLABLE | None |
| start_time | Time | NULLABLE | None |
| end_time | Time | NULLABLE | None |
| status | String(20) | NOT NULL | "Active" |

Unique: `uq_routes_school_route_code` (school_id, route_code)

### route_assignments (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| route_id | UUID | NOT NULL, FK -> routes.id | |
| vehicle_id | UUID | NOT NULL, FK -> vehicles.id | |
| driver_id | UUID | NOT NULL, FK -> drivers.id | |
| helper_id | UUID | NULLABLE, FK -> helpers.id | None |
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| status | String(20) | NOT NULL | "Active" |

Unique: `uq_route_assignments_school_vehicle_year_active` (school_id, vehicle_id, academic_year_id, is_active)
Indexes: `idx_route_assignments_year` (school_id, academic_year_id)

### student_transport (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| student_id | UUID | NOT NULL, FK -> students.id | |
| route_id | UUID | NOT NULL, FK -> routes.id | |
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| pickup_point | String(255) | NULLABLE | None |
| drop_point | String(255) | NULLABLE | None |

Unique: `uq_student_transport_school_student_year` (school_id, student_id, academic_year_id)

---

## Library Module

### library_books (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| title | String(255) | NOT NULL | |
| author | String(255) | NULLABLE | None |
| isbn | String(20) | NULLABLE | None |
| category | String(100) | NULLABLE | None |
| publisher | String(255) | NULLABLE | None |
| total_copies | Integer | | 1 |
| available_copies | Integer | | 1 |
| shelf_location | String(50) | NULLABLE | None |
| status | String(20) | | "Available" |

### library_issues (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| book_id | UUID | NOT NULL, FK -> library_books.id | |
| borrower_id | UUID | NOT NULL, FK -> users.id | |
| borrower_type | String(20) | NOT NULL | "student" |
| issue_date | Date | NOT NULL | |
| due_date | Date | NOT NULL | |
| return_date | Date | NULLABLE | None |
| fine_amount | Float | | 0.0 |
| status | String(20) | | "Issued" |

---

## Notification Module

### notifications (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| title | String(255) | NOT NULL | |
| message | Text | NOT NULL | |
| type | String(50) | NULLABLE | None |
| target_type | String(30) | NOT NULL | |
| target_class_name | String(100) | NULLABLE | None |
| target_section | String(10) | NULLABLE | None |
| send_via | String(20) | NOT NULL | "in_app" |
| status | String(20) | NOT NULL | "Sent" |
| scheduled_at | DateTime | NULLABLE | None |
| sent_at | DateTime | NULLABLE | None |
| archived_at | DateTime | NULLABLE | None |
| recipients_count | Integer | NOT NULL | 0 |
| read_count | Integer | NOT NULL | 0 |
| created_by_user_id | UUID | NULLABLE, FK -> users.id | None |

### notification_recipients (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| notification_id | UUID | NOT NULL, FK -> notifications.id (ondelete=CASCADE) | |
| user_id | UUID | NOT NULL, FK -> users.id | |
| is_read | Boolean | NOT NULL | False |
| read_at | DateTime | NULLABLE | None |

Unique: `uq_notification_recipients_school_notif_user` (school_id, notification_id, user_id)

---

## Activity Module

### activities (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| student_id | UUID | NOT NULL, FK -> students.id | |
| activity_type | String(50) | NOT NULL | |
| name | String(255) | NOT NULL | |
| description | Text | NULLABLE | None |
| role | String(100) | NULLABLE | None |
| start_date | Date | NULLABLE | None |
| end_date | Date | NULLABLE | None |
| achievement | Text | NULLABLE | None |
| certificate_url | Text | NULLABLE | None |
| recorded_by | UUID | NULLABLE, FK -> staff.id | None |
| status | String(20) | NOT NULL | "Active" |

### awards (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| student_id | UUID | NOT NULL, FK -> students.id | |
| title | String(255) | NOT NULL | |
| category | String(100) | NULLABLE | None |
| description | Text | NULLABLE | None |
| awarded_date | Date | NULLABLE | None |
| awarded_by | String(255) | NULLABLE | None |
| level | String(50) | NULLABLE | None |
| certificate_url | Text | NULLABLE | None |
| recorded_by | UUID | NULLABLE, FK -> staff.id | None |

### disciplinary_records (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| student_id | UUID | NOT NULL, FK -> students.id | |
| incident_date | Date | NOT NULL | |
| category | String(50) | NOT NULL | |
| severity | String(20) | NOT NULL | |
| description | Text | NOT NULL | |
| action_taken | Text | NULLABLE | None |
| reported_by | UUID | NULLABLE, FK -> staff.id | None |
| parent_notified | Boolean | NOT NULL | False |
| parent_notified_date | Date | NULLABLE | None |
| follow_up_date | Date | NULLABLE | None |
| follow_up_notes | Text | NULLABLE | None |
| status | String(20) | NOT NULL | "Open" |

---

## Meeting Module

### parent_meetings (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| student_id | UUID | NOT NULL, FK -> students.id | |
| meeting_date | Date | NOT NULL | |
| meeting_time | Time | NULLABLE | None |
| conducted_by | UUID | NULLABLE, FK -> staff.id | None |
| parent_id | UUID | NULLABLE, FK -> parents.id | None |
| attendees | JSON | | [] |
| agenda | Text | NULLABLE | None |
| discussion_notes | Text | NULLABLE | None |
| action_items | JSON | | [] |
| next_meeting_date | Date | NULLABLE | None |
| status | String(20) | NOT NULL | "Scheduled" |
| meeting_type | String(50) | NULLABLE | None |
| follow_up_required | Boolean | NOT NULL | False |
| parent_attended | Boolean | NOT NULL | True |
| remarks | Text | NULLABLE | None |

---

## Adhoc Class Module

### adhoc_classes (BaseModel)

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| academic_year_id | UUID | NOT NULL, FK -> academic_years.id | |
| staff_id | UUID | NOT NULL, FK -> staff.id | |
| class_section_id | UUID | NOT NULL, FK -> class_sections.id | |
| subject_id | UUID | NOT NULL, FK -> subjects.id | |
| date | Date | NOT NULL | |
| start_time | Time | NULLABLE | None |
| end_time | Time | NULLABLE | None |
| duration_minutes | Integer | NULLABLE | None |
| type | String(20) | NOT NULL | |
| reason | Text | NULLABLE | None |
| original_staff_id | UUID | NULLABLE, FK -> staff.id | None |
| topic | String(255) | NULLABLE | None |
| notes | Text | NULLABLE | None |
| student_count | Integer | NOT NULL | 0 |
| status | String(20) | NOT NULL | "Scheduled" |
| description | Text | NULLABLE | None |

---

## Subscription Module (SuperAdmin)

### subscriptions

Does NOT use BaseModel -- uses Base + TimestampMixin only.

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| id | UUID | PRIMARY KEY | uuid4 |
| school_id | UUID | FK -> schools.id, INDEXED | |
| plan_type | String(20) | NOT NULL | |
| amount | Numeric(10,2) | NOT NULL | |
| start_date | Date | NOT NULL | |
| end_date | Date | NOT NULL | |
| auto_renew | Boolean | | True |
| is_active | Boolean | | True |
| created_at | DateTime | | func.now() |
| updated_at | DateTime | | func.now() |

### subscription_payments

Does NOT use BaseModel -- uses Base + TimestampMixin only.

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| id | UUID | PRIMARY KEY | uuid4 |
| subscription_id | UUID | FK -> subscriptions.id, INDEXED | |
| school_id | UUID | FK -> schools.id, INDEXED | |
| amount | Numeric(10,2) | NOT NULL | |
| payment_date | Date | NOT NULL | |
| period_start | Date | NOT NULL | |
| period_end | Date | NOT NULL | |
| status | String(20) | NOT NULL | "paid" |
| notes | Text | NULLABLE | None |
| created_at | DateTime | | func.now() |
| updated_at | DateTime | | func.now() |
