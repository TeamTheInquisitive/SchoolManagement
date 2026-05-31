# School ERP - Database Schema / Data Model

## Design Principles

1. **UUIDs** as primary keys on every table (`gen_random_uuid()`)
2. **Multi-tenancy** via `school_id UUID NOT NULL` FK on every table
3. **Soft deletes** on every table: `is_active BOOLEAN DEFAULT true`, `deleted_at TIMESTAMPTZ NULL`, `deleted_by UUID NULL`
4. **Audit columns** on every table: `created_at TIMESTAMPTZ DEFAULT NOW()`, `updated_at TIMESTAMPTZ DEFAULT NOW()`, `created_by UUID NULL`, `updated_by UUID NULL`
5. **`metadata JSONB DEFAULT '{}'`** on every table for forward-compatible extensions
6. **Academic year scoping** on all transactional tables via `academic_year_id UUID NOT NULL` FK
7. **ISO 8601** for all date/time columns (`DATE`, `TIMESTAMPTZ`)
8. **Configurable enums** stored in `enum_configs` table, never hardcoded in schema
9. **Teacher = Staff** with `is_teacher = true` flag; no separate teacher table
10. **Nullable optional columns** for forward/backward compatibility

### Naming Conventions

- Table names: `snake_case`, plural
- Column names: `snake_case`
- Foreign keys: `<referenced_table_singular>_id`
- Indexes: `idx_<table>_<columns>`
- Unique constraints: `uq_<table>_<columns>`
- Check constraints: `chk_<table>_<description>`

### Common Column Template (on EVERY table)

```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
school_id       UUID NOT NULL REFERENCES schools(id),
is_active       BOOLEAN NOT NULL DEFAULT true,
deleted_at      TIMESTAMPTZ NULL,
deleted_by      UUID NULL,
metadata        JSONB NOT NULL DEFAULT '{}',
created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
created_by      UUID NULL,
updated_by      UUID NULL
```

These columns are present on ALL tables below but omitted from individual table definitions for brevity. Only domain-specific columns are listed.

---

## 1. Core / Tenant

### schools

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | School identifier |
| name | VARCHAR(255) | NOT NULL | School name |
| code | VARCHAR(50) | NOT NULL, UNIQUE | Tenant code (used in X-School-Code header) |
| logo_url | TEXT | NULL | School logo URL |
| address_line1 | VARCHAR(255) | NULL | Street address |
| address_line2 | VARCHAR(255) | NULL | Additional address |
| city | VARCHAR(100) | NULL | City |
| state | VARCHAR(100) | NULL | State/province |
| country | VARCHAR(100) | NULL DEFAULT 'India' | Country |
| pincode | VARCHAR(20) | NULL | ZIP/postal code |
| phone | VARCHAR(20) | NULL | Primary phone |
| email | VARCHAR(255) | NULL | Primary email |
| website | VARCHAR(255) | NULL | School website |
| board_affiliation | VARCHAR(100) | NULL | CBSE/ICSE/State/IB etc. |
| established_year | INTEGER | NULL | Year founded |
| principal_name | VARCHAR(255) | NULL | Current principal |

**Indexes:**
- `uq_schools_code` UNIQUE on `(code)`

**Relationships:** Root table. All other tables reference `schools.id`.

---

### users

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | User auth identity |
| email | VARCHAR(255) | NOT NULL | Login email |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt/Argon2 hashed password |
| role | VARCHAR(20) | NOT NULL | One of: admin, teacher, student, parent |
| staff_id | UUID | NULL, FK staff(id) | Link to staff record (for admin/teacher) |
| student_id | UUID | NULL, FK students(id) | Link to student record |
| parent_id | UUID | NULL, FK parents(id) | Link to parent record |
| last_login_at | TIMESTAMPTZ | NULL | Last successful login |
| password_reset_token | VARCHAR(255) | NULL | Token for password reset |
| password_reset_expires | TIMESTAMPTZ | NULL | Token expiry |
| refresh_token_hash | VARCHAR(255) | NULL | Hashed refresh token |
| refresh_token_expires | TIMESTAMPTZ | NULL | Refresh token expiry |
| is_locked | BOOLEAN | NOT NULL DEFAULT false | Account locked after failed attempts |
| failed_login_attempts | INTEGER | NOT NULL DEFAULT 0 | Failed login counter |

**Indexes:**
- `uq_users_school_email` UNIQUE on `(school_id, email)`
- `idx_users_role` on `(school_id, role)`
- `idx_users_staff_id` on `(staff_id)` WHERE staff_id IS NOT NULL
- `idx_users_student_id` on `(student_id)` WHERE student_id IS NOT NULL

**Relationships:**
- `users.school_id` -> `schools.id`
- `users.staff_id` -> `staff.id`
- `users.student_id` -> `students.id`
- `users.parent_id` -> `parents.id`

---

### academic_years

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Academic year identifier |
| name | VARCHAR(20) | NOT NULL | Display name e.g. "2025-2026" |
| start_date | DATE | NOT NULL | Year start |
| end_date | DATE | NOT NULL | Year end |
| is_current | BOOLEAN | NOT NULL DEFAULT false | Currently active year |

**Indexes:**
- `uq_academic_years_school_name` UNIQUE on `(school_id, name)`
- `idx_academic_years_current` on `(school_id, is_current)` WHERE is_current = true

**Check Constraints:**
- `chk_academic_years_dates` CHECK (end_date > start_date)

**Relationships:**
- Referenced by all transactional tables as `academic_year_id`

---

### settings

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Setting identifier |
| category | VARCHAR(100) | NOT NULL | Setting group: general, academic, fees, notifications, etc. |
| key | VARCHAR(100) | NOT NULL | Setting key |
| value | JSONB | NOT NULL DEFAULT '{}' | Setting value (flexible structure) |
| description | TEXT | NULL | Human-readable description |

**Indexes:**
- `uq_settings_school_category_key` UNIQUE on `(school_id, category, key)`
- `idx_settings_category` on `(school_id, category)`

---

### enum_configs

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Enum value identifier |
| category | VARCHAR(100) | NOT NULL | Category: fee_type, leave_type, exam_type, department, designation, notification_type, grade_scale, activity_type, etc. |
| value | VARCHAR(100) | NOT NULL | The enum value |
| label | VARCHAR(255) | NOT NULL | Display label |
| sort_order | INTEGER | NOT NULL DEFAULT 0 | Display ordering |
| config | JSONB | NOT NULL DEFAULT '{}' | Extra config per value (e.g., max_days for leave type) |

**Indexes:**
- `uq_enum_configs_school_cat_val` UNIQUE on `(school_id, category, value)`
- `idx_enum_configs_category` on `(school_id, category, sort_order)`

---

## 2. Staff & Teachers

### staff

> Teacher is a Staff member with `is_teacher = true`. All employees (admin, accountant, librarian, teacher, peon) live in this table.
>
> **ID Clarification:** `id` (UUID) is the internal primary key used in all foreign key relationships. `employee_id` (e.g., "EMP001") is the human-readable display identifier. There is no separate `staff_id` — references from other tables use `staff.id` (the UUID).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Staff identifier |
| employee_id | VARCHAR(50) | NOT NULL | Human-readable ID e.g. EMP001 |
| first_name | VARCHAR(100) | NOT NULL | First name |
| last_name | VARCHAR(100) | NULL | Last name |
| full_name | VARCHAR(255) | NOT NULL | Computed/stored full name |
| email | VARCHAR(255) | NOT NULL | Work email |
| phone | VARCHAR(20) | NULL | Primary phone |
| alternate_phone | VARCHAR(20) | NULL | Secondary phone |
| gender | VARCHAR(10) | NULL | Male/Female/Other |
| date_of_birth | DATE | NULL | Date of birth |
| photo_url | TEXT | NULL | Profile photo |
| department | VARCHAR(100) | NULL | Department (from enum_configs) |
| designation | VARCHAR(100) | NULL | Designation (from enum_configs) |
| employment_type | VARCHAR(50) | NULL | Full-time/Part-time/Contract |
| joining_date | DATE | NULL | Date joined |
| left_date | DATE | NULL | Date left (if inactive) |
| left_reason | TEXT | NULL | Reason for leaving |
| qualification | VARCHAR(255) | NULL | Highest qualification |
| experience_years | NUMERIC(4,1) | NULL | Years of experience |
| address_line1 | VARCHAR(255) | NULL | Address |
| address_line2 | VARCHAR(255) | NULL | Address line 2 |
| city | VARCHAR(100) | NULL | City |
| state | VARCHAR(100) | NULL | State |
| pincode | VARCHAR(20) | NULL | PIN code |
| blood_group | VARCHAR(5) | NULL | Blood group |
| emergency_contact_name | VARCHAR(255) | NULL | Emergency contact |
| emergency_contact_phone | VARCHAR(20) | NULL | Emergency phone |
| bank_name | VARCHAR(100) | NULL | Bank for salary |
| bank_account_number | VARCHAR(50) | NULL | Account number |
| bank_ifsc | VARCHAR(20) | NULL | IFSC code |
| pan_number | VARCHAR(20) | NULL | PAN |
| aadhar_number | VARCHAR(20) | NULL | Aadhar |
| is_teacher | BOOLEAN | NOT NULL DEFAULT false | Teacher flag |
| primary_subject_id | UUID | NULL, FK subjects(id) | Primary teaching subject |
| max_workload_hours | INTEGER | NULL | Max weekly teaching hours |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Active' | Active/Inactive |

**Indexes:**
- `uq_staff_school_employee_id` UNIQUE on `(school_id, employee_id)`
- `uq_staff_school_email` UNIQUE on `(school_id, email)`
- `idx_staff_is_teacher` on `(school_id, is_teacher)` WHERE is_active = true
- `idx_staff_department` on `(school_id, department)`
- `idx_staff_name` on `(school_id, full_name)`
- `idx_staff_status` on `(school_id, status)`

**Relationships:**
- `staff.primary_subject_id` -> `subjects.id`

---

### staff_subjects

> Many-to-many: a teacher can be qualified to teach multiple subjects.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Record identifier |
| staff_id | UUID | NOT NULL, FK staff(id) | Teacher |
| subject_id | UUID | NOT NULL, FK subjects(id) | Subject qualified to teach |

**Indexes:**
- `uq_staff_subjects_staff_subject` UNIQUE on `(school_id, staff_id, subject_id)`
- `idx_staff_subjects_staff` on `(staff_id)`

**Relationships:**
- `staff_subjects.staff_id` -> `staff.id` ON DELETE CASCADE
- `staff_subjects.subject_id` -> `subjects.id`

---

### class_assignments

> Maps a teacher to a class-section-subject combination for an academic year.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Assignment identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| staff_id | UUID | NOT NULL, FK staff(id) | The teacher |
| class_section_id | UUID | NOT NULL, FK class_sections(id) | Class+section combo |
| subject_id | UUID | NOT NULL, FK subjects(id) | Subject they teach here |
| is_class_teacher | BOOLEAN | NOT NULL DEFAULT false | Is class teacher for this section |
| effective_from | DATE | NULL | Start date of assignment |
| effective_to | DATE | NULL | End date (null = ongoing) |

**Indexes:**
- `uq_class_assignments_unique` UNIQUE on `(school_id, academic_year_id, staff_id, class_section_id, subject_id)` WHERE is_active = true
- `idx_class_assignments_staff` on `(staff_id, academic_year_id)`
- `idx_class_assignments_class_section` on `(class_section_id, academic_year_id)`
- `idx_class_assignments_class_teacher` on `(class_section_id, academic_year_id)` WHERE is_class_teacher = true

**Relationships:**
- `class_assignments.staff_id` -> `staff.id`
- `class_assignments.class_section_id` -> `class_sections.id`
- `class_assignments.subject_id` -> `subjects.id`
- `class_assignments.academic_year_id` -> `academic_years.id`

---

## 3. Students

### students

> Permanent student profile. Enrollment (class/section) is tracked separately per year.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Student identifier |
| admission_number | VARCHAR(50) | NOT NULL | Admission/roll number |
| first_name | VARCHAR(100) | NOT NULL | First name |
| last_name | VARCHAR(100) | NULL | Last name |
| full_name | VARCHAR(255) | NOT NULL | Full name |
| email | VARCHAR(255) | NULL | Student email (if any) |
| phone | VARCHAR(20) | NULL | Student phone |
| gender | VARCHAR(10) | NULL | Male/Female/Other |
| date_of_birth | DATE | NULL | Date of birth |
| photo_url | TEXT | NULL | Profile photo |
| blood_group | VARCHAR(5) | NULL | Blood group |
| nationality | VARCHAR(50) | NULL | Nationality |
| religion | VARCHAR(50) | NULL | Religion |
| caste | VARCHAR(50) | NULL | Caste |
| mother_tongue | VARCHAR(50) | NULL | Mother tongue |
| address_line1 | VARCHAR(255) | NULL | Permanent address |
| address_line2 | VARCHAR(255) | NULL | Address line 2 |
| city | VARCHAR(100) | NULL | City |
| state | VARCHAR(100) | NULL | State |
| pincode | VARCHAR(20) | NULL | PIN code |
| medical_conditions | TEXT | NULL | Known medical conditions |
| allergies | TEXT | NULL | Allergies |
| admission_date | DATE | NULL | Date of admission |
| left_date | DATE | NULL | Date left school |
| left_reason | TEXT | NULL | Reason for leaving |
| previous_school | VARCHAR(255) | NULL | Previous school name |
| transfer_certificate_number | VARCHAR(100) | NULL | TC number |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Active' | Active/Inactive/Alumni/Archived |
| aadhar_number | VARCHAR(20) | NULL | Aadhar number |

**Indexes:**
- `uq_students_school_admission` UNIQUE on `(school_id, admission_number)`
- `idx_students_name` on `(school_id, full_name)`
- `idx_students_status` on `(school_id, status)`

---

### student_enrollments

> Tracks which class+section a student is in for each academic year.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Enrollment identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Academic year |
| student_id | UUID | NOT NULL, FK students(id) | Student |
| class_section_id | UUID | NOT NULL, FK class_sections(id) | Class+section |
| roll_number | VARCHAR(20) | NULL | Roll number in class |
| enrollment_date | DATE | NULL | Date enrolled |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Active' | Active/Promoted/Transferred/Withdrawn |

**Indexes:**
- `uq_student_enrollments_year` UNIQUE on `(school_id, academic_year_id, student_id)` WHERE is_active = true
- `idx_student_enrollments_class` on `(class_section_id, academic_year_id)`
- `idx_student_enrollments_student` on `(student_id, academic_year_id)`

**Relationships:**
- `student_enrollments.student_id` -> `students.id`
- `student_enrollments.class_section_id` -> `class_sections.id`
- `student_enrollments.academic_year_id` -> `academic_years.id`

---

### parents

> Parent/guardian records linked to students.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Parent identifier |
| first_name | VARCHAR(100) | NOT NULL | First name |
| last_name | VARCHAR(100) | NULL | Last name |
| full_name | VARCHAR(255) | NOT NULL | Full name |
| relation | VARCHAR(20) | NOT NULL | Father/Mother/Guardian |
| email | VARCHAR(255) | NULL | Email |
| phone | VARCHAR(20) | NULL | Phone |
| alternate_phone | VARCHAR(20) | NULL | Alternate phone |
| occupation | VARCHAR(100) | NULL | Occupation |
| annual_income | NUMERIC(12,2) | NULL | Annual income |
| address_line1 | VARCHAR(255) | NULL | Address |
| address_line2 | VARCHAR(255) | NULL | Address line 2 |
| city | VARCHAR(100) | NULL | City |
| state | VARCHAR(100) | NULL | State |
| pincode | VARCHAR(20) | NULL | PIN code |
| aadhar_number | VARCHAR(20) | NULL | Aadhar |
| is_primary_contact | BOOLEAN | NOT NULL DEFAULT false | Primary contact for notifications |

**Indexes:**
- `idx_parents_email` on `(school_id, email)` WHERE email IS NOT NULL
- `idx_parents_phone` on `(school_id, phone)` WHERE phone IS NOT NULL

---

### student_parents

> Many-to-many: a student can have multiple parents/guardians.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Record identifier |
| student_id | UUID | NOT NULL, FK students(id) | Student |
| parent_id | UUID | NOT NULL, FK parents(id) | Parent/Guardian |

**Indexes:**
- `uq_student_parents` UNIQUE on `(school_id, student_id, parent_id)`
- `idx_student_parents_student` on `(student_id)`
- `idx_student_parents_parent` on `(parent_id)`

**Relationships:**
- `student_parents.student_id` -> `students.id` ON DELETE CASCADE
- `student_parents.parent_id` -> `parents.id` ON DELETE CASCADE

---

### student_mentors

> Assigns a teacher/staff as mentor to a student for an academic year.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Record identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Academic year |
| student_id | UUID | NOT NULL, FK students(id) | Student |
| staff_id | UUID | NOT NULL, FK staff(id) | Mentor (teacher) |
| assigned_date | DATE | NULL | Date assigned |
| notes | TEXT | NULL | Mentoring notes |

**Indexes:**
- `uq_student_mentors_year` UNIQUE on `(school_id, academic_year_id, student_id)` WHERE is_active = true
- `idx_student_mentors_staff` on `(staff_id, academic_year_id)`

**Relationships:**
- `student_mentors.student_id` -> `students.id`
- `student_mentors.staff_id` -> `staff.id`
- `student_mentors.academic_year_id` -> `academic_years.id`

---

## 4. Academic Structure

### classes

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Class identifier |
| name | VARCHAR(50) | NOT NULL | Class name e.g. "10", "LKG", "XII" |
| numeric_order | INTEGER | NOT NULL | Numeric sort order (1, 2, ... 12) |
| description | TEXT | NULL | Description |

**Indexes:**
- `uq_classes_school_name` UNIQUE on `(school_id, name)`
- `idx_classes_order` on `(school_id, numeric_order)`

---

### sections

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Section identifier |
| name | VARCHAR(10) | NOT NULL | Section name e.g. "A", "B", "C" |

**Indexes:**
- `uq_sections_school_name` UNIQUE on `(school_id, name)`

---

### class_sections

> Composite: which sections exist for which class. A class may have A, B, C sections.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Class-section combo identifier |
| class_id | UUID | NOT NULL, FK classes(id) | Class |
| section_id | UUID | NOT NULL, FK sections(id) | Section |

**Indexes:**
- `uq_class_sections` UNIQUE on `(school_id, class_id, section_id)`
- `idx_class_sections_class` on `(class_id)`

**Relationships:**
- `class_sections.class_id` -> `classes.id`
- `class_sections.section_id` -> `sections.id`

---

### subjects

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Subject identifier |
| name | VARCHAR(100) | NOT NULL | Subject name e.g. "Mathematics" |
| code | VARCHAR(20) | NULL | Subject code e.g. "MATH" |
| type | VARCHAR(20) | NULL | Theory/Practical/Both |
| description | TEXT | NULL | Description |

**Indexes:**
- `uq_subjects_school_name` UNIQUE on `(school_id, name)`
- `uq_subjects_school_code` UNIQUE on `(school_id, code)` WHERE code IS NOT NULL

---

## 5. Timetable

### period_configs

> Defines the period structure (how many periods, their timings).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Period config identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| name | VARCHAR(50) | NULL | Display name e.g. "Period 1", "Lunch" |
| start_time | TIME | NOT NULL | Start time (order is determined by start_time) |
| end_time | TIME | NOT NULL | End time |
| duration_minutes | INTEGER | NULL | Duration in minutes (computed from start/end) |
| is_break | BOOLEAN | NOT NULL DEFAULT false | Break/lunch (not assignable) |
| day_of_week | VARCHAR(10) | NULL | If timing varies by day (NULL = all days) |

**Indexes:**
- `uq_period_configs` UNIQUE on `(school_id, academic_year_id, start_time, COALESCE(day_of_week, 'ALL'))`
- `idx_period_configs_year` on `(school_id, academic_year_id)`

**Check Constraints:**
- `chk_period_configs_time` CHECK (end_time > start_time)

---

### timetable_slots

> Actual timetable assignments: day + period + class-section = subject + teacher + room.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Slot identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| class_section_id | UUID | NOT NULL, FK class_sections(id) | Class+section |
| period_config_id | UUID | NOT NULL, FK period_configs(id) | Which period |
| day_of_week | VARCHAR(10) | NOT NULL | Monday/Tuesday/.../Saturday |
| subject_id | UUID | NOT NULL, FK subjects(id) | Subject |
| staff_id | UUID | NOT NULL, FK staff(id) | Teacher assigned |
| slot_type | VARCHAR(20) | NOT NULL DEFAULT 'Lecture' | Lecture/Practical/Tutorial |

**Indexes:**
- `uq_timetable_slots_class` UNIQUE on `(school_id, academic_year_id, class_section_id, period_config_id, day_of_week)` WHERE is_active = true
- `idx_timetable_slots_teacher` on `(staff_id, academic_year_id, day_of_week)`
- `idx_timetable_slots_class_day` on `(class_section_id, academic_year_id, day_of_week)`

**Check Constraints:**
- `chk_timetable_slots_day` CHECK (day_of_week IN ('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'))

**Relationships:**
- `timetable_slots.class_section_id` -> `class_sections.id`
- `timetable_slots.period_config_id` -> `period_configs.id`
- `timetable_slots.subject_id` -> `subjects.id`
- `timetable_slots.staff_id` -> `staff.id`
- `timetable_slots.academic_year_id` -> `academic_years.id`

---

## 6. Attendance

### attendance_sessions

> One record per attendance-taking event (class + date + who submitted).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Session identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| class_section_id | UUID | NOT NULL, FK class_sections(id) | Class+section |
| date | DATE | NOT NULL | Attendance date |
| subject_id | UUID | NULL, FK subjects(id) | Subject (NULL = general/homeroom) |
| period_config_id | UUID | NULL, FK period_configs(id) | Period (NULL = full day) |
| submitted_by | UUID | NOT NULL, FK staff(id) | Teacher who submitted |
| submitted_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | Submission timestamp |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Submitted' | Submitted/Cancelled |
| total_present | INTEGER | NULL | Cached count |
| total_absent | INTEGER | NULL | Cached count |
| total_late | INTEGER | NULL | Cached count |

**Indexes:**
- `uq_attendance_sessions` UNIQUE on `(school_id, academic_year_id, class_section_id, date, COALESCE(subject_id, '00000000-0000-0000-0000-000000000000'), COALESCE(period_config_id, '00000000-0000-0000-0000-000000000000'))` WHERE is_active = true
- `idx_attendance_sessions_class_date` on `(class_section_id, date)`
- `idx_attendance_sessions_date` on `(school_id, date)`
- `idx_attendance_sessions_submitted_by` on `(submitted_by, date)`

**Relationships:**
- `attendance_sessions.class_section_id` -> `class_sections.id`
- `attendance_sessions.submitted_by` -> `staff.id`
- `attendance_sessions.subject_id` -> `subjects.id`
- `attendance_sessions.period_config_id` -> `period_configs.id`

---

### attendance_records

> Individual student attendance within a session.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Record identifier |
| attendance_session_id | UUID | NOT NULL, FK attendance_sessions(id) | Parent session |
| student_id | UUID | NOT NULL, FK students(id) | Student |
| status | VARCHAR(10) | NOT NULL | Present/Absent/Late/Excused |
| remarks | TEXT | NULL | Optional remarks |

**Indexes:**
- `uq_attendance_records_session_student` UNIQUE on `(attendance_session_id, student_id)`
- `idx_attendance_records_student` on `(student_id)`
- `idx_attendance_records_status` on `(attendance_session_id, status)`

**Check Constraints:**
- `chk_attendance_records_status` CHECK (status IN ('Present', 'Absent', 'Late', 'Excused'))

**Relationships:**
- `attendance_records.attendance_session_id` -> `attendance_sessions.id` ON DELETE CASCADE
- `attendance_records.student_id` -> `students.id`

---

## 7. Assignments

### assignments

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Assignment identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| class_section_id | UUID | NOT NULL, FK class_sections(id) | Target class+section |
| subject_id | UUID | NOT NULL, FK subjects(id) | Subject |
| staff_id | UUID | NOT NULL, FK staff(id) | Created by teacher |
| title | VARCHAR(255) | NOT NULL | Assignment title |
| description | TEXT | NULL | Detailed instructions |
| due_date | DATE | NOT NULL | Submission deadline |
| total_marks | NUMERIC(6,2) | NULL | Max marks (NULL = ungraded) |
| attachment_urls | JSONB | NOT NULL DEFAULT '[]' | Array of file URLs |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Active' | Active/Closed/Cancelled |
| assigned_date | DATE | NOT NULL DEFAULT CURRENT_DATE | Date assigned |

**Indexes:**
- `idx_assignments_class` on `(class_section_id, academic_year_id)`
- `idx_assignments_teacher` on `(staff_id, academic_year_id)`
- `idx_assignments_due` on `(school_id, due_date)`
- `idx_assignments_status` on `(school_id, academic_year_id, status)`

**Relationships:**
- `assignments.class_section_id` -> `class_sections.id`
- `assignments.subject_id` -> `subjects.id`
- `assignments.staff_id` -> `staff.id`

---

### assignment_submissions

> **Backend Logic:** When an assignment is created for a class, the system auto-generates `assignment_submissions` records (with status "Pending") for every enrolled student in that class. This ensures every student has a tracking record from the moment the assignment is created.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Submission identifier |
| assignment_id | UUID | NOT NULL, FK assignments(id) | Parent assignment |
| student_id | UUID | NOT NULL, FK students(id) | Submitting student |
| submitted_at | TIMESTAMPTZ | NULL | Submission timestamp |
| attachment_urls | JSONB | NOT NULL DEFAULT '[]' | Submitted file URLs |
| comments | TEXT | NULL | Student comments |
| marks_obtained | NUMERIC(6,2) | NULL | Marks given by teacher |
| grade | VARCHAR(10) | NULL | Grade (A+, A, B+, etc.) |
| feedback | TEXT | NULL | Teacher feedback |
| graded_by | UUID | NULL, FK staff(id) | Teacher who graded |
| graded_at | TIMESTAMPTZ | NULL | When graded |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Pending' | Pending/Submitted/Graded/Late/Resubmit |
| is_late | BOOLEAN | NOT NULL DEFAULT false | Submitted after due date |

**Indexes:**
- `uq_assignment_submissions` UNIQUE on `(assignment_id, student_id)` WHERE is_active = true
- `idx_assignment_submissions_assignment` on `(assignment_id, status)`
- `idx_assignment_submissions_student` on `(student_id)`
- `idx_assignment_submissions_graded` on `(assignment_id)` WHERE status = 'Pending'

**Relationships:**
- `assignment_submissions.assignment_id` -> `assignments.id` ON DELETE CASCADE
- `assignment_submissions.student_id` -> `students.id`
- `assignment_submissions.graded_by` -> `staff.id`

---

## 8. Examinations

### exams

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Exam identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| name | VARCHAR(255) | NOT NULL | Exam name e.g. "Mid-Term Mathematics" |
| exam_type | VARCHAR(50) | NOT NULL | Type (from enum_configs: Unit Test, Mid-Term, Final, etc.) |
| class_section_id | UUID | NOT NULL, FK class_sections(id) | Target class+section |
| subject_id | UUID | NOT NULL, FK subjects(id) | Subject |
| date | DATE | NULL | Exam date |
| start_time | TIME | NULL | Start time |
| end_time | TIME | NULL | End time |
| total_marks | NUMERIC(6,2) | NOT NULL | Maximum marks |
| passing_marks | NUMERIC(6,2) | NULL | Minimum passing marks |
| weightage | NUMERIC(5,2) | NULL | Weightage in overall grade (%) |
| syllabus | TEXT | NULL | Syllabus/topics covered |
| instructions | TEXT | NULL | Exam instructions |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Scheduled' | Scheduled/Ongoing/Completed/Published/Cancelled |
| published_at | TIMESTAMPTZ | NULL | When results were published |
| conducted_by | UUID | NULL, FK staff(id) | Examiner |

**Indexes:**
- `idx_exams_class_year` on `(class_section_id, academic_year_id)`
- `idx_exams_subject` on `(subject_id, academic_year_id)`
- `idx_exams_date` on `(school_id, date)`
- `idx_exams_status` on `(school_id, academic_year_id, status)`
- `idx_exams_type` on `(school_id, academic_year_id, exam_type)`

**Relationships:**
- `exams.class_section_id` -> `class_sections.id`
- `exams.subject_id` -> `subjects.id`
- `exams.conducted_by` -> `staff.id`

---

### exam_results

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Result identifier |
| exam_id | UUID | NOT NULL, FK exams(id) | Exam |
| student_id | UUID | NOT NULL, FK students(id) | Student |
| marks_obtained | NUMERIC(6,2) | NULL | Marks scored |
| grade | VARCHAR(10) | NULL | Computed grade |
| rank | INTEGER | NULL | Rank in class for this exam |
| percentage | NUMERIC(5,2) | NULL | Percentage |
| remarks | TEXT | NULL | Teacher remarks |
| is_absent | BOOLEAN | NOT NULL DEFAULT false | Was absent for exam |
| entered_by | UUID | NULL, FK staff(id) | Teacher who entered |
| entered_at | TIMESTAMPTZ | NULL | When entered |

**Indexes:**
- `uq_exam_results_exam_student` UNIQUE on `(exam_id, student_id)` WHERE is_active = true
- `idx_exam_results_student` on `(student_id)`
- `idx_exam_results_exam` on `(exam_id, rank)`
- `idx_exam_results_grade` on `(exam_id, grade)`

**Relationships:**
- `exam_results.exam_id` -> `exams.id` ON DELETE CASCADE
- `exam_results.student_id` -> `students.id`
- `exam_results.entered_by` -> `staff.id`

---

### grade_systems

> Configurable grade scales (can have multiple systems, e.g., CBSE, ICSE, internal).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Grade system identifier |
| name | VARCHAR(100) | NOT NULL | System name e.g. "CBSE Grading" |
| is_default | BOOLEAN | NOT NULL DEFAULT false | Default system for school |
| description | TEXT | NULL | Description |

**Indexes:**
- `uq_grade_systems_school_name` UNIQUE on `(school_id, name)`

---

### grade_scales

> Individual grade definitions within a grade system.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Grade scale entry identifier |
| grade_system_id | UUID | NOT NULL, FK grade_systems(id) | Parent system |
| grade | VARCHAR(10) | NOT NULL | Grade label e.g. "A+", "A", "B+" |
| min_percentage | NUMERIC(5,2) | NOT NULL | Minimum % for this grade |
| max_percentage | NUMERIC(5,2) | NOT NULL | Maximum % for this grade |
| grade_point | NUMERIC(3,1) | NULL | GPA points |
| description | VARCHAR(100) | NULL | e.g. "Outstanding", "Very Good" |
| sort_order | INTEGER | NOT NULL DEFAULT 0 | Display order |

**Indexes:**
- `uq_grade_scales_system_grade` UNIQUE on `(grade_system_id, grade)`
- `idx_grade_scales_system` on `(grade_system_id, sort_order)`

**Check Constraints:**
- `chk_grade_scales_range` CHECK (max_percentage >= min_percentage)
- `chk_grade_scales_percentage` CHECK (min_percentage >= 0 AND max_percentage <= 100)

**Relationships:**
- `grade_scales.grade_system_id` -> `grade_systems.id` ON DELETE CASCADE

---

## 9. Leaves

### leave_policies

> Leave policy configuration per academic year (types and limits).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Policy identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| leave_type | VARCHAR(50) | NOT NULL | Type (from enum_configs: Casual, Sick, Earned, etc.) |
| max_days | INTEGER | NOT NULL | Max allowed per year |
| carry_forward | BOOLEAN | NOT NULL DEFAULT false | Can carry unused to next year |
| carry_forward_max | INTEGER | NULL | Max days to carry |
| requires_approval | BOOLEAN | NOT NULL DEFAULT true | Needs admin approval |
| applicable_to | VARCHAR(20) | NOT NULL DEFAULT 'all' | all/teaching/non-teaching |
| min_notice_days | INTEGER | NULL | Advance notice required |
| description | TEXT | NULL | Policy description |

**Indexes:**
- `uq_leave_policies_year_type` UNIQUE on `(school_id, academic_year_id, leave_type)`
- `idx_leave_policies_year` on `(school_id, academic_year_id)`

---

### leave_applications

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Application identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| staff_id | UUID | NOT NULL, FK staff(id) | Applicant |
| leave_type | VARCHAR(50) | NOT NULL | Type (from enum_configs) |
| start_date | DATE | NOT NULL | Leave start |
| end_date | DATE | NOT NULL | Leave end |
| total_days | NUMERIC(4,1) | NOT NULL | Number of days (supports half-days) |
| reason | TEXT | NOT NULL | Reason for leave |
| attachment_url | TEXT | NULL | Supporting document |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Pending' | Pending/Approved/Rejected/Cancelled |
| approved_by | UUID | NULL, FK staff(id) | Admin who approved/rejected |
| approved_at | TIMESTAMPTZ | NULL | Approval timestamp |
| rejection_reason | TEXT | NULL | Reason for rejection |
| substitute_staff_id | UUID | NULL, FK staff(id) | Substitute teacher assigned |
| applied_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | When applied |

**Indexes:**
- `idx_leave_applications_staff` on `(staff_id, academic_year_id)`
- `idx_leave_applications_status` on `(school_id, academic_year_id, status)`
- `idx_leave_applications_dates` on `(school_id, start_date, end_date)`
- `idx_leave_applications_pending` on `(school_id, academic_year_id)` WHERE status = 'Pending'

**Check Constraints:**
- `chk_leave_applications_dates` CHECK (end_date >= start_date)
- `chk_leave_applications_days` CHECK (total_days > 0)

**Relationships:**
- `leave_applications.staff_id` -> `staff.id`
- `leave_applications.approved_by` -> `staff.id`
- `leave_applications.substitute_staff_id` -> `staff.id`

---

## 10. Fees

### fee_structures

> Defines fee components for a class per academic year.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Fee structure identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| class_id | UUID | NOT NULL, FK classes(id) | Applicable class |
| fee_type | VARCHAR(50) | NOT NULL | Type (from enum_configs: Tuition, Transport, Lab, etc.) |
| fee_category | VARCHAR(20) | NOT NULL DEFAULT 'academic' | Category: academic, transport, other |
| component_name | VARCHAR(255) | NOT NULL | Display name |
| amount | NUMERIC(10,2) | NOT NULL | Amount |
| frequency | VARCHAR(20) | NOT NULL | Monthly/Quarterly/Semi-Annual/Annual/One-Time |
| due_day | INTEGER | NULL | Day of month/quarter when due |
| is_mandatory | BOOLEAN | NOT NULL DEFAULT true | Mandatory or optional |
| description | TEXT | NULL | Description |
| late_fee_type | VARCHAR(20) | NULL | Fixed/Percentage |
| late_fee_amount | NUMERIC(10,2) | NULL | Late fee value |
| late_fee_grace_days | INTEGER | NULL | Grace period in days |

**Indexes:**
- `uq_fee_structures` UNIQUE on `(school_id, academic_year_id, class_id, fee_type, component_name)`
- `idx_fee_structures_class` on `(class_id, academic_year_id)`

**Check Constraints:**
- `chk_fee_structures_amount` CHECK (amount >= 0)

**Relationships:**
- `fee_structures.class_id` -> `classes.id`

---

### fee_records

> Individual fee charges assigned to a student.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Fee record identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| student_id | UUID | NOT NULL, FK students(id) | Student charged |
| fee_structure_id | UUID | NULL, FK fee_structures(id) | Source structure (NULL for adhoc) |
| fee_type | VARCHAR(50) | NOT NULL | Fee type |
| fee_category | VARCHAR(20) | NOT NULL DEFAULT 'academic' | Category: academic, transport, other |
| description | VARCHAR(255) | NOT NULL | Description |
| amount | NUMERIC(10,2) | NOT NULL | Original amount |
| discount_amount | NUMERIC(10,2) | NOT NULL DEFAULT 0 | Discount applied |
| late_fee_amount | NUMERIC(10,2) | NOT NULL DEFAULT 0 | Late fee applied |
| late_fee_applied_on | TIMESTAMPTZ | NULL | When late fee was applied |
| total_late_fee | NUMERIC(10,2) | NOT NULL DEFAULT 0 | Total late fee accumulated (sum of all penalties) |
| net_amount | NUMERIC(10,2) | NOT NULL | Amount - Discount + Total Late Fee |
| paid_amount | NUMERIC(10,2) | NOT NULL DEFAULT 0 | Total paid so far |
| balance_amount | NUMERIC(10,2) | NOT NULL | Net - Paid |
| due_date | DATE | NOT NULL | Payment due date |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Pending' | Pending/Partially Paid/Paid/Overdue/Waived |
| period_label | VARCHAR(50) | NULL | "Jan 2026", "Q1 2025-26", etc. |

**Indexes:**
- `idx_fee_records_student` on `(student_id, academic_year_id)`
- `idx_fee_records_status` on `(school_id, academic_year_id, status)`
- `idx_fee_records_due_date` on `(school_id, due_date)` WHERE status IN ('Pending', 'Overdue')
- `idx_fee_records_class` on `(school_id, academic_year_id, fee_type)`

**Check Constraints:**
- `chk_fee_records_amounts` CHECK (amount >= 0 AND discount_amount >= 0 AND late_fee_amount >= 0 AND total_late_fee >= 0 AND paid_amount >= 0)
- `chk_fee_records_net` CHECK (net_amount = amount - discount_amount + total_late_fee)
- `chk_fee_records_balance` CHECK (balance_amount = net_amount - paid_amount)

**Relationships:**
- `fee_records.student_id` -> `students.id`
- `fee_records.fee_structure_id` -> `fee_structures.id`

---

### fee_payments

> Payments made against fee records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Payment identifier |
| fee_record_id | UUID | NOT NULL, FK fee_records(id) | Against which fee |
| student_id | UUID | NOT NULL, FK students(id) | Student (denormalized for queries) |
| amount | NUMERIC(10,2) | NOT NULL | Payment amount |
| payment_date | DATE | NOT NULL | Date of payment |
| payment_mode | VARCHAR(50) | NOT NULL | Cash/Cheque/Online/UPI/Bank Transfer |
| transaction_reference | VARCHAR(100) | NULL | Transaction ID/cheque number |
| receipt_number | VARCHAR(50) | NULL | Receipt number |
| collected_by | UUID | NULL, FK staff(id) | Staff who collected |
| remarks | TEXT | NULL | Payment remarks |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Completed' | Completed/Refunded/Bounced |

**Indexes:**
- `idx_fee_payments_record` on `(fee_record_id)`
- `idx_fee_payments_student` on `(student_id, payment_date)`
- `idx_fee_payments_date` on `(school_id, payment_date)`
- `idx_fee_payments_receipt` on `(school_id, receipt_number)` WHERE receipt_number IS NOT NULL

**Check Constraints:**
- `chk_fee_payments_amount` CHECK (amount > 0)

**Relationships:**
- `fee_payments.fee_record_id` -> `fee_records.id`
- `fee_payments.student_id` -> `students.id`
- `fee_payments.collected_by` -> `staff.id`

---

### fee_reminders

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Reminder identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| fee_record_id | UUID | NULL, FK fee_records(id) | Specific record (NULL = bulk) |
| student_id | UUID | NOT NULL, FK students(id) | Student |
| sent_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | When sent |
| sent_via | VARCHAR(20) | NOT NULL | SMS/Email/WhatsApp/InApp |
| message | TEXT | NULL | Reminder message |
| sent_by | UUID | NOT NULL, FK staff(id) | Admin who triggered |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Sent' | Sent/Delivered/Failed |

**Indexes:**
- `idx_fee_reminders_student` on `(student_id)`
- `idx_fee_reminders_sent` on `(school_id, sent_at)`

**Relationships:**
- `fee_reminders.student_id` -> `students.id`
- `fee_reminders.fee_record_id` -> `fee_records.id`
- `fee_reminders.sent_by` -> `staff.id`

---

## 11. Transport

### vehicles

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Vehicle identifier |
| registration_number | VARCHAR(50) | NOT NULL | Registration plate |
| type | VARCHAR(50) | NOT NULL | Bus/Van/Mini-Bus/Auto |
| make | VARCHAR(100) | NULL | Manufacturer |
| model | VARCHAR(100) | NULL | Model |
| year | INTEGER | NULL | Manufacturing year |
| capacity | INTEGER | NOT NULL | Seating capacity |
| fuel_type | VARCHAR(20) | NULL | Diesel/Petrol/CNG/Electric |
| insurance_expiry | DATE | NULL | Insurance expiry date |
| fitness_expiry | DATE | NULL | Fitness certificate expiry |
| permit_expiry | DATE | NULL | Permit expiry |
| gps_device_id | VARCHAR(100) | NULL | GPS tracker ID |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Active' | Active/Under Maintenance/Retired |

**Indexes:**
- `uq_vehicles_registration` UNIQUE on `(school_id, registration_number)`
- `idx_vehicles_status` on `(school_id, status)`

---

### drivers

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Driver identifier |
| employee_id | VARCHAR(50) | NULL | Employee ID (if also in staff) |
| full_name | VARCHAR(255) | NOT NULL | Driver name |
| phone | VARCHAR(20) | NOT NULL | Phone |
| alternate_phone | VARCHAR(20) | NULL | Alternate phone |
| license_number | VARCHAR(50) | NOT NULL | Driving license |
| license_type | VARCHAR(20) | NULL | LMV/HMV/Both |
| license_expiry | DATE | NULL | License expiry |
| address | TEXT | NULL | Address |
| photo_url | TEXT | NULL | Photo |
| date_of_birth | DATE | NULL | DOB |
| blood_group | VARCHAR(5) | NULL | Blood group |
| experience_years | INTEGER | NULL | Driving experience |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Active' | Active/Inactive/On Leave |

**Indexes:**
- `uq_drivers_license` UNIQUE on `(school_id, license_number)`
- `idx_drivers_status` on `(school_id, status)`

---

### helpers

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Helper identifier |
| full_name | VARCHAR(255) | NOT NULL | Helper/attendant name |
| phone | VARCHAR(20) | NOT NULL | Phone |
| alternate_phone | VARCHAR(20) | NULL | Alternate phone |
| address | TEXT | NULL | Address |
| photo_url | TEXT | NULL | Photo |
| date_of_birth | DATE | NULL | DOB |
| blood_group | VARCHAR(5) | NULL | Blood group |
| id_proof_type | VARCHAR(50) | NULL | Aadhar/Voter ID/etc. |
| id_proof_number | VARCHAR(50) | NULL | ID number |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Active' | Active/Inactive |

**Indexes:**
- `idx_helpers_status` on `(school_id, status)`

---

### routes

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Route identifier |
| name | VARCHAR(100) | NOT NULL | Route name e.g. "Route 1 - Koramangala" |
| code | VARCHAR(20) | NULL | Route code |
| start_point | VARCHAR(255) | NULL | Starting point |
| end_point | VARCHAR(255) | NULL | Ending point |
| stops | JSONB | NOT NULL DEFAULT '[]' | Ordered array of stops with names, times, coordinates |
| distance_km | NUMERIC(6,1) | NULL | Total distance |
| estimated_duration_minutes | INTEGER | NULL | Estimated travel time |
| shift | VARCHAR(20) | NULL | Morning/Afternoon/Both |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Active' | Active/Inactive |

**Indexes:**
- `uq_routes_school_name` UNIQUE on `(school_id, name)`
- `idx_routes_status` on `(school_id, status)`

---

### route_assignments

> Operational mapping: route + vehicle + driver + helper.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Assignment identifier |
| route_id | UUID | NOT NULL, FK routes(id) | Route |
| vehicle_id | UUID | NOT NULL, FK vehicles(id) | Vehicle assigned |
| driver_id | UUID | NOT NULL, FK drivers(id) | Driver assigned |
| helper_id | UUID | NULL, FK helpers(id) | Helper/attendant |
| shift | VARCHAR(20) | NOT NULL DEFAULT 'Both' | Morning/Afternoon/Both |
| effective_from | DATE | NULL | Start date |
| effective_to | DATE | NULL | End date (NULL = ongoing) |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Active' | Active/Inactive |

**Indexes:**
- `uq_route_assignments_active` UNIQUE on `(school_id, route_id, shift)` WHERE is_active = true AND effective_to IS NULL
- `idx_route_assignments_vehicle` on `(vehicle_id)`
- `idx_route_assignments_driver` on `(driver_id)`

**Relationships:**
- `route_assignments.route_id` -> `routes.id`
- `route_assignments.vehicle_id` -> `vehicles.id`
- `route_assignments.driver_id` -> `drivers.id`
- `route_assignments.helper_id` -> `helpers.id`

---

### student_transport

> Maps student to a route + pickup point.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Record identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| student_id | UUID | NOT NULL, FK students(id) | Student |
| route_id | UUID | NOT NULL, FK routes(id) | Route |
| pickup_point | VARCHAR(255) | NULL | Pickup stop name |
| drop_point | VARCHAR(255) | NULL | Drop stop name |
| pickup_time | TIME | NULL | Expected pickup time |
| drop_time | TIME | NULL | Expected drop time |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Active' | Active/Inactive |

**Indexes:**
- `uq_student_transport_year` UNIQUE on `(school_id, academic_year_id, student_id)` WHERE is_active = true
- `idx_student_transport_route` on `(route_id, academic_year_id)`
- `idx_student_transport_student` on `(student_id)`

**Relationships:**
- `student_transport.student_id` -> `students.id`
- `student_transport.route_id` -> `routes.id`

---

---

## 13. Notifications

### notifications

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Notification identifier |
| title | VARCHAR(255) | NOT NULL | Notification title |
| body | TEXT | NOT NULL | Notification content |
| type | VARCHAR(50) | NULL | Type (from enum_configs: Announcement, Alert, Reminder, etc.) |
| priority | VARCHAR(10) | NOT NULL DEFAULT 'Normal' | Low/Normal/High/Urgent |
| sent_by | UUID | NOT NULL, FK staff(id) | Sender (admin/teacher) |
| target_type | VARCHAR(30) | NOT NULL | all/students/teaching_staff/non_teaching_staff/parents/specific_class |
| target_class_section_id | UUID | NULL, FK class_sections(id) | Target class (if class/section) |
| target_role | VARCHAR(20) | NULL | Target role (if role-based) |
| channel | VARCHAR(20) | NOT NULL DEFAULT 'InApp' | InApp/SMS/Email/WhatsApp |
| scheduled_at | TIMESTAMPTZ | NULL | Scheduled send time (NULL = immediate) |
| sent_at | TIMESTAMPTZ | NULL | Actual send time |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Draft' | Draft/Scheduled/Sent/Failed |
| attachment_urls | JSONB | NOT NULL DEFAULT '[]' | Attachments |

**Indexes:**
- `idx_notifications_school_status` on `(school_id, status, sent_at DESC)`
- `idx_notifications_sender` on `(sent_by)`
- `idx_notifications_target` on `(school_id, target_type, target_class_section_id)`
- `idx_notifications_scheduled` on `(school_id)` WHERE status = 'Scheduled'

**Relationships:**
- `notifications.sent_by` -> `staff.id`
- `notifications.target_class_section_id` -> `class_sections.id`

---

### notification_recipients

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Record identifier |
| notification_id | UUID | NOT NULL, FK notifications(id) | Notification |
| user_id | UUID | NOT NULL, FK users(id) | Recipient user |
| is_read | BOOLEAN | NOT NULL DEFAULT false | Read status |
| read_at | TIMESTAMPTZ | NULL | When read |
| delivered_at | TIMESTAMPTZ | NULL | When delivered |
| delivery_status | VARCHAR(20) | NOT NULL DEFAULT 'Pending' | Pending/Delivered/Failed |

**Indexes:**
- `uq_notification_recipients` UNIQUE on `(notification_id, user_id)`
- `idx_notification_recipients_user` on `(user_id, is_read)`
- `idx_notification_recipients_unread` on `(user_id)` WHERE is_read = false
- `idx_notification_recipients_notification` on `(notification_id, delivery_status)`

**Relationships:**
- `notification_recipients.notification_id` -> `notifications.id` ON DELETE CASCADE
- `notification_recipients.user_id` -> `users.id`

---

## 14. Payroll

### salary_structures

> Defines salary components for a staff member per academic year.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Structure identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| staff_id | UUID | NOT NULL, FK staff(id) | Staff member |
| base_salary | NUMERIC(10,2) | NOT NULL | Base/basic salary |
| components | JSONB | NOT NULL DEFAULT '[]' | Array: [{name, type: "earning"|"deduction", amount, percentage, is_taxable}] |
| gross_salary | NUMERIC(10,2) | NOT NULL | Total earnings |
| total_deductions | NUMERIC(10,2) | NOT NULL DEFAULT 0 | Total deductions |
| net_salary | NUMERIC(10,2) | NOT NULL | Gross - Deductions |
| effective_from | DATE | NOT NULL | Start date |
| effective_to | DATE | NULL | End date (NULL = current) |

**Indexes:**
- `idx_salary_structures_staff` on `(staff_id, academic_year_id)`
- `uq_salary_structures_active` UNIQUE on `(school_id, staff_id)` WHERE effective_to IS NULL AND is_active = true

**Check Constraints:**
- `chk_salary_structures_amounts` CHECK (base_salary >= 0 AND gross_salary >= 0 AND net_salary >= 0)

**Relationships:**
- `salary_structures.staff_id` -> `staff.id`

---

### payslips

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Payslip identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| staff_id | UUID | NOT NULL, FK staff(id) | Staff member |
| salary_structure_id | UUID | NOT NULL, FK salary_structures(id) | Source structure |
| month | INTEGER | NOT NULL | Month (1-12) |
| year | INTEGER | NOT NULL | Calendar year |
| working_days | INTEGER | NULL | Total working days in month |
| days_present | INTEGER | NULL | Days present |
| days_absent | INTEGER | NULL | Days absent |
| base_salary | NUMERIC(10,2) | NOT NULL | Base salary |
| earnings | JSONB | NOT NULL DEFAULT '[]' | Array of earning components |
| deductions | JSONB | NOT NULL DEFAULT '[]' | Array of deduction components |
| gross_salary | NUMERIC(10,2) | NOT NULL | Total earnings |
| total_deductions | NUMERIC(10,2) | NOT NULL | Total deductions |
| net_salary | NUMERIC(10,2) | NOT NULL | Take-home |
| advance_deduction | NUMERIC(10,2) | NOT NULL DEFAULT 0 | Salary advance deducted |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Generated' | Generated/Approved/Paid/Cancelled |
| paid_date | DATE | NULL | Date paid |
| payment_mode | VARCHAR(50) | NULL | Bank Transfer/Cheque/Cash |
| transaction_reference | VARCHAR(100) | NULL | Transaction ref |
| generated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | When generated |
| generated_by | UUID | NULL, FK staff(id) | Admin who generated |

**Indexes:**
- `uq_payslips_month` UNIQUE on `(school_id, staff_id, month, year)` WHERE is_active = true
- `idx_payslips_staff` on `(staff_id, year, month)`
- `idx_payslips_period` on `(school_id, year, month)`
- `idx_payslips_status` on `(school_id, year, month, status)`

**Check Constraints:**
- `chk_payslips_month` CHECK (month >= 1 AND month <= 12)
- `chk_payslips_amounts` CHECK (gross_salary >= 0 AND net_salary >= 0)

**Relationships:**
- `payslips.staff_id` -> `staff.id`
- `payslips.salary_structure_id` -> `salary_structures.id`

---

### salary_advances

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Advance identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| staff_id | UUID | NOT NULL, FK staff(id) | Requesting staff |
| amount | NUMERIC(10,2) | NOT NULL | Requested amount |
| reason | TEXT | NULL | Reason for advance |
| requested_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | When requested |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Pending' | Pending/Approved/Rejected/Disbursed/Repaid |
| approved_by | UUID | NULL, FK staff(id) | Admin who approved |
| approved_at | TIMESTAMPTZ | NULL | Approval timestamp |
| rejection_reason | TEXT | NULL | Reason if rejected |
| disbursed_at | TIMESTAMPTZ | NULL | When disbursed |
| disbursed_amount | NUMERIC(10,2) | NULL | Actual disbursed amount |
| repayment_mode | VARCHAR(50) | NULL | Lump-sum/EMI |
| emi_months | INTEGER | NULL | Number of EMI months |
| repaid_amount | NUMERIC(10,2) | NOT NULL DEFAULT 0 | Total repaid |
| remaining_amount | NUMERIC(10,2) | NULL | Remaining to repay |

**Indexes:**
- `idx_salary_advances_staff` on `(staff_id, academic_year_id)`
- `idx_salary_advances_status` on `(school_id, academic_year_id, status)`
- `idx_salary_advances_pending` on `(school_id)` WHERE status = 'Pending'

**Check Constraints:**
- `chk_salary_advances_amount` CHECK (amount > 0)

**Relationships:**
- `salary_advances.staff_id` -> `staff.id`
- `salary_advances.approved_by` -> `staff.id`

---

## 15. Activities, Awards & Discipline

### activities

> Student extra-curricular activities and club memberships.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Activity identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| student_id | UUID | NOT NULL, FK students(id) | Student |
| activity_type | VARCHAR(50) | NOT NULL | Type (from enum_configs: Sports, Arts, Music, Club, etc.) |
| name | VARCHAR(255) | NOT NULL | Activity name |
| description | TEXT | NULL | Description |
| role | VARCHAR(100) | NULL | Student's role (Captain, Member, etc.) |
| start_date | DATE | NULL | Start date |
| end_date | DATE | NULL | End date |
| achievement | TEXT | NULL | Achievement details |
| certificate_url | TEXT | NULL | Certificate file |
| recorded_by | UUID | NULL, FK staff(id) | Staff who recorded |

**Indexes:**
- `idx_activities_student` on `(student_id, academic_year_id)`
- `idx_activities_type` on `(school_id, academic_year_id, activity_type)`

**Relationships:**
- `activities.student_id` -> `students.id`
- `activities.recorded_by` -> `staff.id`

---

### awards

> Student achievements and awards.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Award identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| student_id | UUID | NOT NULL, FK students(id) | Student |
| title | VARCHAR(255) | NOT NULL | Award title |
| category | VARCHAR(100) | NULL | Category (Academic, Sports, Cultural, etc.) |
| description | TEXT | NULL | Description |
| awarded_date | DATE | NULL | Date awarded |
| awarded_by | VARCHAR(255) | NULL | Awarding body/person |
| level | VARCHAR(50) | NULL | School/District/State/National/International |
| certificate_url | TEXT | NULL | Certificate file |
| recorded_by | UUID | NULL, FK staff(id) | Staff who recorded |

**Indexes:**
- `idx_awards_student` on `(student_id, academic_year_id)`
- `idx_awards_category` on `(school_id, academic_year_id, category)`

**Relationships:**
- `awards.student_id` -> `students.id`
- `awards.recorded_by` -> `staff.id`

---

### disciplinary_records

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Record identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| student_id | UUID | NOT NULL, FK students(id) | Student |
| incident_date | DATE | NOT NULL | When incident occurred |
| category | VARCHAR(50) | NOT NULL | Category (from enum_configs: Behavioral, Academic Dishonesty, etc.) |
| severity | VARCHAR(20) | NOT NULL | Minor/Moderate/Major/Critical |
| description | TEXT | NOT NULL | Incident description |
| action_taken | TEXT | NULL | Disciplinary action |
| reported_by | UUID | NOT NULL, FK staff(id) | Staff who reported |
| parent_notified | BOOLEAN | NOT NULL DEFAULT false | Parent informed |
| parent_notified_date | DATE | NULL | When parent was notified |
| follow_up_date | DATE | NULL | Scheduled follow-up |
| follow_up_notes | TEXT | NULL | Follow-up notes |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Open' | Open/Resolved/Escalated |

**Indexes:**
- `idx_disciplinary_student` on `(student_id, academic_year_id)`
- `idx_disciplinary_date` on `(school_id, incident_date)`
- `idx_disciplinary_status` on `(school_id, academic_year_id, status)`

**Relationships:**
- `disciplinary_records.student_id` -> `students.id`
- `disciplinary_records.reported_by` -> `staff.id`

---

## 16. Parent Meetings

### parent_meetings

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Meeting identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| student_id | UUID | NOT NULL, FK students(id) | Student |
| meeting_date | DATE | NOT NULL | Meeting date |
| meeting_time | TIME | NULL | Meeting time |
| conducted_by | UUID | NOT NULL, FK staff(id) | Teacher/staff who conducted |
| parent_id | UUID | NULL, FK parents(id) | Parent who attended |
| attendees | JSONB | NOT NULL DEFAULT '[]' | List of attendees |
| agenda | TEXT | NULL | Meeting agenda |
| discussion_notes | TEXT | NULL | Discussion summary |
| action_items | JSONB | NOT NULL DEFAULT '[]' | Action items |
| next_meeting_date | DATE | NULL | Scheduled follow-up |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Scheduled' | Scheduled/Completed/Cancelled/No-Show |
| meeting_type | VARCHAR(50) | NULL | Regular/Emergency/Follow-up |

**Indexes:**
- `idx_parent_meetings_student` on `(student_id, academic_year_id)`
- `idx_parent_meetings_date` on `(school_id, meeting_date)`
- `idx_parent_meetings_conductor` on `(conducted_by, meeting_date)`
- `idx_parent_meetings_status` on `(school_id, academic_year_id, status)`

**Relationships:**
- `parent_meetings.student_id` -> `students.id`
- `parent_meetings.conducted_by` -> `staff.id`
- `parent_meetings.parent_id` -> `parents.id`

---

## 17. Adhoc Classes

### adhoc_classes

> Substitute/extra classes logged by teachers.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Adhoc class identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| staff_id | UUID | NOT NULL, FK staff(id) | Teacher who took/will take |
| class_section_id | UUID | NOT NULL, FK class_sections(id) | Target class |
| subject_id | UUID | NOT NULL, FK subjects(id) | Subject |
| date | DATE | NOT NULL | Class date |
| start_time | TIME | NULL | Start time |
| end_time | TIME | NULL | End time |
| type | VARCHAR(20) | NOT NULL | Substitute/Extra/Remedial |
| reason | TEXT | NULL | Reason for adhoc class |
| original_staff_id | UUID | NULL, FK staff(id) | Original teacher (for substitution) |
| topic | VARCHAR(255) | NULL | Topic covered |
| notes | TEXT | NULL | Class notes |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Scheduled' | Scheduled/Completed/Cancelled |

**Indexes:**
- `idx_adhoc_classes_staff` on `(staff_id, date)`
- `idx_adhoc_classes_class` on `(class_section_id, date)`
- `idx_adhoc_classes_date` on `(school_id, date)`
- `idx_adhoc_classes_status` on `(school_id, academic_year_id, status)`

**Relationships:**
- `adhoc_classes.staff_id` -> `staff.id`
- `adhoc_classes.class_section_id` -> `class_sections.id`
- `adhoc_classes.subject_id` -> `subjects.id`
- `adhoc_classes.original_staff_id` -> `staff.id`

---

## 18. Leave Balances

### leave_balances

> Tracks per-staff leave balance for each academic year and leave type. Total available = total_allocated + carried_forward - used - pending.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Balance record identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| staff_id | UUID | NOT NULL, FK staff(id) | Staff member |
| leave_type | VARCHAR(50) | NOT NULL | Type (from enum_configs: Casual, Sick, Earned, etc.) |
| total_allocated | INTEGER | NOT NULL | Total days allocated for this type/year |
| carried_forward | INTEGER | NOT NULL DEFAULT 0 | Days carried forward from previous year |
| used | INTEGER | NOT NULL DEFAULT 0 | Days used (approved leaves) |
| pending | INTEGER | NOT NULL DEFAULT 0 | Days in pending applications |

**Indexes:**
- `uq_leave_balances` UNIQUE on `(school_id, academic_year_id, staff_id, leave_type)`
- `idx_leave_balances_staff` on `(staff_id, academic_year_id)`

**Check Constraints:**
- `chk_leave_balances_values` CHECK (total_allocated >= 0 AND carried_forward >= 0 AND used >= 0 AND pending >= 0)

**Relationships:**
- `leave_balances.staff_id` -> `staff.id`
- `leave_balances.academic_year_id` -> `academic_years.id`

---

## 19. Fee Penalties

### fee_penalties

> Tracks individual late fee / penalty applications against fee records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Penalty identifier |
| fee_record_id | UUID | NOT NULL, FK fee_records(id) | Fee record penalized |
| penalty_type | VARCHAR(20) | NOT NULL | fixed/percentage |
| amount | NUMERIC(10,2) | NOT NULL | Penalty amount applied |
| percentage | NUMERIC(5,2) | NULL | Percentage (if percentage-based) |
| applied_on | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | When penalty was applied |
| applied_by | UUID | NOT NULL, FK staff(id) | Admin who applied |
| reason | TEXT | NULL | Reason for penalty |

**Indexes:**
- `idx_fee_penalties_record` on `(fee_record_id)`
- `idx_fee_penalties_date` on `(school_id, applied_on)`

**Relationships:**
- `fee_penalties.fee_record_id` -> `fee_records.id`
- `fee_penalties.applied_by` -> `staff.id`

---

## 20. Salary Revisions

### salary_revisions

> Tracks salary hikes and revisions over time for staff members. Includes standard audit columns (`created_at`, `updated_at`, `created_by`, `updated_by`) and `metadata JSONB` as per common column template.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Revision identifier |
| academic_year_id | UUID | NOT NULL, FK academic_years(id) | Scoped to year |
| staff_id | UUID | NOT NULL, FK staff(id) | Staff member |
| effective_date | DATE | NOT NULL | When revision takes effect |
| previous_basic | NUMERIC(10,2) | NOT NULL | Previous basic salary |
| new_basic | NUMERIC(10,2) | NOT NULL | New basic salary |
| revision_type | VARCHAR(50) | NOT NULL | Annual Hike/Promotion/Adjustment |
| percentage | NUMERIC(5,2) | NULL | Hike percentage |
| increment_amount | NUMERIC(10,2) | NULL | Absolute increment amount (new_basic - previous_basic) |
| approved_by | UUID | NULL, FK staff(id) | Admin who approved |
| approved_on | TIMESTAMPTZ | NULL | When approval was granted |
| remarks | TEXT | NULL | Additional notes |

**Indexes:**
- `idx_salary_revisions_staff` on `(staff_id, effective_date DESC)`
- `idx_salary_revisions_date` on `(school_id, effective_date)`
- `idx_salary_revisions_year` on `(school_id, academic_year_id)`

**Check Constraints:**
- `chk_salary_revisions_amounts` CHECK (previous_basic >= 0 AND new_basic >= 0)

**Relationships:**
- `salary_revisions.staff_id` -> `staff.id`
- `salary_revisions.approved_by` -> `staff.id`
- `salary_revisions.academic_year_id` -> `academic_years.id`

---

---

## Entity Relationship Diagram (Text)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CORE / TENANT                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────┐       ┌──────────────┐       ┌───────────────┐               │
│  │  schools │──┐    │ academic_    │       │    users      │               │
│  │          │  │    │ years        │       │ (auth layer)  │               │
│  └──────────┘  │    └──────────────┘       └───────────────┘               │
│                │           │                   │   │   │                     │
│       All tables FK ───────┘                   │   │   │                     │
│                                                │   │   │                     │
│  ┌──────────┐    ┌──────────────┐             │   │   │                     │
│  │ settings │    │ enum_configs  │             │   │   │                     │
│  └──────────┘    └──────────────┘             │   │   │                     │
└───────────────────────────────────────────────┼───┼───┼─────────────────────┘
                                                │   │   │
┌───────────────────────────────────────────────┼───┼───┼─────────────────────┐
│                         PEOPLE                 │   │   │                      │
├───────────────────────────────────────────────┼───┼───┼─────────────────────┤
│                                                │   │   │                      │
│  ┌────────┐◄───────────────────────────────────┘   │   │                     │
│  │  staff │                                         │   │                     │
│  │        │──┐  ┌────────────────┐                  │   │                     │
│  └────────┘  │  │ staff_subjects │                  │   │                     │
│       │      │  └────────────────┘                  │   │                     │
│       │      │                                      │   │                     │
│       │      └──► class_assignments                 │   │                     │
│       │               │                             │   │                     │
│       │               ▼                             │   │                     │
│       │      ┌────────────────┐                     │   │                     │
│       │      │ student_mentors│                     │   │                     │
│       │      └────────────────┘                     │   │                     │
│       │               │                             │   │                     │
│       │               ▼                             │   │                     │
│  ┌────────────┐◄────────────────────────────────────┘   │                    │
│  │  students  │                                          │                    │
│  │            │──┐  ┌──────────────────────┐            │                    │
│  └────────────┘  │  │ student_enrollments  │            │                    │
│       │          │  └──────────────────────┘            │                    │
│       │          │                                       │                    │
│       │          └──► student_parents                    │                    │
│       │                    │                             │                    │
│       │                    ▼                             │                    │
│  ┌────────────┐◄────────────────────────────────────────┘                   │
│  │  parents   │                                                              │
│  └────────────┘                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        ACADEMIC STRUCTURE                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────┐     ┌──────────┐     ┌────────────────┐     ┌──────────┐     │
│  │ classes │────►│ class_   │◄────│   sections     │     │ subjects │     │
│  │         │     │ sections │     │                │     │          │     │
│  └─────────┘     └────────────┘     └────────────────┘     └──────────┘     │
│                        │                                         │            │
│                        │    Referenced by:                        │            │
│                        │    - student_enrollments                 │            │
│                        │    - class_assignments                   │            │
│                        │    - timetable_slots                     │            │
│                        │    - attendance_sessions                 │            │
│                        │    - assignments                         │            │
│                        │    - exams                               │            │
│                        │    - adhoc_classes                       │            │
│                        │    - notifications                       │            │
│                        ▼                                         │            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           TIMETABLE                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────┐         ┌──────────────────┐                            │
│  │ period_configs │────────►│ timetable_slots  │                            │
│  │ (time slots)   │         │ (day+period+     │                            │
│  └────────────────┘         │  class=teacher+  │                            │
│                             │  subject)        │                            │
│                             └──────────────────┘                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           ATTENDANCE                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────┐         ┌──────────────────────┐                  │
│  │ attendance_sessions  │────────►│ attendance_records   │                  │
│  │ (class+date+teacher) │         │ (student+status)     │                  │
│  └──────────────────────┘         └──────────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXAMINATIONS                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────┐         ┌───────────────┐         ┌───────────────┐           │
│  │  exams  │────────►│ exam_results  │         │ grade_systems │           │
│  └─────────┘         └───────────────┘         │       │       │           │
│                                                 │  grade_scales │           │
│                                                 └───────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              FEES                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────┐       ┌─────────────┐       ┌──────────────┐           │
│  │ fee_structures │──────►│ fee_records │──────►│ fee_payments │           │
│  │ (class-level)  │       │ (student)   │       │              │           │
│  └────────────────┘       └─────────────┘       └──────────────┘           │
│                                   │                                          │
│                                   └───────►┌───────────────┐                │
│                                            │ fee_reminders │                │
│                                            └───────────────┘                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            TRANSPORT                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────┐    ┌─────────┐    ┌─────────┐    ┌────────┐                 │
│  │ vehicles │    │ drivers │    │ helpers │    │ routes │                 │
│  └──────────┘    └─────────┘    └─────────┘    └────────┘                 │
│       │               │              │              │                        │
│       └───────────────┴──────────────┴──────────────┘                       │
│                           │                                                  │
│                           ▼                                                  │
│                  ┌──────────────────┐         ┌───────────────────┐         │
│                  │ route_assignments│         │ student_transport │         │
│                  └──────────────────┘         └───────────────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            PAYROLL                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────┐       ┌──────────┐       ┌──────────────────┐      │
│  │ salary_structures  │──────►│ payslips │       │ salary_advances  │      │
│  └────────────────────┘       └──────────┘       └──────────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                     ADDITIONAL TABLES                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────┐   ┌───────────────┐   ┌───────────────────┐           │
│  │ leave_balances │   │ fee_penalties │   │ salary_revisions  │           │
│  └────────────────┘   └───────────────┘   └───────────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Relationship Summary

| Relationship | Type | Description |
|---|---|---|
| schools -> all tables | 1:N | Multi-tenancy via school_id |
| academic_years -> transactional tables | 1:N | Year scoping |
| staff -> users | 1:1 | Auth link |
| students -> users | 1:1 | Auth link |
| parents -> users | 1:1 | Auth link |
| staff -> staff_subjects | 1:N | Qualified subjects |
| staff -> class_assignments | 1:N | Teaching assignments per year |
| classes + sections -> class_sections | N:M | Class-section combos |
| students -> student_enrollments | 1:N | One per year |
| students -> student_parents -> parents | N:M | Family links |
| students -> student_mentors -> staff | N:1 per year | Mentorship |
| class_sections -> timetable_slots | 1:N | Schedule |
| attendance_sessions -> attendance_records | 1:N | Per-student records |
| assignments -> assignment_submissions | 1:N | Student submissions |
| exams -> exam_results | 1:N | Per-student results |
| grade_systems -> grade_scales | 1:N | Grade definitions |
| fee_structures -> fee_records | 1:N | Generated charges |
| fee_records -> fee_payments | 1:N | Payment history |
| routes -> route_assignments | 1:N | Operational mapping |
| students -> student_transport | 1:1 per year | Route assignment |
| salary_structures -> payslips | 1:N | Monthly payslips |
| notifications -> notification_recipients | 1:N | Distribution |
| leave_balances per staff per year | 1:N | Leave tracking |
| fee_penalties per fee_record | 1:N | Late fee tracking |
| salary_revisions per staff | 1:N | Salary hike history |

---

## Composite Unique Constraints Summary

| Table | Unique Constraint | Purpose |
|---|---|---|
| academic_years | (school_id, name) | One year name per school |
| class_sections | (school_id, class_id, section_id) | No duplicate combos |
| student_enrollments | (school_id, academic_year_id, student_id) WHERE active | One enrollment per student per year |
| class_assignments | (school_id, academic_year_id, staff_id, class_section_id, subject_id) WHERE active | No duplicate assignments |
| attendance_sessions | (school_id, academic_year_id, class_section_id, date, subject_id, period_config_id) WHERE active | One session per class per date per subject per period |
| attendance_records | (attendance_session_id, student_id) | One record per student per session |
| assignment_submissions | (assignment_id, student_id) WHERE active | One submission per student per assignment |
| exam_results | (exam_id, student_id) WHERE active | One result per student per exam |
| timetable_slots | (school_id, academic_year_id, class_section_id, period_config_id, day_of_week) WHERE active | One slot per class per period per day |
| payslips | (school_id, staff_id, month, year) WHERE active | One payslip per staff per month |
| student_transport | (school_id, academic_year_id, student_id) WHERE active | One route per student per year |
| student_mentors | (school_id, academic_year_id, student_id) WHERE active | One mentor per student per year |
| notification_recipients | (notification_id, user_id) | One recipient entry per user per notification |
| leave_balances | (school_id, academic_year_id, staff_id, leave_type) | One balance per staff per type per year |

---

## Foreign Key Cascade Rules

| Scenario | Rule | Reason |
|---|---|---|
| Parent record soft-deleted | No cascade | Soft deletes are logical, not physical |
| Session deleted -> records | CASCADE | Attendance records belong to session |
| Assignment deleted -> submissions | No cascade (soft delete) | Preserve student work |
| Fee record deleted -> fee_penalties | CASCADE | Penalties are record-internal |
| Notification deleted -> recipients | CASCADE | Recipients are notification-internal |
| Grade system deleted -> scales | CASCADE | Scales are system-internal |
| Student_parents -> unlink | CASCADE | Junction table cleanup |
| Staff_subjects -> unlink | CASCADE | Junction table cleanup |

---

## Indexing Strategy

### Query Patterns and Recommended Indexes

| Query Pattern | Index Strategy |
|---|---|
| List by school + status (all tables) | Partial index on `(school_id)` WHERE is_active = true |
| Filter by academic year | Composite: `(school_id, academic_year_id, ...)` |
| Pagination (created_at ordering) | `(school_id, created_at DESC)` |
| Student lookup by name | `(school_id, full_name)` with trigram index for LIKE |
| Attendance for class on date | `(class_section_id, date)` |
| Teacher's schedule | `(staff_id, academic_year_id, day_of_week)` |
| Fee records overdue | Partial index WHERE status IN ('Pending', 'Overdue') |
| Unread notifications per user | Partial index on `(user_id)` WHERE is_read = false |
| Exam results ranked | `(exam_id, rank)` |
| Pending leaves for approval | Partial index WHERE status = 'Pending' |

---

## Migration Notes

1. **Run order matters** - Create tables in dependency order:
   - Phase 1: `schools`, `academic_years`, `settings`, `enum_configs`
   - Phase 2: `classes`, `sections`, `subjects`, `class_sections`
   - Phase 3: `staff`, `students`, `parents`, `student_parents`, `users`
   - Phase 4: `staff_subjects`, `class_assignments`, `student_enrollments`, `student_mentors`
   - Phase 5: All remaining domain tables (attendance, exams, fees, transport, etc.)

2. **Triggers** - Add `updated_at` trigger on all tables:
   ```sql
   CREATE OR REPLACE FUNCTION update_updated_at()
   RETURNS TRIGGER AS $$
   BEGIN
     NEW.updated_at = NOW();
     RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;
   ```

3. **Extensions required**:
   - `uuid-ossp` or use `gen_random_uuid()` (PG 13+)
   - `pg_trgm` for fuzzy text search on names

4. **Row-level security (optional)** - For multi-tenancy enforcement at DB level, add RLS policies filtering on `school_id`.

5. **Partitioning (future)** - For very large schools, consider partitioning `attendance_records`, `fee_payments`, `notification_recipients` by `school_id` or date range.

---

## Configurable Enum Categories (stored in `enum_configs`)

| Category | Example Values |
|---|---|
| `department` | Teaching, Administration, Accounts, IT, Library, Sports, Transport |
| `designation` | Principal, Vice Principal, HOD, Senior Teacher, Teacher, Clerk, Peon |
| `leave_type` | Casual Leave, Sick Leave, Earned Leave, Maternity Leave, Paternity Leave |
| `exam_type` | Unit Test, Mid-Term, Final, Pre-Board, Practice Test |
| `fee_type` | Tuition, Transport, Lab, Library, Sports, Exam, Development |
| `notification_type` | Announcement, Alert, Reminder, Event, Emergency |
| `activity_type` | Sports, Arts, Music, Dance, Drama, Debate, Science Club, Coding |
| `grade_scale` | CBSE 9-point, ICSE, Internal 5-point |
| `blood_group` | A+, A-, B+, B-, AB+, AB-, O+, O- |
| `disciplinary_category` | Behavioral, Academic Dishonesty, Bullying, Property Damage, Attendance |
| `payment_mode` | Cash, Cheque, Online, UPI, Bank Transfer, DD |
| `employment_type` | Full-time, Part-time, Contract, Temporary, Visiting |
| `vehicle_type` | Bus, Van, Mini-Bus, Auto, Car |

---

## Total Table Count

| Domain | Tables | Version |
|---|---|---|
| Core / Tenant | 5 | V1 |
| Staff & Teachers | 3 | V1 |
| Students | 5 | V1 |
| Academic Structure | 4 | V1 |
| Timetable | 2 | V1 |
| Attendance | 2 | V1 |
| Assignments | 2 | V1 |
| Examinations | 4 | V1 |
| Leaves | 2 | V1 |
| Leave Balances | 1 | V1 |
| Fees | 4 | V1 |
| Fee Penalties | 1 | V1 |
| Transport | 6 | V1 |
| Notifications | 2 | V1 |
| Payroll | 3 | V1 |
| Salary Revisions | 1 | V1 |
| Activities/Awards/Discipline | 3 | V1 |
| Parent Meetings | 1 | V1 |
| Adhoc Classes | 1 | V1 |
| **Total** | **52** | |
