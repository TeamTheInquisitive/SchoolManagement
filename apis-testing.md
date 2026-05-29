# API Testing Reference

Base URL: `http://localhost:8000/api/v1`

## Authentication

All requests (except login) require:
- Cookie: `access_token` (auto-set on login)
- Header: `X-School-Code: SCH001`

### Login first:
```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -H "X-School-Code: SCH001" \
  -d '{"email":"admin@school.com","password":"password123"}' \
  -c cookies.txt
```

---

## 1. AUTH MODULE

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 1 | POST | `/auth/login` | Login with email/password | Create (session) |
| 2 | POST | `/auth/logout` | Logout, invalidate token | Delete (session) |
| 3 | POST | `/auth/refresh-token` | Refresh access token | Update (session) |
| 4 | GET | `/auth/me` | Get current user profile | Read |
| 5 | POST | `/auth/forgot-password` | Request password reset email | Create (reset token) |
| 6 | POST | `/auth/reset-password` | Reset password with token | Update |
| 7 | POST | `/auth/change-password` | Change password (logged in) | Update |

---

## 2. ADMIN — DASHBOARD

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 8 | GET | `/admin/dashboard/stats/` | KPI stats (students, staff, fees, attendance) | Read |
| 9 | GET | `/admin/dashboard/attendance-trends/` | Attendance trends chart data | Read |
| 10 | GET | `/admin/dashboard/fee-collection-status/` | Fee collection summary | Read |
| 11 | GET | `/admin/dashboard/student-distribution/` | Student count per class | Read |
| 12 | GET | `/admin/dashboard/recent-activities/` | Recent system activities | Read |
| 13 | GET | `/admin/dashboard/leave-overview/` | Leave applications overview | Read |
| 14 | GET | `/admin/dashboard/low-attendance/` | Students with low attendance | Read |

---

## 3. ADMIN — STUDENTS

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 15 | GET | `/admin/students/` | List all students (paginated, filterable) | List |
| 16 | POST | `/admin/students/` | Create a new student | Create |
| 17 | GET | `/admin/students/export/` | Export students to CSV/Excel | Read |
| 18 | POST | `/admin/students/bulk-import/` | Bulk import students from file | Create |
| 19 | GET | `/admin/students/{student_id}/` | Get student detail | Read |
| 20 | PUT | `/admin/students/{student_id}/` | Update student | Update |
| 21 | DELETE | `/admin/students/{student_id}/` | Soft-delete student | Delete |
| 22 | GET | `/admin/students/{student_id}/exam-results/` | Student's exam results | Read |
| 23 | GET | `/admin/students/{student_id}/parent-meetings/` | Student's parent meetings | Read |
| 24 | GET | `/admin/students/{student_id}/activities/` | Student's activities & awards | Read |
| 25 | GET | `/admin/students/{student_id}/fee-history/` | Student's fee payment history | Read |
| 26 | GET | `/admin/students/{student_id}/disciplinary-records/` | Student's disciplinary records | Read |

---

## 4. ADMIN — TEACHERS

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 27 | GET | `/admin/teachers/` | List all teachers (paginated) | List |
| 28 | POST | `/admin/teachers/` | Create a new teacher | Create |
| 29 | GET | `/admin/teachers/export/` | Export teachers to CSV/Excel | Read |
| 30 | GET | `/admin/teachers/by-class/` | Get teachers grouped by class | Read |
| 31 | GET | `/admin/teachers/{teacher_id}/` | Get teacher detail | Read |
| 32 | PUT | `/admin/teachers/{teacher_id}/` | Update teacher | Update |
| 33 | DELETE | `/admin/teachers/{teacher_id}/` | Soft-delete teacher | Delete |
| 34 | POST | `/admin/teachers/{teacher_id}/assign-class/` | Assign teacher to a class-section-subject | Create |
| 35 | POST | `/admin/teachers/{teacher_id}/bulk-assign/` | Bulk assign classes | Create |
| 36 | GET | `/admin/teachers/{teacher_id}/assignments/` | Get teacher's class assignments | Read |
| 37 | DELETE | `/admin/teachers/{teacher_id}/assignments/{assignment_id}/` | Remove class assignment | Delete |
| 38 | GET | `/admin/teachers/{teacher_id}/history/` | Teacher activity history | Read |

---

## 5. ADMIN — STAFF

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 39 | GET | `/admin/staff/` | List all staff (paginated) | List |
| 40 | POST | `/admin/staff/` | Create staff member | Create |
| 41 | GET | `/admin/staff/export/` | Export staff to CSV/Excel | Read |
| 42 | PUT | `/admin/staff/{staff_id}/` | Update staff member | Update |
| 43 | DELETE | `/admin/staff/{staff_id}/` | Soft-delete staff | Delete |

---

## 6. ADMIN — EXAMINATIONS

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 44 | GET | `/admin/examinations/` | List all exams (filterable) | List |
| 45 | POST | `/admin/examinations/` | Create a new exam | Create |
| 46 | GET | `/admin/examinations/grade-system/` | Get grading system | Read |
| 47 | PUT | `/admin/examinations/grade-system/` | Update grading system | Update |
| 48 | GET | `/admin/examinations/analytics/` | Exam analytics (pass %, avg marks) | Read |
| 49 | GET | `/admin/examinations/report-card/{student_id}/` | Generate student report card | Read |
| 50 | POST | `/admin/examinations/report-card/generate/` | Bulk generate report cards | Create |
| 51 | GET | `/admin/examinations/schedule/` | Exam schedule calendar | Read |
| 52 | GET | `/admin/examinations/{exam_id}/` | Get exam detail | Read |
| 53 | PUT | `/admin/examinations/{exam_id}/` | Update exam | Update |
| 54 | DELETE | `/admin/examinations/{exam_id}/` | Cancel/delete exam | Delete |
| 55 | GET | `/admin/examinations/{exam_id}/results/` | Get exam results | Read |
| 56 | POST | `/admin/examinations/{exam_id}/results/` | Enter results for an exam | Create |
| 57 | POST | `/admin/examinations/{exam_id}/results/bulk-upload/` | Bulk upload results from file | Create |
| 58 | PUT | `/admin/examinations/{exam_id}/results/{result_id}/` | Update a single result | Update |
| 59 | POST | `/admin/examinations/{exam_id}/publish/` | Publish exam results | Update |

---

## 7. ADMIN — FEES

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 60 | GET | `/admin/fees/` | List all fee records (filterable) | List |
| 61 | POST | `/admin/fees/` | Create a fee record | Create |
| 62 | GET | `/admin/fees/export/` | Export fee data to CSV/Excel | Read |
| 63 | GET | `/admin/fees/student/{student_id}/` | Get student's fee records | Read |
| 64 | GET | `/admin/fees/student/{student_id}/receipt/` | Consolidated fee receipt | Read |
| 65 | GET | `/admin/fees/{fee_id}/` | Get fee record detail | Read |
| 66 | GET | `/admin/fees/{fee_id}/receipt/` | Get individual fee receipt | Read |
| 67 | POST | `/admin/fees/generate-due/` | Generate fee dues for class | Create |
| 68 | POST | `/admin/fees/{fee_id}/record-payment/` | Record a payment against fee | Create |
| 69 | POST | `/admin/fees/{fee_id}/apply-late-fee/` | Apply late fee penalty | Create |
| 70 | POST | `/admin/fees/bulk-apply-late-fees/` | Bulk apply late fees | Create |
| 71 | POST | `/admin/fees/send-reminder/` | Send fee reminder notification | Create |

---

## 8. ADMIN — LEAVES

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 72 | GET | `/admin/leaves/` | List all leave applications | List |
| 73 | GET | `/admin/leaves/teacher/{teacher_id}/` | Get teacher's leave detail | Read |
| 74 | GET | `/admin/leaves/balances/` | Get all staff leave balances | Read |
| 75 | GET | `/admin/leaves/policy/` | Get leave policy config | Read |
| 76 | PUT | `/admin/leaves/policy/` | Update leave policy | Update |
| 77 | POST | `/admin/leaves/{leave_id}/approve/` | Approve leave application | Update |
| 78 | POST | `/admin/leaves/{leave_id}/reject/` | Reject leave application | Update |
| 79 | POST | `/admin/leaves/{leave_id}/cancel/` | Cancel leave application | Update |
| 80 | POST | `/admin/leaves/bulk-action/` | Bulk approve/reject leaves | Update |
| 81 | GET | `/admin/leaves/calendar/` | Leave calendar view | Read |
| 82 | POST | `/admin/leaves/allocate/` | Allocate leave balance to staff | Create |

---

## 9. ADMIN — NOTIFICATIONS

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 83 | GET | `/admin/notifications/` | List all notifications | List |
| 84 | POST | `/admin/notifications/` | Create/send notification | Create |
| 85 | GET | `/admin/notifications/{notification_id}/` | Get notification detail | Read |
| 86 | PUT | `/admin/notifications/{notification_id}/` | Update notification | Update |
| 87 | DELETE | `/admin/notifications/{notification_id}/` | Archive/delete notification | Delete |

---

## 10. ADMIN — PAYROLL

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 88 | GET | `/admin/staff/payroll/` | List payroll (payslips) | List |
| 89 | POST | `/admin/staff/payroll/run/` | Run payroll for month | Create |
| 90 | POST | `/admin/staff/payroll/generate-payslips/` | Generate payslips | Create |
| 91 | GET | `/admin/staff/payroll/salary-structure/{employee_id}/` | Get salary structure | Read |
| 92 | GET | `/admin/staff/salary-advances/` | List salary advances | List |
| 93 | POST | `/admin/staff/salary-advances/` | Create salary advance request | Create |
| 94 | POST | `/admin/staff/salary-advances/{advance_id}/approve/` | Approve advance | Update |
| 95 | POST | `/admin/staff/salary-advances/{advance_id}/reject/` | Reject advance | Update |
| 96 | POST | `/admin/staff/salary-advances/{advance_id}/disburse/` | Disburse advance | Update |
| 97 | GET | `/admin/staff/payroll/salary-revisions/{staff_id}/` | Get salary revision history | Read |
| 98 | POST | `/admin/staff/payroll/salary-revisions/` | Create salary revision | Create |

---

## 11. ADMIN — TIMETABLE

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 99 | GET | `/admin/timetable/periods/` | List period configurations | List |
| 100 | POST | `/admin/timetable/periods/` | Create a period | Create |
| 101 | PUT | `/admin/timetable/periods/{period_id}/` | Update a period | Update |
| 102 | DELETE | `/admin/timetable/periods/{period_id}/` | Delete a period | Delete |
| 103 | GET | `/admin/timetable/` | Get timetable grid (class+day) | Read |
| 104 | POST | `/admin/timetable/slot/` | Create timetable slot | Create |
| 105 | PUT | `/admin/timetable/slot/{slot_id}/` | Update timetable slot | Update |
| 106 | DELETE | `/admin/timetable/slot/{slot_id}/` | Delete timetable slot | Delete |
| 107 | POST | `/admin/timetable/bulk-assign/` | Bulk assign timetable slots | Create |
| 108 | GET | `/admin/timetable/teacher/{teacher_id}/` | Get teacher's timetable | Read |
| 109 | GET | `/admin/timetable/conflicts/` | Detect scheduling conflicts | Read |

---

## 12. ADMIN — TRANSPORT

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 110 | GET | `/admin/transport/stats/` | Transport KPI stats | Read |
| 111 | GET | `/admin/transport/vehicles/` | List vehicles | List |
| 112 | POST | `/admin/transport/vehicles/` | Create vehicle | Create |
| 113 | GET | `/admin/transport/vehicles/export/` | Export vehicles CSV | Read |
| 114 | GET | `/admin/transport/vehicles/{vehicle_id}/` | Get vehicle detail | Read |
| 115 | PUT | `/admin/transport/vehicles/{vehicle_id}/` | Update vehicle | Update |
| 116 | DELETE | `/admin/transport/vehicles/{vehicle_id}/` | Delete vehicle | Delete |
| 117 | GET | `/admin/transport/drivers/` | List drivers | List |
| 118 | POST | `/admin/transport/drivers/` | Create driver | Create |
| 119 | GET | `/admin/transport/drivers/export/` | Export drivers CSV | Read |
| 120 | PUT | `/admin/transport/drivers/{driver_id}/` | Update driver | Update |
| 121 | DELETE | `/admin/transport/drivers/{driver_id}/` | Delete driver | Delete |
| 122 | GET | `/admin/transport/helpers/` | List helpers | List |
| 123 | POST | `/admin/transport/helpers/` | Create helper | Create |
| 124 | PUT | `/admin/transport/helpers/{helper_id}/` | Update helper | Update |
| 125 | DELETE | `/admin/transport/helpers/{helper_id}/` | Delete helper | Delete |
| 126 | GET | `/admin/transport/routes/` | List routes | List |
| 127 | POST | `/admin/transport/routes/` | Create route | Create |
| 128 | PUT | `/admin/transport/routes/{route_id}/` | Update route | Update |
| 129 | DELETE | `/admin/transport/routes/{route_id}/` | Delete route | Delete |
| 130 | GET | `/admin/transport/assignments/` | List route assignments | List |
| 131 | POST | `/admin/transport/assignments/` | Create route assignment | Create |
| 132 | PUT | `/admin/transport/assignments/{assignment_id}/` | Update route assignment | Update |
| 133 | DELETE | `/admin/transport/assignments/{assignment_id}/` | Delete route assignment | Delete |

---

## 13. ADMIN — LIBRARY

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 134 | GET | `/admin/library/books/` | List all books (search, filter) | List |
| 135 | POST | `/admin/library/books/` | Add a new book | Create |
| 136 | POST | `/admin/library/issue/` | Issue book to student/staff | Create |
| 137 | POST | `/admin/library/return/` | Return a book | Update |
| 138 | GET | `/admin/library/issued/` | List currently issued books | List |
| 139 | GET | `/admin/library/overdue/` | List overdue books | Read |

---

## 14. ADMIN — SETTINGS

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 140 | GET | `/admin/settings/` | Get all settings | Read |
| 141 | PUT | `/admin/settings/` | Update settings | Update |
| 142 | GET | `/admin/settings/school-profile/` | Get school profile | Read |
| 143 | PUT | `/admin/settings/school-profile/` | Update school profile | Update |
| 144 | GET | `/admin/settings/academic-year/` | Get academic year config | Read |
| 145 | PUT | `/admin/settings/academic-year/` | Update academic year | Update |
| 146 | GET | `/admin/settings/enums/{category}/` | Get enum values (fee types, etc.) | Read |
| 147 | PUT | `/admin/settings/enums/{category}/` | Update enum values | Update |
| 148 | POST | `/admin/settings/classes/bulk/` | Bulk create classes | Create |
| 149 | POST | `/admin/settings/sections/bulk/` | Bulk create sections | Create |
| 150 | POST | `/admin/settings/subjects/bulk/` | Bulk create subjects | Create |
| 151 | GET | `/admin/settings/class-sections/` | List class-sections | Read |
| 152 | GET | `/admin/settings/subjects/` | List subjects | Read |

---

## 15. TEACHER — DASHBOARD

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 153 | GET | `/teacher/dashboard/stats/` | Teacher KPI stats | Read |
| 154 | GET | `/teacher/dashboard/today-schedule/` | Today's class schedule | Read |
| 155 | GET | `/teacher/dashboard/pending-reviews/` | Assignments pending review | Read |
| 156 | GET | `/teacher/dashboard/upcoming-exams/` | Upcoming exams | Read |
| 157 | GET | `/teacher/dashboard/classes-summary/` | Classes with student counts | Read |
| 158 | GET | `/teacher/dashboard/leave-updates/` | Recent leave status | Read |
| 159 | GET | `/teacher/dashboard/mentees-summary/` | Mentees list | Read |
| 160 | GET | `/teacher/dashboard/adhoc-classes/` | Adhoc/substitute classes | Read |
| 161 | GET | `/teacher/dashboard/profile/` | Teacher profile | Read |

---

## 16. TEACHER — ATTENDANCE

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 162 | GET | `/teacher/attendance/` | Get attendance for class+date | Read |
| 163 | POST | `/teacher/attendance/` | Submit attendance | Create |
| 164 | PUT | `/teacher/attendance/` | Update submitted attendance | Update |
| 165 | GET | `/teacher/attendance/history/` | Attendance history | List |
| 166 | DELETE | `/teacher/attendance/{session_id}/` | Cancel attendance session | Delete |
| 167 | GET | `/teacher/attendance/summary/` | Attendance summary stats | Read |

---

## 17. TEACHER — ASSIGNMENTS

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 168 | GET | `/teacher/assignments/` | List assignments | List |
| 169 | POST | `/teacher/assignments/` | Create assignment | Create |
| 170 | GET | `/teacher/assignments/{assignment_id}/` | Get assignment detail | Read |
| 171 | PUT | `/teacher/assignments/{assignment_id}/` | Update assignment | Update |
| 172 | DELETE | `/teacher/assignments/{assignment_id}/` | Delete assignment | Delete |
| 173 | GET | `/teacher/assignments/{assignment_id}/submissions/` | List submissions | Read |
| 174 | POST | `/teacher/assignments/{assignment_id}/submissions/{submission_id}/grade/` | Grade a submission | Update |
| 175 | GET | `/teacher/assignments/{assignment_id}/submissions/export/` | Export submissions | Read |

---

## 18. TEACHER — GRADES

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 176 | GET | `/teacher/grades/` | List grades | List |
| 177 | POST | `/teacher/grades/` | Submit grades | Create |
| 178 | PUT | `/teacher/grades/` | Update grades | Update |
| 179 | GET | `/teacher/grades/exams/` | Exams available for grading | Read |
| 180 | GET | `/teacher/grades/report/` | Grade report | Read |
| 181 | GET | `/teacher/grades/leaderboard/` | Class leaderboard | Read |
| 182 | POST | `/teacher/grades/import/` | Import grades from file | Create |
| 183 | GET | `/teacher/grades/export/` | Export grades | Read |

---

## 19. TEACHER — LEAVES

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 184 | GET | `/teacher/leaves/balance/` | Get leave balances | Read |
| 185 | GET | `/teacher/leaves/upcoming/` | Upcoming approved leaves | Read |
| 186 | GET | `/teacher/leaves/` | Leave application history | List |
| 187 | POST | `/teacher/leaves/` | Apply for leave | Create |
| 188 | GET | `/teacher/leaves/{leave_id}/` | Get leave detail | Read |
| 189 | DELETE | `/teacher/leaves/{leave_id}/` | Cancel leave application | Delete |

---

## 20. TEACHER — STUDENTS

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 190 | GET | `/teacher/students/` | List accessible students | List |
| 191 | GET | `/teacher/students/{student_id}/` | Get student detail | Read |
| 192 | GET | `/teacher/students/{student_id}/exam-results/` | Student exam results | Read |
| 193 | GET | `/teacher/students/{student_id}/parent-meetings/` | Student parent meetings | Read |
| 194 | GET | `/teacher/students/{student_id}/activities/` | Student activities | Read |
| 195 | GET | `/teacher/students/{student_id}/fee-summary/` | Student fee summary | Read |
| 196 | GET | `/teacher/students/{student_id}/behavior/` | Student behavior/conduct | Read |
| 197 | GET | `/teacher/students/{student_id}/recent-attendance/` | Student recent attendance | Read |
| 198 | GET | `/teacher/students/{student_id}/assignments/` | Student assignments | Read |

---

## 21. TEACHER — TIMETABLE

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 199 | GET | `/teacher/timetable/` | Weekly timetable | Read |
| 200 | GET | `/teacher/timetable/today/` | Today's schedule | Read |

---

## 22. TEACHER — ADHOC CLASSES

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 201 | GET | `/teacher/adhoc-classes/` | List adhoc/substitute classes | List |
| 202 | POST | `/teacher/adhoc-classes/` | Create adhoc class | Create |
| 203 | PUT | `/teacher/adhoc-classes/{adhoc_id}/` | Update adhoc class | Update |
| 204 | DELETE | `/teacher/adhoc-classes/{adhoc_id}/` | Delete adhoc class | Delete |

---

## 23. TEACHER — NOTIFICATIONS

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 205 | GET | `/teacher/notifications/` | List notifications | List |
| 206 | GET | `/teacher/notifications/{notification_id}/` | Get notification detail | Read |
| 207 | PUT | `/teacher/notifications/{notification_id}/read/` | Mark as read | Update |

---

## 24. STUDENT — DASHBOARD

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 208 | GET | `/student/dashboard/stats/` | Student KPI stats | Read |
| 209 | GET | `/student/dashboard/today-schedule/` | Today's schedule | Read |
| 210 | GET | `/student/dashboard/pending-assignments/` | Pending assignments | Read |
| 211 | GET | `/student/dashboard/upcoming-exams/` | Upcoming exams | Read |
| 212 | GET | `/student/dashboard/subject-attendance/` | Subject-wise attendance | Read |
| 213 | GET | `/student/dashboard/recent-results/` | Recent exam results | Read |
| 214 | GET | `/student/dashboard/announcements/` | School announcements | Read |
| 215 | GET | `/student/dashboard/notifications/` | Notifications | Read |
| 216 | GET | `/student/dashboard/fee-status/` | Fee payment status | Read |
| 217 | GET | `/student/dashboard/parent-meetings/` | Upcoming parent meetings | Read |

---

## 25. STUDENT — PROFILE

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 218 | GET | `/student/profile/` | Get student profile | Read |
| 219 | PUT | `/student/profile/` | Update profile (limited fields) | Update |
| 220 | GET | `/student/profile/mentor/` | Get assigned mentor | Read |

---

## 26. STUDENT — ATTENDANCE

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 221 | GET | `/student/attendance/` | Attendance overview | Read |
| 222 | GET | `/student/attendance/history/` | Attendance history (date range) | List |
| 223 | GET | `/student/attendance/warnings/` | Low attendance warnings | Read |
| 224 | GET | `/student/attendance/summary/` | Attendance summary | Read |
| 225 | GET | `/student/attendance/monthly/` | Monthly attendance breakdown | Read |

---

## 27. STUDENT — ASSIGNMENTS

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 226 | GET | `/student/assignments/` | List assignments | List |
| 227 | GET | `/student/assignments/{assignment_id}/` | Get assignment detail | Read |
| 228 | POST | `/student/assignments/{assignment_id}/submit/` | Submit assignment | Create |
| 229 | GET | `/student/assignments/{assignment_id}/submission/` | Get my submission | Read |

---

## 28. STUDENT — RESULTS

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 230 | GET | `/student/results/` | Results overview | Read |
| 231 | GET | `/student/results/exams/` | List exam results | List |
| 232 | GET | `/student/results/download-report/` | Download report card | Read |
| 233 | GET | `/student/results/exam/{exam_id}/` | Get specific exam result | Read |
| 234 | GET | `/student/results/exam/{exam_id}/leaderboard/` | Exam leaderboard | Read |

---

## 29. STUDENT — FEES

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 235 | GET | `/student/fees/` | Fee summary | Read |
| 236 | GET | `/student/fees/structure/` | Fee structure breakdown | Read |
| 237 | GET | `/student/fees/dues/` | Pending dues | Read |
| 238 | GET | `/student/fees/history/` | Payment history | List |
| 239 | GET | `/student/fees/receipt/{payment_id}/` | Download receipt | Read |
| 240 | GET | `/student/fees/reminders/` | Fee reminders | Read |

---

## 30. STUDENT — TIMETABLE

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 241 | GET | `/student/timetable/` | Weekly timetable | Read |
| 242 | GET | `/student/timetable/day/` | Specific day schedule | Read |

---

## 31. STUDENT — LIBRARY

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 243 | GET | `/student/library/` | My issued books | Read |
| 244 | GET | `/student/library/catalog/` | Browse book catalog | List |
| 245 | GET | `/student/library/history/` | Borrowing history | List |
| 246 | GET | `/student/library/fines/` | Outstanding fines | Read |

---

## 32. STUDENT — NOTIFICATIONS

| # | Method | Endpoint | Feature | CRUDL |
|---|--------|----------|---------|-------|
| 247 | GET | `/student/notifications/` | List notifications | List |
| 248 | GET | `/student/notifications/{notification_id}/` | Get notification detail | Read |
| 249 | PUT | `/student/notifications/{notification_id}/read/` | Mark as read | Update |

---

## Summary

| Module | Total APIs | Create | Read | Update | Delete | List |
|--------|-----------|--------|------|--------|--------|------|
| Auth | 7 | 3 | 1 | 3 | 0 | 0 |
| Admin Dashboard | 7 | 0 | 7 | 0 | 0 | 0 |
| Admin Students | 12 | 2 | 8 | 1 | 1 | 1 |
| Admin Teachers | 12 | 3 | 4 | 1 | 2 | 1 |
| Admin Staff | 5 | 1 | 1 | 1 | 1 | 1 |
| Admin Examinations | 16 | 5 | 6 | 3 | 1 | 1 |
| Admin Fees | 12 | 5 | 5 | 0 | 0 | 1 |
| Admin Leaves | 11 | 1 | 4 | 4 | 0 | 1 |
| Admin Notifications | 5 | 1 | 1 | 1 | 1 | 1 |
| Admin Payroll | 11 | 4 | 3 | 3 | 0 | 2 |
| Admin Timetable | 11 | 3 | 3 | 2 | 2 | 1 |
| Admin Transport | 24 | 5 | 5 | 5 | 5 | 5 |
| Admin Library | 6 | 2 | 1 | 1 | 0 | 2 |
| Admin Settings | 13 | 3 | 6 | 4 | 0 | 0 |
| Teacher Dashboard | 9 | 0 | 9 | 0 | 0 | 0 |
| Teacher Attendance | 6 | 1 | 2 | 1 | 1 | 1 |
| Teacher Assignments | 8 | 1 | 3 | 2 | 1 | 1 |
| Teacher Grades | 8 | 2 | 4 | 1 | 0 | 1 |
| Teacher Leaves | 6 | 1 | 2 | 0 | 1 | 1 |
| Teacher Students | 9 | 0 | 8 | 0 | 0 | 1 |
| Teacher Timetable | 2 | 0 | 2 | 0 | 0 | 0 |
| Teacher Adhoc Classes | 4 | 1 | 0 | 1 | 1 | 1 |
| Teacher Notifications | 3 | 0 | 1 | 1 | 0 | 1 |
| Student Dashboard | 10 | 0 | 10 | 0 | 0 | 0 |
| Student Profile | 3 | 0 | 2 | 1 | 0 | 0 |
| Student Attendance | 5 | 0 | 3 | 0 | 0 | 1 |
| Student Assignments | 4 | 1 | 2 | 0 | 0 | 1 |
| Student Results | 5 | 0 | 3 | 0 | 0 | 1 |
| Student Fees | 6 | 0 | 4 | 0 | 0 | 1 |
| Student Timetable | 2 | 0 | 2 | 0 | 0 | 0 |
| Student Library | 4 | 0 | 2 | 0 | 0 | 2 |
| Student Notifications | 3 | 0 | 1 | 1 | 0 | 1 |
| **TOTAL** | **249** | **45** | **114** | **37** | **17** | **29** |
