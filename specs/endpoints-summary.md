# School ERP — Endpoints Summary (All Modules)

## Overview

| Module | V1 Endpoints | V2 Endpoints | Total |
|--------|-------------|-------------|-------|
| Admin | 143 | 9 (Library) | 152 |
| Teacher | 66 | 9 (Quizzes) | 75 |
| Student | 53 | 7 (Quiz Portal) | 60 |
| **Shared (Auth)** | **7** | — | **7** |
| **Grand Total** | **262 V1** | **25 V2** | **287** |

> Note: Auth (7 endpoints) is shared across all 3 modules — counted once in the grand total.
> Total unique: Admin 152 + Teacher 75 + Student 60 = 287 designed endpoints.

---

## V1 Breakdown by Module

### Admin Portal — 143 V1 endpoints

| Module | Endpoints | Type |
|--------|-----------|------|
| Auth | 7 | Shared |
| Dashboard | 7 | Read |
| Students | 12 | CRUD |
| Teachers | 12 | CRUD + Assign |
| Leaves | 10 | CRUD + Approve |
| Timetable | 11 | CRUD + Config |
| Examinations | 16 | CRUD + Results + Analytics |
| Fees | 12 | CRUD + Payments + Receipts |
| Transport | 24 | CRUD (Vehicles + Drivers + Helpers + Routes + Assignments) |
| Staff | 5 | CRUD |
| Payroll | 6 | Run + Generate + Salary Revisions |
| Salary Advances | 5 | CRUD + Approve |
| Notifications | 5 | CRUD + Send |
| Settings | 11 | Config + Bulk Create (classes/sections/subjects) |

### Teacher Portal — 66 V1 endpoints

| Module | Endpoints | Type |
|--------|-----------|------|
| Auth | 7 | Shared |
| Dashboard | 8 | Read |
| My Classes | 4 | Read |
| Student Details | 9 | Read (mentor/class teacher only) |
| Attendance | 6 | Read + Write (Present/Absent/Late) |
| Assignments | 8 | CRUD + Grade + Export |
| Grades | 8 | CRUD + Report + Leaderboard + Import/Export |
| Notifications | 4 | Read + Send (WhatsApp) |
| Timetable | 2 | Read |
| Adhoc Classes | 4 | CRUD |
| Leaves | 6 | Read + Apply + Cancel |

### Student Portal — 53 V1 endpoints

| Module | Endpoints | Type |
|--------|-----------|------|
| Auth | 7 | Shared |
| Dashboard | 10 | Read |
| Timetable | 2 | Read |
| Attendance | 3 | Read |
| Assignments | 4 | Read + Submit |
| Results | 5 | Read + Leaderboard + Download |
| Fees | 6 | Read + Receipt + Reminders |
| Library | 4 | Read |
| Notifications | 3 | Read + Mark as read |
| My Profile | 10 | Read + Edit + Export |

---

## V2 (Deferred)

| Module | Portal | Endpoints | Reason |
|--------|--------|-----------|--------|
| Library | Admin | 9 | Full library management deferred to V2 |
| Quizzes | Teacher | 9 | Quiz creation/management deferred to V2 |
| Quiz Portal | Student | 7 | Quiz taking deferred to V2 |

---

## Statistics

### By HTTP Method (V1 only)

| Method | Admin | Teacher | Student | Total |
|--------|-------|---------|---------|-------|
| GET | 87 | 47 | 46 | 180 |
| POST | 37 | 14 | 2 | 53 |
| PUT | 19 | 5 | 1 | 25 |
| DELETE | 14 | 4 | 0 | 18 |
| **Total** | **157** | **70** | **49** | **276** |

### By Access Pattern

| Pattern | Count | Description |
|---------|-------|-------------|
| Read-only (GET) | 167 | List, detail, stats, export |
| Create (POST) | 51 | New records, submissions, actions |
| Update (PUT) | 24 | Modify existing records |
| Soft-delete (DELETE) | 18 | Deactivate records (never hard delete) |
| File download | 12 | CSV exports, PDF receipts, reports |
| File upload | 3 | Bulk import (CSV), assignment submit |

### By Feature Area (V1, across all modules)

| Feature | Admin | Teacher | Student | Total |
|---------|-------|---------|---------|-------|
| Attendance | 0 | 6 | 3 | 9 |
| Assignments | 0 | 8 | 4 | 12 |
| Examinations/Results | 16 | 8 | 5 | 29 |
| Fees/Payments | 12 | 0 | 6 | 18 |
| Leave Management | 10 | 6 | 0 | 16 |
| Timetable | 11 | 2 | 2 | 15 |
| Transport | 24 | 0 | 0 | 24 |
| Notifications | 5 | 4 | 3 | 12 |
| Student Management | 12 | 9 | 10 | 31 |
| Staff/Teacher Mgmt | 12 | 4 | 0 | 16 |
| Settings/Config | 11 | 0 | 0 | 11 |
| Payroll/Salary | 11 | 0 | 0 | 11 |
| Library | 0 | 0 | 4 | 4 |
| Dashboard | 7 | 8 | 10 | 25 |
| Adhoc Classes | 0 | 4 | 0 | 4 |

---

## Shared Infrastructure

These are NOT counted as separate endpoints but are cross-cutting concerns:

| Concern | Implementation |
|---------|----------------|
| Authentication | 7 shared endpoints (`/api/v1/auth/...`) |
| Multi-tenancy | `X-School-Code` header on every request |
| Pagination | `page` + `page_size` on all list endpoints |
| Soft Delete | `is_active` + `status` on all deletable entities |
| Academic Year | `academic_year` param scopes all transactional data |
| Metadata | `metadata: {}` JSON field on every entity |
| Error Format | Consistent `{ error, code, details }` |
| File Exports | CSV/PDF via download URLs |

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Teacher = Staff (same table) | Shared payroll, leaves, HR. Teaching extensions via extra fields. |
| Academic year scoping | Schools operate in cycles — data partitioned per year. |
| Soft deletes everywhere | Full audit trail, rollback capability, no data loss. |
| UUIDs as primary keys | Multi-tenant safe, merge-friendly, no collisions. |
| `metadata: {}` on every entity | Future features without schema migrations. |
| Configurable enums (Settings) | Admin manages all dropdowns — no code changes needed. |
| Student details restricted | Only mentor/class teacher can view full profiles. |
| WhatsApp for teacher notifications | Primary communication channel for Indian schools. |
| No chat in V1 | Messages/chat deferred; only announcements (one-way) in V1. |

---

## API Versioning

| Path | Status |
|------|--------|
| `/api/v1/auth/...` | Shared auth — all roles |
| `/api/v1/admin/...` | Admin portal (role: admin, super_admin) |
| `/api/v1/teacher/...` | Teacher portal (role: teacher) |
| `/api/v1/student/...` | Student portal (role: student) |

All V1. If breaking changes ever needed → deploy under `/api/v2/` while keeping V1 alive.
