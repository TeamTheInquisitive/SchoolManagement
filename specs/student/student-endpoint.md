# School ERP Backend - Student Portal API Endpoints

## Architecture Overview

```
Student Portal API:
├── Runtime: Node.js / Python (Django/FastAPI)
├── Database: MySQL (shared with Admin & Teacher modules)
├── Auth: JWT (httpOnly cookies) + Refresh Token rotation
├── Multi-tenancy: X-School-Code header → DB schema/filter
├── API Style: RESTful, JSON
├── Base URL: /api/v1
├── Student Prefix: /api/v1/student/...
└── Shared Auth: /api/v1/auth/...
```

### Student Portal Design Principles

1. **Self-scoped access** — Student's `id` is derived from the auth token. All endpoints return only the authenticated student's own data. No student_id needed in most requests.

2. **Read-heavy, minimal writes** — Students can READ their own data (attendance, results, timetable, fees, profile). Limited writes: submit assignments, take quizzes, send messages, update profile.

3. **Academic year scoping** — All transactional data (attendance, results, fees, assignments) is scoped by `academic_year`. Defaults to current if omitted.

4. **No admin data** — Student cannot see other students' data, class averages are anonymized, rankings show position only.

5. **Pagination everywhere** — All list endpoints support `page` + `page_size`. Responses include `count`, `page`, `page_size`, `total_pages`, `results[]`.

6. **`metadata: {}` on every entity** — Future extensions without schema changes.

7. **Forward/backward compatible** — Additive-only, optional nullable new fields.

### Request Headers

| Header | Description | Required |
|--------|-------------|----------|
| `Content-Type` | `application/json` | Yes |
| `X-School-Code` | School tenant identifier | Yes (except /auth/login/) |
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

## All Endpoints (53 Student-specific + 7 Shared Auth = 60 total)

---

### Auth — Shared (7)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login/` | Login with email/password |
| POST | `/api/v1/auth/refresh-token/` | Refresh access token |
| GET | `/api/v1/auth/me/` | Get current user profile |
| POST | `/api/v1/auth/logout/` | Logout and clear cookies |
| POST | `/api/v1/auth/forgot-password/` | Send password reset email |
| POST | `/api/v1/auth/reset-password/` | Reset password via token |
| POST | `/api/v1/auth/change-password/` | Change password (authenticated) |

---

### Dashboard (10)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/student/dashboard/stats/` | KPI cards (attendance %, grade, assignments, fee status) |
| GET | `/api/v1/student/dashboard/today-schedule/` | Today's class schedule |
| GET | `/api/v1/student/dashboard/pending-assignments/` | Pending assignments list |
| GET | `/api/v1/student/dashboard/upcoming-exams/` | Upcoming exams |
| GET | `/api/v1/student/dashboard/subject-attendance/` | Per-subject attendance bars |
| GET | `/api/v1/student/dashboard/recent-results/` | Recent exam results |
| GET | `/api/v1/student/dashboard/announcements/` | Recent announcements |
| GET | `/api/v1/student/dashboard/notifications/` | Recent notifications (assignment, fee, library alerts) |
| GET | `/api/v1/student/dashboard/fee-status/` | Fee status overview with upcoming dues |
| GET | `/api/v1/student/dashboard/parent-meetings/` | Parent meeting history with attendance status |

---

### Timetable (2)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/student/timetable/` | Weekly timetable grid (class-based) with day schedule and subject summary |
| GET | `/api/v1/student/timetable/day/` | Single day schedule with period cards (default: today) |

---

### Attendance (3)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/student/attendance/` | Overall + subject-wise attendance with recent records and distribution |
| GET | `/api/v1/student/attendance/history/` | Detailed attendance history (paginated, filterable) |
| GET | `/api/v1/student/attendance/warnings/` | Attendance warnings and compliance status |

---

### Assignments (4)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/student/assignments/` | List assignments + summary (filter: status, subject) |
| GET | `/api/v1/student/assignments/:id/` | Get assignment details |
| POST | `/api/v1/student/assignments/:id/submit/` | Submit assignment (file upload + comments) |
| GET | `/api/v1/student/assignments/:id/submission/` | View own submission + grade |

---

### Results (5)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/student/results/` | Overall results summary + performance trend + subject comparison + radar |
| GET | `/api/v1/student/results/exam/:exam_id/` | Detailed result for a specific exam |
| GET | `/api/v1/student/results/exams/` | List all exams with results (filter: exam type, year, month, subject) |
| GET | `/api/v1/student/results/exam/:exam_id/leaderboard/` | Leaderboard for a specific exam (top performers) |
| GET | `/api/v1/student/results/download-report/` | Download consolidated results report (PDF) |

---

---

### Fees (5)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/student/fees/` | Fee summary + current dues + payment history |
| GET | `/api/v1/student/fees/structure/` | Fee structure breakdown with components and frequency |
| GET | `/api/v1/student/fees/dues/` | Current dues list |
| GET | `/api/v1/student/fees/history/` | Payment history |
| GET | `/api/v1/student/fees/receipt/:payment_id/` | Download payment receipt |
| GET | `/api/v1/student/fees/reminders/` | Fee reminders sent by admin |

---

### Library (4)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/student/library/` | My books + summary (borrowed, overdue, fines, returned) |
| GET | `/api/v1/student/library/catalog/` | Browse book catalog (search, filter) |
| GET | `/api/v1/student/library/history/` | Borrowing history |
| GET | `/api/v1/student/library/fines/` | Fine details and penalty information |

---

### Notifications (3)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/student/notifications/` | List all notifications/announcements (paginated, filterable) |
| GET | `/api/v1/student/notifications/:id/` | Get notification details |
| PUT | `/api/v1/student/notifications/:id/read/` | Mark notification as read |

---

### Quiz Portal (7) — Moved to V2

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/student/quizzes/` | List available + completed quizzes + KPIs (active, completed, best score, best rank) |
| GET | `/api/v1/student/quizzes/:id/` | Quiz details (subject, difficulty, questions, duration, marks, passing, attempts, negative marking) |
| POST | `/api/v1/student/quizzes/:id/start/` | Start attempt (returns questions with options, timer, marks per question) |
| POST | `/api/v1/student/quizzes/:id/submit/` | Submit answers (returns score with negative marking, pass/fail) |
| GET | `/api/v1/student/quizzes/:id/result/` | Result + leaderboard + correct/incorrect/unanswered counts |
| GET | `/api/v1/student/quizzes/:id/review/` | Answer review (questions + correct answers + explanations + your answers) |
| GET | `/api/v1/student/quizzes/completed/` | Completed quizzes with scores and ranks |

---

### My Profile (10)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/student/profile/` | Get full profile (personal, parent, medical, transport, mentor) |
| PUT | `/api/v1/student/profile/` | Update editable profile fields |
| GET | `/api/v1/student/profile/mentor/` | Get assigned mentor details |
| GET | `/api/v1/student/profile/parent-meetings/` | Parent-teacher meeting history with discussion notes |
| GET | `/api/v1/student/profile/behavior/` | Behavior & conduct (rating, discipline, punctuality, notes) |
| GET | `/api/v1/student/profile/activities/` | Extra-curricular activities and club memberships |
| GET | `/api/v1/student/profile/awards/` | Awards and achievements |
| GET | `/api/v1/student/profile/academic-summary/` | Academic performance summary (attendance, grade, rank) |
| GET | `/api/v1/student/profile/print/` | Print-friendly full profile |
| GET | `/api/v1/student/profile/export-pdf/` | Export full student profile as PDF |

---

## Summary

| Module | Endpoints | Notes |
|--------|-----------|-------|
| Auth (shared) | 7 | Same as admin/teacher |
| Dashboard | 10 | KPIs, schedule, assignments, exams, attendance, results, announcements, notifications, fee status, parent meetings |
| Timetable | 2 | Weekly grid + daily schedule with subject summary |
| Attendance | 3 | View own attendance + warnings |
| Assignments | 4 | View + submit |
| Results | 5 | View results + trends + leaderboard + download report |
| Fees | 6 | Structure + dues + history + receipts + reminders |
| Library | 4 | My books + catalog + history + fines |
| Notifications | 3 | View + mark as read |
| Quiz Portal | 6 | Take quizzes + view results |
| My Profile | 10 | View + edit + mentor + meetings + behavior + activities + awards + academic summary + print/export |
| **Student-specific** | **53** | |
| **Total (incl. shared auth)** | **60** | |
