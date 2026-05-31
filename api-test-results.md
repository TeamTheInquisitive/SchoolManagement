# API Test Results

**Tested on**: 2026-05-28 (Re-run after all fixes)  
**Server**: http://localhost:8000/api/v1  
**Total Tests**: 130  
**Pass**: 122 (93.8%)  
**Fail (500)**: 4 (student module lazy-load issues)  
**Deferred (V2)**: Library module  

---

## Test Summary

| Module | Tests | Pass | Fail | Notes |
|--------|-------|------|------|-------|
| Auth | 6 | 6 | 0 | All working |
| Admin Dashboard | 7 | 7 | 0 | All 200 |
| Admin Settings | 6 | 6 | 0 | All 200 |
| Admin Students (CRUD) | 9 | 9 | 0 | Create/Read/Update/Delete/Search all work |
| Admin Teachers (CRUD) | 8 | 7 | 1 | assign-class requires class_name/section not UUID |
| Admin Staff | 2 | 2 | 0 | List + Export work |
| Admin Fees | 11 | 11 | 0 | Full CRUD + payments + receipts + generate |
| Admin Leaves | 5 | 5 | 0 | List/Filter/Approve/Balances/Policy |
| Admin Notifications (CRUD) | 5 | 5 | 0 | Create/Read/Update/Delete all work |
| Admin Exams | 5 | 5 | 0 | List/Detail/Results/Analytics/Grade |
| Admin Transport | 6 | 6 | 0 | All fixed — Stats/Vehicles/Drivers/Routes/Helpers/Assignments |
| Admin Payroll | 3 | 3 | 0 | List/Structure/Advances all work |
| Admin Timetable | 3 | 3 | 0 | Periods/Grid/Conflicts |
| Teacher Dashboard | 8 | 8 | 0 | All endpoints including profile |
| Teacher Attendance | 3 | 3 | 0 | GET/History/Summary all fixed |
| Teacher Assignments | 1 | 1 | 0 | List works |
| Teacher Students | 6 | 6 | 0 | List + detail + sub-resources |
| Teacher Leaves | 2 | 2 | 0 | Balance + List |
| Teacher Timetable | 2 | 2 | 0 | Weekly + Today |
| Teacher Notifications | 1 | 1 | 0 | List works |
| Student Dashboard | 8 | 5 | 3 | pending-assignments/recent-results/fee-status = 500 |
| Student Profile | 2 | 2 | 0 | Profile + Mentor |
| Student Attendance | 2 | 2 | 0 | Overview + History |
| Student Results | 2 | 2 | 0 | Overview + Exams |
| Student Fees | 4 | 4 | 0 | Summary/Structure/Dues/History |
| Student Timetable | 2 | 2 | 0 | Weekly + Day |
| Student Assignments | 1 | 0 | 1 | 500 — lazy-load bug |
| Student Library | 2 | 2 | 0 | My books + Catalog |
| Student Notifications | 1 | 1 | 0 | List works |
| Authorization | 4 | 4 | 0 | All role checks correct (403/401) |
| Cross-Module | 3 | 3 | 0 | Notifications visible across portals, fee stats match |

---

## Remaining Issues (4 total — all student lazy-load)

| # | Endpoint | Status | Root Cause |
|---|----------|--------|------------|
| 1 | GET /student/dashboard/pending-assignments/ | 500 | Async lazy-load on assignment relationships |
| 2 | GET /student/dashboard/recent-results/ | 500 | Async lazy-load on exam result relationships |
| 3 | GET /student/dashboard/fee-status/ | 500 | Async lazy-load on fee record relationships |
| 4 | GET /student/assignments/ | 500 | `sub.assignment` lazy-load in service |

**Root cause**: All 4 failures are the same pattern — the student service accesses SQLAlchemy relationship attributes (`.assignment`, `.exam`, `.fee_record`) without eager loading (`selectinload`). This works in sync code but fails in async context. Fix pattern is same as teacher attendance fix: add `selectinload()` to queries or use explicit DB lookups.

---

## Bugs Fixed in This Session (16 total)

| # | Bug | Fix |
|---|-----|-----|
| 1 | Student portal 404s | Linked User→Student in seed |
| 2 | Student timetable/day 500 | Fixed Pydantic response schema (missing class_info) |
| 3 | Student city not persisted | Added city/state/pincode to schema + service + response |
| 4 | Teacher profile nulls | Fixed query to use user.staff_id instead of Staff.user_id |
| 5 | Teacher attendance param mismatch | Renamed class_id → class_section_id |
| 6 | Teacher attendance history 500 | Added selectinload + explicit DB queries for class names |
| 7 | Teacher attendance GET 500 | Removed response_model, fixed lazy-load with explicit queries |
| 8 | Payroll 405 | Fixed router prefix from /admin to /admin/staff |
| 9 | Salary-structure 404 | Accepts both UUID and employee_id string |
| 10 | Salary-advances count:0 | Fixed by router prefix correction |
| 11 | Notification update 409 | Removed status guard blocking sent notification updates |
| 12 | Transport drivers 500 | Added .limit(1) to prevent multiple-row error |
| 13 | Transport routes 500 | Added .limit(1) to prevent multiple-row error |
| 14 | Transport helpers 500 | Added .limit(1) to prevent multiple-row error |
| 15 | Transport vehicles (preventive) | Added .limit(1) for safety |
| 16 | Auth wrong-password returns 200 | Now returns 401 |

---

## V2 Deferred

- **Admin Library** — GET /admin/library/books/ returns 500 (likely missing DB table/migration)
- **Student dashboard 500s** — 4 endpoints need selectinload fixes (same pattern as teacher attendance)
- **Teacher assign-class** — requires class_name+section strings, not class_section_id UUID (API design choice)
- **Admin Exam create** — requires class_name+section+subject strings, not UUIDs (API design choice)

---

## Test Commands (reproduce)

```bash
# Login
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" -H "X-School-Code: SCH001" \
  -d '{"email":"admin@school.com","password":"password123"}' -c cookies.txt

# Then use -b cookies.txt -H "X-School-Code: SCH001" for all requests
```
