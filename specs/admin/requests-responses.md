# School ERP Backend - Admin Portal: Requests & Responses

> Detailed request/response documentation for all Admin Portal API endpoints.
> For quick endpoint reference, see [admin-endpoints.md](./admin-endpoints.md).

---

## 1. Authentication (Shared)

### POST /api/v1/auth/login

**Request:**
```json
{
  "email": "admin@school.com",
  "password": "password123"
}
```

**Response: 200**
```json
{
  "user": {
    "id": "uuid",
    "email": "admin@school.com",
    "full_name": "John Admin",
    "role": "admin",
    "school_code": "SCH001",
    "avatar_url": null
  }
}
```

---

### POST /api/v1/auth/change-password

**Request:**
```json
{
  "current_password": "oldpass",
  "new_password": "newpass123"
}
```

**Response: 200**
```json
{"message": "Password changed successfully"}
```

---

## 2. Dashboard (`/admin/dashboard`)

### GET /api/v1/admin/dashboard/stats

**Response: 200 — `DashboardStatsResponse`**
```json
{
  "total_students": 1200,
  "total_teachers": 65,
  "active_classes": 30,
  "fee_collection_percentage": 78.5,
  "students_change": "+5%",
  "teachers_change": "+2%",
  "classes_change": "+3",
  "fee_change": "+12%"
}
```

---

### GET /api/v1/admin/dashboard/attendance-trends

**Query Params:** `months` (optional, default 6)

**Response: 200 — `AttendanceTrendsResponse`**
```json
{
  "data": [
    {"month": "Jan", "value": 92.5},
    {"month": "Feb", "value": 91.0}
  ]
}
```

---

### GET /api/v1/admin/dashboard/fee-collection-status

**Response: 200 — `FeeCollectionStatusResponse`**
```json
{
  "data": [
    {"name": "Collected", "value": 78.5, "color": "#4CAF50"},
    {"name": "Pending", "value": 15.0, "color": "#FFC107"},
    {"name": "Overdue", "value": 6.5, "color": "#F44336"}
  ]
}
```

---

### GET /api/v1/admin/dashboard/student-distribution

**Response: 200 — `StudentDistributionResponse`**
```json
{
  "data": [
    {"class_name": "10", "male": 25, "female": 22},
    {"class_name": "9", "male": 28, "female": 24}
  ]
}
```

---

### GET /api/v1/admin/dashboard/recent-activities

**Response: 200 — `RecentActivitiesResponse`**
```json
{
  "data": [
    {
      "id": "uuid",
      "title": "New student enrolled",
      "description": "Rahul Kumar admitted to Class 10-A",
      "date": "2024-01-15",
      "tag": "Admission",
      "category": "student"
    }
  ]
}
```

---

### GET /api/v1/admin/dashboard/leave-overview

**Response: 200 — `LeaveOverviewResponse`**
```json
{
  "pending_requests": 5,
  "approved": 12,
  "on_leave_today": 3,
  "upcoming_leaves": 8,
  "pending_approvals": [
    {
      "id": "uuid",
      "employee_name": "Jane Smith",
      "leave_type": "Casual Leave",
      "duration_days": 2.0,
      "from_date": "2024-01-20",
      "to_date": "2024-01-21"
    }
  ]
}
```

---

### GET /api/v1/admin/dashboard/low-attendance

**Query Params:** `threshold` (optional, default 75)

**Response: 200 — `LowAttendanceResponse`**
```json
{
  "data": [
    {
      "student_id": "uuid",
      "name": "Amit Singh",
      "class_section": "10-A",
      "attendance_percentage": 68.0
    }
  ]
}
```

---

## 3. Settings (`/admin/settings`)

### GET /api/v1/admin/settings

**Response: 200**
```json
{
  "school_name": "Delhi Public School",
  "school_code": "SCH001",
  "academic_year": "2024-25",
  "attendance_threshold": 75,
  "grading_system": "percentage",
  "fee_late_penalty_percentage": 5,
  "metadata": {}
}
```

---

### PUT /api/v1/admin/settings/school-profile

**Request:**
```json
{
  "school_name": "Delhi Public School",
  "address": "Sector 24, Gurugram",
  "phone": "0124-1234567",
  "email": "info@dps.edu",
  "website": "https://dps.edu",
  "principal_name": "Dr. Sharma"
}
```

**Response: 200**
```json
{"message": "School profile updated", "updated_fields": ["phone", "website"]}
```

---

### POST /api/v1/admin/settings/academic-years

**Request:**
```json
{
  "name": "2025-26",
  "start_date": "2025-04-01",
  "end_date": "2026-03-31"
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "name": "2025-26",
  "start_date": "2025-04-01",
  "end_date": "2026-03-31",
  "is_current": false
}
```

---

### POST /api/v1/admin/settings/classes/bulk

**Request:**
```json
{
  "classes": [
    {"name": "1", "display_order": 1},
    {"name": "2", "display_order": 2}
  ]
}
```

**Response: 201**
```json
{"message": "Classes created", "count": 2, "classes": [...]}
```

---

### DELETE /api/v1/admin/settings/classes/{class_id}

Soft-delete a class and its associated class-section mappings.

**Response: 200**
```json
{"message": "Class deleted", "class_id": "uuid"}
```

---

### DELETE /api/v1/admin/settings/class-sections/{class_section_id}

Soft-delete a class-section mapping.

**Response: 200**
```json
{"message": "Class-section deleted", "class_section_id": "uuid"}
```

---

### POST /api/v1/admin/settings/sections/bulk

**Request:**
```json
{
  "class_id": "uuid",
  "sections": [{"name": "A"}, {"name": "B"}, {"name": "C"}]
}
```

**Response: 201**
```json
{"message": "Sections created", "count": 3}
```

---

### POST /api/v1/admin/settings/subjects/bulk

**Request:**
```json
{
  "subjects": [
    {"name": "Mathematics", "code": "MATH", "type": "core"},
    {"name": "Physics", "code": "PHY", "type": "core"}
  ]
}
```

**Response: 201**
```json
{"message": "Subjects created", "count": 2}
```

---

### GET /api/v1/admin/settings/enums/{category}

**Path Params:** `category` — e.g., `leave_types`, `fee_types`, `exam_types`, `departments`

**Response: 200**
```json
{
  "category": "leave_types",
  "values": ["Casual Leave", "Sick Leave", "Earned Leave", "Maternity Leave"]
}
```

---

### PUT /api/v1/admin/settings/enums/{category}

**Request:**
```json
{
  "values": ["Casual Leave", "Sick Leave", "Earned Leave", "Maternity Leave", "Paternity Leave"]
}
```

**Response: 200**
```json
{"message": "Enum updated", "category": "leave_types", "count": 5}
```

---

## 4. Students (`/admin/students`)

### GET /api/v1/admin/students

**Query Params:** `page`, `page_size`, `class_name` (optional), `section` (optional), `search` (optional), `status` (optional), `academic_year` (optional)

**Response: 200**
```json
{
  "count": 1200,
  "page": 1,
  "page_size": 20,
  "total_pages": 60,
  "results": [
    {
      "id": "uuid",
      "roll_number": "STU2024015",
      "full_name": "Rahul Kumar",
      "email": "rahul@student.com",
      "class_name": "10",
      "section": "A",
      "class_section": "10-A",
      "gender": "Male",
      "status": "Active",
      "admission_date": "2022-04-01",
      "avatar_url": null,
      "metadata": {}
    }
  ]
}
```

---

### POST /api/v1/admin/students

**Request:**
```json
{
  "full_name": "Rahul Kumar",
  "email": "rahul@student.com",
  "class_name": "10",
  "section": "A",
  "date_of_birth": "2008-05-15",
  "gender": "Male",
  "parent_name": "Suresh Kumar",
  "parent_phone": "9876543211",
  "address": "123 Main St, Gurugram",
  "academic_year": "2024-25"
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "roll_number": "STU2024015",
  "full_name": "Rahul Kumar",
  "email": "rahul@student.com",
  "class_name": "10",
  "section": "A",
  "class_section": "10-A",
  "status": "Active",
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

### POST /api/v1/admin/students/bulk-import

**Request:** `multipart/form-data` with CSV file

**Response: 200**
```json
{
  "imported": 45,
  "skipped": 3,
  "errors": [{"row": 12, "message": "Duplicate email"}],
  "message": "45 students imported"
}
```

---

### POST /api/v1/admin/students/bulk-import-json

**Request:**
```json
{
  "students": [
    {"full_name": "Student 1", "class_name": "10", "section": "A", ...},
    {"full_name": "Student 2", "class_name": "10", "section": "B", ...}
  ]
}
```

**Response: 200**
```json
{"imported": 2, "skipped": 0, "errors": []}
```

---

### POST /api/v1/admin/students/{student_id}/parent-meetings

**Request:**
```json
{
  "meeting_type": "PTM",
  "date": "2024-01-20",
  "conducted_by": "Ms. Smith",
  "notes": "Discussed academic progress",
  "attendance_status": "Attended"
}
```

**Response: 201**
```json
{"id": "uuid", "message": "Meeting created"}
```

---

### POST /api/v1/admin/students/{student_id}/disciplinary-records

**Request:**
```json
{
  "incident_date": "2024-01-15",
  "type": "Warning",
  "description": "Late to class 3 times this week",
  "action_taken": "Written warning issued"
}
```

**Response: 201**
```json
{"id": "uuid", "message": "Record created"}
```

---

## 5. Teachers (`/admin/teachers`)

### GET /api/v1/admin/teachers

**Query Params:** `page`, `page_size`, `department` (optional), `search` (optional), `status` (optional)

**Response: 200**
```json
{
  "count": 65,
  "page": 1,
  "page_size": 20,
  "total_pages": 4,
  "results": [
    {
      "id": "uuid",
      "employee_id": "TCH001",
      "full_name": "Jane Smith",
      "email": "jane@teacher.com",
      "department": "Mathematics",
      "designation": "Senior Teacher",
      "subjects": ["Mathematics"],
      "class_assignments": ["10-A", "10-B", "9-A"],
      "status": "Active",
      "joining_date": "2015-06-01"
    }
  ]
}
```

---

### POST /api/v1/admin/teachers

**Request:**
```json
{
  "full_name": "Jane Smith",
  "email": "jane@teacher.com",
  "phone": "9876543210",
  "department": "Mathematics",
  "designation": "Senior Teacher",
  "qualification": "M.Sc, B.Ed",
  "subjects": ["Mathematics"],
  "joining_date": "2015-06-01",
  "salary": 75000
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "employee_id": "TCH001",
  "full_name": "Jane Smith",
  "status": "Active",
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

### POST /api/v1/admin/teachers/{teacher_id}/assign-class

**Request:**
```json
{
  "class_name": "10",
  "section": "A",
  "subject": "Mathematics",
  "is_class_teacher": false
}
```

**Response: 201**
```json
{"id": "uuid", "message": "Class assigned successfully"}
```

---

### POST /api/v1/admin/teachers/{teacher_id}/bulk-assign

**Request:**
```json
{
  "assignments": [
    {"class_name": "10", "section": "A", "subject": "Mathematics"},
    {"class_name": "10", "section": "B", "subject": "Mathematics"}
  ]
}
```

**Response: 201**
```json
{"message": "2 assignments created", "count": 2}
```

---

## 6. Staff (`/admin/staff`)

### POST /api/v1/admin/staff

**Request:**
```json
{
  "full_name": "Ram Kumar",
  "email": "ram@school.com",
  "phone": "9876543210",
  "department": "Administration",
  "designation": "Office Assistant",
  "joining_date": "2020-06-01",
  "salary": 25000
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "employee_id": "STF001",
  "full_name": "Ram Kumar",
  "status": "Active"
}
```

---

## 7. Payroll (`/admin/staff/payroll`)

### DELETE /api/v1/admin/staff/payroll

Soft-delete all payslips for a given month/year.

**Request:**
```json
{
  "month": 1,
  "year": 2024
}
```

**Response: 200**
```json
{"message": "Monthly payroll deleted", "deleted_count": 65}
```

---

### POST /api/v1/admin/staff/payroll/run

**Request:**
```json
{
  "month": 1,
  "year": 2024,
  "department": null
}
```

**Response: 200**
```json
{
  "message": "Payroll generated",
  "month": 1,
  "year": 2024,
  "total_staff": 65,
  "total_amount": 4875000.0,
  "payslips_generated": 65
}
```

---

### GET /api/v1/admin/staff/payroll/salary-structure/{employee_id}

**Response: 200**
```json
{
  "employee_id": "uuid",
  "employee_name": "Jane Smith",
  "basic_salary": 50000,
  "hra": 15000,
  "da": 5000,
  "ta": 3000,
  "other_allowances": 2000,
  "gross_salary": 75000,
  "pf_deduction": 6000,
  "tax_deduction": 5000,
  "other_deductions": 0,
  "net_salary": 64000
}
```

---

### POST /api/v1/admin/staff/salary-advances

**Request:**
```json
{
  "staff_id": "uuid",
  "amount": 20000,
  "reason": "Medical emergency",
  "repayment_months": 4
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "status": "Pending",
  "message": "Salary advance request created"
}
```

---

## 8. Fees (`/admin/fees`)

### GET /api/v1/admin/fees

**Query Params:** `page`, `page_size`, `class_name` (optional), `section` (optional), `status` (optional), `fee_type` (optional), `academic_year` (optional)

**Response: 200**
```json
{
  "count": 500,
  "page": 1,
  "page_size": 20,
  "total_pages": 25,
  "results": [
    {
      "id": "uuid",
      "student_id": "uuid",
      "student_name": "Rahul Kumar",
      "roll_number": "STU2024015",
      "class_section": "10-A",
      "fee_type": "Tuition Fee",
      "amount": 15000.00,
      "paid_amount": 15000.00,
      "balance": 0.00,
      "status": "Paid",
      "due_date": "2024-01-01",
      "paid_date": "2024-01-05"
    }
  ]
}
```

---

### POST /api/v1/admin/fees/generate-due

**Request:**
```json
{
  "class_name": "10",
  "section": null,
  "fee_type": "Tuition Fee",
  "amount": 15000,
  "due_date": "2024-02-01",
  "academic_year": "2024-25"
}
```

**Response: 201**
```json
{
  "message": "Fee dues generated",
  "count": 45,
  "total_amount": 675000.0
}
```

---

### POST /api/v1/admin/fees/{fee_id}/record-payment

**Request:**
```json
{
  "amount": 15000,
  "method": "Online",
  "transaction_id": "TXN-123456",
  "paid_date": "2024-01-15"
}
```

**Response: 200**
```json
{
  "message": "Payment recorded",
  "fee_id": "uuid",
  "new_balance": 0.0,
  "status": "Paid",
  "receipt_id": "REC-2024-123"
}
```

---

### POST /api/v1/admin/fees/send-reminder

**Request:**
```json
{
  "class_name": "10",
  "section": "A",
  "message": "Fee payment due on 1st Feb. Please pay at the earliest.",
  "send_via": "notification"
}
```

**Response: 200**
```json
{"message": "Reminders sent", "count": 15}
```

---

## 9. Examinations (`/admin/examinations`)

### POST /api/v1/admin/examinations

**Request:**
```json
{
  "name": "Mid-Term Examination",
  "exam_type": "Term Exam",
  "class_name": "10",
  "section": null,
  "subject": "Mathematics",
  "date": "2024-10-15",
  "start_time": "09:00",
  "end_time": "12:00",
  "total_marks": 100,
  "passing_marks": 35,
  "academic_year": "2024-25"
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "name": "Mid-Term Examination",
  "status": "Scheduled",
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

### GET /api/v1/admin/examinations/grade-system

**Response: 200**
```json
{
  "type": "percentage",
  "grades": [
    {"grade": "A+", "min_percentage": 90, "max_percentage": 100, "gpa": 10},
    {"grade": "A", "min_percentage": 80, "max_percentage": 89, "gpa": 9},
    {"grade": "B+", "min_percentage": 70, "max_percentage": 79, "gpa": 8}
  ]
}
```

---

### POST /api/v1/admin/examinations/{exam_id}/results

**Request:**
```json
{
  "results": [
    {"student_id": "uuid", "marks": 92},
    {"student_id": "uuid", "marks": 85}
  ]
}
```

**Response: 201**
```json
{"message": "Results entered", "count": 2}
```

---

### POST /api/v1/admin/examinations/{exam_id}/publish

**Response: 200**
```json
{"message": "Results published", "exam_id": "uuid", "students_notified": 40}
```

---

## 10. Leaves (`/admin/leaves`)

### GET /api/v1/admin/leaves

**Query Params:** `page`, `page_size`, `status` (optional), `leave_type` (optional), `teacher_id` (optional), `from_date` (optional), `to_date` (optional)

**Response: 200**
```json
{
  "count": 25,
  "page": 1,
  "page_size": 20,
  "total_pages": 2,
  "results": [
    {
      "id": "uuid",
      "teacher_id": "uuid",
      "teacher_name": "Jane Smith",
      "leave_type": "Casual Leave",
      "from_date": "2024-01-20",
      "to_date": "2024-01-21",
      "duration_days": 2.0,
      "reason": "Family function",
      "status": "Pending",
      "applied_on": "2024-01-15T10:00:00Z"
    }
  ]
}
```

---

### POST /api/v1/admin/leaves/{leave_id}/approve

**Request:**
```json
{
  "remarks": "Approved. Substitute arranged."
}
```

**Response: 200**
```json
{
  "message": "Leave approved",
  "id": "uuid",
  "status": "Approved",
  "approved_on": "2024-01-16T09:00:00Z"
}
```

---

### POST /api/v1/admin/leaves/{leave_id}/reject

**Request:**
```json
{
  "remarks": "Cannot approve during exam week"
}
```

**Response: 200**
```json
{
  "message": "Leave rejected",
  "id": "uuid",
  "status": "Rejected"
}
```

---

### PUT /api/v1/admin/leaves/policy

**Request:**
```json
{
  "casual_leave": 12,
  "sick_leave": 10,
  "earned_leave": 15,
  "maternity_leave": 180,
  "carry_forward": true,
  "max_carry_forward_days": 5
}
```

**Response: 200**
```json
{"message": "Leave policy updated"}
```

---

### POST /api/v1/admin/leaves/allocate

**Request:**
```json
{
  "teacher_id": "uuid",
  "leave_type": "Casual Leave",
  "days": 12,
  "academic_year": "2024-25"
}
```

**Response: 200**
```json
{"message": "Leave allocated", "teacher_id": "uuid", "allocated": 12}
```

---

## 11. Transport (`/admin/transport`)

### GET /api/v1/admin/transport/stats

**Response: 200**
```json
{
  "total_vehicles": 12,
  "total_drivers": 12,
  "total_routes": 8,
  "students_using_transport": 450,
  "active_helpers": 10
}
```

---

### POST /api/v1/admin/transport/vehicles

**Request:**
```json
{
  "vehicle_number": "HR-26-1234",
  "type": "Bus",
  "capacity": 50,
  "make": "Tata",
  "model": "Starbus",
  "year": 2022,
  "insurance_expiry": "2025-03-31",
  "fitness_expiry": "2025-06-30"
}
```

**Response: 201**
```json
{"id": "uuid", "vehicle_number": "HR-26-1234", "status": "Active"}
```

---

### POST /api/v1/admin/transport/routes

**Request:**
```json
{
  "name": "Route 5 - Sector 24",
  "description": "Covers Sector 22, 23, 24",
  "stops": [
    {"name": "Sector 22 Market", "pickup_time": "07:15", "drop_time": "14:45"},
    {"name": "Sector 24 Gate", "pickup_time": "07:30", "drop_time": "14:30"}
  ]
}
```

**Response: 201**
```json
{"id": "uuid", "name": "Route 5 - Sector 24", "status": "Active"}
```

---

## 12. Timetable (`/admin/timetable`)

> **Note:** Timetable uses hard-delete (no soft-delete). Deleting a period or slot permanently removes it.

### GET /api/v1/admin/timetable/periods

**Query Params:** `academic_year` (optional)

**Response: 200**
```json
{
  "academic_year": "2025-2026",
  "total_periods": 6,
  "periods": [
    {"id": "uuid", "name": "Period 1", "start_time": "09:00", "end_time": "09:45", "duration_minutes": 45, "is_break": false, "sort_order": 0}
  ],
  "breaks": [
    {"id": "uuid", "name": "Lunch", "start_time": "12:30", "end_time": "13:00", "duration_minutes": 30, "is_break": true, "sort_order": 4}
  ],
  "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
}
```

---

### POST /api/v1/admin/timetable/periods

**Request:**
```json
{
  "name": "Period 1",
  "start_time": "09:00",
  "end_time": "09:45",
  "is_break": false
}
```

**Response: 201**
```json
{"id": "uuid", "name": "Period 1", "start_time": "09:00", "end_time": "09:45", "duration_minutes": 45, "is_break": false, "sort_order": 0}
```

**Errors:** 400 (time overlap with existing period)

---

### PUT /api/v1/admin/timetable/periods/{period_id}

**Request:**
```json
{
  "name": "Period 1 (Updated)",
  "start_time": "09:00",
  "end_time": "09:50"
}
```

**Response: 200** (same as create response)

**Errors:** 400 (time overlap), 404 (period not found)

---

### DELETE /api/v1/admin/timetable/periods/{period_id}

**Response: 200**
```json
{"id": "uuid", "status": "Deleted", "deactivated_on": "2026-06-19", "message": "Period deleted successfully."}
```

---

### GET /api/v1/admin/timetable

**Query Params:** `class_section_id` (required), `academic_year` (optional)

**Response: 200**
```json
{
  "class_name": "8",
  "section": "B",
  "academic_year": "2025-2026",
  "periods": [...],
  "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
  "timetable": {
    "Monday": [
      {"id": "uuid", "subject": "English", "subject_id": "uuid", "teacher_name": "Bhupender", "teacher_id": "uuid", "slot_type": "Subject", "start_time": "09:00", "end_time": "09:45"},
      null
    ]
  },
  "stats": {"total_slots": 36, "filled_slots": 24, "empty_slots": 12, "completion_percentage": 66.7}
}
```

---

### POST /api/v1/admin/timetable/slot

Creates a new slot or **upserts** (updates) if a slot already exists at the same position (class_section + period + day).

**Request:**
```json
{
  "class_section_id": "uuid",
  "period_config_id": "uuid",
  "day": "Monday",
  "subject_id": "uuid",
  "teacher_id": "uuid",
  "slot_type": "Subject"
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "class_name": "8",
  "section": "B",
  "day": "Monday",
  "period_start_time": "09:00",
  "period_end_time": "09:45",
  "subject": "English",
  "subject_id": "uuid",
  "teacher_name": "Bhupender",
  "teacher_id": "uuid",
  "slot_type": "Subject"
}
```

**Behavior:**
- If slot already exists at (class_section, period, day) → updates it with new subject/teacher (upsert)
- Teacher conflict check: raises error if the teacher is already assigned to another class at the same period+day
- Self-conflict is excluded (editing same slot with same teacher won't conflict)

**Errors:** 409 (teacher conflict with another class)

---

### PUT /api/v1/admin/timetable/slot/{slot_id}

Updates an existing slot by ID. Supports changing subject, teacher, slot_type, day, or period.

**Request:**
```json
{
  "subject_id": "uuid",
  "teacher_id": "uuid"
}
```

**Response: 200** (same structure as create response, with `updated_at`)

**Conflict checks:**
- If teacher changes → checks teacher is not double-booked (excludes self)
- If day/period changes → checks no other slot exists at the new position in the same class-section

**Errors:** 409 (teacher conflict or slot position conflict), 404 (slot not found)

---

### DELETE /api/v1/admin/timetable/slot/{slot_id}

Permanently deletes the slot assignment.

**Response: 200**
```json
{"id": "uuid", "day": "", "status": "Deleted", "removed_on": "2026-06-19", "message": "Slot deleted successfully."}
```

---

### GET /api/v1/admin/timetable/teacher/{teacher_id}

**Query Params:** `academic_year` (optional)

**Response: 200**
```json
{
  "teacher_id": "uuid",
  "teacher_name": "Bhupender",
  "academic_year": "2025-2026",
  "total_periods_per_week": 18,
  "timetable": {
    "Monday": [
      {"period_start_time": "09:00", "period_end_time": "09:45", "class_name": "8", "section": "B", "subject": "English", "slot_type": "Subject"}
    ]
  },
  "free_slots": {
    "Monday": ["10:30", "11:15"],
    "Tuesday": ["09:00"]
  }
}
```

---

### GET /api/v1/admin/timetable/teacher-availability

**Query Params:** `period_config_id` (required), `day` (required)

**Response: 200**
```json
{
  "busy_teachers": {
    "teacher-uuid-1": {"class": "8-B", "subject": "English"},
    "teacher-uuid-2": {"class": "9-A", "subject": "Mathematics"}
  }
}
```

---

### GET /api/v1/admin/timetable/conflicts

**Query Params:** `academic_year` (optional), `class_section_id` (optional)

**Response: 200**
```json
{
  "total_conflicts": 1,
  "conflicts": [
    {
      "type": "teacher_double_booked",
      "teacher_id": "uuid",
      "teacher_name": "Bhupender",
      "day": "Monday",
      "period_start_time": "09:00",
      "assignments": [
        {"class_name": "8", "section": "B", "subject": "English"},
        {"class_name": "9", "section": "A", "subject": "English"}
      ]
    }
  ]
}
```

---

## 13. Library (`/admin/library`)

### POST /api/v1/admin/library/books

**Request:**
```json
{
  "title": "Physics NCERT Class 10",
  "author": "NCERT",
  "isbn": "978-81-7450-XXX",
  "category": "Textbook",
  "publisher": "NCERT",
  "total_copies": 10
}
```

**Response: 201**
```json
{"id": "uuid", "title": "Physics NCERT Class 10", "available_copies": 10}
```

---

### POST /api/v1/admin/library/issue

**Request:**
```json
{
  "book_id": "uuid",
  "student_id": "uuid",
  "due_date": "2024-02-01"
}
```

**Response: 201**
```json
{"id": "uuid", "message": "Book issued", "due_date": "2024-02-01"}
```

---

### POST /api/v1/admin/library/return

**Request:**
```json
{
  "issue_id": "uuid",
  "condition": "Good",
  "fine": 0
}
```

**Response: 200**
```json
{"message": "Book returned", "fine_applied": 0}
```

---

## 14. Notifications (`/admin/notifications`)

### POST /api/v1/admin/notifications

**Request:**
```json
{
  "title": "Parent-Teacher Meeting",
  "message": "PTM scheduled for 25th Jan at 10 AM",
  "type": "announcement",
  "target_audience": "all",
  "target_class": null,
  "target_section": null,
  "send_via": "in_app",
  "scheduled_at": null
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "title": "Parent-Teacher Meeting",
  "status": "Sent",
  "recipients_count": 1200,
  "sent_at": "2024-01-15T10:00:00Z"
}
```

---

## 15. Attendance (`/admin/attendance`)

### GET /api/v1/admin/attendance

**Query Params:** `class_section_id` (uuid), `date` (optional), `academic_year` (optional)

**Response: 200**
```json
{
  "class_section": "10-A",
  "date": "2024-01-15",
  "is_submitted": true,
  "summary": {
    "total_students": 40,
    "present": 37,
    "absent": 2,
    "late": 1,
    "attendance_rate": 92.5
  },
  "records": [
    {"student_id": "uuid", "roll_number": "10A-001", "full_name": "Rahul Kumar", "status": "Present"}
  ]
}
```

---

### POST /api/v1/admin/attendance

**Request:**
```json
{
  "class_id": "uuid",
  "date": "2024-01-15",
  "academic_year": "2024-25",
  "records": [
    {"student_id": "uuid", "status": "Present"},
    {"student_id": "uuid", "status": "Absent"}
  ]
}
```

**Response: 201**
```json
{
  "message": "Attendance submitted",
  "class_section": "10-A",
  "summary": {"total_students": 40, "present": 38, "absent": 2, "late": 0, "attendance_rate": 95.0}
}
```

---

## 16. Mentoring (`/admin/mentoring`)

### GET /api/v1/admin/mentoring

**Response: 200**
```json
{
  "mentors": [
    {
      "staff_id": "uuid",
      "teacher_name": "Jane Smith",
      "department": "Mathematics",
      "mentee_count": 8
    }
  ]
}
```

---

### POST /api/v1/admin/mentoring/assign

**Request:**
```json
{
  "staff_id": "uuid",
  "student_ids": ["uuid", "uuid", "uuid"]
}
```

**Response: 201**
```json
{"message": "Mentor assigned", "assigned_count": 3}
```

---

### POST /api/v1/admin/mentoring/shuffle-assign

Auto-assigns all students evenly across all teachers.

**Response: 200**
```json
{"message": "Students shuffled and assigned", "total_assigned": 1200, "mentors_used": 65}
```
