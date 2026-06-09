# School ERP Backend - Admin API Endpoints

## Architecture Overview

```
Tech Stack:
├── Runtime: Python (FastAPI)
├── Database: PostgreSQL
├── Auth: JWT (httpOnly cookies) + Refresh Token rotation
├── Multi-tenancy: X-School-Code header → DB schema/filter
├── API Style: RESTful, JSON
└── Base URL: /api/v1
```

### Forward & Backward Compatibility Principles

1. **`metadata` field on every entity** — Every model includes a `metadata: {}` JSON field for future extensions without schema migrations.

2. **Additive-only API changes** — New fields are always optional and nullable. Existing fields are never removed or renamed.

3. **Versioned API path (`/api/v1/`)** — Breaking changes go under `/api/v2/` while keeping `/api/v1/` alive.

4. **Configurable enums, not hardcoded** — Exam types, leave types, fee types, etc. are stored in config tables. Admin can add new values via API.

5. **Soft deletes everywhere** — No data is permanently removed. Every entity has `is_active`, `status`, and deactivation timestamp.

6. **Pagination on all list endpoints** — All lists support `page` + `page_size`. Responses include `count`, `total_pages`.

7. **Filter parameters are always optional** — Omitting a filter returns all records (of that scope).

8. **ISO 8601 dates everywhere** — `YYYY-MM-DD` or `YYYY-MM-DDTHH:mm:ssZ`.

9. **UUIDs as primary keys** — Avoids collision across schools, allows safe cross-system references.

10. **Idempotent operations** — PUT and DELETE are idempotent. POST returns 409 on duplicates.

### Multi-Tenancy

Every request includes `X-School-Code` header. The backend resolves the school context from this header.

### Authentication

- Access token: short-lived (15 min), stored in httpOnly cookie
- Refresh token: long-lived (7 days), stored in httpOnly cookie
- On 401, client calls `/auth/refresh-token` automatically

### Request Headers

| Header | Description | Required |
|--------|-------------|----------|
| `Content-Type` | `application/json` | Yes |
| `X-School-Code` | School tenant identifier | Yes (except /auth/login) |
| `Cookie` | httpOnly auth cookies | Yes (after login) |

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200  | Success |
| 201  | Created |
| 204  | No Content (successful delete) |
| 400  | Bad Request (validation error) |
| 401  | Unauthorized |
| 403  | Forbidden |
| 404  | Not Found |
| 409  | Conflict (duplicate) |
| 500  | Internal Server Error |

---

## All Endpoints (212 Admin-specific + 8 Shared Auth = 220 total)

---

### Auth — Shared (8)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | Login with email/password |
| POST | `/api/v1/auth/logout` | Logout and clear cookies |
| POST | `/api/v1/auth/refresh-token` | Refresh access token |
| GET | `/api/v1/auth/me` | Get current user profile |
| GET | `/api/v1/auth/school-profile` | Get school profile |
| POST | `/api/v1/auth/forgot-password` | Send password reset email |
| POST | `/api/v1/auth/reset-password` | Reset password via token |
| POST | `/api/v1/auth/change-password` | Change password (authenticated) |

---

### Dashboard (8)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/dashboard/stats` | KPI cards (students, teachers, classes, fee%) |
| GET | `/api/v1/admin/dashboard/attendance-trends` | Monthly attendance trend data |
| GET | `/api/v1/admin/dashboard/fee-collection-status` | Fee collection pie chart data |
| GET | `/api/v1/admin/dashboard/student-distribution` | Student distribution by class/gender |
| GET | `/api/v1/admin/dashboard/recent-activities` | Recent activity feed |
| GET | `/api/v1/admin/dashboard/leave-overview` | Leave overview with pending approvals |
| GET | `/api/v1/admin/dashboard/low-attendance` | Students with low attendance |
| GET | `/api/v1/admin/dashboard/subscription-banner` | Subscription status banner |

---

### Settings (35)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/settings` | Get all settings |
| PUT | `/api/v1/admin/settings` | Update settings |
| GET | `/api/v1/admin/settings/school-profile` | Get school profile |
| PUT | `/api/v1/admin/settings/school-profile` | Update school profile |
| GET | `/api/v1/admin/settings/academic-year` | Get current academic year |
| GET | `/api/v1/admin/settings/academic-years` | List all academic years |
| POST | `/api/v1/admin/settings/academic-years` | Create academic year |
| PUT | `/api/v1/admin/settings/academic-years/{year_id}` | Update academic year |
| DELETE | `/api/v1/admin/settings/academic-years/{year_id}` | Delete academic year |
| POST | `/api/v1/admin/settings/academic-years/{year_id}/set-current` | Set as current year |
| PUT | `/api/v1/admin/settings/academic-year` | Update academic year (legacy) |
| GET | `/api/v1/admin/settings/enums/{category}` | Get enum category values |
| PUT | `/api/v1/admin/settings/enums/{category}` | Update enum category values |
| POST | `/api/v1/admin/settings/classes/bulk` | Bulk create classes |
| POST | `/api/v1/admin/settings/sections/bulk` | Bulk create sections |
| POST | `/api/v1/admin/settings/subjects/bulk` | Bulk create subjects |
| GET | `/api/v1/admin/settings/class-sections` | Get all class-sections |
| GET | `/api/v1/admin/settings/subjects` | List all subjects |
| PUT | `/api/v1/admin/settings/subjects/{subject_id}` | Update subject |
| DELETE | `/api/v1/admin/settings/subjects/{subject_id}` | Delete subject |
| POST | `/api/v1/admin/settings/upload-logo` | Upload school logo |
| PUT | `/api/v1/admin/settings/subjects/{subject_id}/classes` | Assign subject to classes |
| GET | `/api/v1/admin/settings/class-subjects` | Get class-subject mapping |
| PUT | `/api/v1/admin/settings/class-subjects/{class_id}` | Update class subjects |
| GET | `/api/v1/admin/settings/fee-structures` | List fee structures |
| POST | `/api/v1/admin/settings/fee-structures` | Create fee structure |
| PUT | `/api/v1/admin/settings/fee-structures/{structure_id}` | Update fee structure |
| DELETE | `/api/v1/admin/settings/fee-structures/{structure_id}` | Delete fee structure |
| GET | `/api/v1/admin/settings/id-generation` | Get ID generation config |
| PUT | `/api/v1/admin/settings/id-generation` | Update ID generation config |
| GET | `/api/v1/admin/settings/holidays` | Get holidays |
| PUT | `/api/v1/admin/settings/holidays` | Update holidays |
| GET | `/api/v1/admin/settings/next-id` | Get next generated ID |
| GET | `/api/v1/admin/settings/attendance-config` | Get attendance config |
| PUT | `/api/v1/admin/settings/attendance-config` | Update attendance config |

---

### Students (27)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/students` | List students (paginated, filterable) |
| POST | `/api/v1/admin/students` | Create student |
| GET | `/api/v1/admin/students/export` | Export students CSV |
| POST | `/api/v1/admin/students/bulk-import` | Bulk import students (CSV) |
| POST | `/api/v1/admin/students/bulk-import-json` | Bulk import students (JSON) |
| GET | `/api/v1/admin/students/{student_id}` | Get student detail |
| PUT | `/api/v1/admin/students/{student_id}` | Update student |
| DELETE | `/api/v1/admin/students/{student_id}` | Delete (deactivate) student |
| POST | `/api/v1/admin/students/{student_id}/reset-password` | Reset student password |
| GET | `/api/v1/admin/students/{student_id}/exam-results` | Student exam results |
| GET | `/api/v1/admin/students/{student_id}/parent-meetings` | List parent meetings |
| POST | `/api/v1/admin/students/{student_id}/parent-meetings` | Create parent meeting |
| PUT | `/api/v1/admin/students/{student_id}/parent-meetings/{meeting_id}` | Update meeting |
| DELETE | `/api/v1/admin/students/{student_id}/parent-meetings/{meeting_id}` | Delete meeting |
| GET | `/api/v1/admin/students/{student_id}/activities` | List activities |
| POST | `/api/v1/admin/students/{student_id}/activities` | Create activity |
| PUT | `/api/v1/admin/students/{student_id}/activities/{activity_id}` | Update activity |
| DELETE | `/api/v1/admin/students/{student_id}/activities/{activity_id}` | Delete activity |
| POST | `/api/v1/admin/students/{student_id}/awards` | Create award |
| PUT | `/api/v1/admin/students/{student_id}/awards/{award_id}` | Update award |
| DELETE | `/api/v1/admin/students/{student_id}/awards/{award_id}` | Delete award |
| GET | `/api/v1/admin/students/{student_id}/fee-history` | Fee history |
| GET | `/api/v1/admin/students/{student_id}/disciplinary-records` | List disciplinary records |
| POST | `/api/v1/admin/students/{student_id}/disciplinary-records` | Create disciplinary record |
| PUT | `/api/v1/admin/students/{student_id}/disciplinary-records/{record_id}` | Update record |
| DELETE | `/api/v1/admin/students/{student_id}/disciplinary-records/{record_id}` | Delete record |
| GET | `/api/v1/admin/students/{student_id}/attendance` | Student attendance |

---

### Teachers (18)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/teachers` | List teachers (paginated, filterable) |
| POST | `/api/v1/admin/teachers` | Create teacher |
| GET | `/api/v1/admin/teachers/export` | Export teachers CSV |
| POST | `/api/v1/admin/teachers/bulk-import` | Bulk import teachers (CSV) |
| GET | `/api/v1/admin/teachers/by-class` | Get teachers by class |
| GET | `/api/v1/admin/teachers/{teacher_id}` | Get teacher detail |
| PUT | `/api/v1/admin/teachers/{teacher_id}` | Update teacher |
| DELETE | `/api/v1/admin/teachers/{teacher_id}` | Delete (deactivate) teacher |
| POST | `/api/v1/admin/teachers/{teacher_id}/reset-password` | Reset password |
| POST | `/api/v1/admin/teachers/{teacher_id}/assign-class` | Assign class to teacher |
| POST | `/api/v1/admin/teachers/{teacher_id}/bulk-assign` | Bulk assign classes |
| GET | `/api/v1/admin/teachers/{teacher_id}/assignments` | Get class assignments |
| DELETE | `/api/v1/admin/teachers/{teacher_id}/assignments/{assignment_id}` | Remove assignment |
| GET | `/api/v1/admin/teachers/{teacher_id}/awards` | List awards |
| POST | `/api/v1/admin/teachers/{teacher_id}/awards` | Create award |
| PUT | `/api/v1/admin/teachers/{teacher_id}/awards/{award_id}` | Update award |
| DELETE | `/api/v1/admin/teachers/{teacher_id}/awards/{award_id}` | Delete award |
| GET | `/api/v1/admin/teachers/{teacher_id}/history` | Teacher history |

---

### Staff (5)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/staff` | List staff (paginated, filterable) |
| GET | `/api/v1/admin/staff/export` | Export staff CSV |
| POST | `/api/v1/admin/staff` | Create staff member |
| PUT | `/api/v1/admin/staff/{staff_id}` | Update staff |
| DELETE | `/api/v1/admin/staff/{staff_id}` | Delete (deactivate) staff |

---

### Payroll (18) — prefix: `/admin/staff`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/staff/payroll` | List payroll records |
| POST | `/api/v1/admin/staff/payroll/run` | Run payroll for a month |
| POST | `/api/v1/admin/staff/payroll/generate-payslips` | Generate payslips |
| PUT | `/api/v1/admin/staff/payroll/{payslip_id}` | Update payslip |
| POST | `/api/v1/admin/staff/payroll/{payslip_id}/pay` | Mark payslip as paid |
| POST | `/api/v1/admin/staff/payroll/mark-all-paid` | Mark all as paid |
| POST | `/api/v1/admin/staff/payroll/undo-all-paid` | Undo mark all paid |
| GET | `/api/v1/admin/staff/payroll/history` | Payroll history |
| GET | `/api/v1/admin/staff/payroll/salary-structure/{employee_id}` | Get salary structure |
| PUT | `/api/v1/admin/staff/payroll/salary-structure/{staff_id}` | Update salary structure |
| GET | `/api/v1/admin/staff/salary-advances` | List salary advances |
| POST | `/api/v1/admin/staff/salary-advances` | Create salary advance |
| POST | `/api/v1/admin/staff/salary-advances/{advance_id}/approve` | Approve advance |
| POST | `/api/v1/admin/staff/salary-advances/{advance_id}/reject` | Reject advance |
| POST | `/api/v1/admin/staff/salary-advances/{advance_id}/disburse` | Disburse advance |
| GET | `/api/v1/admin/staff/payroll/salary-revisions/{staff_id}` | Salary revision history |
| GET | `/api/v1/admin/staff/payroll/staff/{staff_id}/payslips` | Staff payslip history |
| POST | `/api/v1/admin/staff/payroll/salary-revisions` | Create salary revision |

---

### Fees (13)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/fees` | List fee records (paginated, filterable) |
| GET | `/api/v1/admin/fees/export` | Export fees CSV |
| GET | `/api/v1/admin/fees/student/{student_id}` | Student fee records |
| GET | `/api/v1/admin/fees/student/{student_id}/receipt` | Consolidated receipt |
| GET | `/api/v1/admin/fees/{fee_id}` | Fee record detail |
| GET | `/api/v1/admin/fees/{fee_id}/receipt` | Individual fee receipt |
| PUT | `/api/v1/admin/fees/{fee_id}` | Update fee record |
| POST | `/api/v1/admin/fees` | Create fee record |
| POST | `/api/v1/admin/fees/generate-due` | Generate due fees for class/month |
| POST | `/api/v1/admin/fees/{fee_id}/record-payment` | Record a payment |
| POST | `/api/v1/admin/fees/{fee_id}/apply-late-fee` | Apply late fee |
| POST | `/api/v1/admin/fees/bulk-apply-late-fees` | Bulk apply late fees |
| POST | `/api/v1/admin/fees/send-reminder` | Send fee reminder |

---

### Examinations (16)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/examinations` | List exams (paginated, filterable) |
| POST | `/api/v1/admin/examinations` | Create exam |
| GET | `/api/v1/admin/examinations/grade-system` | Get grading system |
| PUT | `/api/v1/admin/examinations/grade-system` | Update grading system |
| GET | `/api/v1/admin/examinations/analytics` | Exam analytics |
| GET | `/api/v1/admin/examinations/report-card/{student_id}` | Student report card |
| POST | `/api/v1/admin/examinations/report-card/generate` | Generate report cards |
| GET | `/api/v1/admin/examinations/schedule` | Exam schedule |
| GET | `/api/v1/admin/examinations/{exam_id}` | Get exam detail |
| PUT | `/api/v1/admin/examinations/{exam_id}` | Update exam |
| DELETE | `/api/v1/admin/examinations/{exam_id}` | Cancel exam |
| GET | `/api/v1/admin/examinations/{exam_id}/results` | Get exam results |
| POST | `/api/v1/admin/examinations/{exam_id}/results` | Enter results |
| POST | `/api/v1/admin/examinations/{exam_id}/results/bulk-upload` | Bulk upload results |
| PUT | `/api/v1/admin/examinations/{exam_id}/results/{result_id}` | Update individual result |
| POST | `/api/v1/admin/examinations/{exam_id}/publish` | Publish exam results |

---

### Leaves (11)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/leaves` | List leave applications (paginated) |
| GET | `/api/v1/admin/leaves/teacher/{teacher_id}` | Teacher leave detail |
| GET | `/api/v1/admin/leaves/balances` | All teacher leave balances |
| GET | `/api/v1/admin/leaves/policy` | Get leave policy |
| PUT | `/api/v1/admin/leaves/policy` | Update leave policy |
| POST | `/api/v1/admin/leaves/{leave_id}/approve` | Approve leave |
| POST | `/api/v1/admin/leaves/{leave_id}/reject` | Reject leave |
| POST | `/api/v1/admin/leaves/{leave_id}/cancel` | Cancel leave |
| POST | `/api/v1/admin/leaves/bulk-action` | Bulk approve/reject |
| GET | `/api/v1/admin/leaves/calendar` | Leave calendar view |
| POST | `/api/v1/admin/leaves/allocate` | Allocate leave balance |

---

### Transport (28)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/transport/stats` | Transport stats |
| GET | `/api/v1/admin/transport/vehicles/export` | Export vehicles CSV |
| GET | `/api/v1/admin/transport/vehicles` | List vehicles |
| POST | `/api/v1/admin/transport/vehicles` | Create vehicle |
| GET | `/api/v1/admin/transport/vehicles/{vehicle_id}` | Get vehicle |
| PUT | `/api/v1/admin/transport/vehicles/{vehicle_id}` | Update vehicle |
| DELETE | `/api/v1/admin/transport/vehicles/{vehicle_id}` | Delete vehicle |
| GET | `/api/v1/admin/transport/drivers/export` | Export drivers CSV |
| GET | `/api/v1/admin/transport/drivers` | List drivers |
| POST | `/api/v1/admin/transport/drivers` | Create driver |
| PUT | `/api/v1/admin/transport/drivers/{driver_id}` | Update driver |
| DELETE | `/api/v1/admin/transport/drivers/{driver_id}` | Delete driver |
| GET | `/api/v1/admin/transport/helpers` | List helpers |
| POST | `/api/v1/admin/transport/helpers` | Create helper |
| PUT | `/api/v1/admin/transport/helpers/{helper_id}` | Update helper |
| DELETE | `/api/v1/admin/transport/helpers/{helper_id}` | Delete helper |
| GET | `/api/v1/admin/transport/routes` | List routes |
| POST | `/api/v1/admin/transport/routes` | Create route |
| PUT | `/api/v1/admin/transport/routes/{route_id}` | Update route |
| DELETE | `/api/v1/admin/transport/routes/{route_id}` | Delete route |
| GET | `/api/v1/admin/transport/assignments` | List vehicle-driver assignments |
| POST | `/api/v1/admin/transport/assignments` | Create assignment |
| PUT | `/api/v1/admin/transport/assignments/{assignment_id}` | Update assignment |
| DELETE | `/api/v1/admin/transport/assignments/{assignment_id}` | Delete assignment |
| GET | `/api/v1/admin/transport/routes/{route_id}/students` | List students on route |
| POST | `/api/v1/admin/transport/routes/{route_id}/students` | Add student to route |
| DELETE | `/api/v1/admin/transport/routes/{route_id}/students/{student_id}` | Remove student from route |
| POST | `/api/v1/admin/transport/routes/shuffle-assign` | Auto-assign students to routes |

---

### Timetable (12)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/timetable/periods` | List period definitions |
| POST | `/api/v1/admin/timetable/periods` | Create period |
| PUT | `/api/v1/admin/timetable/periods/{period_id}` | Update period |
| DELETE | `/api/v1/admin/timetable/periods/{period_id}` | Delete period |
| GET | `/api/v1/admin/timetable` | Get timetable grid |
| POST | `/api/v1/admin/timetable/slot` | Create timetable slot |
| PUT | `/api/v1/admin/timetable/slot/{slot_id}` | Update slot |
| DELETE | `/api/v1/admin/timetable/slot/{slot_id}` | Delete slot |
| POST | `/api/v1/admin/timetable/bulk-assign` | Bulk assign slots |
| GET | `/api/v1/admin/timetable/teacher/{teacher_id}` | Teacher timetable |
| GET | `/api/v1/admin/timetable/teacher-availability` | Check teacher availability |
| GET | `/api/v1/admin/timetable/conflicts` | Detect timetable conflicts |

---

### Library (6)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/library/books` | List books (paginated, searchable) |
| POST | `/api/v1/admin/library/books` | Add book to library |
| POST | `/api/v1/admin/library/issue` | Issue book to student |
| POST | `/api/v1/admin/library/return` | Return book |
| GET | `/api/v1/admin/library/issued` | List currently issued books |
| GET | `/api/v1/admin/library/overdue` | List overdue books |

---

### Notifications (5)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/notifications` | List notifications (paginated) |
| POST | `/api/v1/admin/notifications` | Create/send notification |
| GET | `/api/v1/admin/notifications/{notification_id}` | Get notification detail |
| PUT | `/api/v1/admin/notifications/{notification_id}` | Update notification |
| DELETE | `/api/v1/admin/notifications/{notification_id}` | Archive notification |

---

### Attendance (3)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/attendance` | Get attendance for a class/date |
| POST | `/api/v1/admin/attendance` | Submit attendance |
| PUT | `/api/v1/admin/attendance` | Update attendance |

---

### Mentoring (7)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/mentoring` | List all mentor assignments |
| GET | `/api/v1/admin/mentoring/teacher/{staff_id}/students` | Get mentor's students |
| GET | `/api/v1/admin/mentoring/teachers` | List available mentor teachers |
| GET | `/api/v1/admin/mentoring/students` | List students (for assignment) |
| POST | `/api/v1/admin/mentoring/assign` | Assign mentor to students |
| DELETE | `/api/v1/admin/mentoring/{assignment_id}` | Remove mentor assignment |
| POST | `/api/v1/admin/mentoring/shuffle-assign` | Auto-assign all students evenly |

---

## Summary

| Module | Endpoints | Notes |
|--------|-----------|-------|
| Auth (shared) | 8 | Login, logout, refresh, profile, password management |
| Dashboard | 8 | KPIs, trends, distributions, activities, leaves, alerts |
| Settings | 35 | School profile, academic years, classes, sections, subjects, enums, fee structures, holidays, ID gen, attendance config |
| Students | 27 | CRUD + bulk import + parent meetings + activities + awards + disciplinary + attendance |
| Teachers | 18 | CRUD + bulk import + class assignments + awards + history |
| Staff | 5 | CRUD + export |
| Payroll | 18 | Payroll run + payslips + salary structure + advances + revisions |
| Fees | 13 | CRUD + payments + late fees + reminders + export |
| Examinations | 16 | CRUD + results + analytics + report cards + schedule |
| Leaves | 11 | Applications + policy + approve/reject + calendar + allocate |
| Transport | 28 | Vehicles + drivers + helpers + routes + assignments + route students |
| Timetable | 12 | Periods + slots + bulk assign + teacher view + conflicts |
| Library | 6 | Books + issue/return + overdue |
| Notifications | 5 | CRUD + archive |
| Attendance | 3 | Get + submit + update |
| Mentoring | 7 | Assign + remove + auto-shuffle |
| **Admin-specific** | **212** | |
| **Total (incl. shared auth)** | **220** | |
