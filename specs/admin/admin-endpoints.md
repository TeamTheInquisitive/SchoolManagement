# Admin API Endpoints Reference

**Last Updated:** 2026-06-21

This document provides a comprehensive reference of all admin API endpoints, organized by module.

---

## 1. Dashboard

**Prefix:** `/admin/dashboard`

| Method | Path | Description | Notes |
|--------|------|-------------|-------|
| GET | `/admin/dashboard/stats` | Get overall school statistics | Returns counts of students, teachers, staff, etc. |
| GET | `/admin/dashboard/stats/students` | Get student statistics | Enrollment counts, active/inactive breakdown |
| GET | `/admin/dashboard/stats/teachers` | Get teacher statistics | Active teachers, subject distribution |
| GET | `/admin/dashboard/stats/staff` | Get staff statistics | Staff count by role/department |
| GET | `/admin/dashboard/stats/attendance` | Get attendance statistics | Today's attendance summary |
| GET | `/admin/dashboard/stats/fees` | Get fee collection statistics | Collection vs pending amounts |
| GET | `/admin/dashboard/stats/transport` | Get transport statistics | Vehicle/route utilization |
| GET | `/admin/dashboard/stats/library` | Get library statistics | Books issued, overdue counts |
| GET | `/admin/dashboard/trends/enrollment` | Get enrollment trends | Monthly/yearly enrollment data |
| GET | `/admin/dashboard/trends/attendance` | Get attendance trends | Attendance patterns over time |
| GET | `/admin/dashboard/trends/fees` | Get fee collection trends | Collection trends over time |
| GET | `/admin/dashboard/trends/performance` | Get academic performance trends | Grade/exam score trends |
| GET | `/admin/dashboard/trends/leaves` | Get leave trends | Staff/teacher leave patterns |
| GET | `/admin/dashboard/analytics/class-performance` | Get class-wise performance analytics | Comparison across classes |
| GET | `/admin/dashboard/analytics/subject-performance` | Get subject-wise performance analytics | Subject-level analysis |
| GET | `/admin/dashboard/analytics/teacher-performance` | Get teacher performance analytics | Teacher effectiveness metrics |
| GET | `/admin/dashboard/analytics/fee-defaulters` | Get fee defaulter analytics | Students with pending fees |
| GET | `/admin/dashboard/analytics/attendance-low` | Get low attendance analytics | Students below threshold |
| GET | `/admin/dashboard/analytics/transport-utilization` | Get transport utilization analytics | Route/vehicle capacity usage |
| GET | `/admin/dashboard/analytics/gender-ratio` | Get gender ratio analytics | Gender distribution across classes |
| GET | `/admin/dashboard/analytics/age-distribution` | Get age distribution analytics | Student age demographics |
| GET | `/admin/dashboard/analytics/new-admissions` | Get new admissions analytics | Recent admission trends |
| GET | `/admin/dashboard/analytics/staff-attendance` | Get staff attendance analytics | Staff attendance patterns |
| GET | `/admin/dashboard/analytics/exam-results` | Get exam results analytics | Recent exam result summaries |
| GET | `/admin/dashboard/analytics/notifications` | Get notification analytics | Notification delivery stats |

---

## 2. Students

**Prefix:** `/admin/students`

| Method | Path | Description | Notes |
|--------|------|-------------|-------|
| GET | `/admin/students` | List all students | Supports pagination, filtering, search |
| POST | `/admin/students` | Create a new student | Creates student record with all details |
| GET | `/admin/students/{id}` | Get student by ID | Returns full student profile |
| PUT | `/admin/students/{id}` | Update student details | Partial or full update |
| DELETE | `/admin/students/{id}` | Delete a student | **SOFT DELETE** - sets is_active=False, student record is preserved |
| GET | `/admin/students/search` | Search students | Full-text search across name, ID, etc. |
| GET | `/admin/students/export` | Export students list | Returns CSV/Excel of student data |
| POST | `/admin/students/bulk-import` | Bulk import students | Upload CSV/Excel for batch creation |
| GET | `/admin/students/{id}/attendance` | Get student attendance history | Attendance records for a student |
| GET | `/admin/students/{id}/fees` | Get student fee records | Fee payment history |
| GET | `/admin/students/{id}/results` | Get student exam results | All exam results for a student |
| GET | `/admin/students/{id}/transport` | Get student transport details | Assigned route/vehicle info |
| GET | `/admin/students/{id}/library` | Get student library records | Books issued/returned |
| GET | `/admin/students/{id}/leaves` | Get student leave history | Leave applications and status |
| GET | `/admin/students/{id}/documents` | Get student documents | Uploaded documents list |
| POST | `/admin/students/{id}/documents` | Upload student document | Attach document to student profile |
| DELETE | `/admin/students/{id}/documents/{doc_id}` | Delete student document | Remove an uploaded document |
| GET | `/admin/students/{id}/siblings` | Get student siblings | Linked sibling records |
| POST | `/admin/students/{id}/siblings` | Link sibling | Associate sibling relationship |
| GET | `/admin/students/{id}/parent-info` | Get parent/guardian info | Parent contact details |
| PUT | `/admin/students/{id}/parent-info` | Update parent/guardian info | Modify parent details |
| POST | `/admin/students/{id}/promote` | Promote student to next class | Handles section assignment |
| POST | `/admin/students/bulk-promote` | Bulk promote students | Promote multiple students at once |
| GET | `/admin/students/{id}/timeline` | Get student activity timeline | Chronological activity log |
| GET | `/admin/students/class/{class_id}` | Get students by class | List students in a specific class |
| GET | `/admin/students/section/{section_id}` | Get students by section | List students in a specific section |
| GET | `/admin/students/{id}/mentor` | Get student mentor details | Assigned mentor information |

---

## 3. Teachers

**Prefix:** `/admin/teachers`

| Method | Path | Description | Notes |
|--------|------|-------------|-------|
| GET | `/admin/teachers` | List all teachers | Supports pagination and filtering |
| POST | `/admin/teachers` | Create a new teacher | Register teacher with qualifications |
| GET | `/admin/teachers/{id}` | Get teacher by ID | Full teacher profile |
| PUT | `/admin/teachers/{id}` | Update teacher details | Modify teacher information |
| DELETE | `/admin/teachers/{id}` | Delete a teacher | **SOFT DELETE** - sets is_active=False, preserves historical data |
| GET | `/admin/teachers/search` | Search teachers | Search by name, subject, etc. |
| GET | `/admin/teachers/export` | Export teachers list | CSV/Excel export |
| GET | `/admin/teachers/{id}/assignments` | Get teacher class/subject assignments | Current teaching assignments |
| POST | `/admin/teachers/{id}/assignments` | Assign teacher to class/subject | Create new assignment |
| PUT | `/admin/teachers/{id}/assignments/{assignment_id}` | Update assignment | Modify existing assignment |
| DELETE | `/admin/teachers/{id}/assignments/{assignment_id}` | Remove assignment | Unassign teacher from class/subject |
| GET | `/admin/teachers/{id}/timetable` | Get teacher timetable | Weekly schedule |
| GET | `/admin/teachers/{id}/attendance` | Get teacher attendance | Attendance history |
| GET | `/admin/teachers/{id}/leaves` | Get teacher leaves | Leave applications and status |
| GET | `/admin/teachers/{id}/awards` | Get teacher awards | Awards and recognitions |
| POST | `/admin/teachers/{id}/awards` | Add teacher award | Create new award entry |
| PUT | `/admin/teachers/{id}/awards/{award_id}` | Update teacher award | Modify award details |
| DELETE | `/admin/teachers/{id}/awards/{award_id}` | Delete teacher award | Remove award record |

---

## 4. Staff

**Prefix:** `/admin/staff`

| Method | Path | Description | Notes |
|--------|------|-------------|-------|
| GET | `/admin/staff` | List all staff members | Supports pagination, filtering by role/department |
| POST | `/admin/staff` | Create a new staff member | Register non-teaching staff |
| GET | `/admin/staff/{id}` | Get staff member by ID | Full staff profile |
| PUT | `/admin/staff/{id}` | Update staff details | Modify staff information |
| DELETE | `/admin/staff/{id}` | Delete a staff member | **SOFT DELETE** - sets is_active=False |
| GET | `/admin/staff/export` | Export staff list | CSV/Excel export |
| POST | `/admin/staff/bulk-import` | Bulk import staff | Upload CSV/Excel for batch creation |

> **Note:** The payroll router shares the `/admin/staff` prefix (see Payroll section below).

---

## 5. Attendance

**Prefix:** `/admin/attendance`

| Method | Path | Description | Notes |
|--------|------|-------------|-------|
| GET | `/admin/attendance` | Get attendance records | Filter by date, class, section |
| POST | `/admin/attendance` | Submit attendance | Mark attendance for a class/section |
| PUT | `/admin/attendance` | Update attendance | Modify existing attendance records |
| GET | `/admin/attendance/class-subjects-status` | Get class-subjects attendance status | Shows which classes have attendance marked today |

> **Note:** Attendance cancel operation sets the `cancelled_at` timestamp rather than deleting the record.

---

## 6. Timetable

**Prefix:** `/admin/timetable`

> **IMPORTANT:** All delete operations in this module perform **HARD DELETE** - records are permanently removed from the database.

| Method | Path | Description | Notes |
|--------|------|-------------|-------|
| GET | `/admin/timetable/periods` | List all periods | Get period definitions |
| POST | `/admin/timetable/periods` | Create a period | Define a new period slot |
| PUT | `/admin/timetable/periods/{id}` | Update a period | Modify period timing/name |
| DELETE | `/admin/timetable/periods/{id}` | Delete a period | **HARD DELETE** - permanently removes period record |
| GET | `/admin/timetable/slots` | List timetable slots | Get assigned slots with filters |
| POST | `/admin/timetable/slots` | Create a timetable slot | Assign teacher/subject to period |
| PUT | `/admin/timetable/slots/{id}` | Update a timetable slot | Modify slot assignment |
| DELETE | `/admin/timetable/slots/{id}` | Delete a timetable slot | **HARD DELETE** - permanently removes slot record |
| POST | `/admin/timetable/slots/bulk` | Bulk create slots | Create multiple slots at once |
| GET | `/admin/timetable/conflicts` | Check for timetable conflicts | Detect teacher/room overlaps |
| POST | `/admin/timetable/reset-class-section` | Reset timetable for class/section | **HARD DELETE** - permanently removes all slots for the specified class-section |
| GET | `/admin/timetable/class/{class_id}/section/{section_id}` | Get timetable for class-section | Full weekly timetable view |

---

## 7. Examinations

**Prefix:** `/admin/examinations`

| Method | Path | Description | Notes |
|--------|------|-------------|-------|
| GET | `/admin/examinations` | List all examinations | Filter by term, class, status |
| POST | `/admin/examinations` | Create an examination | Define new exam with schedule |
| GET | `/admin/examinations/{id}` | Get examination details | Full exam configuration |
| PUT | `/admin/examinations/{id}` | Update examination | Modify exam details |
| DELETE | `/admin/examinations/{id}` | Delete examination | Remove exam and associated data |
| GET | `/admin/examinations/{id}/results` | Get exam results | Results for all students in exam |
| POST | `/admin/examinations/{id}/results` | Submit exam results | Enter marks/grades for students |
| PUT | `/admin/examinations/{id}/results` | Update exam results | Modify submitted results |
| GET | `/admin/examinations/{id}/results/export` | Export exam results | CSV/Excel export of results |
| GET | `/admin/examinations/grade-system` | Get grade system configuration | Current grading scale |
| POST | `/admin/examinations/grade-system` | Create grade system | Define new grading scale |
| PUT | `/admin/examinations/grade-system/{id}` | Update grade system | Modify grading thresholds |
| DELETE | `/admin/examinations/grade-system/{id}` | Delete grade system | Remove grading scale |
| GET | `/admin/examinations/analytics/class/{class_id}` | Get class exam analytics | Class-level performance analysis |
| GET | `/admin/examinations/analytics/subject/{subject_id}` | Get subject exam analytics | Subject-level performance analysis |
| GET | `/admin/examinations/analytics/student/{student_id}` | Get student exam analytics | Individual student performance trends |

---

## 8. Fees

**Prefix:** `/admin/fees`

| Method | Path | Description | Notes |
|--------|------|-------------|-------|
| GET | `/admin/fees` | List all fee records | Filter by class, student, status |
| POST | `/admin/fees` | Create a fee record | Assign fee to student(s) |
| GET | `/admin/fees/{id}` | Get fee record details | Individual fee record |
| PUT | `/admin/fees/{id}` | Update fee record | Modify fee amount/details |
| DELETE | `/admin/fees/{id}` | Delete fee record | **DELETE** - removes fee record |
| GET | `/admin/fees/{id}/payments` | Get payments for a fee | Payment history for a fee record |
| POST | `/admin/fees/{id}/payments` | Record a payment | Add payment against fee |
| GET | `/admin/fees/payments/{payment_id}` | Get payment details | Individual payment record |
| PUT | `/admin/fees/payments/{payment_id}` | Update payment | Modify payment details |
| GET | `/admin/fees/late-fees` | Get late fee records | List overdue fee entries |
| POST | `/admin/fees/late-fees/apply` | Apply late fees | Calculate and apply late fee charges |
| GET | `/admin/fees/reminders` | Get fee reminders | List sent/pending reminders |
| POST | `/admin/fees/reminders` | Send fee reminder | Trigger reminder notification |
| GET | `/admin/fees/summary` | Get fee collection summary | Aggregated collection stats |
| GET | `/admin/fees/export` | Export fee records | CSV/Excel export |

---

## 9. Leaves

**Prefix:** `/admin/leaves`

| Method | Path | Description | Notes |
|--------|------|-------------|-------|
| GET | `/admin/leaves` | List all leave applications | Filter by status, type, user |
| GET | `/admin/leaves/{id}` | Get leave application details | Individual leave record |
| POST | `/admin/leaves` | Create leave application | Submit leave on behalf of user |
| PUT | `/admin/leaves/{id}` | Update leave application | Modify leave details |
| POST | `/admin/leaves/{id}/approve` | Approve leave application | Sets status to approved |
| POST | `/admin/leaves/{id}/reject` | Reject leave application | Sets status to rejected with reason |
| POST | `/admin/leaves/{id}/cancel` | Cancel leave application | Cancel previously approved leave |
| GET | `/admin/leaves/policy` | Get leave policies | List all leave type policies |
| POST | `/admin/leaves/policy` | Create leave policy | Define new leave type with quota |
| PUT | `/admin/leaves/policy/{id}` | Update leave policy | Modify leave policy rules |
| GET | `/admin/leaves/calendar` | Get leave calendar | Visual calendar of approved leaves |

---

## 10. Payroll

**Prefix:** `/admin/staff/payroll`

> **Note:** This router shares the `/admin/staff` prefix with the Staff router.

| Method | Path | Description | Notes |
|--------|------|-------------|-------|
| GET | `/admin/staff/payroll/payslips` | List all payslips | Filter by month, staff, status |
| POST | `/admin/staff/payroll/payslips` | Generate payslips | Create payslips for a pay period |
| GET | `/admin/staff/payroll/payslips/{id}` | Get payslip details | Individual payslip record |
| PUT | `/admin/staff/payroll/payslips/{id}` | Update payslip | Modify payslip before finalization |
| POST | `/admin/staff/payroll/payslips/{id}/approve` | Approve payslip | Mark payslip as approved |
| POST | `/admin/staff/payroll/payslips/bulk-approve` | Bulk approve payslips | Approve multiple payslips at once |
| GET | `/admin/staff/payroll/salary-structures` | List salary structures | All defined salary structures |
| POST | `/admin/staff/payroll/salary-structures` | Create salary structure | Define new salary components |
| GET | `/admin/staff/payroll/salary-structures/{id}` | Get salary structure details | Individual structure breakdown |
| PUT | `/admin/staff/payroll/salary-structures/{id}` | Update salary structure | Modify salary components |
| DELETE | `/admin/staff/payroll/salary-structures/{id}` | Delete salary structure | Remove salary structure |
| GET | `/admin/staff/payroll/advances` | List salary advances | All advance requests |
| POST | `/admin/staff/payroll/advances` | Create salary advance | Record advance payment |
| PUT | `/admin/staff/payroll/advances/{id}` | Update salary advance | Modify advance details |
| POST | `/admin/staff/payroll/advances/{id}/approve` | Approve salary advance | Approve advance request |
| GET | `/admin/staff/payroll/revisions` | List salary revisions | Salary revision history |
| POST | `/admin/staff/payroll/revisions` | Create salary revision | Record salary increment/revision |
| GET | `/admin/staff/payroll/revisions/{id}` | Get revision details | Individual revision record |
| GET | `/admin/staff/payroll/summary` | Get payroll summary | Monthly payroll aggregates |

---

## 11. Settings

**Prefix:** `/admin/settings`

| Method | Path | Description | Notes |
|--------|------|-------------|-------|
| GET | `/admin/settings/school` | Get school configuration | School name, logo, contact info |
| PUT | `/admin/settings/school` | Update school configuration | Modify school details |
| GET | `/admin/settings/academic-years` | List academic years | All defined academic years |
| POST | `/admin/settings/academic-years` | Create academic year | Define new academic year |
| PUT | `/admin/settings/academic-years/{id}` | Update academic year | Modify academic year dates |
| DELETE | `/admin/settings/academic-years/{id}` | Delete academic year | Remove academic year |
| POST | `/admin/settings/academic-years/{id}/activate` | Set active academic year | Switch current academic year |
| GET | `/admin/settings/enums` | Get all enum values | List configurable dropdowns |
| POST | `/admin/settings/enums` | Create enum value | Add new dropdown option |
| PUT | `/admin/settings/enums/{id}` | Update enum value | Modify enum option |
| DELETE | `/admin/settings/enums/{id}` | Delete enum value | Remove enum option |
| GET | `/admin/settings/classes` | List all classes | Class definitions |
| POST | `/admin/settings/classes` | Create a class | Define new class |
| PUT | `/admin/settings/classes/{id}` | Update class | Modify class details |
| DELETE | `/admin/settings/classes/{id}` | Delete class | Remove class definition |
| GET | `/admin/settings/sections` | List all sections | Section definitions |
| POST | `/admin/settings/sections` | Create a section | Define new section |
| PUT | `/admin/settings/sections/{id}` | Update section | Modify section details |
| DELETE | `/admin/settings/sections/{id}` | Delete section | Remove section definition |
| GET | `/admin/settings/subjects` | List all subjects | Subject definitions |
| POST | `/admin/settings/subjects` | Create a subject | Define new subject |
| PUT | `/admin/settings/subjects/{id}` | Update subject | Modify subject details |
| DELETE | `/admin/settings/subjects/{id}` | Delete subject | Remove subject definition |
| GET | `/admin/settings/fee-structures` | List fee structures | Fee structure templates |
| POST | `/admin/settings/fee-structures` | Create fee structure | Define new fee structure |
| PUT | `/admin/settings/fee-structures/{id}` | Update fee structure | Modify fee structure |
| DELETE | `/admin/settings/fee-structures/{id}` | Delete fee structure | Remove fee structure |
| GET | `/admin/settings/holidays` | List holidays | Calendar holidays |
| POST | `/admin/settings/holidays` | Create holiday | Add holiday to calendar |
| PUT | `/admin/settings/holidays/{id}` | Update holiday | Modify holiday details |
| DELETE | `/admin/settings/holidays/{id}` | Delete holiday | Remove holiday |
| GET | `/admin/settings/id-generation` | Get ID generation config | Auto-ID format settings |
| PUT | `/admin/settings/id-generation` | Update ID generation config | Modify ID format/sequence |
| GET | `/admin/settings/attendance-config` | Get attendance configuration | Attendance rules and thresholds |
| PUT | `/admin/settings/attendance-config` | Update attendance configuration | Modify attendance settings |
| GET | `/admin/settings/class-subjects` | Get class-subject mappings | Which subjects are taught in which class |
| POST | `/admin/settings/class-subjects` | Create class-subject mapping | Assign subject to class |
| DELETE | `/admin/settings/class-subjects/{id}` | Delete class-subject mapping | Remove subject from class |

---

## 12. Transport

**Prefix:** `/admin/transport`

| Method | Path | Description | Notes |
|--------|------|-------------|-------|
| GET | `/admin/transport/vehicles` | List all vehicles | Fleet inventory |
| POST | `/admin/transport/vehicles` | Create a vehicle | Register new vehicle |
| GET | `/admin/transport/vehicles/{id}` | Get vehicle details | Individual vehicle record |
| PUT | `/admin/transport/vehicles/{id}` | Update vehicle | Modify vehicle details |
| DELETE | `/admin/transport/vehicles/{id}` | Delete vehicle | **SOFT DELETE** - deactivates vehicle |
| GET | `/admin/transport/drivers` | List all drivers | Driver roster |
| POST | `/admin/transport/drivers` | Create a driver | Register new driver |
| GET | `/admin/transport/drivers/{id}` | Get driver details | Individual driver record |
| PUT | `/admin/transport/drivers/{id}` | Update driver | Modify driver details |
| DELETE | `/admin/transport/drivers/{id}` | Delete driver | **SOFT DELETE** - deactivates driver |
| GET | `/admin/transport/helpers` | List all helpers | Helper/attendant roster |
| POST | `/admin/transport/helpers` | Create a helper | Register new helper |
| GET | `/admin/transport/helpers/{id}` | Get helper details | Individual helper record |
| PUT | `/admin/transport/helpers/{id}` | Update helper | Modify helper details |
| DELETE | `/admin/transport/helpers/{id}` | Delete helper | **SOFT DELETE** - deactivates helper |
| GET | `/admin/transport/routes` | List all routes | Route definitions |
| POST | `/admin/transport/routes` | Create a route | Define new route with stops |
| GET | `/admin/transport/routes/{id}` | Get route details | Individual route with stops |
| PUT | `/admin/transport/routes/{id}` | Update route | Modify route details/stops |
| DELETE | `/admin/transport/routes/{id}` | Delete route | **SOFT DELETE** - deactivates route |
| GET | `/admin/transport/assignments` | List vehicle-route assignments | Which vehicle serves which route |
| POST | `/admin/transport/assignments` | Create vehicle-route assignment | Assign vehicle to route |
| PUT | `/admin/transport/assignments/{id}` | Update assignment | Modify assignment details |
| DELETE | `/admin/transport/assignments/{id}` | Delete assignment | Remove vehicle-route assignment |
| GET | `/admin/transport/students` | List student transport assignments | Students assigned to routes |
| POST | `/admin/transport/students` | Assign student to route | Add student to transport route |
| PUT | `/admin/transport/students/{id}` | Update student assignment | Modify student stop/route |
| DELETE | `/admin/transport/students/{id}` | Remove student from route | Unassign student from transport |

---

## 13. Library

**Prefix:** `/admin/library`

| Method | Path | Description | Notes |
|--------|------|-------------|-------|
| GET | `/admin/library/books` | List all books | Library catalog with filters |
| POST | `/admin/library/books` | Add a book | Register new book in library |
| GET | `/admin/library/books/{id}` | Get book details | Individual book record |
| PUT | `/admin/library/books/{id}` | Update book | Modify book details |
| POST | `/admin/library/issues` | Issue a book | Lend book to student/staff |
| POST | `/admin/library/issues/{id}/return` | Return a book | Process book return |

---

## 14. Notifications

**Prefix:** `/admin/notifications`

| Method | Path | Description | Notes |
|--------|------|-------------|-------|
| GET | `/admin/notifications` | List all notifications | Sent/scheduled notifications |
| POST | `/admin/notifications` | Create a notification | Send new notification |
| GET | `/admin/notifications/{id}` | Get notification details | Individual notification record |
| PUT | `/admin/notifications/{id}` | Update notification | Modify notification (if not sent) |
| DELETE | `/admin/notifications/{id}` | Delete notification | Remove notification |
| GET | `/admin/notifications/templates` | List notification templates | Reusable templates |
| POST | `/admin/notifications/templates` | Create notification template | Define new template |
| GET | `/admin/notifications/teacher-sent` | Get teacher-sent notifications | Notifications sent by teachers |

---

## 15. Mentoring

**Prefix:** `/admin/mentoring`

| Method | Path | Description | Notes |
|--------|------|-------------|-------|
| GET | `/admin/mentoring/assignments` | List mentor assignments | All mentor-student pairs |
| POST | `/admin/mentoring/assignments` | Create mentor assignment | Assign mentor to student(s) |
| GET | `/admin/mentoring/assignments/{id}` | Get assignment details | Individual assignment record |
| PUT | `/admin/mentoring/assignments/{id}` | Update mentor assignment | Modify assignment |
| DELETE | `/admin/mentoring/assignments/{id}` | Delete mentor assignment | Remove mentor-student pairing |
| POST | `/admin/mentoring/auto-assign` | Auto-assign mentors | Automatically distribute students to mentors |
| GET | `/admin/mentoring/auto-assign/preview` | Preview auto-assignment | Preview proposed assignments before applying |

---

## Behavioral Notes Summary

| Module | Delete Behavior | Details |
|--------|----------------|---------|
| Students | SOFT DELETE | Sets `is_active=False`, preserves all historical records |
| Teachers | SOFT DELETE | Sets `is_active=False`, preserves assignments and historical data |
| Staff | SOFT DELETE | Sets `is_active=False` |
| Timetable | **HARD DELETE** | Periods, slots, and reset-class-section all permanently delete records from the database |
| Transport | SOFT DELETE | Vehicles, drivers, helpers, and routes are deactivated rather than removed |
| Attendance | Cancel via timestamp | Cancel operation sets `cancelled_at` timestamp rather than deleting |
| Fees | DELETE available | Fee records can be deleted |
| Superadmin School | **HARD DELETE + CASCADE** | School hard-delete cascades across ALL related tables |

---

## Shared Prefix Note

The **Payroll** router (`/admin/staff/payroll`) shares the `/admin/staff` prefix with the **Staff** router. Both are mounted under the same base path, with payroll endpoints distinguished by the `/payroll` sub-path.
