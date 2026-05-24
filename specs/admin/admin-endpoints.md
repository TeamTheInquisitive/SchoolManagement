# School ERP Backend - API Endpoints

## Architecture Overview

```
Tech Stack (Recommended):
├── Runtime: Node.js / Python (Django/FastAPI)
├── Database: MySQL
├── Auth: JWT (httpOnly cookies) + Refresh Token rotation
├── Multi-tenancy: School code in header → DB schema/filter
├── API Style: RESTful, JSON
└── Base URL: /api/v1
```

### Forward & Backward Compatibility Principles

These rules apply across ALL modules and endpoints:

1. **`metadata` field on every entity** — Every model includes a `metadata: {}` JSON field. Future features (e.g., online exam proctoring, biometric attendance, parent app integration) can store data here without schema migrations or breaking existing clients.

2. **Additive-only API changes** — New fields are always optional and nullable. Existing fields are never removed or renamed. Clients that don't know about new fields simply ignore them.

3. **Versioned API path (`/api/v1/`)** — If a breaking change is ever needed, deploy it under `/api/v2/` while keeping `/api/v1/` alive. Both versions coexist.

4. **Configurable enums, not hardcoded** — Exam types, leave types, fee types, notification types, grade scales, departments, designations are all stored in config tables. Admin can add new values via API without code changes.

5. **Soft deletes everywhere** — No data is ever permanently removed. Every entity has `is_active`, `status`, and a deactivation timestamp. Allows full audit trail and rollback.

6. **Pagination on all list endpoints** — All lists support `page` + `page_size`. Responses always include `count`, `total_pages`. This ensures the API works at any scale.

7. **Filter parameters are always optional** — Omitting a filter returns all records (of that scope). Adding new filter params in the future won't break existing queries.

8. **ISO 8601 dates everywhere** — All date/time fields use `YYYY-MM-DD` or `YYYY-MM-DDTHH:mm:ssZ`. Never locale-specific formats.

9. **UUIDs as primary keys** — Avoids collision across schools, allows safe cross-system references, and is merge-friendly if schools consolidate.

10. **Idempotent operations** — PUT and DELETE are idempotent. Calling them multiple times produces the same result. POST endpoints that create resources return 409 on duplicates rather than creating duplicates.

### Multi-Tenancy

Every request includes `X-School-Code` header. The backend resolves the school context from this header and scopes all queries to that school.

### Authentication

- Access token: short-lived (15 min), stored in httpOnly cookie
- Refresh token: long-lived (7 days), stored in httpOnly cookie
- On 401, client calls `/auth/refresh-token/` automatically

### Soft Delete & Active Flag Convention

All DELETE operations across the application are **soft deletes**. No data is ever permanently removed.

Every entity that supports deletion includes these fields in responses:

| Field | Type | Description |
|-------|------|-------------|
| `is_active` | boolean | `true` = currently active, `false` = deactivated/former |
| `status` | string | Human-readable status: `Active`, `Inactive`, `Alumni`, `Archived` |
| `left_date` / `deactivated_on` / `archived_on` | string (date) | When the record was deactivated (null if active) |
| `left_reason` / `reason` | string | Why the record was deactivated (null if active) |

**Frontend usage:** When displaying a record where `is_active === false`, show a visual indicator (badge, greyed-out row, "Former" tag) so admins can clearly distinguish active vs. inactive records.

**Default behavior:** All list endpoints return only active records by default. Use `?include_inactive=true` or `?status=Inactive` to retrieve deactivated records.

---

## Database Models (High-Level)

```
School, User, Staff, Student, Parent
ClassSection, Subject, AcademicYear
Attendance, Exam, ExamResult
Leave, Timetable, FeeStructure, FeePayment
Book, BookIssue
Vehicle, Driver, Helper, Route, RouteAssignment
Notification, Activity, SalaryStructure, Payslip, SalaryAdvance
```

### Academic Year Scoping

> **IMPORTANT FOR ALL MODULES:**
>
> Everything operational is scoped to an **academic year**. The academic year is the top-level filter that partitions transactional data.
>
> **What is scoped to academic year:**
> - Students → class/section enrollment (a student is in 10-A for AY 2025-2026, promoted to 11-A for 2026-2027)
> - Teachers → class assignments, workload, privileges (reassigned each year)
> - Leaves → leave balance, leave history (resets/carries over per year)
> - Timetable → entire timetable is per academic year (rebuilt each year)
> - Exams → all exams, results, report cards belong to an academic year
> - Fees → fee assignments, payments, dues are per academic year
> - Staff → salary structure can change per year
> - Payroll → payslips are year/month scoped
>
> **What is NOT scoped (basic/permanent details):**
> - Student profile (name, DOB, parent info, medical, address)
> - Staff/Teacher profile (name, email, phone, qualification, joining_date)
> - Vehicle, Driver, Route master data
> - Book catalog
> - School settings
>
> **How it works:**
> - Every transactional table has an `academic_year` column (e.g., `"2025-2026"`)
> - The "current" academic year is set in Settings → all queries default to it
> - Admin can switch academic year to view historical data
> - All list APIs accept `?academic_year=2025-2026` param (defaults to current if omitted)
> - At year rollover: students get promoted, leaves reset, timetable is rebuilt, new fee dues are generated — old year data is preserved and queryable

---

### Key Relationship: Staff → Teacher

> **IMPORTANT FOR MODELLING:**
>
> `Teacher` is NOT a separate table — it is derived from `Staff`.
> A Teacher is a Staff member with `department = 'Teaching'` (or a role flag like `is_teacher = true`).
>
> **Inheritance model:**
> ```
> Staff (base)
>   ├── employee_id, full_name, email, phone, department, designation,
>   │   employment_type, joining_date, left_date, salary, status, is_active
>   │
>   └── Teacher (extension / same table with extra fields)
>         ├── subjects[] (qualified subjects)
>         ├── primary_subject
>         ├── qualification
>         ├── max_workload_hours
>         ├── class_assignments[] (FK → ClassAssignment)
>         └── is_class_teacher_of[]
> ```
>
> **Implementation options:**
> 1. **Single table (recommended):** `staff` table with nullable teacher-specific columns. Filter by `department = 'Teaching'` or `is_teacher = true` to get teachers.
> 2. **Joined table:** `staff` base + `teacher_profile` extension table (1:1 FK to staff).
>
> **Why this matters:**
> - Payroll, leaves, salary advances all reference `staff_id` — teachers share the same payroll/leave system as non-teaching staff.
> - Teacher-specific features (class assignments, privileges, timetable, exams) reference the same `staff_id` with teacher extensions.
> - When a teacher is listed in Staff Directory, they appear as any other staff member. When viewed in Teachers module, their teaching-specific data (subjects, assignments) is shown additionally.
> - `employee_id` is shared: EMP001 is the same person in Staff and Teachers modules.

---

## Request Headers

| Header | Description | Required |
|--------|-------------|----------|
| `Content-Type` | `application/json` | Yes |
| `X-School-Code` | School tenant identifier | Yes (except /auth/login/) |
| `Cookie` | httpOnly auth cookies (sent automatically) | Yes (after login) |

## Pagination Convention

All list endpoints support pagination:

| Param | Default | Description |
|-------|---------|-------------|
| `page` | 1 | Page number |
| `page_size` | 20 | Items per page (max 100) |

Response includes: `count`, `page`, `page_size`, `total_pages`, `results[]`

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200  | Success / Soft-delete successful |
| 201  | Created |
| 207  | Partial success (bulk operations) |
| 400  | Bad Request (validation error) |
| 401  | Unauthorized (not logged in / token expired) |
| 403  | Forbidden (insufficient permissions) |
| 404  | Not Found |
| 409  | Conflict (e.g., timetable conflict, duplicate entry) |
| 422  | Unprocessable Entity |
| 500  | Internal Server Error |

## Error Response Format

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {
    "field_name": ["Field-specific error messages"]
  }
}
```

---

## All Endpoints (143 V1 + 9 V2 = 152 total)

---

### Auth (7)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login/` | Login with email/password |
| POST | `/api/v1/auth/refresh-token/` | Refresh access token |
| GET | `/api/v1/auth/me/` | Get current user profile |
| POST | `/api/v1/auth/logout/` | Logout and clear cookies |
| POST | `/api/v1/auth/forgot-password/` | Send password reset email |
| POST | `/api/v1/auth/reset-password/` | Reset password via token |
| POST | `/api/v1/auth/change-password/` | Change password (authenticated) |

### Dashboard (7)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/dashboard/stats/` | KPI summary cards |
| GET | `/api/v1/admin/dashboard/attendance-trends/` | Monthly attendance chart data |
| GET | `/api/v1/admin/dashboard/fee-collection-status/` | Fee pie chart data |
| GET | `/api/v1/admin/dashboard/student-distribution/` | Class/gender bar chart data |
| GET | `/api/v1/admin/dashboard/recent-activities/` | Recent activity feed |
| GET | `/api/v1/admin/dashboard/leave-overview/` | Teacher leave summary + pending |
| GET | `/api/v1/admin/dashboard/low-attendance/` | Low attendance alerts |

### Students (12)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/students/` | List students (filtered, paginated) |
| POST | `/api/v1/admin/students/` | Create student |
| GET | `/api/v1/admin/students/:id/` | Get student full details |
| PUT | `/api/v1/admin/students/:id/` | Update student |
| DELETE | `/api/v1/admin/students/:id/` | Soft-delete student |
| GET | `/api/v1/admin/students/:id/exam-results/` | Student exam results + trends |
| GET | `/api/v1/admin/students/:id/parent-meetings/` | Meeting history |
| GET | `/api/v1/admin/students/:id/activities/` | Activities + awards |
| GET | `/api/v1/admin/students/:id/fee-history/` | Fee structure + payments |
| GET | `/api/v1/admin/students/:id/disciplinary-records/` | Disciplinary records |
| GET | `/api/v1/admin/students/export/` | Export CSV |
| POST | `/api/v1/admin/students/bulk-import/` | Bulk import via CSV |

### Teachers (12)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/teachers/` | List teachers (multi-class, multi-subject) |
| POST | `/api/v1/admin/teachers/` | Create teacher (subjects array) |
| GET | `/api/v1/admin/teachers/:id/` | Get teacher full profile + all assignments |
| PUT | `/api/v1/admin/teachers/:id/` | Update teacher |
| DELETE | `/api/v1/admin/teachers/:id/` | Soft-delete teacher (preserves history) |
| POST | `/api/v1/admin/teachers/:id/assign-class/` | Assign one class-subject combo |
| POST | `/api/v1/admin/teachers/:id/bulk-assign/` | Assign multiple classes at once |
| GET | `/api/v1/admin/teachers/:id/assignments/` | List all assignments for a teacher |
| DELETE | `/api/v1/admin/teachers/:id/class-assignment/:assignment_id/` | Soft-remove assignment (preserves history) |
| GET | `/api/v1/admin/teachers/export/` | Export CSV |
| GET | `/api/v1/admin/teachers/by-class/` | Get teachers for a class/section |
| GET | `/api/v1/admin/teachers/:id/history/` | Get teacher's historical records |

### Leaves (10)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/leaves/` | List all leave applications (filtered) |
| GET | `/api/v1/admin/leaves/teacher/:teacher_id/` | Teacher-wise balance + history |
| GET | `/api/v1/admin/leaves/balances/` | All teachers' leave balances overview |
| GET | `/api/v1/admin/leaves/policy/` | Get leave policy config |
| PUT | `/api/v1/admin/leaves/policy/` | Update leave policy |
| POST | `/api/v1/admin/leaves/:id/approve/` | Approve leave (+ assign substitute) |
| POST | `/api/v1/admin/leaves/:id/reject/` | Reject leave |
| POST | `/api/v1/admin/leaves/:id/cancel/` | Cancel approved leave |
| POST | `/api/v1/admin/leaves/bulk-action/` | Bulk approve/reject |
| GET | `/api/v1/admin/leaves/calendar/` | Calendar view (who's on leave when) |

### Timetable (11)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/timetable/periods/` | Get period configuration (time slots) |
| POST | `/api/v1/admin/timetable/periods/` | Add new period |
| PUT | `/api/v1/admin/timetable/periods/:id/` | Update period timing |
| DELETE | `/api/v1/admin/timetable/periods/:id/` | Soft-delete period |
| GET | `/api/v1/admin/timetable/` | Get full timetable grid for class/section |
| POST | `/api/v1/admin/timetable/slot/` | Assign subject+teacher to a slot |
| PUT | `/api/v1/admin/timetable/slot/:id/` | Update a slot assignment |
| DELETE | `/api/v1/admin/timetable/slot/:id/` | Clear a slot |
| POST | `/api/v1/admin/timetable/bulk-assign/` | Bulk assign multiple slots |
| GET | `/api/v1/admin/timetable/teacher/:teacher_id/` | Get teacher's weekly schedule |
| GET | `/api/v1/admin/timetable/conflicts/` | Detect scheduling conflicts |

### Examinations (16)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/examinations/` | List exams (filtered, paginated) |
| POST | `/api/v1/admin/examinations/` | Create exam |
| GET | `/api/v1/admin/examinations/:id/` | Get exam details + summary |
| PUT | `/api/v1/admin/examinations/:id/` | Update exam |
| DELETE | `/api/v1/admin/examinations/:id/` | Soft-delete (cancel) exam |
| GET | `/api/v1/admin/examinations/:id/results/` | Get all results for an exam |
| POST | `/api/v1/admin/examinations/:id/results/` | Enter results (single/bulk) |
| POST | `/api/v1/admin/examinations/:id/results/bulk-upload/` | Upload results via CSV |
| PUT | `/api/v1/admin/examinations/:id/results/:result_id/` | Update a student's result |
| POST | `/api/v1/admin/examinations/:id/publish/` | Publish results + notify |
| GET | `/api/v1/admin/examinations/grade-system/` | Get grade scale config |
| PUT | `/api/v1/admin/examinations/grade-system/` | Update grade scale |
| GET | `/api/v1/admin/examinations/analytics/` | Class/subject performance analytics |
| GET | `/api/v1/admin/examinations/report-card/:student_id/` | Get student report card |
| POST | `/api/v1/admin/examinations/report-card/generate/` | Batch generate report cards |
| GET | `/api/v1/admin/examinations/schedule/` | Get exam timetable for a class |

### Fees (12)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/fees/` | List fee records (filter: status, class, fee_type) |
| GET | `/api/v1/admin/fees/:id/` | Get fee record + payment history |
| POST | `/api/v1/admin/fees/` | Create fee record (assign to student) |
| POST | `/api/v1/admin/fees/generate-due/` | Bulk generate due fees for a class |
| POST | `/api/v1/admin/fees/:id/record-payment/` | Record payment (partial/full) |
| POST | `/api/v1/admin/fees/:id/apply-late-fee/` | Apply late fee (fixed or %) |
| POST | `/api/v1/admin/fees/bulk-apply-late-fees/` | Bulk apply late fees to overdue |
| POST | `/api/v1/admin/fees/send-reminder/` | Send fee reminders |
| GET | `/api/v1/admin/fees/:id/receipt/` | Generate receipt per fee record |
| GET | `/api/v1/admin/fees/student/:student_id/` | Student's fee records + summary |
| GET | `/api/v1/admin/fees/student/:student_id/receipt/` | Consolidated receipt per student |
| GET | `/api/v1/admin/fees/export/` | Export CSV |

### Transport (22)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/transport/stats/` | KPI summary (vehicles, drivers, routes) |
| GET | `/api/v1/admin/transport/vehicles/` | List vehicles (filter: type, status) |
| POST | `/api/v1/admin/transport/vehicles/` | Add vehicle |
| GET | `/api/v1/admin/transport/vehicles/:id/` | Get vehicle details |
| PUT | `/api/v1/admin/transport/vehicles/:id/` | Update vehicle |
| DELETE | `/api/v1/admin/transport/vehicles/:id/` | Soft-delete vehicle |
| GET | `/api/v1/admin/transport/drivers/` | List drivers (filter: status, license) |
| POST | `/api/v1/admin/transport/drivers/` | Add driver |
| PUT | `/api/v1/admin/transport/drivers/:id/` | Update driver |
| DELETE | `/api/v1/admin/transport/drivers/:id/` | Soft-delete driver |
| GET | `/api/v1/admin/transport/helpers/` | List helpers/attendants |
| POST | `/api/v1/admin/transport/helpers/` | Add helper |
| PUT | `/api/v1/admin/transport/helpers/:id/` | Update helper |
| DELETE | `/api/v1/admin/transport/helpers/:id/` | Soft-delete helper |
| GET | `/api/v1/admin/transport/routes/` | List routes |
| POST | `/api/v1/admin/transport/routes/` | Create route |
| PUT | `/api/v1/admin/transport/routes/:id/` | Update route |
| DELETE | `/api/v1/admin/transport/routes/:id/` | Soft-delete route |
| GET | `/api/v1/admin/transport/assignments/` | List operational mappings |
| POST | `/api/v1/admin/transport/assignments/` | Create assignment (route+vehicle+driver+helper) |
| PUT | `/api/v1/admin/transport/assignments/:id/` | Update assignment |
| DELETE | `/api/v1/admin/transport/assignments/:id/` | Remove assignment |
| GET | `/api/v1/admin/transport/vehicles/export/` | Export vehicles CSV |
| GET | `/api/v1/admin/transport/drivers/export/` | Export drivers CSV |

### Staff (5)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/staff/` | List staff |
| POST | `/api/v1/admin/staff/` | Create staff |
| PUT | `/api/v1/admin/staff/:id/` | Update staff |
| DELETE | `/api/v1/admin/staff/:id/` | Soft-delete staff (preserves history) |
| GET | `/api/v1/admin/staff/export/` | Export CSV |

### Payroll (6)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/payroll/` | Get payroll for month/year |
| POST | `/api/v1/admin/payroll/run/` | Run payroll generation |
| POST | `/api/v1/admin/payroll/generate-payslips/` | Generate payslip PDFs |
| GET | `/api/v1/admin/payroll/salary-structure/:employee_id/` | Get salary breakdown |
| GET | `/api/v1/admin/payroll/salary-revisions/:staff_id/` | Get salary revision history |
| POST | `/api/v1/admin/payroll/salary-revisions/` | Create salary revision/hike |

### Salary Advances (5)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/salary-advances/` | List advance requests |
| POST | `/api/v1/admin/salary-advances/` | Create advance request |
| POST | `/api/v1/admin/salary-advances/:id/approve/` | Approve advance |
| POST | `/api/v1/admin/salary-advances/:id/reject/` | Reject advance |
| POST | `/api/v1/admin/salary-advances/:id/disburse/` | Disburse advance |

### Notifications (5)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/notifications/` | List notifications |
| POST | `/api/v1/admin/notifications/` | Create/send notification |
| GET | `/api/v1/admin/notifications/:id/` | Get notification details |
| PUT | `/api/v1/admin/notifications/:id/` | Update notification |
| DELETE | `/api/v1/admin/notifications/:id/` | Soft-delete (archive) notification |

### Settings (11)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/settings/` | Get all settings (grouped by category) |
| PUT | `/api/v1/admin/settings/` | Update settings (partial update) |
| GET | `/api/v1/admin/settings/school-profile/` | Get school info (name, logo, address, contact) |
| PUT | `/api/v1/admin/settings/school-profile/` | Update school profile |
| GET | `/api/v1/admin/settings/academic-year/` | Get academic year config |
| PUT | `/api/v1/admin/settings/academic-year/` | Update academic year |
| GET | `/api/v1/admin/settings/enums/:category/` | Get configurable enum values (fee types, leave types, etc.) |
| PUT | `/api/v1/admin/settings/enums/:category/` | Add/update enum values for a category |
| POST | `/api/v1/admin/settings/classes/bulk/` | Bulk create classes |
| POST | `/api/v1/admin/settings/sections/bulk/` | Bulk create sections |
| POST | `/api/v1/admin/settings/subjects/bulk/` | Bulk create subjects |

---

### Library (9) — Moved to V2
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/library/books/` | List books (filter: category, available, search) |
| GET | `/api/v1/admin/library/books/:id/` | Get book details + current holders |
| GET | `/api/v1/admin/library/books/:id/history/` | Book's complete issue history |
| GET | `/api/v1/admin/library/issued/` | List issued books (filter: user_type, class, overdue) |
| GET | `/api/v1/admin/library/overdue/` | List overdue books + fines |
| GET | `/api/v1/admin/library/user-history/:user_id/` | Student/teacher wise borrow history |
| POST | `/api/v1/admin/library/issue/` | Issue book to student or teacher |
| POST | `/api/v1/admin/library/return/` | Return a book |
| POST | `/api/v1/admin/library/renew/` | Renew/extend due date |

---

## Summary

| Module | Endpoints | Version |
|--------|-----------|---------|
| Auth | 7 | V1 |
| Dashboard | 7 | V1 |
| Students | 12 | V1 |
| Teachers | 12 | V1 |
| Leaves | 10 | V1 |
| Timetable | 11 | V1 |
| Examinations | 16 | V1 |
| Library | 9 | **Moved to V2** |
| Fees | 12 | V1 |
| Transport | 24 | V1 |
| Staff | 5 | V1 |
| Payroll | 6 | V1 |
| Salary Advances | 5 | V1 |
| Notifications | 5 | V1 |
| Settings | 11 | V1 |
| **V1 Total** | **143** | |
| **Grand Total (incl. V2)** | **152** | |
