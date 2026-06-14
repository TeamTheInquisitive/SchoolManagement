# Database Schema (58 Tables)

**Last Updated: 2026-06-14** | **Total Tables: 58**

## Academic

### `classes` (Class)

| Column | Type |
|--------|------|
| name | `str` |
| display_name | `str?` |
| sort_order | `int` |
| max_periods | `int?` |

### `sections` (Section)

| Column | Type |
|--------|------|
| name | `str` |
| sort_order | `int` |

### `class_sections` (ClassSection)

| Column | Type |
|--------|------|
| class_id | `UUID` |
| section_id | `UUID` |
| academic_year_id | `UUID` |

### `subjects` (Subject)

| Column | Type |
|--------|------|
| name | `str` |
| code | `str?` |
| description | `str?` |

### `class_subjects` (ClassSubject)

| Column | Type |
|--------|------|
| class_id | `UUID` |
| subject_id | `UUID` |
| academic_year_id | `UUID` |

## Activity

### `activities` (Activity)

| Column | Type |
|--------|------|
| academic_year_id | `UUID` |
| student_id | `UUID` |
| activity_type | `str` |
| name | `str` |
| description | `str?` |
| role | `str?` |
| start_date | `date?` |
| end_date | `date?` |
| achievement | `str?` |
| certificate_url | `str?` |
| recorded_by | `UUID?` |
| status | `str` |

### `awards` (Award)

| Column | Type |
|--------|------|
| academic_year_id | `UUID` |
| student_id | `UUID` |
| title | `str` |
| category | `str?` |
| description | `str?` |
| awarded_date | `date?` |
| awarded_by | `str?` |
| level | `str?` |
| certificate_url | `str?` |
| recorded_by | `UUID?` |

### `disciplinary_records` (DisciplinaryRecord)

| Column | Type |
|--------|------|
| academic_year_id | `UUID` |
| student_id | `UUID` |
| incident_date | `date` |
| category | `str` |
| severity | `str` |
| description | `str` |
| action_taken | `str?` |
| reported_by | `UUID` |
| parent_notified | `bool` |
| parent_notified_date | `date?` |
| follow_up_date | `date?` |
| follow_up_notes | `str?` |
| status | `str` |

## Adhoc_Class

### `adhoc_classes` (AdhocClass)

| Column | Type |
|--------|------|
| academic_year_id | `UUID` |
| staff_id | `UUID` |
| class_section_id | `UUID` |
| subject_id | `UUID` |
| date | `date` |
| start_time | `time?` |
| end_time | `time?` |
| duration_minutes | `int?` |
| type | `str` |
| reason | `str?` |
| original_staff_id | `UUID?` |
| topic | `str?` |
| notes | `str?` |
| student_count | `int` |
| status | `str` |
| description | `str?` |

## Assignment

### `assignments` (Assignment)

| Column | Type |
|--------|------|
| academic_year_id | `UUID` |
| class_section_id | `UUID` |
| subject_id | `UUID` |
| staff_id | `UUID` |
| title | `str` |
| description | `str?` |
| due_date | `date` |
| max_marks | `float?` |
| status | `str` |
| assigned_date | `date` |
| subject | `Subject` |

### `assignment_submissions` (AssignmentSubmission)

| Column | Type |
|--------|------|
| assignment_id | `UUID` |
| student_id | `UUID` |
| status | `str` |
| submitted_at | `datetime?` |
| comments | `str?` |
| file_urls | `list?` |
| marks | `float?` |
| feedback | `str?` |
| graded_at | `datetime?` |
| graded_by | `UUID?` |
| is_late | `bool` |

## Attendance

### `attendance_sessions` (AttendanceSession)

| Column | Type |
|--------|------|
| academic_year_id | `UUID` |
| class_section_id | `UUID` |
| date | `date` |
| subject_id | `UUID?` |
| period_number | `int?` |
| submitted_by | `UUID?` |
| submitted_at | `datetime` |
| status | `str` |
| cancelled_at | `datetime?` |
| cancelled_by | `UUID?` |
| total_present | `int?` |
| total_absent | `int?` |
| total_late | `int?` |
| subject | `Subject?` |

### `attendance_records` (AttendanceRecord)

| Column | Type |
|--------|------|
| attendance_session_id | `UUID` |
| student_id | `UUID` |
| status | `str` |
| remarks | `str?` |

## Core

### `schools` (School)

| Column | Type |
|--------|------|
| id | `UUID` |
| name | `str` |
| code | `str` |
| logo_url | `str?` |
| address_line1 | `str?` |
| address_line2 | `str?` |
| city | `str?` |
| state | `str?` |
| country | `str?` |
| pincode | `str?` |
| phone | `str?` |
| email | `str?` |
| website | `str?` |
| board_affiliation | `str?` |
| established_year | `int?` |
| principal_name | `str?` |
| enrollment_date | `date?` |
| subscription_status | `str` |
| trial_start_date | `date?` |
| trial_end_date | `date?` |
| metadata_ | `dict` |
| subscriptions | `list` |

### `users` (User)

| Column | Type |
|--------|------|
| id | `UUID` |
| school_id | `UUID` |
| email | `str` |
| password_hash | `str` |
| password_changed | `bool` |
| full_name | `str` |
| role | `str` |
| phone | `str?` |
| avatar_url | `str?` |
| last_login_at | `datetime?` |
| password_reset_token | `str?` |
| password_reset_expires | `datetime?` |
| is_locked | `bool` |
| failed_login_attempts | `int` |
| staff_id | `UUID?` |
| student_id | `UUID?` |
| parent_id | `UUID?` |
| metadata_ | `dict` |

### `academic_years` (AcademicYear)

| Column | Type |
|--------|------|
| name | `str` |
| start_date | `date` |
| end_date | `date` |
| is_current | `bool` |

### `settings` (Settings)

| Column | Type |
|--------|------|
| category | `str` |
| key | `str` |
| value | `dict` |
| description | `str?` |

### `enum_configs` (EnumConfig)

| Column | Type |
|--------|------|
| category | `str` |
| value | `str` |
| label | `str` |
| sort_order | `int` |
| config | `dict` |

## Examination

### `exams` (Exam)

| Column | Type |
|--------|------|
| academic_year_id | `UUID` |
| name | `str` |
| exam_type | `str` |
| class_section_id | `UUID` |
| subject_id | `UUID` |
| date | `date?` |
| start_time | `str?` |
| end_time | `str?` |
| total_marks | `Decimal` |
| passing_marks | `Decimal?` |
| status | `str` |
| examiner_id | `UUID?` |
| term | `str?` |
| published_at | `datetime?` |
| cancelled_at | `datetime?` |
| subject | `Subject` |

### `exam_results` (ExamResult)

| Column | Type |
|--------|------|
| exam_id | `UUID` |
| student_id | `UUID` |
| marks_obtained | `Decimal?` |
| grade | `str?` |
| rank | `int?` |
| attendance | `str` |
| remarks | `str?` |
| is_pass | `bool?` |

### `grade_systems` (GradeSystem)

| Column | Type |
|--------|------|
| academic_year_id | `UUID` |
| name | `str` |
| is_default | `bool` |

### `grade_scales` (GradeScale)

| Column | Type |
|--------|------|
| grade_system_id | `UUID` |
| grade | `str` |
| min_percentage | `Decimal` |
| max_percentage | `Decimal` |
| grade_point | `Decimal?` |
| description | `str?` |
| sort_order | `int` |

## Fee

### `fee_structures` (FeeStructure)

| Column | Type |
|--------|------|
| academic_year_id | `UUID` |
| class_id | `UUID?` |
| class_section_id | `UUID?` |
| fee_type | `str` |
| fee_category | `str` |
| amount | `Decimal` |
| frequency | `str` |

### `fee_records` (FeeRecord)

| Column | Type |
|--------|------|
| academic_year_id | `UUID` |
| student_id | `UUID` |
| fee_structure_id | `UUID?` |
| fee_type | `str` |
| fee_category | `str` |
| total_amount | `Decimal` |
| paid | `Decimal` |
| pending | `Decimal` |
| total_late_fee | `Decimal` |
| due_date | `date` |
| status | `str` |
| description | `str?` |
| concession_amount | `Decimal` |

### `fee_payments` (FeePayment)

| Column | Type |
|--------|------|
| fee_record_id | `UUID` |
| amount | `Decimal` |
| payment_date | `date` |
| payment_method | `str` |
| reference | `str?` |
| recorded_by | `UUID?` |

### `fee_reminders` (FeeReminder)

| Column | Type |
|--------|------|
| academic_year_id | `UUID` |
| target_group | `str` |
| class_name | `str?` |
| section | `str?` |
| message | `str` |
| send_via | `str` |
| sent_to_count | `int` |
| sent_by | `UUID` |
| sent_at | `datetime` |

### `fee_penalties` (FeePenalty)

| Column | Type |
|--------|------|
| fee_record_id | `UUID` |
| penalty_type | `str` |
| amount | `Decimal` |
| percentage | `Decimal?` |
| applied_on | `datetime` |
| applied_by | `UUID` |

## Leave

### `leave_policies` (LeavePolicy)

| Column | Type |
|--------|------|
| academic_year_id | `UUID` |
| leave_type | `str` |
| display_name | `str?` |
| code | `str?` |
| total_per_year | `int` |
| carry_forward | `bool` |
| max_carry_forward | `int?` |
| max_consecutive_days | `int?` |
| requires_approval | `bool` |
| half_day_allowed | `bool` |
| medical_certificate_required_after_days | `int?` |
| advance_notice_days | `int?` |
| applicable_to | `str?` |
| members | `list?` |

### `leave_applications` (LeaveApplication)

| Column | Type |
|--------|------|
| academic_year_id | `UUID` |
| staff_id | `UUID` |
| leave_type | `str` |
| from_date | `date` |
| to_date | `date` |
| days | `Decimal` |
| is_half_day | `bool` |
| reason | `str` |
| status | `str` |
| applied_on | `datetime` |
| approved_by | `UUID?` |
| approved_on | `datetime?` |
| rejected_by | `UUID?` |
| rejected_on | `datetime?` |
| remarks | `str?` |
| substitute_teacher_id | `UUID?` |
| cancelled_on | `datetime?` |

### `leave_balances` (LeaveBalance)

| Column | Type |
|--------|------|
| academic_year_id | `UUID` |
| staff_id | `UUID` |
| leave_type | `str` |
| total_allocated | `int` |
| carried_forward | `int` |
| used | `Decimal` |
| pending | `Decimal` |

## Library

### `library_books` (Book)

| Column | Type |
|--------|------|
| title | `str` |
| author | `str?` |
| isbn | `str?` |
| category | `str?` |
| publisher | `str?` |
| total_copies | `int` |
| available_copies | `int` |
| shelf_location | `str?` |
| status | `str` |

### `library_issues` (BookIssue)

| Column | Type |
|--------|------|
| book_id | `UUID` |
| borrower_id | `UUID` |
| borrower_type | `str` |
| issue_date | `date` |
| due_date | `date` |
| return_date | `date?` |
| fine_amount | `float` |
| status | `str` |

## Meeting

### `parent_meetings` (ParentMeeting)

| Column | Type |
|--------|------|
| academic_year_id | `UUID` |
| student_id | `UUID` |
| meeting_date | `date` |
| meeting_time | `time?` |
| conducted_by | `UUID` |
| parent_id | `UUID?` |
| attendees | `dict` |
| agenda | `str?` |
| discussion_notes | `str?` |
| action_items | `dict` |
| next_meeting_date | `date?` |
| status | `str` |
| meeting_type | `str?` |
| follow_up_required | `bool` |
| parent_attended | `bool` |
| remarks | `str?` |

## Notification

### `notifications` (Notification)

| Column | Type |
|--------|------|
| title | `str` |
| message | `str` |
| type | `str?` |
| target_type | `str` |
| target_class_name | `str?` |
| target_section | `str?` |
| send_via | `str` |
| status | `str` |
| scheduled_at | `datetime?` |
| sent_at | `datetime?` |
| archived_at | `datetime?` |
| recipients_count | `int` |
| read_count | `int` |
| created_by_user_id | `UUID?` |

### `notification_recipients` (NotificationRecipient)

| Column | Type |
|--------|------|
| notification_id | `UUID` |
| user_id | `UUID` |
| is_read | `bool` |
| read_at | `datetime?` |

## Payroll

### `salary_structures` (SalaryStructure)

| Column | Type |
|--------|------|
| staff_id | `UUID` |
| academic_year_id | `UUID` |
| basic_salary | `Decimal` |
| hra | `Decimal` |
| da | `Decimal` |
| transport_allowance | `Decimal` |
| medical_allowance | `Decimal` |
| other_allowances | `dict` |
| pf_deduction | `Decimal` |
| professional_tax | `Decimal` |
| tds | `Decimal` |
| other_deductions | `dict` |
| net_salary | `Decimal` |
| effective_from | `date` |

### `payslips` (Payslip)

| Column | Type |
|--------|------|
| staff_id | `UUID` |
| academic_year_id | `UUID` |
| month | `int` |
| year | `int` |
| basic_salary | `Decimal` |
| hra | `Decimal` |
| da | `Decimal` |
| transport_allowance | `Decimal` |
| total_allowances | `Decimal` |
| total_deductions | `Decimal` |
| net_salary | `Decimal` |
| paid_amount | `Decimal` |
| working_days | `int` |
| total_days | `int` |
| status | `str` |
| paid_on | `date?` |
| payment_method | `str?` |
| reference | `str?` |
| notes | `str?` |
| payment_history | `list?` |
| generated_at | `datetime` |
| generated_by | `UUID?` |

### `salary_advances` (SalaryAdvance)

| Column | Type |
|--------|------|
| staff_id | `UUID` |
| amount | `Decimal` |
| reason | `str?` |
| recovery_months | `int?` |
| per_month_deduction | `Decimal?` |
| status | `str` |
| applied_on | `datetime` |
| approved_by | `UUID?` |
| approved_on | `datetime?` |
| rejected_by | `UUID?` |
| remarks | `str?` |
| disbursed_on | `datetime?` |

### `salary_revisions` (SalaryRevision)

| Column | Type |
|--------|------|
| staff_id | `UUID` |
| academic_year_id | `UUID` |
| effective_date | `date` |
| previous_basic | `Decimal` |
| new_basic | `Decimal` |
| revision_type | `str` |
| percentage | `Decimal?` |
| increment_amount | `Decimal?` |
| approved_by | `UUID?` |
| approved_on | `datetime?` |
| remarks | `str?` |

## Platform_Settings

### `platform_settings` (PlatformSettings)

| Column | Type |
|--------|------|
| key | `str` |
| value | `str` |
| updated_at | `datetime` |

## Staff

### `staff` (Staff)

| Column | Type |
|--------|------|
| employee_id | `str` |
| first_name | `str` |
| last_name | `str?` |
| full_name | `str` |
| email | `str` |
| phone | `str?` |
| alternate_phone | `str?` |
| gender | `str?` |
| date_of_birth | `date?` |
| photo_url | `str?` |
| department | `str?` |
| designation | `str?` |
| employment_type | `str?` |
| joining_date | `date?` |
| left_date | `date?` |
| left_reason | `str?` |
| qualification | `str?` |
| experience_years | `Decimal?` |
| address_line1 | `str?` |
| address_line2 | `str?` |
| city | `str?` |
| state | `str?` |
| pincode | `str?` |
| blood_group | `str?` |
| emergency_contact_name | `str?` |
| emergency_contact_phone | `str?` |
| emergency_contact_relationship | `str?` |
| bank_name | `str?` |
| bank_account_number | `str?` |
| bank_ifsc | `str?` |
| pan_number | `str?` |
| aadhar_number | `str?` |
| is_teacher | `bool` |
| primary_subject_id | `UUID?` |
| max_workload_hours | `int?` |
| salary | `Decimal?` |
| status | `str` |
| user_id | `UUID?` |

### `staff_subjects` (StaffSubject)

| Column | Type |
|--------|------|
| staff_id | `UUID` |
| subject_id | `UUID` |
| is_primary | `bool` |
| subject | `Subject` |

### `class_assignments` (ClassAssignment)

| Column | Type |
|--------|------|
| staff_id | `UUID` |
| class_section_id | `UUID` |
| subject_id | `UUID?` |
| academic_year_id | `UUID` |
| is_class_teacher | `bool` |
| periods_per_week | `int?` |
| status | `str` |
| end_date | `date?` |
| end_reason | `str?` |
| subject | `Subject` |

## Student

### `students` (Student)

| Column | Type |
|--------|------|
| admission_number | `str` |
| first_name | `str` |
| last_name | `str?` |
| full_name | `str` |
| email | `str?` |
| phone | `str?` |
| gender | `str?` |
| date_of_birth | `date?` |
| photo_url | `str?` |
| blood_group | `str?` |
| nationality | `str?` |
| religion | `str?` |
| caste | `str?` |
| mother_tongue | `str?` |
| medical_conditions | `str?` |
| allergies | `str?` |
| address_line1 | `str?` |
| address_line2 | `str?` |
| city | `str?` |
| state | `str?` |
| pincode | `str?` |
| admission_date | `date?` |
| left_date | `date?` |
| left_reason | `str?` |
| previous_school | `str?` |
| transfer_certificate_number | `str?` |
| status | `str` |
| aadhar_number | `str?` |

### `student_enrollments` (StudentEnrollment)

| Column | Type |
|--------|------|
| academic_year_id | `UUID` |
| student_id | `UUID` |
| class_section_id | `UUID` |
| roll_number | `str?` |
| enrollment_date | `date?` |
| status | `str` |

### `parents` (Parent)

| Column | Type |
|--------|------|
| first_name | `str` |
| last_name | `str?` |
| full_name | `str` |
| relation | `str` |
| email | `str?` |
| phone | `str?` |
| alternate_phone | `str?` |
| occupation | `str?` |
| annual_income | `str?` |
| address_line1 | `str?` |
| address_line2 | `str?` |
| city | `str?` |
| state | `str?` |
| pincode | `str?` |
| aadhar_number | `str?` |
| is_primary_contact | `bool` |

### `student_parents` (StudentParent)

| Column | Type |
|--------|------|
| student_id | `UUID` |
| parent_id | `UUID` |

### `student_mentors` (StudentMentor)

| Column | Type |
|--------|------|
| academic_year_id | `UUID` |
| student_id | `UUID` |
| staff_id | `UUID` |
| assigned_date | `date?` |
| notes | `str?` |

## Subscription

### `subscriptions` (Subscription)

| Column | Type |
|--------|------|
| id | `UUID` |
| school_id | `UUID` |
| plan_type | `str` |
| amount | `Decimal` |
| start_date | `date` |
| end_date | `date` |
| auto_renew | `bool` |
| is_active | `bool` |

### `subscription_payments` (SubscriptionPayment)

| Column | Type |
|--------|------|
| id | `UUID` |
| subscription_id | `UUID` |
| school_id | `UUID` |
| amount | `Decimal` |
| payment_date | `date` |
| period_start | `date` |
| period_end | `date` |
| status | `str` |
| notes | `str?` |
| subscription | `Subscription` |

## Timetable

### `period_configs` (PeriodConfig)

| Column | Type |
|--------|------|
| academic_year_id | `UUID` |
| name | `str?` |
| start_time | `time` |
| end_time | `time` |
| duration_minutes | `int?` |
| is_break | `bool` |
| sort_order | `int` |

### `timetable_slots` (TimetableSlot)

| Column | Type |
|--------|------|
| academic_year_id | `UUID` |
| class_section_id | `UUID` |
| period_config_id | `UUID` |
| day_of_week | `str` |
| subject_id | `UUID?` |
| staff_id | `UUID?` |
| slot_type | `str` |
| period_config | `PeriodConfig` |
| subject | `Subject?` |

## Transport

### `vehicles` (Vehicle)

| Column | Type |
|--------|------|
| vehicle_number | `str` |
| plate_number | `str?` |
| type | `str` |
| model | `str?` |
| year | `int?` |
| fuel_type | `str?` |
| capacity | `int` |
| occupied_seats | `int` |
| status | `str` |
| next_service_date | `date?` |
| insurance_expiry | `date?` |
| fitness_expiry | `date?` |

### `drivers` (Driver)

| Column | Type |
|--------|------|
| driver_id | `str` |
| full_name | `str` |
| phone | `str` |
| email | `str?` |
| license_number | `str` |
| license_type | `str?` |
| license_expiry | `date?` |
| experience_years | `int?` |
| join_date | `date?` |
| status | `str` |
| emergency_contact_name | `str?` |
| emergency_contact_phone | `str?` |

### `helpers` (Helper)

| Column | Type |
|--------|------|
| helper_id | `str` |
| full_name | `str` |
| phone | `str` |
| join_date | `date?` |
| status | `str` |

### `routes` (Route)

| Column | Type |
|--------|------|
| route_code | `str` |
| name | `str` |
| area | `str?` |
| shift | `str?` |
| stops | `dict` |
| distance_km | `float?` |
| start_time | `time?` |
| end_time | `time?` |
| status | `str` |

### `route_assignments` (RouteAssignment)

| Column | Type |
|--------|------|
| route_id | `UUID` |
| vehicle_id | `UUID` |
| driver_id | `UUID` |
| helper_id | `UUID?` |
| status | `str` |

### `student_transport` (StudentTransport)

| Column | Type |
|--------|------|
| student_id | `UUID` |
| route_id | `UUID` |
| academic_year_id | `UUID` |
| pickup_point | `str?` |
| drop_point | `str?` |
