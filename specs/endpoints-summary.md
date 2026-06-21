# API Endpoints Summary

**Last Updated: 2026-06-21**

## Authentication (`/auth`)

| Method | Path | Description |
|--------|------|-------------|
| POST | /auth/login | Login with email/password |
| POST | /auth/logout | Logout (invalidate token) |
| POST | /auth/refresh-token | Refresh access token |
| GET | /auth/me | Get current user profile |
| GET | /auth/school-profile | Get current school profile |
| POST | /auth/forgot-password | Request password reset email |
| POST | /auth/reset-password | Reset password with token |
| POST | /auth/change-password | Change password (authenticated) |

## Super Admin (`/superadmin`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /superadmin/dashboard/stats | Platform-wide dashboard stats |
| GET | /superadmin/schools | List all schools |
| POST | /superadmin/schools | Create a new school |
| GET | /superadmin/schools/{school_id} | Get school details |
| PUT | /superadmin/schools/{school_id} | Update school |
| DELETE | /superadmin/schools/{school_id}/hard-delete | Hard-delete school (all tables) |
| POST | /superadmin/schools/{school_id}/logo | Upload school logo |
| PUT | /superadmin/schools/{school_id}/subscription-status | Update subscription status |
| GET | /superadmin/schools/{school_id}/subscription | Get active subscription |
| GET | /superadmin/schools/{school_id}/subscription-history | Get subscription history |
| POST | /superadmin/schools/{school_id}/subscription | Create subscription |
| PUT | /superadmin/schools/{school_id}/subscription | Update subscription |
| GET | /superadmin/schools/{school_id}/payments | List payments |
| POST | /superadmin/schools/{school_id}/payments | Record payment |
| POST | /superadmin/schools/{school_id}/admin | Create admin user for school |
| GET | /superadmin/settings | Get platform settings |
| PUT | /superadmin/settings | Update platform settings |
| GET | /superadmin/users | List all users (with filters) |
| POST | /superadmin/users/{user_id}/unlock | Unlock a locked user |
| POST | /superadmin/users/{user_id}/reset-password | Reset user password |

## Admin - Dashboard (`/admin/dashboard`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/dashboard/stats | Dashboard KPI stats |
| GET | /admin/dashboard/attendance-trends | Attendance trend data |
| GET | /admin/dashboard/fee-collection-status | Fee collection status |
| GET | /admin/dashboard/student-distribution | Student distribution by class |
| GET | /admin/dashboard/recent-activities | Recent activity feed |
| GET | /admin/dashboard/leave-overview | Leave overview/pending |
| GET | /admin/dashboard/low-attendance | Low attendance alerts |
| GET | /admin/dashboard/subscription-banner | Subscription status banner |
| GET | /admin/dashboard/analytics/attendance-by-class | Analytics: attendance by class |
| GET | /admin/dashboard/analytics/fee-collection-trend | Analytics: fee trend |
| GET | /admin/dashboard/analytics/exam-performance | Analytics: exam performance |
| GET | /admin/dashboard/analytics/teacher-workload | Analytics: teacher workload |
| GET | /admin/dashboard/analytics/enrollment-trend | Analytics: enrollment trend |
| GET | /admin/dashboard/analytics/fee-defaulters-by-class | Analytics: fee defaulters |
| GET | /admin/dashboard/analytics/attendance-monthly-comparison | Analytics: monthly attendance |
| GET | /admin/dashboard/analytics/student-type-ratio | Analytics: student types |
| GET | /admin/dashboard/analytics/subject-performance | Analytics: subject performance |
| GET | /admin/dashboard/analytics/class-toppers | Analytics: class toppers |
| GET | /admin/dashboard/analytics/attendance-marks-correlation | Analytics: correlation |
| GET | /admin/dashboard/analytics/revenue-vs-target | Analytics: revenue vs target |
| GET | /admin/dashboard/analytics/teacher-leave-patterns | Analytics: leave patterns |
| GET | /admin/dashboard/analytics/transport-utilization | Analytics: transport |
| GET | /admin/dashboard/analytics/concession-summary | Analytics: concessions |
| GET | /admin/dashboard/analytics/growth-rate | Analytics: growth rate |
| GET | /admin/dashboard/analytics/fee-collection-rate | Analytics: fee rate |

## Admin - Students (`/admin/students`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/students | List students (paginated, filterable) |
| POST | /admin/students | Create student |
| GET | /admin/students/export | Export students to CSV |
| POST | /admin/students/bulk-import | Bulk import from CSV |
| POST | /admin/students/bulk-import-json | Bulk import from JSON |
| GET | /admin/students/{student_id} | Get student detail |
| PUT | /admin/students/{student_id} | Update student |
| DELETE | /admin/students/{student_id} | Soft-delete student |
| POST | /admin/students/{student_id}/reset-password | Reset student password |
| GET | /admin/students/{student_id}/exam-results | Student exam results |
| GET | /admin/students/{student_id}/parent-meetings | List parent meetings |
| POST | /admin/students/{student_id}/parent-meetings | Create meeting |
| PUT | /admin/students/{student_id}/parent-meetings/{meeting_id} | Update meeting |
| DELETE | /admin/students/{student_id}/parent-meetings/{meeting_id} | Delete meeting |
| GET | /admin/students/{student_id}/activities | List activities & awards |
| POST | /admin/students/{student_id}/activities | Create activity |
| PUT | /admin/students/{student_id}/activities/{activity_id} | Update activity |
| DELETE | /admin/students/{student_id}/activities/{activity_id} | Delete activity |
| POST | /admin/students/{student_id}/awards | Create award |
| PUT | /admin/students/{student_id}/awards/{award_id} | Update award |
| DELETE | /admin/students/{student_id}/awards/{award_id} | Delete award |
| GET | /admin/students/{student_id}/fee-history | Fee history |
| GET | /admin/students/{student_id}/disciplinary-records | List disciplinary records |
| POST | /admin/students/{student_id}/disciplinary-records | Create record |
| PUT | /admin/students/{student_id}/disciplinary-records/{record_id} | Update record |
| DELETE | /admin/students/{student_id}/disciplinary-records/{record_id} | Delete record |
| GET | /admin/students/{student_id}/attendance | Attendance calendar |

## Admin - Teachers (`/admin/teachers`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/teachers | List teachers (paginated) |
| POST | /admin/teachers | Create teacher |
| GET | /admin/teachers/export | Export to CSV |
| POST | /admin/teachers/bulk-import | Bulk import from CSV |
| GET | /admin/teachers/by-class | Teachers grouped by class |
| GET | /admin/teachers/{teacher_id} | Get teacher detail |
| PUT | /admin/teachers/{teacher_id} | Update teacher |
| DELETE | /admin/teachers/{teacher_id} | Soft-delete teacher |
| POST | /admin/teachers/{teacher_id}/reset-password | Reset password |
| POST | /admin/teachers/{teacher_id}/assign-class | Assign to class-section-subject |
| POST | /admin/teachers/{teacher_id}/bulk-assign | Bulk assign classes |
| GET | /admin/teachers/{teacher_id}/assignments | List assignments |
| DELETE | /admin/teachers/{teacher_id}/assignments/{assignment_id} | Remove assignment |
| GET | /admin/teachers/{teacher_id}/awards | List teacher awards |
| POST | /admin/teachers/{teacher_id}/awards | Create award |
| PUT | /admin/teachers/{teacher_id}/awards/{award_id} | Update award |
| DELETE | /admin/teachers/{teacher_id}/awards/{award_id} | Delete award |
| GET | /admin/teachers/{teacher_id}/history | Teacher history |

## Admin - Staff (`/admin/staff`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/staff | List all staff (paginated) |
| GET | /admin/staff/export | Export to CSV |
| POST | /admin/staff/bulk-import | Bulk import from CSV |
| POST | /admin/staff | Create staff member |
| PUT | /admin/staff/{staff_id} | Update staff |
| DELETE | /admin/staff/{staff_id} | Soft-delete staff |

## Admin - Attendance (`/admin/attendance`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/attendance | Get attendance for class+date |
| GET | /admin/attendance/class-subjects-status | Subject attendance grid |
| POST | /admin/attendance | Submit attendance |
| PUT | /admin/attendance | Update attendance |

## Admin - Timetable (`/admin/timetable`) -- HARD DELETE

| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/timetable/periods | List period configs |
| POST | /admin/timetable/periods | Create period |
| PUT | /admin/timetable/periods/{period_id} | Update period |
| DELETE | /admin/timetable/periods/{period_id} | Delete period (hard) |
| GET | /admin/timetable | Get timetable grid |
| POST | /admin/timetable/slot | Create slot |
| PUT | /admin/timetable/slot/{slot_id} | Update slot |
| DELETE | /admin/timetable/slot/{slot_id} | Delete slot (hard) |
| DELETE | /admin/timetable/slots/class-section/{class_section_id} | Reset all slots (hard) |
| GET | /admin/timetable/teacher/{teacher_id} | Teacher timetable |
| GET | /admin/timetable/teacher-availability | Teacher availability for slot |
| GET | /admin/timetable/conflicts | Detect conflicts |

## Admin - Examinations (`/admin/examinations`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/examinations | List exams |
| POST | /admin/examinations | Create exam |
| GET | /admin/examinations/grade-system | Get grade system |
| PUT | /admin/examinations/grade-system | Update grade system |
| GET | /admin/examinations/analytics | Exam analytics |
| GET | /admin/examinations/report-card/{student_id} | Student report card |
| POST | /admin/examinations/report-card/generate | Generate report cards |
| GET | /admin/examinations/schedule | Exam schedule |
| GET | /admin/examinations/{exam_id} | Exam detail |
| PUT | /admin/examinations/{exam_id} | Update exam |
| DELETE | /admin/examinations/{exam_id} | Cancel exam |
| GET | /admin/examinations/{exam_id}/results | Get results |
| POST | /admin/examinations/{exam_id}/results | Enter results |
| POST | /admin/examinations/{exam_id}/results/bulk-upload | Bulk upload results |
| PUT | /admin/examinations/{exam_id}/results/{result_id} | Update result |
| POST | /admin/examinations/{exam_id}/publish | Publish results |

## Admin - Fees (`/admin/fees`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/fees | List fee records (paginated) |
| GET | /admin/fees/export | Export fee records |
| GET | /admin/fees/student/{student_id} | Student fee records |
| GET | /admin/fees/student/{student_id}/receipt | Consolidated receipt |
| GET | /admin/fees/{fee_id} | Fee record detail |
| GET | /admin/fees/{fee_id}/receipt | Fee receipt |
| PUT | /admin/fees/{fee_id} | Update fee record |
| DELETE | /admin/fees/{fee_id} | Delete fee record |
| POST | /admin/fees | Create fee record |
| POST | /admin/fees/generate-due | Generate due fees |
| POST | /admin/fees/{fee_id}/record-payment | Record payment |
| POST | /admin/fees/student/{student_id}/bulk-record-payment | Bulk record payment |
| POST | /admin/fees/{fee_id}/apply-late-fee | Apply late fee |
| POST | /admin/fees/bulk-apply-late-fees | Bulk apply late fees |
| POST | /admin/fees/send-reminder | Send fee reminder |

## Admin - Leaves (`/admin/leaves`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/leaves | List leave applications |
| GET | /admin/leaves/teacher/{teacher_id} | Teacher leave detail |
| GET | /admin/leaves/balances | All leave balances |
| GET | /admin/leaves/policy | Get leave policy |
| PUT | /admin/leaves/policy | Update leave policy |
| POST | /admin/leaves/{leave_id}/approve | Approve leave |
| POST | /admin/leaves/{leave_id}/reject | Reject leave |
| POST | /admin/leaves/{leave_id}/cancel | Cancel leave |
| POST | /admin/leaves/bulk-action | Bulk approve/reject |
| GET | /admin/leaves/calendar | Leave calendar |
| POST | /admin/leaves/allocate | Allocate leave balances |

## Admin - Payroll (`/admin/staff/payroll`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/staff/payroll | List payslips |
| POST | /admin/staff/payroll/run | Run payroll |
| POST | /admin/staff/payroll/generate-payslips | Generate payslips |
| PUT | /admin/staff/payroll/{payslip_id} | Update payslip |
| POST | /admin/staff/payroll/{payslip_id}/pay | Mark payslip paid |
| POST | /admin/staff/payroll/mark-all-paid | Mark all paid |
| POST | /admin/staff/payroll/undo-all-paid | Undo mark all paid |
| POST | /admin/staff/payroll/delete | Delete payslips |
| GET | /admin/staff/payroll/history | Payroll history |
| GET | /admin/staff/payroll/salary-structure/{employee_id} | Get salary structure |
| PUT | /admin/staff/payroll/salary-structure/{staff_id} | Update salary structure |
| GET | /admin/staff/salary-advances | List salary advances |
| POST | /admin/staff/salary-advances | Create advance request |
| POST | /admin/staff/salary-advances/{advance_id}/approve | Approve advance |
| POST | /admin/staff/salary-advances/{advance_id}/reject | Reject advance |
| POST | /admin/staff/salary-advances/{advance_id}/disburse | Disburse advance |
| GET | /admin/staff/payroll/salary-revisions/{staff_id} | Revision history |
| GET | /admin/staff/payroll/staff/{staff_id}/payslips | Staff payslip history |
| POST | /admin/staff/payroll/salary-revisions | Create revision |

## Admin - Settings (`/admin/settings`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/settings | Get all settings |
| PUT | /admin/settings | Update settings |
| GET | /admin/settings/school-profile | Get school profile |
| PUT | /admin/settings/school-profile | Update school profile |
| GET | /admin/settings/academic-year | Get current academic year |
| GET | /admin/settings/academic-years | List all academic years |
| POST | /admin/settings/academic-years | Create academic year |
| PUT | /admin/settings/academic-years/{year_id} | Update academic year |
| DELETE | /admin/settings/academic-years/{year_id} | Delete academic year |
| POST | /admin/settings/academic-years/{year_id}/set-current | Set as current |
| PUT | /admin/settings/academic-year | Update academic year (legacy) |
| GET | /admin/settings/enums/{category} | Get enum values |
| PUT | /admin/settings/enums/{category} | Update enum values |
| POST | /admin/settings/classes/bulk | Bulk create classes |
| DELETE | /admin/settings/classes/{class_id} | Delete class |
| DELETE | /admin/settings/class-sections/{class_section_id} | Delete class-section |
| POST | /admin/settings/sections/bulk | Bulk create sections |
| POST | /admin/settings/subjects/bulk | Bulk create subjects |
| GET | /admin/settings/class-sections | List class-sections |
| GET | /admin/settings/subjects | List subjects |
| PUT | /admin/settings/subjects/{subject_id} | Update subject |
| DELETE | /admin/settings/subjects/{subject_id} | Delete subject |
| POST | /admin/settings/upload-logo | Upload school logo |
| PUT | /admin/settings/subjects/{subject_id}/classes | Update subject-class mapping |
| GET | /admin/settings/class-subjects | Get class-subject mappings |
| PUT | /admin/settings/class-subjects/{class_id} | Update class subjects |
| GET | /admin/settings/fee-structures | List fee structures |
| POST | /admin/settings/fee-structures | Create fee structure |
| PUT | /admin/settings/fee-structures/{structure_id} | Update fee structure |
| DELETE | /admin/settings/fee-structures/{structure_id} | Delete fee structure |
| GET | /admin/settings/id-generation | Get ID generation config |
| PUT | /admin/settings/id-generation | Update ID generation |
| GET | /admin/settings/holidays | Get holidays |
| PUT | /admin/settings/holidays | Update holidays |
| GET | /admin/settings/next-id | Get next auto-generated ID |
| GET | /admin/settings/attendance-config | Get attendance config |
| PUT | /admin/settings/attendance-config | Update attendance config |
| GET | /admin/settings/class-section-assignments | Get class-section staff assignments |
| PUT | /admin/settings/class-section-assignments/{class_section_id} | Update assignments |

## Admin - Transport (`/admin/transport`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/transport/stats | Transport statistics |
| GET | /admin/transport/vehicles/export | Export vehicles |
| GET | /admin/transport/vehicles | List vehicles |
| POST | /admin/transport/vehicles | Create vehicle |
| GET | /admin/transport/vehicles/{vehicle_id} | Vehicle detail |
| PUT | /admin/transport/vehicles/{vehicle_id} | Update vehicle |
| DELETE | /admin/transport/vehicles/{vehicle_id} | Delete vehicle |
| GET | /admin/transport/drivers/export | Export drivers |
| GET | /admin/transport/drivers | List drivers |
| POST | /admin/transport/drivers | Create driver |
| PUT | /admin/transport/drivers/{driver_id} | Update driver |
| DELETE | /admin/transport/drivers/{driver_id} | Delete driver |
| GET | /admin/transport/helpers | List helpers |
| POST | /admin/transport/helpers | Create helper |
| PUT | /admin/transport/helpers/{helper_id} | Update helper |
| DELETE | /admin/transport/helpers/{helper_id} | Delete helper |
| GET | /admin/transport/routes | List routes |
| POST | /admin/transport/routes | Create route |
| PUT | /admin/transport/routes/{route_id} | Update route |
| DELETE | /admin/transport/routes/{route_id} | Delete route |
| GET | /admin/transport/assignments | List route assignments |
| POST | /admin/transport/assignments | Create assignment |
| PUT | /admin/transport/assignments/{assignment_id} | Update assignment |
| DELETE | /admin/transport/assignments/{assignment_id} | Delete assignment |
| GET | /admin/transport/routes/{route_id}/students | List students on route |
| POST | /admin/transport/routes/{route_id}/students | Assign student to route |
| DELETE | /admin/transport/routes/{route_id}/students/{student_id} | Remove from route |

## Admin - Library (`/admin/library`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/library/books | List books |
| POST | /admin/library/books | Add book |
| POST | /admin/library/issue | Issue book |
| POST | /admin/library/return | Return book |
| GET | /admin/library/issued | List issued books |
| GET | /admin/library/overdue | List overdue books |

## Admin - Notifications (`/admin/notifications`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/notifications | List notifications |
| POST | /admin/notifications | Create notification |
| GET | /admin/notifications/templates | Get notification templates |
| PUT | /admin/notifications/templates | Update templates |
| GET | /admin/notifications/teacher-sent | Teacher-sent notifications |
| GET | /admin/notifications/{notification_id} | Notification detail |
| PUT | /admin/notifications/{notification_id} | Update notification |
| DELETE | /admin/notifications/{notification_id} | Archive notification |

## Admin - Mentoring (`/admin/mentoring`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/mentoring | List mentor assignments |
| GET | /admin/mentoring/teacher/{staff_id}/students | Mentor's students |
| GET | /admin/mentoring/teachers | List available teachers |
| GET | /admin/mentoring/students | List unassigned students |
| POST | /admin/mentoring/assign | Assign mentor |
| DELETE | /admin/mentoring/{assignment_id} | Remove assignment |
| POST | /admin/mentoring/shuffle-assign | Auto-assign mentors |

## Teacher - Dashboard (`/teacher/dashboard`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /teacher/dashboard/stats | Teacher dashboard stats |
| GET | /teacher/dashboard/today-schedule | Today's schedule |
| GET | /teacher/dashboard/pending-reviews | Pending assignment reviews |
| GET | /teacher/dashboard/upcoming-exams | Upcoming exams |
| GET | /teacher/dashboard/classes-summary | Classes summary |
| GET | /teacher/dashboard/leave-updates | Leave status updates |
| GET | /teacher/dashboard/mentees-summary | Mentees overview |
| GET | /teacher/dashboard/adhoc-classes | Adhoc classes summary |
| GET | /teacher/dashboard/attendance-status | Today attendance status |
| GET | /teacher/dashboard/upcoming-meetings | Upcoming meetings |
| GET | /teacher/dashboard/profile | Get teacher profile |
| PUT | /teacher/dashboard/profile | Update teacher profile |

## Teacher - Attendance (`/teacher/attendance`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /teacher/attendance | Get attendance for class+date |
| POST | /teacher/attendance | Submit attendance |
| PUT | /teacher/attendance | Update attendance |
| GET | /teacher/attendance/history | Attendance history |
| DELETE | /teacher/attendance/{session_id} | Cancel attendance session |
| GET | /teacher/attendance/summary | Attendance summary |

## Teacher - Assignments (`/teacher/assignments`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /teacher/assignments | List assignments |
| POST | /teacher/assignments | Create assignment |
| GET | /teacher/assignments/{assignment_id} | Assignment detail |
| PUT | /teacher/assignments/{assignment_id} | Update assignment |
| DELETE | /teacher/assignments/{assignment_id} | Delete assignment |
| GET | /teacher/assignments/{assignment_id}/submissions | List submissions |
| POST | /teacher/assignments/{assignment_id}/submissions/{submission_id}/grade | Grade submission |
| GET | /teacher/assignments/{assignment_id}/submissions/export | Export submissions |

## Teacher - Grades (`/teacher/grades`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /teacher/grades | Get grades |
| POST | /teacher/grades | Submit grades |
| PUT | /teacher/grades | Update grades |
| GET | /teacher/grades/exams | Exams for grading |
| POST | /teacher/grades/exams/{exam_id}/publish | Publish exam results |
| GET | /teacher/grades/report | Grade report |
| GET | /teacher/grades/leaderboard | Class leaderboard |
| POST | /teacher/grades/import | Import grades |
| GET | /teacher/grades/export | Export grades |

## Teacher - Leaves (`/teacher/leaves`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /teacher/leaves/balance | Get leave balance |
| GET | /teacher/leaves/holidays | Get holidays |
| GET | /teacher/leaves/upcoming | Upcoming leaves |
| GET | /teacher/leaves | Leave history |
| POST | /teacher/leaves | Apply for leave |
| GET | /teacher/leaves/{leave_id} | Leave detail |
| DELETE | /teacher/leaves/{leave_id} | Cancel leave |

## Teacher - Students (`/teacher/students`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /teacher/students | List students (class-based) |
| GET | /teacher/students/mentees | List mentees |
| GET | /teacher/students/{student_id} | Student detail |
| GET | /teacher/students/{student_id}/exam-results | Exam results |
| GET | /teacher/students/{student_id}/parent-meetings | Parent meetings |
| GET | /teacher/students/{student_id}/activities | Activities |
| GET | /teacher/students/{student_id}/fee-summary | Fee summary |
| GET | /teacher/students/{student_id}/behavior | Behavior info |
| GET | /teacher/students/{student_id}/recent-attendance | Recent attendance |
| GET | /teacher/students/{student_id}/assignments | Assignments |
| PUT | /teacher/students/{student_id} | Update student (mentor) |
| POST | /teacher/students/{student_id}/parent-meetings | Create meeting |
| PUT | /teacher/students/{student_id}/parent-meetings/{meeting_id} | Update meeting |
| DELETE | /teacher/students/{student_id}/parent-meetings/{meeting_id} | Delete meeting |
| POST | /teacher/students/{student_id}/activities | Create activity |
| PUT | /teacher/students/{student_id}/activities/{activity_id} | Update activity |
| DELETE | /teacher/students/{student_id}/activities/{activity_id} | Delete activity |
| POST | /teacher/students/{student_id}/awards | Create award |
| PUT | /teacher/students/{student_id}/awards/{award_id} | Update award |
| DELETE | /teacher/students/{student_id}/awards/{award_id} | Delete award |
| POST | /teacher/students/{student_id}/disciplinary-records | Create record |
| PUT | /teacher/students/{student_id}/disciplinary-records/{record_id} | Update record |
| DELETE | /teacher/students/{student_id}/disciplinary-records/{record_id} | Delete record |
| GET | /teacher/students/{student_id}/mentor-notes | Get mentor notes |
| PUT | /teacher/students/{student_id}/mentor-notes | Update mentor notes |

## Teacher - Adhoc Classes (`/teacher/adhoc-classes`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /teacher/adhoc-classes | List adhoc classes |
| POST | /teacher/adhoc-classes | Create adhoc class |
| PUT | /teacher/adhoc-classes/{adhoc_id} | Update adhoc class |
| DELETE | /teacher/adhoc-classes/{adhoc_id} | Delete adhoc class |

## Teacher - Timetable (`/teacher/timetable`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /teacher/timetable | Weekly timetable |
| GET | /teacher/timetable/today | Today's schedule |

## Teacher - Notifications (`/teacher/notifications`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /teacher/notifications/sent | Sent notifications |
| GET | /teacher/notifications | Inbox notifications |
| GET | /teacher/notifications/{notification_id} | Notification detail |
| PUT | /teacher/notifications/{notification_id}/read | Mark as read |

## Student - Dashboard (`/student/dashboard`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /student/dashboard/stats | Student dashboard stats |
| GET | /student/dashboard/today-schedule | Today's schedule |
| GET | /student/dashboard/pending-assignments | Pending assignments |
| GET | /student/dashboard/upcoming-exams | Upcoming exams |
| GET | /student/dashboard/subject-attendance | Subject-wise attendance |
| GET | /student/dashboard/recent-results | Recent results |
| GET | /student/dashboard/announcements | Announcements |
| GET | /student/dashboard/notifications | Notifications |
| GET | /student/dashboard/fee-status | Fee status |
| GET | /student/dashboard/parent-meetings | Parent meetings |

## Student - Attendance (`/student/attendance`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /student/attendance | Attendance overview |
| GET | /student/attendance/history | Attendance history |
| GET | /student/attendance/warnings | Attendance warnings |
| GET | /student/attendance/summary | Attendance summary |
| GET | /student/attendance/monthly | Monthly breakdown |

## Student - Assignments (`/student/assignments`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /student/assignments | List assignments |
| GET | /student/assignments/{assignment_id} | Assignment detail |
| POST | /student/assignments/{assignment_id}/submit | Submit assignment |
| GET | /student/assignments/{assignment_id}/submission | Get submission |

## Student - Results (`/student/results`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /student/results | Results overview |
| GET | /student/results/exams | Exam results list |
| GET | /student/results/download-report | Download report card |
| GET | /student/results/exam/{exam_id} | Exam detail |
| GET | /student/results/exam/{exam_id}/leaderboard | Exam leaderboard |

## Student - Fees (`/student/fees`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /student/fees | Fee summary |
| GET | /student/fees/structure | Fee structure |
| GET | /student/fees/dues | Current dues |
| GET | /student/fees/history | Payment history |
| GET | /student/fees/receipt/{payment_id} | Payment receipt |
| GET | /student/fees/reminders | Fee reminders |

## Student - Library (`/student/library`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /student/library | My borrowed books |
| GET | /student/library/catalog | Browse catalog |
| GET | /student/library/history | Borrowing history |
| GET | /student/library/fines | Outstanding fines |

## Student - Profile (`/student/profile`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /student/profile | Get profile |
| PUT | /student/profile | Update profile |
| GET | /student/profile/mentor | Get mentor info |

## Student - Timetable (`/student/timetable`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /student/timetable | Weekly timetable |
| GET | /student/timetable/day | Day schedule |

## Student - Notifications (`/student/notifications`)

| Method | Path | Description |
|--------|------|-------------|
| GET | /student/notifications | List notifications |
| GET | /student/notifications/{notification_id} | Notification detail |
| PUT | /student/notifications/{notification_id}/read | Mark as read |
