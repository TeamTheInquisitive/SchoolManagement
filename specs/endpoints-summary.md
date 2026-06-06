# API Endpoints Summary

**Total Endpoints: 327** | **Last Updated: 2026-06-06**

## Auth (8 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/auth/login | Login with email/password |
| POST | /api/v1/auth/logout | Logout |
| GET | /api/v1/auth/me | Current user profile |
| POST | /api/v1/auth/refresh-token | Refresh JWT |
| POST | /api/v1/auth/change-password | Change own password |
| POST | /api/v1/auth/forgot-password | Initiate reset |
| POST | /api/v1/auth/reset-password | Reset with token |
| GET | /api/v1/auth/school-profile | School info (any auth user) |

## Admin - Students (25 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/students | List (paginated, filtered by status/class/section/search) |
| POST | /admin/students | Create student + user account |
| POST | /admin/students/bulk-import | CSV import |
| POST | /admin/students/bulk-import-json | JSON bulk import |
| GET | /admin/students/export | Export CSV |
| GET | /admin/students/{id} | Detail with stats (attendance%, grade avg, fee due) |
| PUT | /admin/students/{id} | Update |
| DELETE | /admin/students/{id} | Soft-delete |
| GET | /admin/students/{id}/exam-results | Exam results grouped by exam |
| GET | /admin/students/{id}/fee-history | Fee structure + payment transactions |
| GET | /admin/students/{id}/activities | Activities + Awards |
| POST | /admin/students/{id}/activities | Create activity |
| PUT | /admin/students/{id}/activities/{aid} | Update activity |
| DELETE | /admin/students/{id}/activities/{aid} | Delete activity |
| POST | /admin/students/{id}/awards | Create award |
| PUT | /admin/students/{id}/awards/{aid} | Update award |
| DELETE | /admin/students/{id}/awards/{aid} | Delete award |
| GET | /admin/students/{id}/disciplinary-records | List records |
| POST | /admin/students/{id}/disciplinary-records | Create |
| PUT | /admin/students/{id}/disciplinary-records/{rid} | Update |
| DELETE | /admin/students/{id}/disciplinary-records/{rid} | Delete |
| GET | /admin/students/{id}/parent-meetings | List meetings |
| POST | /admin/students/{id}/parent-meetings | Create |
| PUT | /admin/students/{id}/parent-meetings/{mid} | Update |
| DELETE | /admin/students/{id}/parent-meetings/{mid} | Delete |
| POST | /admin/students/{id}/reset-password | Reset/create password |

## Admin - Teachers (18 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/teachers | List (paginated) |
| POST | /admin/teachers | Create teacher + user + salary |
| POST | /admin/teachers/bulk-import | JSON bulk import |
| GET | /admin/teachers/by-class | Teachers by class |
| GET | /admin/teachers/export | Export CSV |
| GET | /admin/teachers/{id} | Detail + leave balances + awards |
| PUT | /admin/teachers/{id} | Update all fields + salary |
| DELETE | /admin/teachers/{id} | Soft-delete |
| POST | /admin/teachers/{id}/assign-class | Assign class/subject/class-teacher |
| GET | /admin/teachers/{id}/assignments | Class assignments |
| GET | /admin/teachers/{id}/awards | List awards |
| POST | /admin/teachers/{id}/awards | Create award |
| PUT | /admin/teachers/{id}/awards/{aid} | Update award |
| DELETE | /admin/teachers/{id}/awards/{aid} | Delete award |
| POST | /admin/teachers/{id}/bulk-assign | Bulk assign classes |
| DELETE | /admin/teachers/{id}/class-assignment/{aid} | Remove assignment |
| GET | /admin/teachers/{id}/history | Teacher history |
| POST | /admin/teachers/{id}/reset-password | Reset password |

## Admin - Fees (14 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/fees | List grouped by student |
| POST | /admin/fees | Create fee record |
| GET | /admin/fees/export | Export CSV |
| POST | /admin/fees/generate-due | Generate dues |
| POST | /admin/fees/send-reminder | Send reminders |
| POST | /admin/fees/bulk-apply-late-fees | Bulk late fees |
| GET | /admin/fees/student/{id} | Student fee components |
| GET | /admin/fees/student/{id}/receipt | Consolidated receipt |
| GET | /admin/fees/{id} | Fee record detail + payment history |
| PUT | /admin/fees/{id} | Update fee record |
| POST | /admin/fees/{id}/record-payment | Record payment |
| POST | /admin/fees/{id}/apply-late-fee | Apply late fee |
| GET | /admin/fees/{id}/receipt | Fee receipt |

## Admin - Staff & Payroll (16 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/staff | List staff |
| POST | /admin/staff | Create staff |
| GET | /admin/staff/export | Export |
| PUT | /admin/staff/{id} | Update |
| DELETE | /admin/staff/{id} | Delete |
| GET | /admin/staff/payroll | Get payslips (month/year) |
| POST | /admin/staff/payroll/run | Generate payroll |
| POST | /admin/staff/payroll/mark-all-paid | Bulk mark paid |
| PUT | /admin/staff/payroll/{id} | Update payslip components |
| POST | /admin/staff/payroll/{id}/pay | Record payment |
| GET | /admin/staff/payroll/salary-structure/{id} | Get salary |
| PUT | /admin/staff/payroll/salary-structure/{id} | Update salary |
| GET | /admin/staff/payroll/salary-revisions/{id} | Revision history |
| POST | /admin/staff/payroll/salary-revisions | Create revision |
| GET | /admin/staff/salary-advances | List advances |
| POST | /admin/staff/salary-advances | Create advance |

## Admin - Settings (20 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET/PUT | /admin/settings | General settings |
| GET/PUT | /admin/settings/school-profile | School profile |
| GET/PUT | /admin/settings/academic-year | Current year |
| CRUD | /admin/settings/academic-years | Academic years |
| GET | /admin/settings/class-sections | Classes + sections |
| POST | /admin/settings/classes/bulk | Bulk create classes |
| POST | /admin/settings/sections/bulk | Bulk create sections |
| CRUD | /admin/settings/subjects | Subjects |
| GET/PUT | /admin/settings/class-subjects | Class-subject mapping |
| CRUD | /admin/settings/fee-structures | Fee structures |
| GET/PUT | /admin/settings/id-generation | ID config |
| GET | /admin/settings/next-id?type= | Generate next ID |
| POST | /admin/settings/upload-logo | Upload logo |

## Admin - Examinations (12 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/examinations | List (paginated by exam name groups) |
| POST | /admin/examinations | Create exam |
| GET/PUT | /admin/examinations/grade-system | Grade config |
| GET/PUT/DELETE | /admin/examinations/{id} | Exam CRUD |
| POST | /admin/examinations/{id}/publish | Publish results |
| GET/POST | /admin/examinations/{id}/results | Results CRUD |
| POST | /admin/examinations/{id}/results/bulk-upload | Bulk upload |

## Admin - Attendance (3 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/attendance | Get attendance (class + date) |
| POST | /admin/attendance | Submit attendance |
| PUT | /admin/attendance | Update attendance |

## Admin - Leaves (9 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/leaves | List applications |
| GET/PUT | /admin/leaves/policy | Leave policy |
| POST | /admin/leaves/allocate | Allocate to staff |
| GET | /admin/leaves/balances | All balances |
| POST | /admin/leaves/{id}/approve | Approve |
| POST | /admin/leaves/{id}/reject | Reject |
| POST | /admin/leaves/{id}/cancel | Cancel |

## Admin - Transport (18 endpoints)
Full CRUD for vehicles, drivers, helpers, routes, assignments + stats + exports.

## Admin - Timetable (10 endpoints)
Periods CRUD, slots CRUD, bulk-assign, teacher-availability, conflicts.

## Admin - Dashboard (8 endpoints)
Stats, attendance-trends, fee-collection, student-distribution, recent-activities, leave-overview, low-attendance, subscription-banner.

## Teacher Module (40+ endpoints)
Attendance, assignments, grades, leaves, students, timetable, dashboard, notifications.

## Student Module (30+ endpoints)
Profile, attendance, assignments, fees, results, timetable, library, notifications, dashboard.

## SuperAdmin (15 endpoints)
Schools CRUD, subscriptions, payments, settings, users.


---

## Recent Additions (2026-06-06)

**Total Endpoints: 332**

### New Endpoints Added:

| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/students/{id}/attendance?month=X&year=Y | Student monthly attendance records |
| GET | /admin/settings/holidays | Get holidays (seeds defaults for new schools) |
| PUT | /admin/settings/holidays | Update holidays list |
| POST | /admin/staff/payroll/undo-all-paid | Bulk undo all paid payslips for month |
| POST | /admin/mentoring/shuffle-assign | Shuffle all students & auto-assign evenly across teachers |
| GET | /admin/teachers/{id}/awards | List teacher awards |
| POST | /admin/teachers/{id}/awards | Create teacher award |
| PUT | /admin/teachers/{id}/awards/{aid} | Update teacher award |
| DELETE | /admin/teachers/{id}/awards/{aid} | Delete teacher award |
| POST | /admin/students/{id}/activities | Create activity |
| PUT | /admin/students/{id}/activities/{aid} | Update activity |
| DELETE | /admin/students/{id}/activities/{aid} | Delete activity |
| POST | /admin/students/{id}/awards | Create student award |
| PUT | /admin/students/{id}/awards/{aid} | Update award |
| DELETE | /admin/students/{id}/awards/{aid} | Delete award |
| POST | /admin/students/{id}/disciplinary-records | Create record |
| PUT | /admin/students/{id}/disciplinary-records/{rid} | Update record |
| DELETE | /admin/students/{id}/disciplinary-records/{rid} | Delete record |
| POST | /admin/students/{id}/parent-meetings | Create meeting |
| PUT | /admin/students/{id}/parent-meetings/{mid} | Update meeting |
| DELETE | /admin/students/{id}/parent-meetings/{mid} | Delete meeting |

### New Features:
- **Holidays Management** — Admin can configure holidays per academic year (default Indian public holidays seeded)
- **Payroll Undo** — Bulk undo all paid payslips back to unpaid
- **Payroll Working Days** — Admin sets working days during payroll processing (stored per payslip)
- **Student Attendance Calendar** — Monthly view with color-coded days, stats, pie chart
- **Mentoring Shuffle & Auto Assign** — Randomly distributes all students evenly across all teachers
- **Student CRUD Sections** — Full CRUD for Activities, Awards, Disciplinary Records, Parent Meetings
- **Teacher Awards CRUD** — Awards stored in staff metadata
- **New Admissions Page** — Track new student admissions with token advance
- **ID Auto-Generation** — Configurable patterns (STU260001, TCH260001)

### Data Model Changes:
- `payslips` — Added `working_days` (int), `total_days` (int), `hra`, `da`, `transport_allowance`, `paid_amount` columns
- `leave_policies` — Added `display_name`, `applicable_to`, `members` columns
- `class_assignments` — `subject_id` made nullable (for class teacher without subject)
- `attendance_sessions` — `submitted_by` made nullable (admin submissions)
- `grade_scales` — `description` changed from VARCHAR(100) to TEXT
- `staff` — Added `emergency_contact_relationship` column
- `users` — Added `password_changed` column
