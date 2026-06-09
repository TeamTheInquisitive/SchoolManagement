# School ERP Backend - Student Portal API Endpoints

## Architecture Overview

```
Student Portal API:
├── Runtime: Python (FastAPI)
├── Database: PostgreSQL (shared with Admin & Teacher modules)
├── Auth: JWT (httpOnly cookies) + Refresh Token rotation
├── Multi-tenancy: X-School-Code header → DB schema/filter
├── API Style: RESTful, JSON
├── Base URL: /api/v1
├── Student Prefix: /api/v1/student/...
└── Shared Auth: /api/v1/auth/...
```

### Student Portal Design Principles

1. **Self-scoped access** — Student's `id` is derived from the auth token. All endpoints return only the authenticated student's own data. No student_id needed in most requests.

2. **Read-heavy, minimal writes** — Students can READ their own data (attendance, results, timetable, fees, profile). Limited writes: submit assignments, update profile.

3. **Academic year scoping** — All transactional data (attendance, results, fees, assignments) is scoped by `academic_year`. Defaults to current if omitted.

4. **No admin data** — Student cannot see other students' data, class averages are anonymized, rankings show position only.

5. **Pagination everywhere** — All list endpoints support `page` + `page_size`. Responses include `count`, `page`, `page_size`, `total_pages`, `results[]`.

6. **`metadata: {}` on every entity** — Future extensions without schema changes.

7. **Forward/backward compatible** — Additive-only, optional nullable new fields.

### Request Headers

| Header | Description | Required |
|--------|-------------|----------|
| `Content-Type` | `application/json` | Yes |
| `X-School-Code` | School tenant identifier | Yes (except /auth/login) |
| `Cookie` | httpOnly auth cookies (sent automatically) | Yes (after login) |

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200  | Success |
| 201  | Created |
| 400  | Bad Request (validation error) |
| 401  | Unauthorized |
| 403  | Forbidden (wrong role) |
| 404  | Not Found |
| 409  | Conflict (duplicate submission) |
| 500  | Internal Server Error |

---

## All Endpoints (42 Student-specific + 7 Shared Auth = 49 total)

---

### Auth — Shared (7)

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

### Dashboard (10)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/student/dashboard/stats` | KPI cards (attendance %, grade, assignments, fee status) |
| GET | `/api/v1/student/dashboard/today-schedule` | Today's class schedule |
| GET | `/api/v1/student/dashboard/pending-assignments` | Pending assignments list |
| GET | `/api/v1/student/dashboard/upcoming-exams` | Upcoming exams |
| GET | `/api/v1/student/dashboard/subject-attendance` | Per-subject attendance bars |
| GET | `/api/v1/student/dashboard/recent-results` | Recent exam results |
| GET | `/api/v1/student/dashboard/announcements` | Recent announcements |
| GET | `/api/v1/student/dashboard/notifications` | Recent notifications |
| GET | `/api/v1/student/dashboard/fee-status` | Fee status overview with upcoming dues |
| GET | `/api/v1/student/dashboard/parent-meetings` | Parent meeting history |

---

### Timetable (2)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/student/timetable` | Weekly timetable grid (class-based) with day schedule and subject summary |
| GET | `/api/v1/student/timetable/day` | Single day schedule with period cards (default: today) |

**Query Parameters:**

| Endpoint | Param | Type | Description |
|----------|-------|------|-------------|
| `GET /timetable` | `academic_year` | string? | Filter by academic year |
| `GET /timetable/day` | `date` | date? | Target date (defaults to today) |

---

### Attendance (5)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/student/attendance` | Overall + subject-wise attendance with recent records and distribution |
| GET | `/api/v1/student/attendance/history` | Detailed attendance history (paginated, filterable) |
| GET | `/api/v1/student/attendance/warnings` | Attendance warnings and compliance status |
| GET | `/api/v1/student/attendance/summary` | Alias for attendance overview |
| GET | `/api/v1/student/attendance/monthly` | Monthly attendance breakdown |

**Query Parameters:**

| Endpoint | Param | Type | Description |
|----------|-------|------|-------------|
| `GET /attendance` | `academic_year` | string? | Filter by academic year |
| `GET /attendance` | `month` | string? | Filter by month (YYYY-MM) |
| `GET /attendance/history` | `page` | int | Page number |
| `GET /attendance/history` | `page_size` | int | Page size |
| `GET /attendance/history` | `subject` | string? | Filter by subject |
| `GET /attendance/history` | `month` | string? | Filter by month (YYYY-MM) |
| `GET /attendance/history` | `status` | string? | Filter by status |
| `GET /attendance/warnings` | `academic_year` | string? | Filter by academic year |
| `GET /attendance/monthly` | `month` | string? | Filter by month (YYYY-MM) |

---

### Assignments (4)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/student/assignments` | List assignments + summary (filter: status, subject) |
| GET | `/api/v1/student/assignments/{assignment_id}` | Get assignment details |
| POST | `/api/v1/student/assignments/{assignment_id}/submit/` | Submit assignment (file upload + comments) |
| GET | `/api/v1/student/assignments/{assignment_id}/submission/` | View own submission + grade |

**Query Parameters:**

| Endpoint | Param | Type | Description |
|----------|-------|------|-------------|
| `GET /assignments` | `page` | int | Page number |
| `GET /assignments` | `page_size` | int | Page size |
| `GET /assignments` | `status` | string? | Filter by status |
| `GET /assignments` | `subject` | string? | Filter by subject |
| `GET /assignments` | `academic_year` | string? | Filter by academic year |

---

### Results (5)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/student/results` | Overall results summary + performance trend + subject comparison + radar |
| GET | `/api/v1/student/results/exams` | List all exams with results (paginated, filterable) |
| GET | `/api/v1/student/results/download-report` | Download consolidated results report |
| GET | `/api/v1/student/results/exam/{exam_id}` | Detailed result for a specific exam |
| GET | `/api/v1/student/results/exam/{exam_id}/leaderboard` | Leaderboard for a specific exam |

**Query Parameters:**

| Endpoint | Param | Type | Description |
|----------|-------|------|-------------|
| `GET /results` | `academic_year` | string? | Filter by academic year |
| `GET /results/exams` | `page` | int | Page number |
| `GET /results/exams` | `page_size` | int | Page size |
| `GET /results/exams` | `exam_type` | string? | Filter by exam type |
| `GET /results/exams` | `academic_year` | string? | Filter by academic year |
| `GET /results/download-report` | `academic_year` | string? | Academic year |
| `GET /results/download-report` | `exam_id` | uuid? | Specific exam |
| `GET /results/exam/{exam_id}/leaderboard` | `subject` | string? | Filter by subject |

---

### Fees (6)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/student/fees` | Fee summary + current dues + recent payments |
| GET | `/api/v1/student/fees/structure` | Fee structure breakdown with components and frequency |
| GET | `/api/v1/student/fees/dues` | Current dues list (paginated) |
| GET | `/api/v1/student/fees/history` | Payment history (paginated) |
| GET | `/api/v1/student/fees/receipt/{payment_id}` | Payment receipt details with download URL |
| GET | `/api/v1/student/fees/reminders` | Fee reminders sent by admin |

**Query Parameters:**

| Endpoint | Param | Type | Description |
|----------|-------|------|-------------|
| `GET /fees` | `academic_year` | string? | Filter by academic year |
| `GET /fees/structure` | `academic_year` | string? | Filter by academic year |
| `GET /fees/dues` | `page` | int | Page number |
| `GET /fees/dues` | `page_size` | int | Page size |
| `GET /fees/dues` | `academic_year` | string? | Filter by academic year |
| `GET /fees/history` | `page` | int | Page number |
| `GET /fees/history` | `page_size` | int | Page size |
| `GET /fees/history` | `academic_year` | string? | Filter by academic year |

---

### Library (4)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/student/library` | My books + summary (borrowed, overdue, fines) |
| GET | `/api/v1/student/library/catalog` | Browse book catalog (search, filter by category) |
| GET | `/api/v1/student/library/history` | Borrowing history (paginated) |
| GET | `/api/v1/student/library/fines` | Fine details and penalty information |

**Query Parameters:**

| Endpoint | Param | Type | Description |
|----------|-------|------|-------------|
| `GET /library/catalog` | `page` | int | Page number |
| `GET /library/catalog` | `page_size` | int | Page size |
| `GET /library/catalog` | `search` | string? | Search by title/author |
| `GET /library/catalog` | `category` | string? | Filter by category |
| `GET /library/history` | `page` | int | Page number |
| `GET /library/history` | `page_size` | int | Page size |

---

### Notifications (3)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/student/notifications` | List all notifications (paginated, filterable) |
| GET | `/api/v1/student/notifications/{notification_id}` | Get notification details |
| PUT | `/api/v1/student/notifications/{notification_id}/read` | Mark notification as read |

**Query Parameters:**

| Endpoint | Param | Type | Description |
|----------|-------|------|-------------|
| `GET /notifications` | `page` | int | Page number |
| `GET /notifications` | `page_size` | int | Page size |
| `GET /notifications` | `type` | string? | Filter by type |
| `GET /notifications` | `is_read` | bool? | Filter by read status |

---

### Profile (3)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/student/profile` | Get full profile (personal, parent, medical, transport, mentor) |
| PUT | `/api/v1/student/profile` | Update editable profile fields (phone, address, emergency contact) |
| GET | `/api/v1/student/profile/mentor` | Get assigned mentor details |

---

## Summary

| Module | Endpoints | Notes |
|--------|-----------|-------|
| Auth (shared) | 8 | Same as admin/teacher |
| Dashboard | 10 | KPIs, schedule, assignments, exams, attendance, results, announcements, notifications, fee status, parent meetings |
| Timetable | 2 | Weekly grid + daily schedule |
| Attendance | 5 | Overview + history + warnings + summary + monthly |
| Assignments | 4 | View + submit |
| Results | 5 | View results + trends + leaderboard + download report |
| Fees | 6 | Summary + structure + dues + history + receipts + reminders |
| Library | 4 | My books + catalog + history + fines |
| Notifications | 3 | View + mark as read |
| Profile | 3 | View + edit + mentor |
| **Student-specific** | **42** | |
| **Total (incl. shared auth)** | **50** | |
