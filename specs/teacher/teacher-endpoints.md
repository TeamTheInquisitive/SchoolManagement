# School ERP Backend - Teacher Portal API Endpoints

## Architecture Overview

```
Teacher Portal API:
├── Runtime: Python (FastAPI)
├── Database: PostgreSQL (shared with Admin module)
├── Auth: JWT (httpOnly cookies) + Refresh Token rotation
├── Multi-tenancy: X-School-Code header → DB schema/filter
├── API Style: RESTful, JSON
├── Base URL: /api/v1
├── Teacher Prefix: /api/v1/teacher/...
└── Shared Auth: /api/v1/auth/...
```

### Teacher Portal Design Principles

1. **Teacher = Staff with teaching role** — Same `staff` DB table, filtered by `is_teacher=true` or `department='Teaching'`. Teacher-specific extensions: `subjects[]`, `class_assignments[]`.

2. **Self-scoped access** — Teacher's `id` is derived from the auth token. All endpoints implicitly scope data to the authenticated teacher. No need to pass `teacher_id` in most requests.

3. **Academic year scoping** — All transactional data (attendance, grades, assignments, leaves, timetable) is scoped by `academic_year`. If the `?academic_year` param is omitted, the current academic year is used.

4. **Read-heavy, limited writes** — Teachers can CREATE/UPDATE attendance, assignments, grades, and adhoc classes for their own classes. They can READ their timetable, student details, and dashboard data. They can APPLY for leaves (admin approves/rejects).

5. **Class-bound operations** — Write operations (attendance, grades, assignments) are restricted to classes assigned to the authenticated teacher. Attempting to write to an unassigned class returns 403.

6. **Pagination everywhere** — All list endpoints support `page` + `page_size` params. Responses include `count`, `page`, `page_size`, `total_pages`, `results[]`.

7. **Filtering is always optional** — Omitting a filter returns all records within the teacher's scope.

8. **Soft deletes** — All DELETE operations are soft deletes (`is_active=false`, deactivation timestamp set).

9. **`metadata: {}` on every entity** — JSON field for future extensions without schema migrations.

10. **Forward/backward compatible** — Additive-only changes, optional nullable new fields, no removals.

### Authentication & Authorization

- Auth endpoints are shared: `/api/v1/auth/...`
- Teacher endpoints require role = `teacher` in the auth token
- Admin can also read teacher-created data via admin endpoints
- Teacher CANNOT access admin endpoints (returns 403)

### Request Headers

| Header | Description | Required |
|--------|-------------|----------|
| `Content-Type` | `application/json` | Yes |
| `X-School-Code` | School tenant identifier | Yes (except /auth/login) |
| `Cookie` | httpOnly auth cookies (sent automatically) | Yes (after login) |

### Pagination Convention

All list endpoints support:

| Param | Default | Description |
|-------|---------|-------------|
| `page` | 1 | Page number |
| `page_size` | 20 | Items per page |

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200  | Success |
| 201  | Created |
| 400  | Bad Request (validation error) |
| 401  | Unauthorized |
| 403  | Forbidden (wrong role or unassigned class) |
| 404  | Not Found |
| 409  | Conflict (duplicate) |
| 500  | Internal Server Error |

---

## All Endpoints (77 Teacher-specific + 8 Shared Auth = 85 total)

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

### Dashboard (12)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teacher/dashboard/stats` | KPI cards (students, pending reviews, upcoming exams, classes today) |
| GET | `/api/v1/teacher/dashboard/today-schedule` | Today's class schedule |
| GET | `/api/v1/teacher/dashboard/pending-reviews` | Assignments pending review |
| GET | `/api/v1/teacher/dashboard/upcoming-exams` | Upcoming exams for teacher's classes |
| GET | `/api/v1/teacher/dashboard/classes-summary` | Summary of assigned classes |
| GET | `/api/v1/teacher/dashboard/leave-updates` | Recent leave application updates |
| GET | `/api/v1/teacher/dashboard/mentees-summary` | Mentee students summary |
| GET | `/api/v1/teacher/dashboard/adhoc-classes` | Adhoc classes summary |
| GET | `/api/v1/teacher/dashboard/attendance-status` | Attendance status for class teacher's classes (today) |
| GET | `/api/v1/teacher/dashboard/upcoming-meetings` | Upcoming parent-teacher meetings |
| GET | `/api/v1/teacher/dashboard/profile` | Get own profile |
| PUT | `/api/v1/teacher/dashboard/profile` | Update own profile |

---

### Attendance (6)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teacher/attendance` | Get attendance for a class/date |
| POST | `/api/v1/teacher/attendance` | Submit attendance for a class |
| PUT | `/api/v1/teacher/attendance` | Update previously submitted attendance |
| GET | `/api/v1/teacher/attendance/history` | Attendance submission history (paginated) |
| DELETE | `/api/v1/teacher/attendance/{session_id}` | Cancel an attendance session |
| GET | `/api/v1/teacher/attendance/summary` | Monthly attendance summary with students below threshold |

**Query Parameters:**

| Endpoint | Param | Type | Description |
|----------|-------|------|-------------|
| `GET /attendance` | `class_section_id` | uuid | Class section ID |
| `GET /attendance` | `date` | date? | Target date |
| `GET /attendance/history` | `page`, `page_size` | int | Pagination |
| `GET /attendance/history` | `class_section_id` | uuid? | Filter by class |
| `GET /attendance/history` | `from_date` | date? | Filter from date |
| `GET /attendance/history` | `to_date` | date? | Filter to date |
| `GET /attendance/summary` | `class_section_id` | uuid | Class section |
| `GET /attendance/summary` | `month` | int | Month number (required) |
| `GET /attendance/summary` | `year` | int | Year (required) |
| `GET /attendance/summary` | `academic_year` | string? | Academic year |

---

### Grades (9)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teacher/grades` | List grades for a class/exam |
| POST | `/api/v1/teacher/grades` | Submit grades (bulk) |
| PUT | `/api/v1/teacher/grades` | Update grades |
| GET | `/api/v1/teacher/grades/exams` | List exams available for grading |
| POST | `/api/v1/teacher/grades/exams/{exam_id}/publish` | Publish exam results |
| GET | `/api/v1/teacher/grades/report` | Grade report with distribution |
| GET | `/api/v1/teacher/grades/leaderboard` | Leaderboard for a class/exam |
| POST | `/api/v1/teacher/grades/import` | Import grades from CSV |
| GET | `/api/v1/teacher/grades/export` | Export grades as CSV/PDF |

**Query Parameters:**

| Endpoint | Param | Type | Description |
|----------|-------|------|-------------|
| `GET /grades` | `class_id` | uuid? | Class section ID |
| `GET /grades` | `exam_id` | uuid? | Exam ID |
| `GET /grades` | `page`, `page_size` | int | Pagination |
| `GET /grades/exams` | `class_id` | uuid? | Filter by class |
| `GET /grades/exams` | `academic_year` | string? | Filter by year |
| `GET /grades/report` | `class_id` | uuid? | Class section |
| `GET /grades/report` | `exam_id` | uuid? | Exam ID |
| `GET /grades/leaderboard` | `class_id` | uuid? | Class section |
| `GET /grades/leaderboard` | `exam_id` | uuid? | Exam ID |
| `GET /grades/leaderboard` | `limit` | int? | Limit results (default=20, max=100) |
| `GET /grades/export` | `class_id` | uuid? | Class section |
| `GET /grades/export` | `exam_id` | uuid? | Exam ID |
| `GET /grades/export` | `format` | string? | Export format (default="csv") |

---

### Assignments (8)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teacher/assignments` | List assignments (paginated, filterable) |
| POST | `/api/v1/teacher/assignments` | Create new assignment |
| GET | `/api/v1/teacher/assignments/{assignment_id}` | Get assignment detail |
| PUT | `/api/v1/teacher/assignments/{assignment_id}` | Update assignment |
| DELETE | `/api/v1/teacher/assignments/{assignment_id}` | Delete (deactivate) assignment |
| GET | `/api/v1/teacher/assignments/{assignment_id}/submissions` | List student submissions |
| POST | `/api/v1/teacher/assignments/{assignment_id}/submissions/{submission_id}/grade` | Grade a submission |
| GET | `/api/v1/teacher/assignments/{assignment_id}/submissions/export` | Export submissions as CSV |

**Query Parameters:**

| Endpoint | Param | Type | Description |
|----------|-------|------|-------------|
| `GET /assignments` | `page`, `page_size` | int | Pagination |
| `GET /assignments` | `class_id` | uuid? | Filter by class |
| `GET /assignments` | `search` | string? | Search assignments |
| `GET /assignments` | `subject` | string? | Filter by subject |
| `GET /assignments` | `status` | string? | Filter by status |
| `GET /assignments` | `academic_year` | string? | Filter by year |
| `GET /{id}/submissions` | `page`, `page_size` | int | Pagination |
| `GET /{id}/submissions` | `status` | string? | Filter by status |

---

### Adhoc Classes (4)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teacher/adhoc-classes` | List adhoc classes (paginated) |
| POST | `/api/v1/teacher/adhoc-classes` | Create adhoc class (extra/substitute) |
| PUT | `/api/v1/teacher/adhoc-classes/{adhoc_id}` | Update adhoc class |
| DELETE | `/api/v1/teacher/adhoc-classes/{adhoc_id}` | Cancel adhoc class |

**Query Parameters:**

| Endpoint | Param | Type | Description |
|----------|-------|------|-------------|
| `GET /adhoc-classes` | `page`, `page_size` | int | Pagination |
| `GET /adhoc-classes` | `status` | string? | Filter by status |
| `GET /adhoc-classes` | `from_date` | date? | Filter from date |
| `GET /adhoc-classes` | `to_date` | date? | Filter to date |

---

### Leaves (7)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teacher/leaves/balance` | Get leave balance by type |
| GET | `/api/v1/teacher/leaves/holidays` | Get holidays list for leave calculation |
| GET | `/api/v1/teacher/leaves/upcoming` | Get upcoming approved leaves |
| GET | `/api/v1/teacher/leaves` | Leave application history (paginated) |
| POST | `/api/v1/teacher/leaves` | Apply for leave |
| GET | `/api/v1/teacher/leaves/{leave_id}` | Get leave application detail |
| DELETE | `/api/v1/teacher/leaves/{leave_id}` | Cancel a pending/approved leave |

**Query Parameters:**

| Endpoint | Param | Type | Description |
|----------|-------|------|-------------|
| `GET /leaves` | `page`, `page_size` | int | Pagination |
| `GET /leaves` | `status` | string? | Filter by status |
| `GET /leaves` | `leave_type` | string? | Filter by type |

---

### Students (25)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teacher/students` | List students in teacher's classes |
| GET | `/api/v1/teacher/students/mentees` | List assigned mentee students |
| GET | `/api/v1/teacher/students/{student_id}` | Get full student detail |
| GET | `/api/v1/teacher/students/{student_id}/exam-results` | Student exam results & performance |
| GET | `/api/v1/teacher/students/{student_id}/parent-meetings` | Parent meeting history |
| POST | `/api/v1/teacher/students/{student_id}/parent-meetings` | Create a parent meeting |
| PUT | `/api/v1/teacher/students/{student_id}/parent-meetings/{meeting_id}` | Update a parent meeting |
| DELETE | `/api/v1/teacher/students/{student_id}/parent-meetings/{meeting_id}` | Delete a parent meeting |
| GET | `/api/v1/teacher/students/{student_id}/activities` | Activities & awards |
| POST | `/api/v1/teacher/students/{student_id}/activities` | Create an activity |
| PUT | `/api/v1/teacher/students/{student_id}/activities/{activity_id}` | Update an activity |
| DELETE | `/api/v1/teacher/students/{student_id}/activities/{activity_id}` | Delete an activity |
| POST | `/api/v1/teacher/students/{student_id}/awards` | Create an award |
| PUT | `/api/v1/teacher/students/{student_id}/awards/{award_id}` | Update an award |
| DELETE | `/api/v1/teacher/students/{student_id}/awards/{award_id}` | Delete an award |
| POST | `/api/v1/teacher/students/{student_id}/disciplinary-records` | Create a disciplinary record |
| PUT | `/api/v1/teacher/students/{student_id}/disciplinary-records/{record_id}` | Update a disciplinary record |
| DELETE | `/api/v1/teacher/students/{student_id}/disciplinary-records/{record_id}` | Delete a disciplinary record |
| GET | `/api/v1/teacher/students/{student_id}/fee-summary` | Student fee summary |
| GET | `/api/v1/teacher/students/{student_id}/behavior` | Behavior & conduct |
| GET | `/api/v1/teacher/students/{student_id}/recent-attendance` | Recent attendance records |
| GET | `/api/v1/teacher/students/{student_id}/assignments` | Student assignment submissions |
| PUT | `/api/v1/teacher/students/{student_id}` | Update student info (mentor notes) |
| GET | `/api/v1/teacher/students/{student_id}/mentor-notes` | Get mentor notes for a student |
| PUT | `/api/v1/teacher/students/{student_id}/mentor-notes` | Update mentor notes for a student |

**Query Parameters:**

| Endpoint | Param | Type | Description |
|----------|-------|------|-------------|
| `GET /students` | `page`, `page_size` | int | Pagination |
| `GET /students` | `search` | string? | Search by name/roll |
| `GET /students` | `class_name` | string? | Filter by class |
| `GET /students` | `section` | string? | Filter by section |
| `GET /{id}/exam-results` | `academic_year` | string? | Filter by academic year |
| `GET /{id}/fee-summary` | `academic_year` | string? | Filter by academic year |
| `GET /{id}/recent-attendance` | `limit` | int? | Number of records (default=10) |
| `GET /{id}/assignments` | `academic_year` | string? | Filter by academic year |

---

### Notifications (4)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teacher/notifications/sent` | List notifications sent by this teacher |
| GET | `/api/v1/teacher/notifications` | List notifications (paginated) |
| GET | `/api/v1/teacher/notifications/{notification_id}` | Get notification detail |
| PUT | `/api/v1/teacher/notifications/{notification_id}/read` | Mark notification as read |

**Query Parameters:**

| Endpoint | Param | Type | Description |
|----------|-------|------|-------------|
| `GET /notifications/sent` | `page`, `page_size` | int | Pagination |
| `GET /notifications` | `page`, `page_size` | int | Pagination |
| `GET /notifications` | `type` | string? | Filter by type |
| `GET /notifications` | `is_read` | bool? | Filter by read status |

---

### Timetable (2)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teacher/timetable` | Weekly timetable with stats |
| GET | `/api/v1/teacher/timetable/today` | Today's schedule |

**Query Parameters:**

| Endpoint | Param | Type | Description |
|----------|-------|------|-------------|
| `GET /timetable` | `academic_year` | string? | Filter by academic year |
| `GET /timetable` | `day` | string? | Filter by day of week |
| `GET /timetable/today` | `date` | date? | Target date (defaults to today) |

---

## Summary

| Module | Endpoints | Notes |
|--------|-----------|-------|
| Auth (shared) | 8 | Same as admin/student |
| Dashboard | 12 | KPIs, schedule, reviews, exams, classes, leaves, mentees, adhoc, attendance-status, upcoming-meetings, profile |
| Attendance | 6 | Submit + update + history + cancel + summary |
| Grades | 9 | Submit + update + exams list + publish + report + leaderboard + import/export |
| Assignments | 8 | CRUD + submissions + grading + export |
| Adhoc Classes | 4 | CRUD for extra/substitute classes |
| Leaves | 7 | Balance + holidays + upcoming + history + apply + detail + cancel |
| Students | 25 | List + mentees + detail + results + meetings CRUD + activities CRUD + awards CRUD + disciplinary CRUD + fees + behavior + attendance + assignments + update + mentor-notes |
| Notifications | 4 | Sent + list + detail + mark read |
| Timetable | 2 | Weekly + today |
| **Teacher-specific** | **77** | |
| **Total (incl. shared auth)** | **85** | |
