# School ERP Backend - Teacher Portal API Endpoints

## Architecture Overview

```
Teacher Portal API:
├── Runtime: Node.js / Python (Django/FastAPI)
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

4. **Read-heavy, limited writes** — Teachers can CREATE/UPDATE attendance, assignments, grades, quizzes, and notifications for their own classes. They can READ their timetable, student details, and dashboard data. They can APPLY for leaves (admin approves/rejects).

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
| `X-School-Code` | School tenant identifier | Yes (except /auth/login/) |
| `Cookie` | httpOnly auth cookies (sent automatically) | Yes (after login) |

### Pagination Convention

All list endpoints support:

| Param | Default | Description |
|-------|---------|-------------|
| `page` | 1 | Page number |
| `page_size` | 20 | Items per page (max 100) |

Response shape: `{ count, page, page_size, total_pages, results[] }`

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200  | Success / Soft-delete successful |
| 201  | Created |
| 400  | Bad Request (validation error) |
| 401  | Unauthorized (not logged in / token expired) |
| 403  | Forbidden (not assigned to this class / insufficient role) |
| 404  | Not Found |
| 409  | Conflict (duplicate entry) |
| 422  | Unprocessable Entity |
| 500  | Internal Server Error |

### Error Response Format

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

## All Endpoints (65 Teacher-specific + 7 Shared Auth = 72 total)

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

### Dashboard (8)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teacher/dashboard/stats/` | KPI cards (total students, pending reviews, upcoming exams, classes today) |
| GET | `/api/v1/teacher/dashboard/today-schedule/` | Today's class schedule (time, class, subject, duration) |
| GET | `/api/v1/teacher/dashboard/pending-reviews/` | Assignments pending review |
| GET | `/api/v1/teacher/dashboard/upcoming-exams/` | Upcoming exams for teacher's classes |
| GET | `/api/v1/teacher/dashboard/classes-summary/` | My Classes with progress (attendance %, assignments %) |
| GET | `/api/v1/teacher/dashboard/leave-updates/` | Recent leave applications + their status |
| GET | `/api/v1/teacher/dashboard/mentees-summary/` | My Mentees quick list |
| GET | `/api/v1/teacher/dashboard/adhoc-classes/` | Adhoc/substitute classes (past + upcoming) |

---

### My Classes (4)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teacher/classes/` | List teacher's assigned classes with subject & student count |
| GET | `/api/v1/teacher/classes/:class_id/students/` | List students in a specific class (teacher must be assigned) |
| GET | `/api/v1/teacher/mentees/` | List teacher's assigned mentees |
| GET | `/api/v1/teacher/mentees/:student_id/` | Get mentee details with mentoring info |

---

### Student Details (9)

> **Access Control:** Full student profile is ONLY accessible if the teacher is:
> - The student's **assigned mentor**, OR
> - The **class teacher** for the student's class
>
> Subject teachers (who only teach a class) can access class-level data (attendance, grades, assignments) but NOT individual student profiles. Returns 403 for unauthorized access.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teacher/students/` | List students (mentor's mentees + class teacher's students only) |
| GET | `/api/v1/teacher/students/:id/` | Get student full profile (mentor/class teacher only) |
| GET | `/api/v1/teacher/students/:id/exam-results/` | Exam results + performance analysis charts data |
| GET | `/api/v1/teacher/students/:id/parent-meetings/` | Parent meeting history |
| GET | `/api/v1/teacher/students/:id/activities/` | Extra-curricular activities + awards |
| GET | `/api/v1/teacher/students/:id/fee-summary/` | Fee structure + payments + download receipt |
| GET | `/api/v1/teacher/students/:id/behavior/` | Behavior, conduct notes, disciplinary records |
| GET | `/api/v1/teacher/students/:id/recent-attendance/` | Recent attendance records |
| GET | `/api/v1/teacher/students/:id/assignments/` | Assignment submissions for this student |

---

### Attendance (6)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teacher/attendance/` | Get attendance for class + date (form data) |
| POST | `/api/v1/teacher/attendance/` | Submit attendance (Present/Absent/Late per student) |
| PUT | `/api/v1/teacher/attendance/` | Update attendance (corrections) |
| GET | `/api/v1/teacher/attendance/history/` | Past submissions list (with counts) |
| DELETE | `/api/v1/teacher/attendance/:id/` | Soft-delete attendance record |
| GET | `/api/v1/teacher/attendance/summary/` | Attendance summary stats for a class |

---

### Assignments (8)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teacher/assignments/` | List assignments + KPI summary |
| POST | `/api/v1/teacher/assignments/` | Create assignment (class + section + due + marks) |
| GET | `/api/v1/teacher/assignments/:id/` | Get assignment details + submission stats |
| PUT | `/api/v1/teacher/assignments/:id/` | Update assignment |
| DELETE | `/api/v1/teacher/assignments/:id/` | Soft-delete assignment |
| GET | `/api/v1/teacher/assignments/:id/submissions/` | List submissions (graded/pending review) |
| POST | `/api/v1/teacher/assignments/:id/submissions/:submission_id/grade/` | Grade a submission |
| GET | `/api/v1/teacher/assignments/:id/submissions/export/` | Export submissions CSV |

---

### Grades (8)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teacher/grades/` | Get grades for class + exam (with KPI stats) |
| POST | `/api/v1/teacher/grades/` | Submit grades (bulk) for a class + exam |
| PUT | `/api/v1/teacher/grades/` | Update grades for a class + exam |
| GET | `/api/v1/teacher/grades/exams/` | List available exams for grading |
| GET | `/api/v1/teacher/grades/report/` | Exam report (marks + grade distribution) |
| GET | `/api/v1/teacher/grades/leaderboard/` | Ranked leaderboard for exam + class |
| POST | `/api/v1/teacher/grades/import/` | Import grades from CSV |
| GET | `/api/v1/teacher/grades/export/` | Export grades report (CSV/PDF) |

---

### Quizzes (9) — Moved to V2

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teacher/quizzes/` | List quizzes + KPIs (total, active, drafts, total attempts) |
| POST | `/api/v1/teacher/quizzes/` | Create quiz (title, subject, chapter, class, difficulty, duration, questions, passing %, dates, negative marking) |
| GET | `/api/v1/teacher/quizzes/:id/` | Get quiz details + attempt stats |
| PUT | `/api/v1/teacher/quizzes/:id/` | Update quiz (title, subject, chapter, class, difficulty, duration, passing %, dates, description) |
| DELETE | `/api/v1/teacher/quizzes/:id/` | Soft-delete quiz |
| POST | `/api/v1/teacher/quizzes/:id/publish/` | Publish a draft quiz |
| POST | `/api/v1/teacher/quizzes/:id/duplicate/` | Duplicate an existing quiz |
| GET | `/api/v1/teacher/quizzes/:id/leaderboard/` | Leaderboard (total attempts, avg score, highest, pass rate, ranked table with time taken) |
| GET | `/api/v1/teacher/quizzes/:id/questions/` | Get/manage questions for a quiz |

---

### Notifications & Messaging (4)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teacher/notifications/` | List sent messages + KPI stats |
| POST | `/api/v1/teacher/notifications/` | Send WhatsApp message (immediate or scheduled) |
| GET | `/api/v1/teacher/notifications/:id/` | Get message details + delivery stats |
| GET | `/api/v1/teacher/notifications/recipients/` | Get recipient groups + class filtering |

---

### Timetable (2)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teacher/timetable/` | Weekly timetable + KPIs + day filter (type: Lecture/Practical/Free/Break) |
| GET | `/api/v1/teacher/timetable/today/` | Today's schedule with stats |

---

### Adhoc Classes (4)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teacher/adhoc-classes/` | List adhoc/substitute classes (past + upcoming) |
| POST | `/api/v1/teacher/adhoc-classes/` | Create/log an adhoc class |
| PUT | `/api/v1/teacher/adhoc-classes/:id/` | Update adhoc class (mark done, add notes) |
| DELETE | `/api/v1/teacher/adhoc-classes/:id/` | Soft-delete adhoc class |

---

### Leaves (6)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teacher/leaves/balance/` | Leave balance per type + overall summary |
| GET | `/api/v1/teacher/leaves/` | Leave history (filter: status, type) |
| GET | `/api/v1/teacher/leaves/upcoming/` | Upcoming/planned leaves (future dates) |
| POST | `/api/v1/teacher/leaves/` | Apply for leave (type, dates, reason) |
| GET | `/api/v1/teacher/leaves/:id/` | Get leave application details |
| DELETE | `/api/v1/teacher/leaves/:id/` | Cancel a pending leave |

---

## Summary

| Module | Endpoints | Notes |
|--------|-----------|-------|
| Auth (shared) | 7 | Same as admin module |
| Dashboard | 8 | KPIs, schedule, classes summary, leave updates, mentees, adhoc |
| My Classes | 4 | Class cards + students + mentees |
| Student Details | 9 | Read-only profiles + transport, attendance, assignments |
| Attendance | 6 | Write access (Present/Absent/Late) + history |
| Assignments | 8 | CRUD + grade submissions + export |
| Grades | 8 | Grade + report + leaderboard + import/export |
| Quizzes | 9 | **Moved to V2** |
| Notifications | 4 | WhatsApp messaging + scheduling |
| Timetable | 2 | Read-only (own schedule) |
| Adhoc Classes | 4 | Substitute/extra class tracking |
| Leaves | 6 | Balance + history + upcoming + apply/cancel |
| **V1 Teacher-specific** | **59** | |
| **V2 (Quizzes)** | **9** | |
| **Total (incl. shared auth)** | **75 (66 V1 + 9 V2)** | |
