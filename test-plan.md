# API Test Plan — School ERP Backend

**Base URL:** `http://localhost:8000/api/v1`  
**Required header on every request:** `X-School-Code: SCH001`  
**Auth:** Cookie-based (`access_token`). Login first, reuse cookie for session.

---

## Credentials

| Portal  | Email                | Password    |
|---------|----------------------|-------------|
| Admin   | admin@school.com     | password123 |
| Teacher | jane@teacher.com     | password123 |
| Student | john@student.com     | password123 |

---

## Module Testing Order

1. Auth
2. Settings (classes, sections, subjects — required by almost everything)
3. Students
4. Teachers
5. Staff
6. Timetable
7. Examinations
8. Fees
9. Attendance
10. Assignments
11. Leaves
12. Transport
13. Library
14. Notifications
15. Payroll
16. Admin Dashboard
17. Teacher Portal APIs
18. Student Portal APIs

---

## 1. Auth

### Login
- `POST /auth/login` — `{"email": "admin@school.com", "password": "password123"}` → 200, cookie set
- `POST /auth/login` — wrong password → 401
- `POST /auth/login` — unknown email → 401
- `POST /auth/login` — missing email field → 422

### Authenticated endpoints
- `GET /auth/me` — with valid cookie → 200, user object returned
- `GET /auth/me` — no cookie → 401

### Token refresh
- `POST /auth/refresh-token` — with valid refresh_token cookie → 200, new access_token set
- `POST /auth/refresh-token` — no cookie → 401

### Change password
- `POST /auth/change-password` — `{"current_password": "password123", "new_password": "newpass456", "confirm_password": "newpass456"}` → 200
- `POST /auth/change-password` — wrong current password → 400/401
- `POST /auth/change-password` — mismatched new/confirm → 400

### Logout
- `POST /auth/logout` — clears cookies → 200

### Forgot/Reset password (smoke test only)
- `POST /auth/forgot-password` — `{"email": "admin@school.com"}` → 200 (always succeeds to prevent enumeration)

---

## 2. Settings (Admin only — as admin@school.com)

### General settings
- `GET /admin/settings/` → 200
- `PUT /admin/settings/` — partial update of a known field → 200

### School profile
- `GET /admin/settings/school-profile/` → 200
- `PUT /admin/settings/school-profile/` — `{"name": "Updated School Name"}` → 200
- `GET /admin/settings/school-profile/` — verify name change persisted

### Academic year
- `GET /admin/settings/academic-year/` → 200
- `PUT /admin/settings/academic-year/` — update dates → 200

### Enums
- `GET /admin/settings/enums/blood_group/` → 200
- `PUT /admin/settings/enums/blood_group/` — add a value → 200
- `GET /admin/settings/enums/blood_group/` — verify new value present

### Classes (save returned IDs for later)
- `POST /admin/settings/classes/bulk/` — `{"classes": [{"name": "Class 1"}, {"name": "Class 2"}]}` → 201
- `POST /admin/settings/classes/bulk/` — empty list → 422 or 0 created

### Sections (save returned IDs for later)
- `POST /admin/settings/sections/bulk/` — `{"sections": [{"name": "A"}, {"name": "B"}]}` → 201

### Subjects (save returned IDs for later)
- `POST /admin/settings/subjects/bulk/` — `{"subjects": [{"name": "Mathematics", "code": "MATH"}, {"name": "Science", "code": "SCI"}]}` → 201
- `GET /admin/settings/subjects/` → 200, list contains created subjects

### Class-sections lookup (save IDs for timetable/exam tests)
- `GET /admin/settings/class-sections/` → 200, non-empty list

### Authorization check
- `GET /admin/settings/` — using teacher cookie → 403
- `GET /admin/settings/` — no cookie → 401

---

## 3. Students (Admin)

### CRUD lifecycle
- `POST /admin/students/` — `{"full_name": "Test Student", "admission_number": "ADM001", "class_name": "Class 1", "section": "A", "date_of_birth": "2010-01-15", "gender": "Male", "email": "teststudent@example.com"}` → 201, save `student_id`
- `GET /admin/students/` → 200, includes created student
- `GET /admin/students/?search=Test Student` → 200, filtered result
- `GET /admin/students/?class_name=Class 1&section=A` → 200
- `GET /admin/students/{student_id}/` → 200, full profile
- `PUT /admin/students/{student_id}/` — `{"phone": "9876543210"}` → 200
- `GET /admin/students/{student_id}/` — verify phone update persisted
- `DELETE /admin/students/{student_id}/` — `{"status": "Inactive", "reason": "Test cleanup"}` → 200, status=Inactive
- `GET /admin/students/{student_id}/` — verify status is Inactive

### Sub-resources (use a different active student_id from seed data for data-rich tests)
- `GET /admin/students/{student_id}/exam-results/` → 200
- `GET /admin/students/{student_id}/fee-history/` → 200
- `GET /admin/students/{student_id}/parent-meetings/` → 200
- `GET /admin/students/{student_id}/activities/` → 200
- `GET /admin/students/{student_id}/disciplinary-records/` → 200

### Edge cases
- `GET /admin/students/00000000-0000-0000-0000-000000000000/` → 404
- `POST /admin/students/` — missing `full_name` → 422

### Export
- `GET /admin/students/export/` → 200, Content-Type: text/csv

---

## 4. Teachers (Admin)

### CRUD lifecycle
- `POST /admin/teachers/` — `{"full_name": "Test Teacher", "email": "testteacher@school.com", "employee_id": "EMP001", "department": "Science", "designation": "Teacher", "joining_date": "2024-01-01"}` → 201, save `teacher_id`
- `GET /admin/teachers/` → 200
- `GET /admin/teachers/?search=Test Teacher` → 200
- `GET /admin/teachers/{teacher_id}/` → 200
- `PUT /admin/teachers/{teacher_id}/` — `{"phone": "1234567890"}` → 200
- `GET /admin/teachers/{teacher_id}/` — verify update persisted

### Class assignments
- `POST /admin/teachers/{teacher_id}/assign-class/` — `{"class_section_id": "<class_section_id>", "subject_id": "<subject_id>", "is_class_teacher": false, "periods_per_week": 5}` → 201, save `assignment_id`
- `GET /admin/teachers/{teacher_id}/assignments/` → 200, contains assignment
- `POST /admin/teachers/{teacher_id}/bulk-assign/` — multiple assignments → 201
- `DELETE /admin/teachers/{teacher_id}/class-assignment/{assignment_id}/` → 200

### By-class filter
- `GET /admin/teachers/by-class/?class_name=Class 1&section=A` → 200

### History
- `GET /admin/teachers/{teacher_id}/history/` → 200

### Delete
- `DELETE /admin/teachers/{teacher_id}/` → 200, status=Inactive
- `GET /admin/teachers/{teacher_id}/` — verify status

### Edge cases
- `GET /admin/teachers/00000000-0000-0000-0000-000000000000/` → 404
- `POST /admin/teachers/` — duplicate email → 400/409

---

## 5. Staff (Admin)

### CRUD lifecycle
- `POST /admin/staff/` — `{"full_name": "Test Staff", "email": "teststaff@school.com", "employee_id": "STAFF001", "department": "Admin", "designation": "Clerk", "joining_date": "2024-01-01", "staff_type": "Non-Teaching"}` → 201, save `staff_id`
- `GET /admin/staff/` → 200
- `GET /admin/staff/?department=Admin` → 200
- `PUT /admin/staff/{staff_id}/` — `{"phone": "9999999999"}` → 200
- `DELETE /admin/staff/{staff_id}/` → 200, status=Inactive

### Export
- `GET /admin/staff/export/` → 200, CSV

---

## 6. Timetable (Admin) — requires teachers + class_sections from above

### Period configuration
- `POST /admin/timetable/periods/` — `{"name": "Period 1", "start_time": "08:00", "end_time": "08:45", "order": 1}` → 201, save `period_id`
- `GET /admin/timetable/periods/` → 200, contains period
- `PUT /admin/timetable/periods/{period_id}/` — `{"end_time": "08:50"}` → 200
- `GET /admin/timetable/periods/` — verify update

### Slot assignment
- `POST /admin/timetable/slot/` — `{"class_section_id": "<id>", "period_config_id": "<period_id>", "day_of_week": "Monday", "subject_id": "<subject_id>", "teacher_id": "<teacher_id>"}` → 201, save `slot_id`
- `GET /admin/timetable/?class_section_id=<class_section_id>` → 200, contains slot
- `PUT /admin/timetable/slot/{slot_id}/` — change subject → 200
- `GET /admin/timetable/?class_section_id=<class_section_id>` — verify update

### Bulk assign
- `POST /admin/timetable/bulk-assign/` — 3 slots at once → 201 or 207 on conflict

### Teacher timetable view
- `GET /admin/timetable/teacher/{teacher_id}/` → 200

### Conflicts
- `GET /admin/timetable/conflicts/` → 200

### Delete slot
- `DELETE /admin/timetable/slot/{slot_id}/` → 200
- `GET /admin/timetable/?class_section_id=<class_section_id>` — verify slot gone

### Delete period
- `DELETE /admin/timetable/periods/{period_id}/` → 200

---

## 7. Examinations (Admin) — requires class_sections + subjects + students

### Grade system
- `GET /admin/examinations/grade-system/` → 200
- `PUT /admin/examinations/grade-system/` — update a grade band → 200

### Exam CRUD lifecycle
- `POST /admin/examinations/` — `{"name": "Mid-Term 2024", "type": "Written", "class_section_id": "<id>", "subject_id": "<id>", "exam_date": "2024-06-15", "total_marks": 100, "passing_marks": 40, "term": "Term 1", "academic_year": "2024-25"}` → 201, save `exam_id`
- `GET /admin/examinations/` → 200, contains exam
- `GET /admin/examinations/?class_name=Class 1&section=A` → 200
- `GET /admin/examinations/{exam_id}/` → 200
- `PUT /admin/examinations/{exam_id}/` — `{"total_marks": 120}` → 200
- `GET /admin/examinations/{exam_id}/` — verify update

### Exam schedule
- `GET /admin/examinations/schedule/?class_name=Class 1&section=A` → 200

### Results
- `POST /admin/examinations/{exam_id}/results/` — `{"results": [{"student_id": "<student_id>", "marks_obtained": 75, "is_present": true}]}` → 201
- `GET /admin/examinations/{exam_id}/results/` → 200, contains result
- `PUT /admin/examinations/{exam_id}/results/{result_id}/` — `{"marks_obtained": 80}` → 200

### Publish
- `POST /admin/examinations/{exam_id}/publish/` — `{"publish_to_students": true}` → 200

### Analytics
- `GET /admin/examinations/analytics/?class_name=Class 1` → 200

### Report card
- `GET /admin/examinations/report-card/{student_id}/` → 200
- `POST /admin/examinations/report-card/generate/` — `{"class_name": "Class 1", "section": "A", "academic_year": "2024-25"}` → 200

### Cancel exam
- Create a new exam for cancellation test
- `DELETE /admin/examinations/{new_exam_id}/` → 200
- `GET /admin/examinations/{new_exam_id}/` → 404 or status=Cancelled

### Edge cases
- `GET /admin/examinations/00000000-0000-0000-0000-000000000000/` → 404
- `POST /admin/examinations/` — missing class_section_id → 422

---

## 8. Fees (Admin) — requires students

### Fee record CRUD
- `POST /admin/fees/` — `{"student_id": "<student_id>", "fee_type": "Tuition", "fee_category": "Term Fee", "total_amount": 5000, "due_date": "2024-04-30", "academic_year": "2024-25"}` → 201, save `fee_id`
- `GET /admin/fees/` → 200
- `GET /admin/fees/?class_name=Class 1&status=Pending` → 200
- `GET /admin/fees/{fee_id}/` → 200
- `GET /admin/fees/student/{student_id}/` → 200

### Payments
- `POST /admin/fees/{fee_id}/record-payment/` — `{"amount": 2500, "payment_mode": "Cash", "payment_date": "2024-04-20"}` → 200
- `GET /admin/fees/{fee_id}/` — verify paid_amount updated

### Late fee
- `POST /admin/fees/{fee_id}/apply-late-fee/` — `{"amount": 100, "reason": "Overdue"}` → 200

### Bulk generate
- `POST /admin/fees/generate-due/` — `{"class_name": "Class 1", "section": "A", "fee_type": "Tuition", "total_amount": 5000, "due_date": "2024-05-31", "academic_year": "2024-25"}` → 201

### Bulk late fees
- `POST /admin/fees/bulk-apply-late-fees/` — `{"fee_category": "Term Fee", "fine_amount": 50}` → 200

### Reminders
- `POST /admin/fees/send-reminder/` — `{"student_ids": ["<student_id>"]}` → 200

### Receipts
- `GET /admin/fees/{fee_id}/receipt/` → 200
- `GET /admin/fees/student/{student_id}/receipt/` → 200

### Export
- `GET /admin/fees/export/` → 200, CSV

---

## 9. Attendance (Teacher portal) — requires teacher login + class_sections + students enrolled

### Login as teacher first
- `POST /auth/login` — jane@teacher.com / password123

### Get attendance form
- `GET /teacher/attendance/?class_id=<class_section_id>&date=2024-06-10` → 200, student list

### Submit attendance
- `POST /teacher/attendance/` — `{"class_section_id": "<id>", "date": "2024-06-10", "records": [{"student_id": "<id>", "status": "Present"}, {"student_id": "<id2>", "status": "Absent"}]}` → 201, save `session_id`
- `GET /teacher/attendance/?class_id=<class_section_id>&date=2024-06-10` → 200, submitted records

### Update attendance
- `PUT /teacher/attendance/` — change one student from Absent to Present → 200
- `GET /teacher/attendance/?class_id=<class_section_id>&date=2024-06-10` — verify change

### History
- `GET /teacher/attendance/history/` → 200
- `GET /teacher/attendance/history/?class_id=<class_section_id>` → 200

### Summary
- `GET /teacher/attendance/summary/?class_id=<class_section_id>&month=6&year=2024` → 200

### Cancel
- `DELETE /teacher/attendance/{session_id}/` → 200
- `GET /teacher/attendance/?class_id=<class_section_id>&date=2024-06-10` — verify cancelled

### Edge cases
- `POST /teacher/attendance/` — duplicate submission for same class+date → 400/409
- `GET /teacher/attendance/?class_id=<class_section_id>&date=2024-06-10` — as admin (wrong role) → 403

---

## 10. Assignments (Teacher portal) — requires teacher login + class_sections + students

### CRUD lifecycle (as teacher)
- `POST /teacher/assignments/` — `{"class_section_id": "<id>", "subject_id": "<id>", "title": "Test Assignment 1", "description": "Complete exercises", "due_date": "2024-06-20", "total_marks": 50}` → 201, save `assignment_id`
- `GET /teacher/assignments/` → 200
- `GET /teacher/assignments/?class_id=<class_section_id>` → 200
- `GET /teacher/assignments/{assignment_id}/` → 200, includes submission_count
- `PUT /teacher/assignments/{assignment_id}/` — `{"due_date": "2024-06-25"}` → 200
- `GET /teacher/assignments/{assignment_id}/` — verify update

### Submissions
- `GET /teacher/assignments/{assignment_id}/submissions/` → 200, auto-created entries
- `POST /teacher/assignments/{assignment_id}/submissions/{submission_id}/grade/` — `{"marks": 42, "feedback": "Good work"}` → 200
- `GET /teacher/assignments/{assignment_id}/submissions/` — verify graded entry

### Export
- `GET /teacher/assignments/{assignment_id}/submissions/export/` → 200, CSV

### Delete
- Create a second assignment for deletion test
- `DELETE /teacher/assignments/{assignment_id2}/` → 200
- `GET /teacher/assignments/{assignment_id2}/` → 404

---

## 11. Leaves

### Teacher portal (as teacher)
- `GET /teacher/leaves/balance/` → 200
- `GET /teacher/leaves/upcoming/` → 200
- `GET /teacher/leaves/` → 200
- `POST /teacher/leaves/` — `{"leave_type": "Casual", "from_date": "2024-07-10", "to_date": "2024-07-11", "reason": "Personal work"}` → 201, save `leave_id`
- `GET /teacher/leaves/{leave_id}/` → 200
- `DELETE /teacher/leaves/{leave_id}/` — cancel pending leave → 200

### Admin portal (as admin)
- `GET /admin/leaves/` → 200
- `GET /admin/leaves/?status=Pending` → 200
- `GET /admin/leaves/balances/` → 200
- `GET /admin/leaves/policy/` → 200
- `PUT /admin/leaves/policy/` — update a leave type quota → 200

### Apply leave as teacher then manage as admin
- `POST /teacher/leaves/` — new leave application → 201, save `leave_id2`
- As admin: `POST /admin/leaves/{leave_id2}/approve/` — `{"remarks": "Approved"}` → 200
- `GET /admin/leaves/?status=Approved` — verify approval
- As admin: `POST /admin/leaves/{leave_id2}/cancel/` — `{"reason": "Schedule conflict"}` → 200

### Bulk action
- Apply 2 leave requests as teacher
- As admin: `POST /admin/leaves/bulk-action/` — `{"action": "reject", "leave_ids": ["<id1>", "<id2>"], "remarks": "Short staff"}` → 200

### Leave allocate
- `POST /admin/leaves/allocate/` — `{"teacher_ids": ["<teacher_id>"], "leave_type": "Casual", "days": 12}` → 200

### Calendar
- `GET /admin/leaves/calendar/?from_date=2024-07-01&to_date=2024-07-31` → 200

### Teacher detail
- `GET /admin/leaves/teacher/{teacher_id}/` → 200

---

## 12. Transport (Admin — standalone)

### Vehicles
- `POST /admin/transport/vehicles/` — `{"vehicle_number": "VH001", "plate_number": "KA01AB1234", "type": "Bus", "capacity": 40, "fuel_type": "Diesel", "status": "Active"}` → 201, save `vehicle_id`
- `GET /admin/transport/vehicles/` → 200
- `GET /admin/transport/vehicles/{vehicle_id}/` → 200
- `PUT /admin/transport/vehicles/{vehicle_id}/` — `{"capacity": 45}` → 200
- `GET /admin/transport/vehicles/{vehicle_id}/` — verify update

### Drivers
- `POST /admin/transport/drivers/` — `{"full_name": "Test Driver", "phone": "9876543210", "license_number": "DL123456", "license_type": "Heavy", "license_expiry": "2026-12-31", "experience_years": 5}` → 201, save `driver_id`
- `GET /admin/transport/drivers/` → 200
- `PUT /admin/transport/drivers/{driver_id}/` — `{"phone": "1111111111"}` → 200

### Helpers
- `POST /admin/transport/helpers/` — `{"full_name": "Test Helper", "phone": "8888888888"}` → 201, save `helper_id`
- `GET /admin/transport/helpers/` → 200
- `PUT /admin/transport/helpers/{helper_id}/` — `{"status": "Active"}` → 200

### Routes
- `POST /admin/transport/routes/` — `{"name": "Route 1", "start_point": "School", "end_point": "North Zone", "distance_km": 15}` → 201, save `route_id`
- `GET /admin/transport/routes/` → 200
- `PUT /admin/transport/routes/{route_id}/` — `{"distance_km": 18}` → 200

### Route assignments
- `POST /admin/transport/assignments/` — `{"route_id": "<route_id>", "vehicle_id": "<vehicle_id>", "driver_id": "<driver_id>", "helper_id": "<helper_id>", "shift": "Morning", "academic_year": "2024-25"}` → 201, save `assignment_id`
- `GET /admin/transport/assignments/` → 200
- `PUT /admin/transport/assignments/{assignment_id}/` — `{"shift": "Evening"}` → 200

### Stats
- `GET /admin/transport/stats/` → 200

### Soft-deletes and verify gone
- `DELETE /admin/transport/assignments/{assignment_id}/` → 200
- `DELETE /admin/transport/routes/{route_id}/` → 200
- `DELETE /admin/transport/drivers/{driver_id}/` → 200
- `DELETE /admin/transport/helpers/{helper_id}/` → 200
- `DELETE /admin/transport/vehicles/{vehicle_id}/` → 200

### Edge cases
- `POST /admin/transport/assignments/` — assign same vehicle twice → 409
- `GET /admin/transport/vehicles/00000000-0000-0000-0000-000000000000/` → 404

---

## 13. Library (Admin + Student)

### Admin: Book CRUD
- `POST /admin/library/books/` — `{"title": "Test Book", "author": "Test Author", "isbn": "978-0000000001", "category": "Science", "total_copies": 3}` → 201, save `book_id`
- `GET /admin/library/books/` → 200
- `GET /admin/library/books/?search=Test Book` → 200

### Issue and return
- `POST /admin/library/issue/` — `{"book_id": "<book_id>", "student_id": "<student_id>", "due_date": "2024-07-30"}` → 201, save `issue_id`
- `GET /admin/library/issued/` → 200, contains issued record
- `POST /admin/library/return/` — `{"issue_id": "<issue_id>"}` → 200
- `GET /admin/library/issued/` — verify returned

### Overdue list
- `GET /admin/library/overdue/` → 200

### Student: Library views (as student)
- `GET /student/library/` → 200
- `GET /student/library/catalog/` → 200
- `GET /student/library/catalog/?search=Test` → 200
- `GET /student/library/history/` → 200
- `GET /student/library/fines/` → 200

---

## 14. Notifications (Admin + Teacher + Student)

### Admin CRUD
- `POST /admin/notifications/` — `{"title": "Test Notice", "message": "This is a test notification", "type": "Announcement", "target_type": "All"}` → 201, save `notification_id`
- `GET /admin/notifications/` → 200
- `GET /admin/notifications/{notification_id}/` → 200
- `PUT /admin/notifications/{notification_id}/` — `{"title": "Updated Notice"}` → 200 (only if Scheduled/Draft)
- `GET /admin/notifications/{notification_id}/` — verify update

### Send to specific target
- `POST /admin/notifications/` — `{"title": "Class Notice", "message": "...", "type": "Academic", "target_type": "Class", "target_class": "Class 1", "target_section": "A"}` → 201

### Teacher portal (as teacher)
- `GET /teacher/notifications/` → 200
- `GET /teacher/notifications/?is_read=false` → 200
- `GET /teacher/notifications/{notification_id}/` → 200
- `PUT /teacher/notifications/{notification_id}/read/` → 200
- `GET /teacher/notifications/{notification_id}/` — verify is_read=true

### Student portal (as student)
- `GET /student/notifications/` → 200
- `GET /student/notifications/{notification_id}/` → 200
- `PUT /student/notifications/{notification_id}/read/` → 200

### Archive (admin)
- `DELETE /admin/notifications/{notification_id}/` → 200
- `GET /admin/notifications/{notification_id}/` → 404 or archived status

---

## 15. Payroll (Admin) — requires staff

### Salary structure
- `GET /admin/payroll/salary-structure/{staff_id}/` → 200

### Run payroll
- `POST /admin/payroll/run/` — `{"month": 6, "year": 2024}` → 200, save payroll records
- `GET /admin/payroll/?month=6&year=2024` → 200, contains payroll

### Generate payslips
- `POST /admin/payroll/generate-payslips/` — `{"month": 6, "year": 2024}` → 200

### Salary advances
- `POST /admin/salary-advances/` — `{"staff_id": "<staff_id>", "amount": 5000, "reason": "Medical emergency", "requested_for_month": 7, "requested_for_year": 2024}` → 201, save `advance_id`
- `GET /admin/salary-advances/` → 200
- `POST /admin/salary-advances/{advance_id}/approve/` → 200
- `POST /admin/salary-advances/{advance_id}/disburse/` → 200

### Reject advance flow
- Create another advance → 201, save `advance_id2`
- `POST /admin/salary-advances/{advance_id2}/reject/` — `{"reason": "Policy limit exceeded"}` → 200

### Salary revisions
- `POST /admin/payroll/salary-revisions/` — `{"staff_id": "<staff_id>", "new_basic": 45000, "effective_date": "2024-07-01", "reason": "Annual hike"}` → 201
- `GET /admin/payroll/salary-revisions/{staff_id}/` → 200, contains revision

---

## 16. Admin Dashboard

All read-only — test after all modules have data.

- `GET /admin/dashboard/stats/` → 200
- `GET /admin/dashboard/attendance-trends/` → 200
- `GET /admin/dashboard/attendance-trends/?year=2024` → 200
- `GET /admin/dashboard/fee-collection-status/` → 200
- `GET /admin/dashboard/student-distribution/` → 200
- `GET /admin/dashboard/recent-activities/` → 200
- `GET /admin/dashboard/recent-activities/?limit=5` → 200
- `GET /admin/dashboard/leave-overview/` → 200
- `GET /admin/dashboard/low-attendance/?threshold=80` → 200

---

## 17. Teacher Portal APIs (as teacher jane@teacher.com)

### Dashboard
- `GET /teacher/dashboard/stats/` → 200
- `GET /teacher/dashboard/today-schedule/` → 200
- `GET /teacher/dashboard/pending-reviews/` → 200
- `GET /teacher/dashboard/upcoming-exams/` → 200
- `GET /teacher/dashboard/classes-summary/` → 200
- `GET /teacher/dashboard/leave-updates/` → 200
- `GET /teacher/dashboard/mentees-summary/` → 200
- `GET /teacher/dashboard/adhoc-classes/` → 200
- `GET /teacher/dashboard/profile/` → 200

### Timetable
- `GET /teacher/timetable/` → 200
- `GET /teacher/timetable/?day=Monday` → 200
- `GET /teacher/timetable/today/` → 200
- `GET /teacher/timetable/today/?date=2024-06-10` → 200

### Students view
- `GET /teacher/students/` → 200 (only mentor's/class teacher's students)
- `GET /teacher/students/?class_name=Class 1` → 200
- `GET /teacher/students/{student_id}/` → 200
- `GET /teacher/students/{student_id}/exam-results/` → 200
- `GET /teacher/students/{student_id}/parent-meetings/` → 200
- `GET /teacher/students/{student_id}/activities/` → 200
- `GET /teacher/students/{student_id}/fee-summary/` → 200
- `GET /teacher/students/{student_id}/behavior/` → 200
- `GET /teacher/students/{student_id}/recent-attendance/` → 200
- `GET /teacher/students/{student_id}/assignments/` → 200

### Grades
- `GET /teacher/grades/exams/` → 200
- `GET /teacher/grades/?class_id=<class_section_id>&exam_id=<exam_id>` → 200
- `POST /teacher/grades/` — `{"class_section_id": "<id>", "exam_id": "<id>", "grades": [{"student_id": "<id>", "marks_obtained": 88}]}` → 201
- `PUT /teacher/grades/` — update a mark → 200
- `GET /teacher/grades/report/?class_id=<id>&exam_id=<id>` → 200
- `GET /teacher/grades/leaderboard/?class_id=<id>&exam_id=<id>` → 200

### Adhoc classes
- `POST /teacher/adhoc-classes/` — `{"class_section_id": "<id>", "subject_id": "<id>", "title": "Extra Class", "date": "2024-06-12", "start_time": "14:00", "end_time": "15:00"}` → 201, save `adhoc_id`
- `GET /teacher/adhoc-classes/` → 200
- `PUT /teacher/adhoc-classes/{adhoc_id}/` — `{"status": "Completed", "student_count": 25}` → 200
- `DELETE /teacher/adhoc-classes/{adhoc_id}/` → 200

---

## 18. Student Portal APIs (as student john@student.com)

### Dashboard
- `GET /student/dashboard/stats/` → 200
- `GET /student/dashboard/today-schedule/` → 200
- `GET /student/dashboard/pending-assignments/` → 200
- `GET /student/dashboard/upcoming-exams/` → 200
- `GET /student/dashboard/subject-attendance/` → 200
- `GET /student/dashboard/recent-results/` → 200
- `GET /student/dashboard/announcements/` → 200
- `GET /student/dashboard/notifications/` → 200
- `GET /student/dashboard/fee-status/` → 200
- `GET /student/dashboard/parent-meetings/` → 200

### Profile
- `GET /student/profile/` → 200
- `PUT /student/profile/` — `{"phone": "9000000001"}` → 200
- `GET /student/profile/` — verify update
- `GET /student/profile/mentor/` → 200

### Timetable
- `GET /student/timetable/` → 200
- `GET /student/timetable/day/` → 200
- `GET /student/timetable/day/?date=2024-06-10` → 200

### Attendance
- `GET /student/attendance/` → 200
- `GET /student/attendance/?academic_year=2024-25` → 200
- `GET /student/attendance/?month=2024-06` → 200
- `GET /student/attendance/history/` → 200
- `GET /student/attendance/history/?subject=Mathematics` → 200
- `GET /student/attendance/warnings/` → 200
- `GET /student/attendance/summary/` → 200
- `GET /student/attendance/monthly/?month=2024-06` → 200

### Assignments
- `GET /student/assignments/` → 200
- `GET /student/assignments/?status=Pending` → 200
- `GET /student/assignments/{assignment_id}/` → 200
- `POST /student/assignments/{assignment_id}/submit/` — multipart form with `comments=Test submission` → 201
- `GET /student/assignments/{assignment_id}/submission/` → 200, verify submitted

### Results
- `GET /student/results/` → 200
- `GET /student/results/exams/` → 200
- `GET /student/results/exam/{exam_id}/` → 200
- `GET /student/results/exam/{exam_id}/leaderboard/` → 200
- `GET /student/results/download-report/` → 200

### Fees
- `GET /student/fees/` → 200
- `GET /student/fees/structure/` → 200
- `GET /student/fees/dues/` → 200
- `GET /student/fees/history/` → 200
- `GET /student/fees/reminders/` → 200
- `GET /student/fees/receipt/{payment_id}/` — use a real payment_id from fee tests → 200

---

## Cross-Module Tests

### Admin creates → Teacher sees → Student sees
1. Admin creates exam for Class 1-A (`POST /admin/examinations/`)
2. Teacher logs in: `GET /teacher/dashboard/upcoming-exams/` — exam appears
3. Student logs in: `GET /student/dashboard/upcoming-exams/` — exam appears
4. Student: `GET /student/results/exams/` — before publish, no result
5. Admin enters results: `POST /admin/examinations/{exam_id}/results/`
6. Admin publishes: `POST /admin/examinations/{exam_id}/publish/`
7. Student: `GET /student/results/exam/{exam_id}/` → 200, result visible
8. Teacher: `GET /teacher/grades/?exam_id=<exam_id>` → 200, results visible

### Admin creates assignment via teacher
1. Teacher creates assignment for Class 1-A
2. Student: `GET /student/assignments/` — assignment appears as Pending
3. Student submits: `POST /student/assignments/{assignment_id}/submit/`
4. Teacher: `GET /teacher/assignments/{assignment_id}/submissions/` — submission visible
5. Teacher grades: `POST /teacher/assignments/{assignment_id}/submissions/{submission_id}/grade/`
6. Student: `GET /student/assignments/{assignment_id}/submission/` — grade visible

### Admin creates notification → portals receive it
1. Admin: `POST /admin/notifications/` — target_type=All
2. Teacher: `GET /teacher/notifications/` — notification visible, is_read=false
3. Teacher: `PUT /teacher/notifications/{id}/read/` → mark read
4. Student: `GET /student/notifications/` — notification visible
5. Student: `PUT /student/notifications/{id}/read/` → mark read

### Attendance flow
1. Teacher submits attendance for Class 1-A
2. Student: `GET /student/attendance/` — session visible
3. Admin: `GET /admin/dashboard/low-attendance/` — reflects updated data

### Fee flow
1. Admin creates fee record for student
2. Student: `GET /student/fees/dues/` — fee appears as Pending
3. Admin records payment
4. Student: `GET /student/fees/history/` — payment visible
5. Student: `GET /student/fees/receipt/{payment_id}/` → 200

---

## Authorization (Role Enforcement) Tests

| Endpoint | Correct Role | Wrong Role Test |
|---|---|---|
| `GET /admin/students/` | Admin | Teacher → 403, Student → 403 |
| `GET /admin/teachers/` | Admin | Student → 403 |
| `GET /admin/dashboard/stats/` | Admin | Teacher → 403 |
| `POST /teacher/attendance/` | Teacher | Student → 403, Admin → 403 |
| `POST /teacher/grades/` | Teacher | Student → 403 |
| `GET /student/profile/` | Student | Teacher → 403, Admin → 403 |
| `PUT /student/profile/` | Student | Teacher → 403 |
| Any endpoint | Any | No cookie → 401 |

---

## Edge Cases (Global)

- All UUID path params: send `00000000-0000-0000-0000-000000000000` → 404
- All UUID path params: send `not-a-uuid` → 422
- Pagination: `?page=0` or `?page=-1` → 422 or sensible default
- Missing required body fields → 422
- Wrong `X-School-Code` header (`SCH999`) → 401 or 404
- Missing `X-School-Code` header → 401 or 400
