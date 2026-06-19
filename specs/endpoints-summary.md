# API Endpoints Summary

**Total Endpoints: 339** | **Last Updated: 2026-06-10**

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

## Admin - Dashboard & Analytics (16 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/dashboard/stats | KPI cards |
| GET | /admin/dashboard/attendance-trends | Monthly attendance trend |
| GET | /admin/dashboard/fee-collection-status | Fee pie chart data |
| GET | /admin/dashboard/student-distribution | By class/gender |
| GET | /admin/dashboard/recent-activities | Activity feed |
| GET | /admin/dashboard/leave-overview | Leave status + pending approvals |
| GET | /admin/dashboard/low-attendance | Students below threshold |
| GET | /admin/dashboard/subscription-banner | Subscription status |
| GET | /admin/dashboard/analytics/attendance-by-class | Attendance % per class |
| GET | /admin/dashboard/analytics/fee-collection-trend | Monthly fee collection (6 months) |
| GET | /admin/dashboard/analytics/exam-performance | Avg marks & pass rate per class |
| GET | /admin/dashboard/analytics/teacher-workload | Staff period utilization |
| GET | /admin/dashboard/analytics/enrollment-trend | Student count per academic year |
| GET | /admin/dashboard/analytics/fee-defaulters-by-class | Overdue students per class |
| GET | /admin/dashboard/analytics/attendance-monthly-comparison | This month vs last month |
| GET | /admin/dashboard/analytics/student-type-ratio | Dayscholar/Hostler student type counts |

## Admin - Settings (37 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/settings | Get all settings |
| PUT | /admin/settings | Update settings |
| GET | /admin/settings/school-profile | School profile |
| PUT | /admin/settings/school-profile | Update school profile |
| GET | /admin/settings/academic-year | Current year |
| GET | /admin/settings/academic-years | List all years |
| POST | /admin/settings/academic-years | Create year |
| PUT | /admin/settings/academic-years/{id} | Update year |
| DELETE | /admin/settings/academic-years/{id} | Delete year |
| POST | /admin/settings/academic-years/{id}/set-current | Set current |
| PUT | /admin/settings/academic-year | Update year (legacy) |
| GET | /admin/settings/enums/{category} | Get enum values |
| PUT | /admin/settings/enums/{category} | Update enum values |
| POST | /admin/settings/classes/bulk | Bulk create classes |
| DELETE | /admin/settings/classes/{class_id} | Delete class |
| DELETE | /admin/settings/class-sections/{id} | Delete class-section |
| POST | /admin/settings/sections/bulk | Bulk create sections |
| POST | /admin/settings/subjects/bulk | Bulk create subjects |
| GET | /admin/settings/class-sections | Get all class-sections |
| GET | /admin/settings/subjects | List subjects |
| PUT | /admin/settings/subjects/{id} | Update subject |
| DELETE | /admin/settings/subjects/{id} | Delete subject |
| POST | /admin/settings/upload-logo | Upload school logo |
| PUT | /admin/settings/subjects/{id}/classes | Assign subject to classes |
| GET | /admin/settings/class-subjects | Class-subject mapping |
| PUT | /admin/settings/class-subjects/{id} | Update class subjects |
| GET | /admin/settings/fee-structures | List fee structures |
| POST | /admin/settings/fee-structures | Create fee structure |
| PUT | /admin/settings/fee-structures/{id} | Update fee structure |
| DELETE | /admin/settings/fee-structures/{id} | Delete fee structure |
| GET | /admin/settings/id-generation | ID generation config |
| PUT | /admin/settings/id-generation | Update ID config |
| GET | /admin/settings/holidays | Get holidays |
| PUT | /admin/settings/holidays | Update holidays |
| GET | /admin/settings/next-id | Get next generated ID |
| GET | /admin/settings/attendance-config | Attendance config |
| PUT | /admin/settings/attendance-config | Update attendance config |

## Admin - Students (27 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/students | List (paginated, filtered) |
| POST | /admin/students | Create student + user account |
| GET | /admin/students/export | Export CSV |
| POST | /admin/students/bulk-import | CSV import |
| POST | /admin/students/bulk-import-json | JSON bulk import |
| GET | /admin/students/{id} | Detail with stats |
| PUT | /admin/students/{id} | Update |
| DELETE | /admin/students/{id} | Soft-delete |
| POST | /admin/students/{id}/reset-password | Reset password |
| GET | /admin/students/{id}/exam-results | Exam results |
| GET | /admin/students/{id}/parent-meetings | List meetings |
| POST | /admin/students/{id}/parent-meetings | Create meeting |
| PUT | /admin/students/{id}/parent-meetings/{mid} | Update meeting |
| DELETE | /admin/students/{id}/parent-meetings/{mid} | Delete meeting |
| GET | /admin/students/{id}/activities | List activities |
| POST | /admin/students/{id}/activities | Create activity |
| PUT | /admin/students/{id}/activities/{aid} | Update activity |
| DELETE | /admin/students/{id}/activities/{aid} | Delete activity |
| POST | /admin/students/{id}/awards | Create award |
| PUT | /admin/students/{id}/awards/{aid} | Update award |
| DELETE | /admin/students/{id}/awards/{aid} | Delete award |
| GET | /admin/students/{id}/fee-history | Fee history |
| GET | /admin/students/{id}/disciplinary-records | List records |
| POST | /admin/students/{id}/disciplinary-records | Create record |
| PUT | /admin/students/{id}/disciplinary-records/{rid} | Update record |
| DELETE | /admin/students/{id}/disciplinary-records/{rid} | Delete record |
| GET | /admin/students/{id}/attendance | Student attendance |

## Admin - Teachers (18 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/teachers | List (paginated) |
| POST | /admin/teachers | Create teacher |
| GET | /admin/teachers/export | Export CSV |
| POST | /admin/teachers/bulk-import | Bulk import |
| GET | /admin/teachers/by-class | Teachers by class |
| GET | /admin/teachers/{id} | Detail |
| PUT | /admin/teachers/{id} | Update |
| DELETE | /admin/teachers/{id} | Soft-delete |
| POST | /admin/teachers/{id}/reset-password | Reset password |
| POST | /admin/teachers/{id}/assign-class | Assign class |
| POST | /admin/teachers/{id}/bulk-assign | Bulk assign classes |
| GET | /admin/teachers/{id}/assignments | Class assignments |
| DELETE | /admin/teachers/{id}/assignments/{aid} | Remove assignment |
| GET | /admin/teachers/{id}/awards | List awards |
| POST | /admin/teachers/{id}/awards | Create award |
| PUT | /admin/teachers/{id}/awards/{aid} | Update award |
| DELETE | /admin/teachers/{id}/awards/{aid} | Delete award |
| GET | /admin/teachers/{id}/history | Teacher history |

## Admin - Staff & Payroll (24 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/staff | List staff |
| POST | /admin/staff | Create staff |
| GET | /admin/staff/export | Export |
| PUT | /admin/staff/{id} | Update |
| DELETE | /admin/staff/{id} | Delete |
| GET | /admin/staff/payroll | Get payslips (month/year) |
| POST | /admin/staff/payroll/run | Generate payroll |
| POST | /admin/staff/payroll/generate-payslips | Generate payslips |
| PUT | /admin/staff/payroll/{id} | Update payslip |
| POST | /admin/staff/payroll/{id}/pay | Record payment |
| POST | /admin/staff/payroll/mark-all-paid | Bulk mark paid |
| POST | /admin/staff/payroll/undo-all-paid | Undo mark all paid |
| DELETE | /admin/staff/payroll | Delete monthly payroll |
| GET | /admin/staff/payroll/history | Payroll history |
| GET | /admin/staff/payroll/salary-structure/{id} | Get salary |
| PUT | /admin/staff/payroll/salary-structure/{id} | Update salary |
| GET | /admin/staff/salary-advances | List advances |
| POST | /admin/staff/salary-advances | Create advance |
| POST | /admin/staff/salary-advances/{id}/approve | Approve |
| POST | /admin/staff/salary-advances/{id}/reject | Reject |
| POST | /admin/staff/salary-advances/{id}/disburse | Disburse |
| GET | /admin/staff/payroll/salary-revisions/{id} | Revision history |
| GET | /admin/staff/payroll/staff/{id}/payslips | Staff payslip history |
| POST | /admin/staff/payroll/salary-revisions | Create revision |

## Admin - Fees (13 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/fees | List fee records |
| POST | /admin/fees | Create fee record |
| GET | /admin/fees/export | Export CSV |
| POST | /admin/fees/generate-due | Generate dues |
| POST | /admin/fees/send-reminder | Send reminders |
| POST | /admin/fees/bulk-apply-late-fees | Bulk late fees |
| GET | /admin/fees/student/{id} | Student fee records |
| GET | /admin/fees/student/{id}/receipt | Consolidated receipt |
| GET | /admin/fees/{id} | Fee record detail |
| PUT | /admin/fees/{id} | Update fee record |
| POST | /admin/fees/{id}/record-payment | Record payment |
| POST | /admin/fees/{id}/apply-late-fee | Apply late fee |
| GET | /admin/fees/{id}/receipt | Fee receipt |

## Admin - Examinations (16 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/examinations | List exams |
| POST | /admin/examinations | Create exam |
| GET | /admin/examinations/grade-system | Get grading system |
| PUT | /admin/examinations/grade-system | Update grading system |
| GET | /admin/examinations/analytics | Exam analytics |
| GET | /admin/examinations/report-card/{id} | Student report card |
| POST | /admin/examinations/report-card/generate | Generate report cards |
| GET | /admin/examinations/schedule | Exam schedule |
| GET | /admin/examinations/{id} | Exam detail |
| PUT | /admin/examinations/{id} | Update exam |
| DELETE | /admin/examinations/{id} | Cancel exam |
| GET | /admin/examinations/{id}/results | Get results |
| POST | /admin/examinations/{id}/results | Enter results |
| POST | /admin/examinations/{id}/results/bulk-upload | Bulk upload |
| PUT | /admin/examinations/{id}/results/{rid} | Update result |
| POST | /admin/examinations/{id}/publish | Publish results |

## Admin - Attendance (3 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/attendance | Get attendance (class + date) |
| POST | /admin/attendance | Submit attendance |
| PUT | /admin/attendance | Update attendance |

## Admin - Leaves (11 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/leaves | List applications |
| GET | /admin/leaves/teacher/{id} | Teacher leave detail |
| GET | /admin/leaves/balances | All balances |
| GET | /admin/leaves/policy | Get policy |
| PUT | /admin/leaves/policy | Update policy |
| POST | /admin/leaves/{id}/approve | Approve |
| POST | /admin/leaves/{id}/reject | Reject |
| POST | /admin/leaves/{id}/cancel | Cancel |
| POST | /admin/leaves/bulk-action | Bulk approve/reject |
| GET | /admin/leaves/calendar | Calendar view |
| POST | /admin/leaves/allocate | Allocate balance |

## Admin - Transport (28 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/transport/stats | Transport stats |
| GET | /admin/transport/vehicles | List vehicles |
| POST | /admin/transport/vehicles | Create vehicle |
| GET | /admin/transport/vehicles/export | Export CSV |
| GET | /admin/transport/vehicles/{id} | Get vehicle |
| PUT | /admin/transport/vehicles/{id} | Update vehicle |
| DELETE | /admin/transport/vehicles/{id} | Delete vehicle |
| GET | /admin/transport/drivers | List drivers |
| POST | /admin/transport/drivers | Create driver |
| GET | /admin/transport/drivers/export | Export CSV |
| PUT | /admin/transport/drivers/{id} | Update driver |
| DELETE | /admin/transport/drivers/{id} | Delete driver |
| GET | /admin/transport/helpers | List helpers |
| POST | /admin/transport/helpers | Create helper |
| PUT | /admin/transport/helpers/{id} | Update helper |
| DELETE | /admin/transport/helpers/{id} | Delete helper |
| GET | /admin/transport/routes | List routes |
| POST | /admin/transport/routes | Create route |
| PUT | /admin/transport/routes/{id} | Update route |
| DELETE | /admin/transport/routes/{id} | Delete route |
| GET | /admin/transport/assignments | List assignments |
| POST | /admin/transport/assignments | Create assignment |
| PUT | /admin/transport/assignments/{id} | Update assignment |
| DELETE | /admin/transport/assignments/{id} | Delete assignment |
| GET | /admin/transport/routes/{id}/students | Route students |
| POST | /admin/transport/routes/{id}/students | Add student to route |
| DELETE | /admin/transport/routes/{id}/students/{sid} | Remove student |

## Admin - Timetable (12 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/timetable/periods | List period configurations |
| POST | /admin/timetable/periods | Create period (validates time overlap) |
| PUT | /admin/timetable/periods/{id} | Update period timing |
| DELETE | /admin/timetable/periods/{id} | Hard-delete period |
| GET | /admin/timetable | Timetable grid for a class-section |
| POST | /admin/timetable/slot | Create/upsert slot (updates if exists at same position) |
| PUT | /admin/timetable/slot/{id} | Update slot (checks teacher + position conflicts) |
| DELETE | /admin/timetable/slot/{id} | Hard-delete slot |
| GET | /admin/timetable/teacher/{id} | Teacher's weekly timetable + free slots |
| GET | /admin/timetable/teacher-availability | Check which teachers are busy at a period+day |
| GET | /admin/timetable/conflicts | Detect teacher double-booking conflicts |

## Admin - Library (6 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/library/books | List books |
| POST | /admin/library/books | Add book |
| POST | /admin/library/issue | Issue book |
| POST | /admin/library/return | Return book |
| GET | /admin/library/issued | Issued list |
| GET | /admin/library/overdue | Overdue list |

## Admin - Notifications (5 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/notifications | List |
| POST | /admin/notifications | Create/send |
| GET | /admin/notifications/{id} | Detail |
| PUT | /admin/notifications/{id} | Update |
| DELETE | /admin/notifications/{id} | Archive |

## Admin - Mentoring (7 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/mentoring | List mentor assignments |
| GET | /admin/mentoring/teacher/{id}/students | Mentor's students |
| GET | /admin/mentoring/teachers | List mentor teachers |
| GET | /admin/mentoring/students | List students |
| POST | /admin/mentoring/assign | Assign mentor |
| DELETE | /admin/mentoring/{id} | Remove assignment |
| POST | /admin/mentoring/shuffle-assign | Auto-assign all |

## Teacher Module (58 endpoints)
| Module | Count | Key Endpoints |
|--------|-------|---------------|
| Dashboard | 10 | stats, today-schedule, pending-reviews, upcoming-exams, classes-summary, leave-updates, mentees-summary, adhoc-classes, profile GET/PUT |
| Attendance | 6 | GET/POST/PUT, history, cancel, summary |
| Grades | 8 | GET/POST/PUT, exams, report, leaderboard, import, export |
| Assignments | 8 | CRUD, submissions, grade, export |
| Adhoc Classes | 4 | CRUD |
| Leaves | 6 | balance, upcoming, history, apply, detail, cancel |
| Students | 11 | list, mentees, detail, exam-results, meetings, activities, fees, behavior, attendance, assignments, update |
| Notifications | 3 | list, detail, mark-read |
| Timetable | 2 | weekly, today |

## Student Module (42 endpoints)
| Module | Count | Key Endpoints |
|--------|-------|---------------|
| Dashboard | 10 | stats, schedule, assignments, exams, attendance, results, announcements, notifications, fee-status, meetings |
| Attendance | 5 | overview, history, warnings, summary, monthly |
| Assignments | 4 | list, detail, submit, submission |
| Results | 5 | overview, exams, download-report, exam detail, leaderboard |
| Fees | 6 | summary, structure, dues, history, receipt, reminders |
| Library | 4 | my-books, catalog, history, fines |
| Notifications | 3 | list, detail, mark-read |
| Profile | 3 | get, update, mentor |
| Timetable | 2 | weekly, day |

## SuperAdmin (18 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | /superadmin/dashboard/stats | Platform stats |
| GET | /superadmin/schools | List schools |
| POST | /superadmin/schools | Create school |
| GET | /superadmin/schools/{id} | School detail |
| PUT | /superadmin/schools/{id} | Update school |
| POST | /superadmin/schools/{id}/logo | Upload logo |
| PUT | /superadmin/schools/{id}/subscription-status | Update status |
| GET | /superadmin/schools/{id}/subscription | Get subscription |
| GET | /superadmin/schools/{id}/subscription-history | History |
| POST | /superadmin/schools/{id}/subscription | Create subscription |
| PUT | /superadmin/schools/{id}/subscription | Update subscription |
| GET | /superadmin/schools/{id}/payments | List payments |
| POST | /superadmin/schools/{id}/payments | Create payment |
| POST | /superadmin/schools/{id}/admin | Create school admin |
| GET | /superadmin/settings | Platform settings |
| PUT | /superadmin/settings | Update settings |
| GET | /superadmin/users | List users |

---

## Endpoint Count Breakdown

| Role | Endpoints |
|------|-----------|
| Auth (shared) | 8 |
| Admin | 215 |
| Teacher | 58 |
| Student | 42 |
| SuperAdmin | 18 |
| **Total (unique)** | **339** |

Note: Auth endpoints are shared across all roles but counted once.
