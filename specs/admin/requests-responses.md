# School ERP Backend - Requests & Responses

> Detailed request/response documentation for all API endpoints.
> For quick endpoint reference, see [endpoints.md](./endpoints.md).

---

## 1. Authentication

### POST /api/v1/auth/login/

Login with email and password. Sets httpOnly cookies for access + refresh tokens.

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

**Response: 401**
```json
{
  "error": "Invalid email or password"
}
```

---

### POST /api/v1/auth/refresh-token/

Refresh the access token using the refresh token cookie.

**Request:** No body (cookies sent automatically)

**Response: 200**
```json
{
  "message": "Token refreshed"
}
```

**Response: 401**
```json
{
  "error": "Invalid or expired refresh token"
}
```

---

### GET /api/v1/auth/me/

Get the current authenticated user's profile.

**Response: 200**
```json
{
  "id": "uuid",
  "email": "admin@school.com",
  "full_name": "John Admin",
  "role": "admin",
  "school_code": "SCH001",
  "avatar_url": null,
  "phone": "+91 9876543210"
}
```

---

### POST /api/v1/auth/logout/

Clear auth cookies and invalidate the refresh token.

**Response: 200**
```json
{
  "message": "Logged out successfully"
}
```

---

### POST /api/v1/auth/forgot-password/

Send a password reset link to the user's email.

**Request:**
```json
{
  "email": "admin@school.com"
}
```

**Response: 200**
```json
{
  "message": "Password reset link sent to your email"
}
```

**Response: 404**
```json
{
  "error": "No account found with this email"
}
```

---

### POST /api/v1/auth/reset-password/

Reset password using the token received via email.

**Request:**
```json
{
  "token": "reset-token-from-email-link",
  "new_password": "newSecurePass123",
  "confirm_password": "newSecurePass123"
}
```

**Response: 200**
```json
{
  "message": "Password reset successfully"
}
```

**Response: 400**
```json
{
  "error": "Invalid or expired reset token"
}
```

**Response: 422**
```json
{
  "error": "Passwords do not match"
}
```

---

### POST /api/v1/auth/change-password/

Change password for the currently authenticated user. Requires the current password for verification.

**Request:**
```json
{
  "current_password": "oldPassword123",
  "new_password": "newSecurePass456",
  "confirm_password": "newSecurePass456"
}
```

**Response: 200**
```json
{
  "message": "Password changed successfully"
}
```

**Response: 400**
```json
{
  "error": "Current password is incorrect"
}
```

**Response: 422**
```json
{
  "error": "New password must be different from current password"
}
```

---

## 2. Dashboard

### GET /api/v1/admin/dashboard/stats/

Get KPI summary cards for the dashboard.

**Response: 200**
```json
{
  "total_students": 156,
  "total_teachers": 24,
  "active_classes": 12,
  "fee_collection_percentage": 85,
  "students_change": "+12%",
  "teachers_change": "+3%",
  "classes_change": "+2",
  "fee_change": "+5%"
}
```

---

### GET /api/v1/admin/dashboard/attendance-trends/

**Query Params:** `?year=2026`

**Response: 200**
```json
{
  "data": [
    { "month": "Jan", "value": 92 },
    { "month": "Feb", "value": 95 },
    { "month": "Mar", "value": 88 },
    { "month": "Apr", "value": 90 },
    { "month": "May", "value": 85 },
    { "month": "Jun", "value": 91 }
  ]
}
```

---

### GET /api/v1/admin/dashboard/fee-collection-status/

**Query Params:** `?year=2026`

**Response: 200**
```json
{
  "data": [
    { "name": "Paid", "value": 45, "color": "#22c55e" },
    { "name": "Pending", "value": 20, "color": "#3b82f6" },
    { "name": "Partial", "value": 15, "color": "#f59e0b" },
    { "name": "Overdue", "value": 20, "color": "#ef4444" }
  ]
}
```

---

### GET /api/v1/admin/dashboard/student-distribution/

**Response: 200**
```json
{
  "data": [
    { "class_name": "Class 9", "male": 28, "female": 24 },
    { "class_name": "Class 10", "male": 30, "female": 26 },
    { "class_name": "Class 11", "male": 22, "female": 20 },
    { "class_name": "Class 12", "male": 18, "female": 16 }
  ]
}
```

---

### GET /api/v1/admin/dashboard/recent-activities/

**Query Params:** `?limit=10`

**Response: 200**
```json
{
  "data": [
    {
      "id": "uuid",
      "title": "New Student Enrolled",
      "description": "John Smith enrolled in Grade 10-A",
      "date": "2026-05-21",
      "tag": "New",
      "category": "student"
    }
  ]
}
```

---

### GET /api/v1/admin/dashboard/leave-overview/

**Response: 200**
```json
{
  "pending_requests": 2,
  "approved": 5,
  "on_leave_today": 0,
  "upcoming_leaves": 3,
  "pending_approvals": [
    {
      "id": "uuid",
      "employee_name": "Priya Sharma",
      "leave_type": "Sick Leave",
      "duration_days": 2,
      "from_date": "2026-05-23",
      "to_date": "2026-05-24"
    }
  ]
}
```

---

### GET /api/v1/admin/dashboard/low-attendance/

**Query Params:** `?threshold=70&limit=5`

**Response: 200**
```json
{
  "data": [
    {
      "student_id": "uuid",
      "name": "Sophia Garcia",
      "class_section": "9-A",
      "attendance_percentage": 60
    }
  ]
}
```

---

## 3. Students

### GET /api/v1/admin/students/

List students with filters and pagination.

**Query Params:** `?search=john&class_name=10&section=A&status=Active&gender=Male&page=1&page_size=20`

**Response: 200**
```json
{
  "count": 156,
  "page": 1,
  "page_size": 20,
  "total_pages": 8,
  "results": [
    {
      "id": "uuid",
      "roll_number": "STU2024001",
      "full_name": "John Doe",
      "email": "john@student.com",
      "phone": "+1-555-0101",
      "class_name": "10",
      "section": "A",
      "status": "Active",
      "gender": "Male",
      "date_of_birth": "2011-03-15",
      "admission_date": "2023-04-01"
    }
  ],
  "summary": {
    "total": 156,
    "active": 148,
    "inactive": 8
  }
}
```

---

### POST /api/v1/admin/students/

Create a new student.

**Request:**
```json
{
  "roll_number": "STU2024010",
  "full_name": "New Student",
  "email": "new.student@school.com",
  "phone": "+91-9876543210",
  "class_name": "10",
  "section": "A",
  "date_of_birth": "2011-05-20",
  "admission_date": "2026-04-01",
  "gender": "Male",
  "parent_name": "Parent Name",
  "parent_phone": "+91-9876543211",
  "parent_email": "parent@email.com",
  "address": "123 Main St, City"
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "roll_number": "STU2024010",
  "full_name": "New Student",
  "email": "new.student@school.com",
  "phone": "+91-9876543210",
  "class_name": "10",
  "section": "A",
  "status": "Active",
  "date_of_birth": "2011-05-20",
  "admission_date": "2026-04-01",
  "gender": "Male",
  "parent_name": "Parent Name",
  "parent_phone": "+91-9876543211",
  "parent_email": "parent@email.com",
  "address": "123 Main St, City",
  "created_at": "2026-05-23T10:00:00Z"
}
```

---

### GET /api/v1/admin/students/:id/

Get a single student's full details.

**Response: 200**
```json
{
  "id": "uuid",
  "roll_number": "STU2025001",
  "full_name": "Arjun Sharma",
  "email": "arjun.sharma@school.edu",
  "phone": "+91 98765 43210",
  "class_name": "10",
  "section": "A",
  "status": "Active",
  "type": "Day Scholar",
  "gender": "Male",
  "date_of_birth": "2011-03-15",
  "admission_date": "2023-04-01",
  "address": "42, MG Road, Jayanagar, Bangalore - 560041",
  "parent": {
    "name": "Rajesh Sharma",
    "phone": "+91 98765 12345",
    "email": "rajesh.sharma@email.com",
    "emergency_contact": "+91 98765 67890",
    "relationship": "Father"
  },
  "medical": {
    "blood_group": "B+",
    "religion": "Hindu",
    "conditions": "None reported",
    "allergies": []
  },
  "mentor": {
    "id": "uuid",
    "name": "Dr. Anita Desai",
    "subject": "Mathematics",
    "qualification": "M.Sc., Ph.D.",
    "email": "anita.desai@school.edu",
    "phone": "+91 99887 76655"
  },
  "stats": {
    "attendance_percentage": 67,
    "average_grade": 83.5,
    "assignments_submitted": 12,
    "assignments_total": 14,
    "fee_due": 0,
    "class_rank": 5,
    "class_strength": 45
  },
  "behavior": {
    "overall_rating": "A",
    "discipline_score": 95,
    "punctuality_score": 98
  }
}
```

---

### PUT /api/v1/admin/students/:id/

Update student details.

**Request:** (partial update supported)
```json
{
  "phone": "+91-9876543210",
  "address": "New Address, City"
}
```

**Response: 200** — Same as GET response with updated fields.

---

### DELETE /api/v1/admin/students/:id/

Soft-delete — sets `status` to `Inactive` or `Alumni`. Student records, fee history, exam results, and activities are fully preserved. Student no longer appears in active lists but accessible via `?status=Inactive` or `?status=Alumni`.

**Request (optional):**
```json
{
  "status": "Alumni",
  "reason": "Graduated",
  "notes": "Completed 12th grade, 2025-2026 batch"
}
```

**Response: 200**
```json
{
  "id": "uuid",
  "roll_number": "STU2024001",
  "full_name": "John Doe",
  "status": "Alumni",
  "reason": "Graduated",
  "deactivated_on": "2026-05-23",
  "message": "Student deactivated. All records preserved."
}
```

---

### GET /api/v1/admin/students/:id/exam-results/

**Query Params:** `?academic_year=2025-2026`

**Response: 200**
```json
{
  "exams": [
    {
      "id": "uuid",
      "name": "Mid-Term Mar 2026",
      "total_marks": 500,
      "marks_obtained": 403,
      "percentage": 80.6,
      "subjects": [
        { "name": "Mathematics", "marks": 78, "total": 100, "grade": "B+" },
        { "name": "Science", "marks": 85, "total": 100, "grade": "A" },
        { "name": "English", "marks": 72, "total": 100, "grade": "B" },
        { "name": "Social Studies", "marks": 80, "total": 100, "grade": "A-" },
        { "name": "Hindi", "marks": 88, "total": 100, "grade": "A" }
      ]
    }
  ],
  "trend": [
    { "exam": "Q1", "Math": 70, "Science": 82, "English": 68, "Hindi": 85 },
    { "exam": "Annual", "Math": 82, "Science": 88, "English": 75, "Hindi": 90 },
    { "exam": "Mid-Term", "Math": 78, "Science": 85, "English": 72, "Hindi": 88 }
  ]
}
```

---

### GET /api/v1/admin/students/:id/parent-meetings/

**Response: 200**
```json
{
  "total_meetings": 4,
  "attended": 3,
  "meetings": [
    {
      "id": "uuid",
      "type": "Parent-Teacher Meeting",
      "date": "2026-03-15",
      "attendee": "Rajesh Sharma",
      "conductor": "Ms. Anita Desai",
      "notes": "Discussed academic progress",
      "status": "Attended"
    }
  ]
}
```

---

### GET /api/v1/admin/students/:id/activities/

**Response: 200**
```json
{
  "extra_curricular": [
    {
      "id": "uuid",
      "name": "Cricket Team",
      "since": "2023",
      "role": "Batsman",
      "status": "Active"
    }
  ],
  "awards": [
    {
      "id": "uuid",
      "name": "Best in Mathematics",
      "category": "Academic",
      "year": "2025",
      "description": "Scored highest in annual mathematics olympiad"
    }
  ]
}
```

---

### GET /api/v1/admin/students/:id/fee-history/

**Response: 200**
```json
{
  "summary": {
    "total_fees": 60000,
    "total_paid": 60000,
    "total_due": 0
  },
  "fee_structure": [
    { "component": "Tuition Fee", "amount": 45000, "frequency": "Annual" },
    { "component": "Lab Fee", "amount": 5000, "frequency": "Annual" },
    { "component": "Library Fee", "amount": 3000, "frequency": "Annual" },
    { "component": "Sports Fee", "amount": 4000, "frequency": "Annual" },
    { "component": "Exam Fee", "amount": 3000, "frequency": "Per Term" }
  ],
  "payments": [
    {
      "id": "uuid",
      "date": "2025-04-01",
      "amount": 30000,
      "method": "Online",
      "status": "Paid",
      "reference": "TXN001"
    }
  ]
}
```

---

### GET /api/v1/admin/students/:id/disciplinary-records/

**Response: 200**
```json
{
  "records": [],
  "status": "Clean"
}
```

---

### GET /api/v1/admin/students/export/

Export students as CSV file.

**Query Params:** `?class_name=10&section=A&status=Active`

**Response: 200** — `Content-Type: text/csv` file download.

---

### POST /api/v1/admin/students/bulk-import/

Bulk import students via CSV.

**Request:** `Content-Type: multipart/form-data`
- `file`: CSV file

**Response: 200**
```json
{
  "imported": 25,
  "skipped": 2,
  "errors": [
    { "row": 5, "error": "Duplicate roll number STU2024001" }
  ]
}
```

---

## 4. Teachers

> **Design Note:** A teacher can teach **multiple subjects** across **multiple classes/sections**.
> The `subjects` field on the teacher profile lists their qualified subjects.
> The `class_assignments` array is the many-to-many mapping: each entry ties one teacher
> to one class-section-subject combination.
> A single teacher can have assignments like: Math in 10-A, Math in 10-B, Physics in 11-A.

### GET /api/v1/admin/teachers/

List teachers with search and pagination.

**Query Params:** `?search=jane&subject=Mathematics&class_name=10&section=A&status=Active&include_inactive=false&page=1&page_size=20`

**Response: 200**
```json
{
  "count": 24,
  "page": 1,
  "page_size": 20,
  "total_pages": 2,
  "results": [
    {
      "id": "uuid",
      "employee_id": "EMP001",
      "user": {
        "full_name": "Dr. Jane Smith",
        "email": "jane.smith@school.com",
        "phone": "+1-555-1001"
      },
      "subjects": ["Mathematics", "Physics"],
      "primary_subject": "Mathematics",
      "qualification": "Ph.D. in Mathematics",
      "joining_date": "2020-06-15",
      "workload_hours": 24,
      "max_workload_hours": 30,
      "class_assignments": [
        {
          "id": "uuid",
          "class_name": "10",
          "section": "A",
          "subject": "Mathematics",
          "is_class_teacher": true,
          "periods_per_week": 6,
          "is_class_teacher": true
        },
        {
          "id": "uuid",
          "class_name": "10",
          "section": "B",
          "subject": "Mathematics",
          "is_class_teacher": false,
          "periods_per_week": 6,
          "is_class_teacher": false
        },
        {
          "id": "uuid",
          "class_name": "11",
          "section": "A",
          "subject": "Physics",
          "is_class_teacher": false,
          "periods_per_week": 5,
          "is_class_teacher": false
        }
      ],
      "total_periods_per_week": 17,
      "classes_count": 3,
      "is_class_teacher_of": ["10-A"],
      "status": "Active",
      "is_active": true,
      "left_date": null,
      "left_reason": null
    }
  ]
}
```

**Example response when inactive teachers are included (`?include_inactive=true`):**
```json
{
  "id": "uuid",
  "employee_id": "EMP008",
  "user": {
    "full_name": "Mr. Old Teacher",
    "email": "old.teacher@school.com",
    "phone": "+1-555-9999"
  },
  "subjects": ["History"],
  "primary_subject": "History",
  "qualification": "M.A. in History",
  "joining_date": "2018-06-15",
  "workload_hours": 0,
  "max_workload_hours": 28,
  "class_assignments": [],
  "total_periods_per_week": 0,
  "classes_count": 0,
  "is_class_teacher_of": [],
  "status": "Inactive",
  "is_active": false,
  "left_date": "2025-03-31",
  "left_reason": "Resigned"
}
```

---

### POST /api/v1/admin/teachers/

Create a new teacher. `subjects` is an array — a teacher can be qualified in multiple subjects.

**Request:**
```json
{
  "employee_id": "EMP010",
  "full_name": "New Teacher",
  "email": "new.teacher@school.com",
  "phone": "+91-9876543210",
  "subjects": ["Biology", "Chemistry"],
  "primary_subject": "Biology",
  "qualification": "M.Sc. in Biology",
  "joining_date": "2026-05-01",
  "max_workload_hours": 28
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "employee_id": "EMP010",
  "user": {
    "full_name": "New Teacher",
    "email": "new.teacher@school.com",
    "phone": "+91-9876543210"
  },
  "subjects": ["Biology", "Chemistry"],
  "primary_subject": "Biology",
  "qualification": "M.Sc. in Biology",
  "joining_date": "2026-05-01",
  "workload_hours": 0,
  "max_workload_hours": 28,
  "class_assignments": [],
  "total_periods_per_week": 0,
  "classes_count": 0,
  "is_class_teacher_of": [],
  "created_at": "2026-05-23T10:00:00Z"
}
```

---

### GET /api/v1/admin/teachers/:id/

Get a single teacher's full profile with all assignments.

**Response: 200** — Same structure as list item, plus additional fields:

```json
{
  "id": "uuid",
  "employee_id": "EMP001",
  "user": {
    "full_name": "Dr. Jane Smith",
    "email": "jane.smith@school.com",
    "phone": "+1-555-1001"
  },
  "subjects": ["Mathematics", "Physics"],
  "primary_subject": "Mathematics",
  "qualification": "Ph.D. in Mathematics",
  "joining_date": "2020-06-15",
  "workload_hours": 24,
  "max_workload_hours": 30,
  "class_assignments": [
    {
      "id": "uuid",
      "class_name": "10",
      "section": "A",
      "subject": "Mathematics",
      "is_class_teacher": true,
      "periods_per_week": 6,
      "periods_per_week": 6
    },
    {
      "id": "uuid",
      "class_name": "10",
      "section": "B",
      "subject": "Mathematics",
      "is_class_teacher": false,
      "periods_per_week": 6,
      "periods_per_week": 6
    },
    {
      "id": "uuid",
      "class_name": "11",
      "section": "A",
      "subject": "Physics",
      "is_class_teacher": false,
      "periods_per_week": 5,
      "periods_per_week": 6
    }
  ],
  "total_periods_per_week": 17,
  "classes_count": 3,
  "is_class_teacher_of": ["10-A"],
  "created_at": "2020-06-15T00:00:00Z"
}
```

---

### PUT /api/v1/admin/teachers/:id/

Update teacher details. Can update subjects list, qualification, workload, etc.

**Request:**
```json
{
  "subjects": ["Mathematics", "Physics", "Computer Science"],
  "max_workload_hours": 32,
  "qualification": "Ph.D. in Mathematics, M.Sc. Physics"
}
```

**Response: 200** — Full teacher object with updated fields.

---

### DELETE /api/v1/admin/teachers/:id/

Soft-delete a teacher. Sets `status` to `Inactive` and `left_date` to today. Does NOT remove records — all historical data (assignments, attendance marked, grades given, exam results) is preserved for audit. The teacher no longer appears in active lists but can be found via `?status=Inactive` or `?include_inactive=true`.

**Request (optional):**
```json
{
  "reason": "Resigned",
  "left_date": "2026-05-23",
  "notes": "Moved to another city"
}
```

**Response: 200**
```json
{
  "id": "uuid",
  "employee_id": "EMP001",
  "full_name": "Dr. Jane Smith",
  "status": "Inactive",
  "left_date": "2026-05-23",
  "reason": "Resigned",
  "notes": "Moved to another city",
  "message": "Teacher deactivated. Historical records preserved."
}
```

---

### GET /api/v1/admin/teachers/:id/history/

Get complete historical records for a teacher (including inactive/former teachers). Useful for auditing past assignments, classes taught, and tenure details.

**Query Params:** `?academic_year=2025-2026`

**Response: 200**
```json
{
  "teacher_id": "uuid",
  "employee_id": "EMP001",
  "full_name": "Dr. Jane Smith",
  "status": "Inactive",
  "joining_date": "2020-06-15",
  "left_date": "2026-05-23",
  "reason": "Resigned",
  "tenure_years": 5.9,
  "subjects_taught": ["Mathematics", "Physics"],
  "academic_years_served": ["2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025", "2025-2026"],
  "assignment_history": [
    {
      "academic_year": "2025-2026",
      "assignments": [
        { "class_name": "10", "section": "A", "subject": "Mathematics", "is_class_teacher": true, "periods_per_week": 6 },
        { "class_name": "10", "section": "B", "subject": "Mathematics", "is_class_teacher": false, "periods_per_week": 6 },
        { "class_name": "11", "section": "A", "subject": "Physics", "is_class_teacher": false, "periods_per_week": 5 }
      ]
    },
    {
      "academic_year": "2024-2025",
      "assignments": [
        { "class_name": "9", "section": "A", "subject": "Mathematics", "is_class_teacher": true, "periods_per_week": 6 },
        { "class_name": "9", "section": "B", "subject": "Mathematics", "is_class_teacher": false, "periods_per_week": 6 }
      ]
    }
  ],
  "performance_summary": {
    "total_classes_taught": 12,
    "total_students_taught": 450,
    "average_student_pass_rate": 87,
    "total_exams_conducted": 36
  }
}
```

---

### POST /api/v1/admin/teachers/:id/assign-class/

Assign a class-section-subject combination to a teacher. The same teacher can be assigned to multiple classes and/or multiple subjects. The backend validates:
- Teacher is qualified in the given subject (subject exists in teacher's `subjects` array)
- No duplicate assignment (same class + section + subject already assigned to this teacher)
- Workload doesn't exceed `max_workload_hours`

**Request:**
```json
{
  "class_name": "11",
  "section": "A",
  "subject": "Physics",
  "is_class_teacher": false,
  "periods_per_week": 5
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "class_name": "11",
  "section": "A",
  "subject": "Physics",
  "is_class_teacher": false,
  "periods_per_week": 5
}
```

**Response: 400 (Validation)**
```json
{
  "error": "Teacher is not qualified to teach Physics. Qualified subjects: [Mathematics]"
}
```

**Response: 409 (Duplicate)**
```json
{
  "error": "Teacher is already assigned to Class 11-A for Physics"
}
```

**Response: 422 (Workload exceeded)**
```json
{
  "error": "Assignment would exceed max workload. Current: 24hrs, Adding: 5hrs, Max: 28hrs"
}
```

---

### POST /api/v1/admin/teachers/:id/bulk-assign/

Assign multiple class-section-subject combinations at once.

**Request:**
```json
{
  "assignments": [
    { "class_name": "10", "section": "A", "subject": "Mathematics", "is_class_teacher": true, "periods_per_week": 6 },
    { "class_name": "10", "section": "B", "subject": "Mathematics", "is_class_teacher": false, "periods_per_week": 6 },
    { "class_name": "11", "section": "A", "subject": "Physics", "is_class_teacher": false, "periods_per_week": 5 }
  ]
}
```

**Response: 201**
```json
{
  "assigned": 3,
  "skipped": 0,
  "assignments": [
    { "id": "uuid", "class_name": "10", "section": "A", "subject": "Mathematics", "is_class_teacher": true, "periods_per_week": 6 },
    { "id": "uuid", "class_name": "10", "section": "B", "subject": "Mathematics", "is_class_teacher": false, "periods_per_week": 6 },
    { "id": "uuid", "class_name": "11", "section": "A", "subject": "Physics", "is_class_teacher": false, "periods_per_week": 5 }
  ],
  "total_periods_per_week": 17,
  "workload_hours": 24
}
```

---

### GET /api/v1/admin/teachers/:id/assignments/

Get all class assignments for a specific teacher.

**Query Params:** `?subject=Mathematics&class_name=10`

**Response: 200**
```json
{
  "teacher_id": "uuid",
  "teacher_name": "Dr. Jane Smith",
  "total_assignments": 3,
  "total_periods_per_week": 17,
  "assignments": [
    {
      "id": "uuid",
      "class_name": "10",
      "section": "A",
      "subject": "Mathematics",
      "is_class_teacher": true,
      "periods_per_week": 6,
      "periods_per_week": 6
    },
    {
      "id": "uuid",
      "class_name": "10",
      "section": "B",
      "subject": "Mathematics",
      "is_class_teacher": false,
      "periods_per_week": 6,
      "periods_per_week": 6
    },
    {
      "id": "uuid",
      "class_name": "11",
      "section": "A",
      "subject": "Physics",
      "is_class_teacher": false,
      "periods_per_week": 5,
      "periods_per_week": 6
    }
  ]
}
```

---

### DELETE /api/v1/admin/teachers/:id/class-assignment/:assignment_id/

Soft-delete a class-subject assignment. Marks the assignment as `Inactive` and records the end date. Historical data (attendance marked, grades given during this assignment) is preserved.

**Request (optional):**
```json
{
  "reason": "Reassigned to another teacher",
  "end_date": "2026-05-23"
}
```

**Response: 200**
```json
{
  "id": "uuid",
  "class_name": "10",
  "section": "B",
  "subject": "Mathematics",
  "status": "Inactive",
  "end_date": "2026-05-23",
  "reason": "Reassigned to another teacher",
  "message": "Assignment removed. Historical records preserved."
}
```

---

### GET /api/v1/admin/teachers/export/

Export teachers as CSV.

**Response: 200** — `Content-Type: text/csv` file download.

---

### GET /api/v1/admin/teachers/by-class/

Get all teachers assigned to a specific class/section (useful for timetable planning).

**Query Params:** `?class_name=10&section=A`

**Response: 200**
```json
{
  "class_name": "10",
  "section": "A",
  "teachers": [
    {
      "teacher_id": "uuid",
      "teacher_name": "Dr. Jane Smith",
      "subject": "Mathematics",
      "is_class_teacher": true,
      "periods_per_week": 6
    },
    {
      "teacher_id": "uuid",
      "teacher_name": "Prof. Robert Johnson",
      "subject": "Physics",
      "is_class_teacher": false,
      "periods_per_week": 5
    }
  ]
}
```

---

## 5. Leave Management

> **Design:** Every teacher has a yearly leave allocation broken down by type (Casual, Sick, Annual).
> The system tracks availed vs total per type per teacher. Leave policy is configurable per academic year.

### GET /api/v1/admin/leaves/

List all leave applications with filters.

**Query Params:** `?status=Pending&teacher_id=uuid&type=Sick&department=Teaching&from_date=2026-05-01&to_date=2026-05-31&page=1&page_size=20`

**Response: 200**
```json
{
  "count": 30,
  "page": 1,
  "page_size": 20,
  "total_pages": 2,
  "results": [
    {
      "id": "uuid",
      "teacher_id": "uuid",
      "employee_id": "EMP001",
      "teacher_name": "Rahul Sharma",
      "department": "Teaching",
      "leave_type": "Sick",
      "from_date": "2026-05-10",
      "to_date": "2026-05-11",
      "days": 2,
      "is_half_day": false,
      "reason": "Fever",
      "status": "Approved",
      "applied_on": "2026-05-08",
      "approved_by": "Admin Name",
      "approved_on": "2026-05-09",
      "substitute_teacher": "Priya Patel",
      "substitute_teacher_id": "uuid"
    }
  ],
  "overall_summary": {
    "total_applications": 30,
    "approved": 20,
    "pending": 5,
    "rejected": 5,
    "on_leave_today": 2
  }
}
```

---

### GET /api/v1/admin/leaves/teacher/:teacher_id/

Get leave balance and history for a specific teacher. Shows type-wise breakdown of availed vs total.

**Query Params:** `?academic_year=2025-2026`

**Response: 200**
```json
{
  "teacher_id": "uuid",
  "employee_id": "EMP001",
  "teacher_name": "Rahul Sharma",
  "department": "Teaching",
  "academic_year": "2025-2026",
  "leave_balance": {
    "casual": {
      "total": 12,
      "availed": 4,
      "pending": 1,
      "remaining": 7
    },
    "sick": {
      "total": 10,
      "availed": 2,
      "pending": 0,
      "remaining": 8
    },
    "annual": {
      "total": 15,
      "availed": 5,
      "pending": 0,
      "remaining": 10
    }
  },
  "total_summary": {
    "total_allocated": 37,
    "total_availed": 11,
    "total_pending": 1,
    "total_remaining": 25
  },
  "leave_history": [
    {
      "id": "uuid",
      "leave_type": "Sick",
      "from_date": "2026-05-10",
      "to_date": "2026-05-11",
      "days": 2,
      "is_half_day": false,
      "reason": "Fever",
      "status": "Approved",
      "applied_on": "2026-05-08"
    },
    {
      "id": "uuid",
      "leave_type": "Casual",
      "from_date": "2026-04-15",
      "to_date": "2026-04-15",
      "days": 0.5,
      "is_half_day": true,
      "reason": "Personal work",
      "status": "Approved",
      "applied_on": "2026-04-12"
    }
  ]
}
```

---

### GET /api/v1/admin/leaves/balances/

Get leave balances for ALL teachers at a glance. Used for the admin overview table.

**Query Params:** `?academic_year=2025-2026&department=Teaching&search=rahul`

**Response: 200**
```json
{
  "academic_year": "2025-2026",
  "results": [
    {
      "teacher_id": "uuid",
      "employee_id": "EMP001",
      "teacher_name": "Rahul Sharma",
      "department": "Teaching",
      "casual": { "total": 12, "availed": 4, "remaining": 8 },
      "sick": { "total": 10, "availed": 2, "remaining": 8 },
      "annual": { "total": 15, "availed": 5, "remaining": 10 },
      "total_availed": 11,
      "total_remaining": 26,
      "is_active": true
    },
    {
      "teacher_id": "uuid",
      "employee_id": "EMP002",
      "teacher_name": "Priya Patel",
      "department": "Teaching",
      "casual": { "total": 12, "availed": 6, "remaining": 6 },
      "sick": { "total": 10, "availed": 0, "remaining": 10 },
      "annual": { "total": 15, "availed": 8, "remaining": 7 },
      "total_availed": 14,
      "total_remaining": 23,
      "is_active": true
    }
  ]
}
```

---

### GET /api/v1/admin/leaves/policy/

Get the leave policy configuration for the current academic year.

**Response: 200**
```json
{
  "academic_year": "2025-2026",
  "leave_types": [
    {
      "type": "Casual",
      "code": "CL",
      "total_per_year": 12,
      "carry_forward": false,
      "max_consecutive_days": 3,
      "requires_approval": true,
      "half_day_allowed": true
    },
    {
      "type": "Sick",
      "code": "SL",
      "total_per_year": 10,
      "carry_forward": false,
      "max_consecutive_days": 7,
      "requires_approval": true,
      "half_day_allowed": false,
      "medical_certificate_required_after_days": 3
    },
    {
      "type": "Annual",
      "code": "AL",
      "total_per_year": 15,
      "carry_forward": true,
      "max_carry_forward": 5,
      "max_consecutive_days": 10,
      "requires_approval": true,
      "half_day_allowed": true,
      "advance_notice_days": 7
    }
  ]
}
```

---

### PUT /api/v1/admin/leaves/policy/

Update leave policy (admin only). Applies to the current academic year.

**Request:**
```json
{
  "academic_year": "2025-2026",
  "leave_types": [
    {
      "type": "Casual",
      "total_per_year": 14,
      "carry_forward": false,
      "max_consecutive_days": 3,
      "half_day_allowed": true
    },
    {
      "type": "Sick",
      "total_per_year": 12,
      "carry_forward": false,
      "max_consecutive_days": 7,
      "medical_certificate_required_after_days": 3
    },
    {
      "type": "Annual",
      "total_per_year": 15,
      "carry_forward": true,
      "max_carry_forward": 5,
      "max_consecutive_days": 10,
      "advance_notice_days": 7
    }
  ]
}
```

**Response: 200**
```json
{
  "message": "Leave policy updated for academic year 2025-2026",
  "academic_year": "2025-2026",
  "leave_types": ["...updated policy..."]
}
```

---

### POST /api/v1/admin/leaves/:id/approve/

Approve a pending leave application. Optionally assign a substitute teacher.

**Request:**
```json
{
  "remarks": "Approved",
  "substitute_teacher_id": "uuid"
}
```

**Response: 200**
```json
{
  "id": "uuid",
  "status": "Approved",
  "approved_by": "Admin Name",
  "approved_on": "2026-05-23",
  "substitute_teacher": "Priya Patel",
  "substitute_teacher_id": "uuid",
  "leave_balance_after": {
    "casual": { "total": 12, "availed": 5, "remaining": 7 }
  }
}
```

---

### POST /api/v1/admin/leaves/:id/reject/

Reject a pending leave application.

**Request:**
```json
{
  "remarks": "Insufficient notice period"
}
```

**Response: 200**
```json
{
  "id": "uuid",
  "status": "Rejected",
  "rejected_by": "Admin Name",
  "rejected_on": "2026-05-23",
  "remarks": "Insufficient notice period"
}
```

---

### POST /api/v1/admin/leaves/:id/cancel/

Cancel an already approved leave (before the leave dates start, or during leave).

**Request:**
```json
{
  "reason": "Plans changed, no longer needed"
}
```

**Response: 200**
```json
{
  "id": "uuid",
  "status": "Cancelled",
  "cancelled_by": "Admin Name",
  "cancelled_on": "2026-05-23",
  "days_restored": 2,
  "leave_balance_after": {
    "casual": { "total": 12, "availed": 3, "remaining": 9 }
  }
}
```

---

### POST /api/v1/admin/leaves/bulk-action/

Approve or reject multiple pending leaves at once.

**Request:**
```json
{
  "action": "approve",
  "leave_ids": ["uuid1", "uuid2", "uuid3"],
  "remarks": "Approved in bulk"
}
```

**Response: 200**
```json
{
  "processed": 3,
  "action": "approve",
  "results": [
    { "id": "uuid1", "status": "Approved" },
    { "id": "uuid2", "status": "Approved" },
    { "id": "uuid3", "status": "Approved" }
  ]
}
```

---

### GET /api/v1/admin/leaves/calendar/

Get a calendar view showing who is on leave for a given date range.

**Query Params:** `?from_date=2026-05-01&to_date=2026-05-31&department=Teaching`

**Response: 200**
```json
{
  "from_date": "2026-05-01",
  "to_date": "2026-05-31",
  "leaves_by_date": {
    "2026-05-10": [
      { "teacher_id": "uuid", "teacher_name": "Rahul Sharma", "leave_type": "Sick", "is_half_day": false }
    ],
    "2026-05-11": [
      { "teacher_id": "uuid", "teacher_name": "Rahul Sharma", "leave_type": "Sick", "is_half_day": false }
    ],
    "2026-05-15": [
      { "teacher_id": "uuid", "teacher_name": "Priya Patel", "leave_type": "Casual", "is_half_day": true },
      { "teacher_id": "uuid", "teacher_name": "Amit Kumar", "leave_type": "Annual", "is_half_day": false }
    ]
  },
  "conflict_dates": ["2026-05-15"],
  "total_leave_days_this_month": 8
}
```

---

## 6. Timetable

> **Design:** Timetable has two parts:
> 1. **Period Configuration** — defines time slots (Period 1 = 8:00–8:45, etc.). Configurable per school, editable.
> 2. **Timetable Grid** — Day × Period matrix. Each cell holds: subject, teacher. Cells can be empty ("+ Add").
>
> Filtered by Class + Section. Conflict detection prevents a teacher from being double-booked.

### GET /api/v1/admin/timetable/periods/

Get period configuration (time slots). These define the rows of the timetable grid.

**Query Params:** `?academic_year=2025-2026`

**Response: 200**
```json
{
  "academic_year": "2025-2026",
  "total_periods": 6,
  "periods": [
    { "id": "uuid", "start_time": "08:00", "end_time": "08:45", "duration_minutes": 45 },
    { "id": "uuid", "start_time": "08:50", "end_time": "09:35", "duration_minutes": 45 },
    { "id": "uuid", "start_time": "09:40", "end_time": "10:25", "duration_minutes": 45 },
    { "id": "uuid", "start_time": "10:45", "end_time": "11:30", "duration_minutes": 45 },
    { "id": "uuid", "start_time": "11:35", "end_time": "12:20", "duration_minutes": 45 },
    { "id": "uuid", "start_time": "13:00", "end_time": "13:45", "duration_minutes": 45 }
  ],
  "breaks": [
    { "after_period": 3, "start_time": "10:25", "end_time": "10:45", "label": "Short Break" },
    { "after_period": 5, "start_time": "12:20", "end_time": "13:00", "label": "Lunch Break" }
  ],
  "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
  "metadata": {}
}
```

---

### POST /api/v1/admin/timetable/periods/

Add a new period to the configuration.

**Request:**
```json
{
  "start_time": "13:50",
  "end_time": "14:35"
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "start_time": "13:50",
  "end_time": "14:35",
  "duration_minutes": 45,
  "created_at": "2026-05-23T10:00:00Z"
}
```

**Response: 409**
```json
{
  "error": "Time overlap with Period 6 (13:00 - 13:45)"
}
```

---

### PUT /api/v1/admin/timetable/periods/:id/

Update an existing period's timing.

**Request:**
```json
{
  "start_time": "08:00",
  "end_time": "08:50"
}
```

**Response: 200**
```json
{
  "id": "uuid",
  "start_time": "08:00",
  "end_time": "08:50",
  "duration_minutes": 50,
  "updated_at": "2026-05-23T10:00:00Z"
}
```

---

### DELETE /api/v1/admin/timetable/periods/:id/

Soft-delete a period. Removes it from future timetables. Existing historical timetable data is preserved.

**Response: 200**
```json
{
  "id": "uuid",
  "status": "Inactive",
  "deactivated_on": "2026-05-23",
  "message": "Period removed. Existing timetable entries preserved."
}
```

---

### GET /api/v1/admin/timetable/

Get the full timetable grid for a class/section.

**Query Params:** `?class_name=10&section=A&academic_year=2025-2026`

**Response: 200**
```json
{
  "class_name": "10",
  "section": "A",
  "academic_year": "2025-2026",
  "periods": [
    { "period_number": 1, "start_time": "08:00", "end_time": "08:45", "duration_minutes": 45 },
    { "period_number": 2, "start_time": "08:50", "end_time": "09:35", "duration_minutes": 45 },
    { "period_number": 3, "start_time": "09:40", "end_time": "10:25", "duration_minutes": 45 },
    { "period_number": 4, "start_time": "10:45", "end_time": "11:30", "duration_minutes": 45 },
    { "period_number": 5, "start_time": "11:35", "end_time": "12:20", "duration_minutes": 45 },
    { "period_number": 6, "start_time": "13:00", "end_time": "13:45", "duration_minutes": 45 }
  ],
  "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
  "timetable": {
    "Monday": [
      { "id": "uuid", "period_number": 1, "subject": "Mathematics", "teacher_name": "Dr. Jane Smith", "teacher_id": "uuid", "slot_type": "Lecture" },
      { "id": "uuid", "period_number": 2, "subject": "Physics", "teacher_name": "Prof. Robert Johnson", "teacher_id": "uuid" },
      { "id": "uuid", "period_number": 3, "subject": "English", "teacher_name": "Ms. Emily Davis", "teacher_id": "uuid", "slot_type": "Lecture" },
      { "id": "uuid", "period_number": 4, "subject": "Chemistry", "teacher_name": "Mr. William Anderson", "teacher_id": "uuid" },
      null,
      null
    ],
    "Tuesday": [
      { "id": "uuid", "period_number": 1, "subject": "English", "teacher_name": "Ms. Emily Davis", "teacher_id": "uuid", "slot_type": "Lecture" },
      { "id": "uuid", "period_number": 2, "subject": "Mathematics", "teacher_name": "Dr. Jane Smith", "teacher_id": "uuid", "slot_type": "Lecture" },
      null,
      null,
      null,
      null
    ],
    "Wednesday": [null, null, null, null, null, null],
    "Thursday": [null, null, null, null, null, null],
    "Friday": [null, null, null, null, null, null],
    "Saturday": [null, null, null, null, null, null]
  },
  "stats": {
    "total_slots": 36,
    "filled_slots": 6,
    "empty_slots": 30,
    "completion_percentage": 16.7
  },
  "metadata": {}
}
```

---

### POST /api/v1/admin/timetable/slot/

Assign a subject + teacher to a specific slot (day + period) for a class. This is the "+ Add" action.

**Request:**
```json
{
  "class_name": "10",
  "section": "A",
  "day": "Monday",
  "period_number": 5,
  "subject": "Hindi",
  "teacher_id": "uuid",
  "slot_type": "Lecture"
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "class_name": "10",
  "section": "A",
  "day": "Monday",
  "period_number": 5,
  "subject": "Hindi",
  "teacher_name": "Mrs. Priya Sharma",
  "teacher_id": "uuid",
  "slot_type": "Lecture",
  "created_at": "2026-05-23T10:00:00Z"
}
```

**Response: 409 (Teacher Conflict)**
```json
{
  "error": "Conflict: Teacher already assigned to another class at this time.",
  "conflict": {
    "teacher_name": "Mrs. Priya Sharma",
    "existing_class": "9-B",
    "existing_subject": "Hindi",
    "day": "Monday",
    "period_number": 5
  }
}
```


---

### PUT /api/v1/admin/timetable/slot/:id/

Update an existing timetable slot (change teacher or subject).

**Request:**
```json
{
  "subject": "Mathematics",
  "teacher_id": "uuid",
  "slot_type": "Lecture"
}
```

**Response: 200**
```json
{
  "id": "uuid",
  "class_name": "10",
  "section": "A",
  "day": "Monday",
  "period_number": 5,
  "subject": "Mathematics",
  "teacher_name": "Dr. Jane Smith",
  "teacher_id": "uuid",
  "slot_type": "Lecture",
  "updated_at": "2026-05-23T10:00:00Z"
}
```

**Response: 409** — Same conflict responses as POST.

---

### DELETE /api/v1/admin/timetable/slot/:id/

Remove a slot assignment (makes it empty/"+ Add" again). Soft-delete — historical data preserved.

**Response: 200**
```json
{
  "id": "uuid",
  "day": "Monday",
  "period_number": 5,
  "status": "Removed",
  "removed_on": "2026-05-23",
  "message": "Slot cleared. Historical record preserved."
}
```

---

### POST /api/v1/admin/timetable/bulk-assign/

Assign multiple slots at once (e.g., fill an entire day or copy from another class).

**Request:**
```json
{
  "class_name": "10",
  "section": "A",
  "slots": [
    { "day": "Wednesday", "period_number": 1, "subject": "Mathematics", "teacher_id": "uuid", "slot_type": "Lecture" },
    { "day": "Wednesday", "period_number": 2, "subject": "Science", "teacher_id": "uuid" },
    { "day": "Wednesday", "period_number": 3, "subject": "English", "teacher_id": "uuid", "slot_type": "Lecture" }
  ]
}
```

**Response: 201**
```json
{
  "assigned": 3,
  "conflicts": 0,
  "slots": [
    { "id": "uuid", "day": "Wednesday", "period_number": 1, "subject": "Mathematics", "teacher_name": "Dr. Jane Smith", "slot_type": "Lecture" },
    { "id": "uuid", "day": "Wednesday", "period_number": 2, "subject": "Science", "teacher_name": "Prof. Robert Johnson" },
    { "id": "uuid", "day": "Wednesday", "period_number": 3, "subject": "English", "teacher_name": "Ms. Emily Davis", "slot_type": "Lecture" }
  ]
}
```

**Response: 207 (Partial success)**
```json
{
  "assigned": 2,
  "conflicts": 1,
  "slots": [
    { "id": "uuid", "day": "Wednesday", "period_number": 1, "subject": "Mathematics", "teacher_name": "Dr. Jane Smith", "slot_type": "Lecture", "status": "Assigned" },
    { "day": "Wednesday", "period_number": 2, "subject": "Science", "teacher_id": "uuid", "status": "Conflict", "conflict": { "teacher_name": "Prof. Robert Johnson", "existing_class": "11-A" } },
    { "id": "uuid", "day": "Wednesday", "period_number": 3, "subject": "English", "teacher_name": "Ms. Emily Davis", "slot_type": "Lecture", "status": "Assigned" }
  ]
}
```

---

### GET /api/v1/admin/timetable/teacher/:teacher_id/

Get a teacher's weekly timetable (all their assigned slots across all classes).

**Query Params:** `?academic_year=2025-2026`

**Response: 200**
```json
{
  "teacher_id": "uuid",
  "teacher_name": "Dr. Jane Smith",
  "academic_year": "2025-2026",
  "total_periods_per_week": 17,
  "timetable": {
    "Monday": [
      { "period_number": 1, "start_time": "08:00", "end_time": "08:45", "class_name": "10", "section": "A", "subject": "Mathematics", "slot_type": "Lecture" },
      { "period_number": 3, "start_time": "09:40", "end_time": "10:25", "class_name": "10", "section": "B", "subject": "Mathematics", "slot_type": "Lecture" }
    ],
    "Tuesday": [
      { "period_number": 2, "start_time": "08:50", "end_time": "09:35", "class_name": "10", "section": "A", "subject": "Mathematics", "slot_type": "Lecture" },
      { "period_number": 4, "start_time": "10:45", "end_time": "11:30", "class_name": "11", "section": "A", "subject": "Physics" }
    ],
    "Wednesday": [],
    "Thursday": [],
    "Friday": [],
    "Saturday": []
  },
  "free_slots": {
    "Monday": [2, 4, 5, 6],
    "Tuesday": [1, 3, 5, 6],
    "Wednesday": [1, 2, 3, 4, 5, 6],
    "Thursday": [1, 2, 3, 4, 5, 6],
    "Friday": [1, 2, 3, 4, 5, 6],
    "Saturday": [1, 2, 3, 4, 5, 6]
  },
  "metadata": {}
}
```

---

### GET /api/v1/admin/timetable/conflicts/

Check for any scheduling conflicts across all timetables.

**Query Params:** `?academic_year=2025-2026&class_name=10&section=A`

**Response: 200**
```json
{
  "total_conflicts": 1,
  "conflicts": [
    {
      "type": "teacher_double_booked",
      "teacher_id": "uuid",
      "teacher_name": "Dr. Jane Smith",
      "day": "Thursday",
      "period_number": 3,
      "assignments": [
        { "class_name": "10", "section": "A", "subject": "Mathematics" },
        { "class_name": "10", "section": "B", "subject": "Mathematics" }
      ]
    }
  ]
}
```

---

## 7. Examinations

> **Design Principles:**
> - **Forward-compatible:** All entities use a flexible `metadata` JSON field for future extensions (e.g., online exams, proctoring) without schema changes.
> - **Backward-compatible:** New optional fields never break existing responses. Clients ignore unknown fields.
> - **Extensible types:** Exam types, grade scales, and weightage configs are admin-configurable — not hardcoded.
> - **Lifecycle:** Draft → Scheduled → In Progress → Completed → Results Entered → Published

### GET /api/v1/admin/examinations/

List exams with filters.

**Query Params:** `?type=Term&class_name=10&section=A&subject=Mathematics&status=Published&academic_year=2025-2026&page=1&page_size=20`

**Response: 200**
```json
{
  "count": 12,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "uuid",
      "name": "Mid Term",
      "type": "Term",
      "class_name": "10",
      "section": "A",
      "subject": "Mathematics",
      "date": "2026-03-15",
      "start_time": "09:00",
      "end_time": "12:00",
      "total_marks": 100,
      "passing_marks": 35,
      "total_students": 45,
      "present": 42,
      "absent": 3,
      "pass_count": 37,
      "fail_count": 5,
      "pass_rate": 88,
      "class_average": 72.4,
      "highest_marks": 98,
      "lowest_marks": 22,
      "status": "Published",
      "academic_year": "2025-2026",
      "term": "Term 1",
      "weightage_percentage": 30,
      "examiner_id": "uuid",
      "examiner_name": "Dr. Jane Smith",
      "created_at": "2026-02-01T10:00:00Z",
      "published_at": "2026-03-20T10:00:00Z",
      "metadata": {}
    }
  ],
  "summary": {
    "total_exams": 12,
    "published": 8,
    "upcoming": 3,
    "draft": 1,
    "average_pass_rate": 82
  }
}
```

---

### POST /api/v1/admin/examinations/

Create a new exam.

**Request:**
```json
{
  "name": "Final Exam",
  "type": "Term",
  "class_name": "10",
  "section": "A",
  "subject": "Mathematics",
  "date": "2026-06-15",
  "start_time": "09:00",
  "end_time": "12:00",
  "total_marks": 100,
  "passing_marks": 35,
  "academic_year": "2025-2026",
  "term": "Term 2",
  "weightage_percentage": 50,
  "examiner_id": "uuid",
  "room": "Hall A",
  "status": "Draft",
  "metadata": {}
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "name": "Final Exam",
  "type": "Term",
  "class_name": "10",
  "section": "A",
  "subject": "Mathematics",
  "date": "2026-06-15",
  "start_time": "09:00",
  "end_time": "12:00",
  "total_marks": 100,
  "passing_marks": 35,
  "total_students": 45,
  "present": 0,
  "pass_rate": 0,
  "status": "Draft",
  "academic_year": "2025-2026",
  "term": "Term 2",
  "weightage_percentage": 50,
  "examiner_id": "uuid",
  "examiner_name": "Dr. Jane Smith",
  "room": "Hall A",
  "created_at": "2026-05-23T10:00:00Z",
  "metadata": {}
}
```

---

### GET /api/v1/admin/examinations/:id/

Get full exam details including result summary.

**Response: 200**
```json
{
  "id": "uuid",
  "name": "Mid Term",
  "type": "Term",
  "class_name": "10",
  "section": "A",
  "subject": "Mathematics",
  "date": "2026-03-15",
  "start_time": "09:00",
  "end_time": "12:00",
  "total_marks": 100,
  "passing_marks": 35,
  "total_students": 45,
  "present": 42,
  "absent": 3,
  "pass_count": 37,
  "fail_count": 5,
  "pass_rate": 88,
  "class_average": 72.4,
  "highest_marks": 98,
  "lowest_marks": 22,
  "status": "Published",
  "academic_year": "2025-2026",
  "term": "Term 1",
  "weightage_percentage": 30,
  "examiner_id": "uuid",
  "examiner_name": "Dr. Jane Smith",
  "room": "Hall A",
  "created_at": "2026-02-01T10:00:00Z",
  "published_at": "2026-03-20T10:00:00Z",
  "grade_distribution": [
    { "grade": "A+", "count": 5, "percentage": 11.9 },
    { "grade": "A", "count": 8, "percentage": 19.0 },
    { "grade": "B+", "count": 10, "percentage": 23.8 },
    { "grade": "B", "count": 8, "percentage": 19.0 },
    { "grade": "C", "count": 6, "percentage": 14.3 },
    { "grade": "F", "count": 5, "percentage": 11.9 }
  ],
  "toppers": [
    { "student_id": "uuid", "student_name": "Arjun Sharma", "roll_number": "STU2025001", "marks": 98, "grade": "A+", "rank": 1 },
    { "student_id": "uuid", "student_name": "Priya Patel", "roll_number": "STU2025002", "marks": 95, "grade": "A+", "rank": 2 },
    { "student_id": "uuid", "student_name": "Sneha Gupta", "roll_number": "STU2025004", "marks": 92, "grade": "A+", "rank": 3 }
  ],
  "metadata": {}
}
```

---

### PUT /api/v1/admin/examinations/:id/

Update exam details. Status transitions: Draft → Scheduled → In Progress → Completed → Published.

**Request:**
```json
{
  "status": "Scheduled",
  "date": "2026-06-16",
  "room": "Hall B"
}
```

**Response: 200** — Full exam object with updated fields.

---

### DELETE /api/v1/admin/examinations/:id/

Soft-delete — sets status to `Cancelled`. Only allowed for Draft/Scheduled exams. Published exams cannot be deleted.

**Response: 200**
```json
{
  "id": "uuid",
  "name": "Final Exam",
  "status": "Cancelled",
  "cancelled_on": "2026-05-23",
  "message": "Exam cancelled. Records preserved."
}
```

**Response: 400 (if Published)**
```json
{
  "error": "Published exams cannot be cancelled. Create a re-evaluation instead."
}
```

---

### GET /api/v1/admin/examinations/:id/results/

Get all student results for a specific exam.

**Query Params:** `?sort_by=rank&status=pass&search=arjun`

**Response: 200**
```json
{
  "exam_id": "uuid",
  "exam_name": "Mid Term",
  "subject": "Mathematics",
  "class_section": "10-A",
  "total_marks": 100,
  "passing_marks": 35,
  "results": [
    {
      "id": "uuid",
      "student_id": "uuid",
      "student_name": "Arjun Sharma",
      "roll_number": "STU2025001",
      "marks_obtained": 98,
      "percentage": 98.0,
      "grade": "A+",
      "rank": 1,
      "status": "Pass",
      "attendance": "Present",
      "remarks": "Excellent performance",
      "internal_marks": null,
      "total_with_internal": null
    },
    {
      "id": "uuid",
      "student_id": "uuid",
      "student_name": "Rahul Verma",
      "roll_number": "STU2025003",
      "marks_obtained": 28,
      "percentage": 28.0,
      "grade": "F",
      "rank": 42,
      "status": "Fail",
      "attendance": "Present",
      "remarks": "Needs improvement",
      "internal_marks": null,
      "total_with_internal": null
    }
  ],
  "summary": {
    "total_students": 45,
    "present": 42,
    "absent": 3,
    "pass": 37,
    "fail": 5,
    "class_average": 72.4,
    "highest": 98,
    "lowest": 22
  }
}
```

---

### POST /api/v1/admin/examinations/:id/results/

Enter results for students (single or multiple). Marks are validated against `total_marks`. Grades are auto-computed based on the active grade system.

**Request:**
```json
{
  "results": [
    { "student_id": "uuid", "marks_obtained": 98, "attendance": "Present", "remarks": "Excellent" },
    { "student_id": "uuid", "marks_obtained": 72, "attendance": "Present", "remarks": "" },
    { "student_id": "uuid", "marks_obtained": null, "attendance": "Absent", "remarks": "Medical leave" }
  ]
}
```

**Response: 201**
```json
{
  "exam_id": "uuid",
  "entered": 3,
  "results": [
    { "student_id": "uuid", "marks_obtained": 98, "grade": "A+", "rank": 1, "status": "Pass" },
    { "student_id": "uuid", "marks_obtained": 72, "grade": "B", "rank": 15, "status": "Pass" },
    { "student_id": "uuid", "marks_obtained": null, "grade": "-", "rank": null, "status": "Absent" }
  ],
  "message": "Results entered for 3 students. Ranks auto-computed."
}
```

**Response: 400 (Validation)**
```json
{
  "error": "Marks cannot exceed total_marks (100)",
  "invalid_entries": [
    { "student_id": "uuid", "marks_obtained": 105, "issue": "Exceeds total marks" }
  ]
}
```

---

### POST /api/v1/admin/examinations/:id/results/bulk-upload/

Upload results via CSV file for faster entry.

**Request:** `Content-Type: multipart/form-data`
- `file`: CSV with columns — `roll_number, marks_obtained, attendance, remarks`

**Response: 200**
```json
{
  "exam_id": "uuid",
  "imported": 42,
  "skipped": 1,
  "errors": [
    { "row": 15, "roll_number": "STU2025099", "error": "Student not found in class 10-A" }
  ],
  "message": "42 results imported. Grades and ranks auto-computed."
}
```

---

### PUT /api/v1/admin/examinations/:id/results/:result_id/

Update a single student's result (e.g., after re-evaluation).

**Request:**
```json
{
  "marks_obtained": 75,
  "remarks": "Updated after re-evaluation"
}
```

**Response: 200**
```json
{
  "id": "uuid",
  "student_id": "uuid",
  "student_name": "Rahul Verma",
  "marks_obtained": 75,
  "previous_marks": 72,
  "grade": "B+",
  "previous_grade": "B",
  "rank": 12,
  "status": "Pass",
  "updated_at": "2026-05-23T10:00:00Z",
  "updated_by": "Admin Name",
  "update_reason": "Updated after re-evaluation"
}
```

---

### POST /api/v1/admin/examinations/:id/publish/

Publish results for an exam. Triggers notifications to students/parents if configured. Only allowed when all results are entered.

**Request:**
```json
{
  "notify_students": true,
  "notify_parents": true,
  "notification_message": "Mid-Term results for Mathematics have been published. Check your portal."
}
```

**Response: 200**
```json
{
  "exam_id": "uuid",
  "status": "Published",
  "published_at": "2026-05-23T10:00:00Z",
  "published_by": "Admin Name",
  "notifications_sent": {
    "students": 42,
    "parents": 42
  },
  "message": "Results published and notifications sent."
}
```

**Response: 400**
```json
{
  "error": "Cannot publish. Results pending for 3 students.",
  "pending_students": [
    { "student_id": "uuid", "roll_number": "STU2025010", "student_name": "Student Name" }
  ]
}
```

---

### GET /api/v1/admin/examinations/grade-system/

Get the active grade system configuration.

**Response: 200**
```json
{
  "id": "uuid",
  "name": "CBSE Grade System",
  "academic_year": "2025-2026",
  "is_active": true,
  "grades": [
    { "grade": "A+", "min_percentage": 90, "max_percentage": 100, "grade_point": 10, "description": "Outstanding" },
    { "grade": "A", "min_percentage": 80, "max_percentage": 89, "grade_point": 9, "description": "Excellent" },
    { "grade": "B+", "min_percentage": 70, "max_percentage": 79, "grade_point": 8, "description": "Very Good" },
    { "grade": "B", "min_percentage": 60, "max_percentage": 69, "grade_point": 7, "description": "Good" },
    { "grade": "C", "min_percentage": 50, "max_percentage": 59, "grade_point": 6, "description": "Average" },
    { "grade": "D", "min_percentage": 35, "max_percentage": 49, "grade_point": 5, "description": "Below Average" },
    { "grade": "F", "min_percentage": 0, "max_percentage": 34, "grade_point": 0, "description": "Fail" }
  ],
  "metadata": {}
}
```

---

### PUT /api/v1/admin/examinations/grade-system/

Update the grade system. Changes only apply to future result publications — previously published results retain their original grades.

**Request:**
```json
{
  "name": "Updated Grade System",
  "grades": [
    { "grade": "A+", "min_percentage": 91, "max_percentage": 100, "grade_point": 10 },
    { "grade": "A", "min_percentage": 81, "max_percentage": 90, "grade_point": 9 },
    { "grade": "B+", "min_percentage": 71, "max_percentage": 80, "grade_point": 8 },
    { "grade": "B", "min_percentage": 61, "max_percentage": 70, "grade_point": 7 },
    { "grade": "C", "min_percentage": 50, "max_percentage": 60, "grade_point": 6 },
    { "grade": "D", "min_percentage": 35, "max_percentage": 49, "grade_point": 5 },
    { "grade": "F", "min_percentage": 0, "max_percentage": 34, "grade_point": 0 }
  ]
}
```

**Response: 200**
```json
{
  "message": "Grade system updated. Applies to future publications only.",
  "id": "uuid",
  "grades": ["...updated grades..."]
}
```

---

### GET /api/v1/admin/examinations/analytics/

Get exam analytics — class performance, subject-wise, term comparison.

**Query Params:** `?class_name=10&section=A&subject=Mathematics&academic_year=2025-2026&term=Term 1`

**Response: 200**
```json
{
  "class_name": "10",
  "section": "A",
  "academic_year": "2025-2026",
  "subject_performance": [
    {
      "subject": "Mathematics",
      "exams_conducted": 4,
      "average_pass_rate": 85,
      "class_average": 71.2,
      "highest_average": 95.5,
      "lowest_average": 28.0,
      "trend": [
        { "exam_name": "Unit Test 1", "date": "2025-07-15", "average": 68.5, "pass_rate": 80 },
        { "exam_name": "Mid Term", "date": "2025-09-20", "average": 71.0, "pass_rate": 84 },
        { "exam_name": "Unit Test 2", "date": "2025-11-10", "average": 70.8, "pass_rate": 82 },
        { "exam_name": "Final", "date": "2026-03-15", "average": 74.5, "pass_rate": 88 }
      ]
    }
  ],
  "term_comparison": [
    { "term": "Term 1", "class_average": 69.8, "pass_rate": 82, "toppers_count": 5 },
    { "term": "Term 2", "class_average": 73.2, "pass_rate": 86, "toppers_count": 7 }
  ],
  "student_rankings": [
    { "rank": 1, "student_id": "uuid", "student_name": "Arjun Sharma", "weighted_average": 92.5, "grade": "A+" },
    { "rank": 2, "student_id": "uuid", "student_name": "Priya Patel", "weighted_average": 89.3, "grade": "A+" },
    { "rank": 3, "student_id": "uuid", "student_name": "Sneha Gupta", "weighted_average": 87.1, "grade": "A" }
  ],
  "grade_distribution": [
    { "grade": "A+", "count": 5, "percentage": 11.1 },
    { "grade": "A", "count": 9, "percentage": 20.0 },
    { "grade": "B+", "count": 11, "percentage": 24.4 },
    { "grade": "B", "count": 8, "percentage": 17.8 },
    { "grade": "C", "count": 7, "percentage": 15.6 },
    { "grade": "D", "count": 3, "percentage": 6.7 },
    { "grade": "F", "count": 2, "percentage": 4.4 }
  ],
  "at_risk_students": [
    { "student_id": "uuid", "student_name": "Vikram Singh", "weighted_average": 38.2, "grade": "D", "trend": "declining" }
  ]
}
```

---

### GET /api/v1/admin/examinations/report-card/:student_id/

Generate report card data for a student (for a given academic year/term).

**Query Params:** `?academic_year=2025-2026&term=Term 1`

**Response: 200**
```json
{
  "student_id": "uuid",
  "student_name": "Arjun Sharma",
  "roll_number": "STU2025001",
  "class_section": "10-A",
  "academic_year": "2025-2026",
  "term": "Term 1",
  "school_name": "ABC International School",
  "subjects": [
    {
      "subject": "Mathematics",
      "unit_test_1": { "marks": 18, "total": 20 },
      "unit_test_2": { "marks": 17, "total": 20 },
      "mid_term": { "marks": 78, "total": 100 },
      "final": { "marks": 82, "total": 100 },
      "internal": { "marks": 9, "total": 10 },
      "weighted_total": 82.4,
      "grade": "A",
      "grade_point": 9,
      "remarks": "Good improvement"
    },
    {
      "subject": "Science",
      "unit_test_1": { "marks": 19, "total": 20 },
      "unit_test_2": { "marks": 18, "total": 20 },
      "mid_term": { "marks": 85, "total": 100 },
      "final": { "marks": 88, "total": 100 },
      "internal": { "marks": 10, "total": 10 },
      "weighted_total": 87.2,
      "grade": "A",
      "grade_point": 9,
      "remarks": "Excellent"
    }
  ],
  "overall": {
    "total_weighted_average": 83.5,
    "overall_grade": "A",
    "overall_gpa": 8.8,
    "rank": 5,
    "class_strength": 45,
    "attendance_percentage": 67,
    "total_working_days": 120,
    "days_present": 80
  },
  "class_teacher_remarks": "Arjun is a dedicated student with good potential. Needs to improve attendance.",
  "principal_remarks": null,
  "generated_at": "2026-05-23T10:00:00Z",
  "metadata": {}
}
```

---

### POST /api/v1/admin/examinations/report-card/generate/

Batch-generate report cards for an entire class (returns download link for PDF).

**Request:**
```json
{
  "class_name": "10",
  "section": "A",
  "academic_year": "2025-2026",
  "term": "Term 1",
  "include_attendance": true,
  "include_remarks": true
}
```

**Response: 200**
```json
{
  "generated": 45,
  "class_section": "10-A",
  "academic_year": "2025-2026",
  "term": "Term 1",
  "download_url": "/api/v1/admin/examinations/report-card/download/?class_name=10&section=A&term=Term+1&academic_year=2025-2026",
  "expires_at": "2026-05-24T10:00:00Z"
}
```

---

### GET /api/v1/admin/examinations/schedule/

Get the exam schedule/timetable for a class.

**Query Params:** `?class_name=10&section=A&term=Term 2&academic_year=2025-2026`

**Response: 200**
```json
{
  "class_name": "10",
  "section": "A",
  "term": "Term 2",
  "academic_year": "2025-2026",
  "exams": [
    { "date": "2026-06-10", "subject": "Mathematics", "start_time": "09:00", "end_time": "12:00", "room": "Hall A", "total_marks": 100, "type": "Final" },
    { "date": "2026-06-12", "subject": "Science", "start_time": "09:00", "end_time": "12:00", "room": "Hall A", "total_marks": 100, "type": "Final" },
    { "date": "2026-06-14", "subject": "English", "start_time": "09:00", "end_time": "11:00", "room": "Hall B", "total_marks": 80, "type": "Final" },
    { "date": "2026-06-16", "subject": "Hindi", "start_time": "09:00", "end_time": "11:00", "room": "Hall B", "total_marks": 80, "type": "Final" },
    { "date": "2026-06-18", "subject": "Social Studies", "start_time": "09:00", "end_time": "12:00", "room": "Hall A", "total_marks": 100, "type": "Final" }
  ]
}
```

---

## 8. Library — Moved to V2

> **Status:** This module is designed and ready but will NOT be implemented in V1.
> Full spec is preserved below for V2 implementation.
>
> **Design:** Books can be issued to both students and teachers. Issue history is tracked per-user (student or teacher) and per-book. All list endpoints support full filtering and pagination.

### GET /api/v1/admin/library/books/

List books in catalog.

**Query Params:** `?search=physics&category=Science&author=HC Verma&availability=available&page=1&page_size=20`

- `availability` filter options: `available` (has copies), `issued_out` (all copies issued), `all` (default)
- Other filters: `search` (title/author/ISBN), `category`, `author`, `year`, `publisher`

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
      "title": "Physics Vol 1",
      "author": "HC Verma",
      "isbn": "978-81-7709",
      "category": "Science",
      "publisher": "Bharati Bhawan",
      "edition": "2nd",
      "year": 2020,
      "total_copies": 5,
      "available_copies": 3,
      "issued_copies": 2,
      "times_issued_total": 47,
      "is_active": true,
      "metadata": {}
    }
  ],
  "summary": {
    "total_books": 500,
    "total_titles": 320,
    "total_issued": 45,
    "overdue": 8,
    "fine_collected": 2400
  }
}
```

---

### GET /api/v1/admin/library/books/:id/

Get full details for a specific book including its issue history.

**Response: 200**
```json
{
  "id": "uuid",
  "title": "Physics Vol 1",
  "author": "HC Verma",
  "isbn": "978-81-7709",
  "category": "Science",
  "publisher": "Bharati Bhawan",
  "edition": "2nd",
  "year": 2020,
  "description": "Concepts of Physics for competitive exam preparation",
  "total_copies": 5,
  "available_copies": 3,
  "issued_copies": 2,
  "location": "Shelf A-12",
  "added_on": "2022-06-15",
  "is_active": true,
  "times_issued_total": 47,
  "current_holders": [
    {
      "issue_id": "uuid",
      "user_type": "student",
      "user_id": "uuid",
      "user_name": "Rahul Sharma",
      "class_section": "10-A",
      "issue_date": "2026-05-01",
      "due_date": "2026-05-15",
      "status": "Active"
    },
    {
      "issue_id": "uuid",
      "user_type": "teacher",
      "user_id": "uuid",
      "user_name": "Dr. Jane Smith",
      "department": "Mathematics",
      "issue_date": "2026-05-10",
      "due_date": "2026-06-10",
      "status": "Active"
    }
  ],
  "recent_history": [
    {
      "issue_id": "uuid",
      "user_type": "student",
      "user_name": "Priya Patel",
      "issue_date": "2026-04-01",
      "return_date": "2026-04-14",
      "status": "Returned",
      "fine_paid": 0
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/admin/library/books/:id/history/

Get complete issue history for a specific book.

**Query Params:** `?user_type=student&status=Returned&from_date=2025-01-01&to_date=2026-05-23&page=1&page_size=20`

**Response: 200**
```json
{
  "book_id": "uuid",
  "book_title": "Physics Vol 1",
  "count": 47,
  "page": 1,
  "page_size": 20,
  "total_pages": 3,
  "results": [
    {
      "issue_id": "uuid",
      "user_type": "student",
      "user_id": "uuid",
      "user_name": "Rahul Sharma",
      "class_section": "10-A",
      "issue_date": "2026-05-01",
      "due_date": "2026-05-15",
      "return_date": null,
      "status": "Active",
      "fine_amount": 0
    },
    {
      "issue_id": "uuid",
      "user_type": "teacher",
      "user_id": "uuid",
      "user_name": "Dr. Jane Smith",
      "department": "Mathematics",
      "issue_date": "2026-04-01",
      "due_date": "2026-04-30",
      "return_date": "2026-04-28",
      "status": "Returned",
      "fine_amount": 0
    }
  ]
}
```

---

### GET /api/v1/admin/library/issued/

List all currently issued books.

**Query Params:** `?status=Active&user_type=student&user_id=uuid&class_name=10&section=A&overdue_only=false&page=1&page_size=20`

**Response: 200**
```json
{
  "count": 45,
  "page": 1,
  "page_size": 20,
  "total_pages": 3,
  "results": [
    {
      "id": "uuid",
      "book_id": "uuid",
      "book_title": "Physics Vol 1",
      "isbn": "978-81-7709",
      "user_type": "student",
      "user_id": "uuid",
      "user_name": "Rahul Sharma",
      "class_section": "10-A",
      "issue_date": "2026-05-01",
      "due_date": "2026-05-15",
      "status": "Active",
      "is_overdue": false,
      "overdue_days": 0,
      "fine": 0
    },
    {
      "id": "uuid",
      "book_id": "uuid",
      "book_title": "Advanced Chemistry",
      "isbn": "978-81-1234",
      "user_type": "teacher",
      "user_id": "uuid",
      "user_name": "Mr. William Anderson",
      "department": "Chemistry",
      "issue_date": "2026-04-15",
      "due_date": "2026-05-15",
      "status": "Active",
      "is_overdue": true,
      "overdue_days": 8,
      "fine": 16
    }
  ]
}
```

---

### GET /api/v1/admin/library/overdue/

List overdue books with fine calculation.

**Query Params:** `?user_type=student&class_name=10&page=1&page_size=20`

**Response: 200**
```json
{
  "count": 8,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "uuid",
      "book_id": "uuid",
      "book_title": "English Grammar",
      "user_type": "student",
      "user_id": "uuid",
      "user_name": "Priya Patel",
      "class_section": "9-B",
      "issue_date": "2026-04-20",
      "due_date": "2026-05-04",
      "overdue_days": 19,
      "fine": 38,
      "fine_rate_per_day": 2
    }
  ],
  "total_fine_pending": 248
}
```

---

### GET /api/v1/admin/library/user-history/:user_id/

Get complete book issue history for a specific student or teacher. Shows all books they ever borrowed.

**Query Params:** `?user_type=student&status=Returned&category=Science&from_date=2025-01-01&page=1&page_size=20`

**Response: 200**
```json
{
  "user_id": "uuid",
  "user_type": "student",
  "user_name": "Rahul Sharma",
  "class_section": "10-A",
  "total_books_borrowed": 12,
  "currently_holding": 2,
  "overdue_count": 0,
  "total_fines_paid": 20,
  "count": 12,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "issue_id": "uuid",
      "book_id": "uuid",
      "book_title": "Physics Vol 1",
      "author": "HC Verma",
      "category": "Science",
      "issue_date": "2026-05-01",
      "due_date": "2026-05-15",
      "return_date": null,
      "status": "Active",
      "fine_paid": 0
    },
    {
      "issue_id": "uuid",
      "book_id": "uuid",
      "book_title": "Mathematics NCERT",
      "author": "NCERT",
      "category": "Maths",
      "issue_date": "2026-03-10",
      "due_date": "2026-03-24",
      "return_date": "2026-03-22",
      "status": "Returned",
      "fine_paid": 0
    },
    {
      "issue_id": "uuid",
      "book_id": "uuid",
      "book_title": "English Grammar",
      "author": "Wren & Martin",
      "category": "English",
      "issue_date": "2026-01-05",
      "due_date": "2026-01-19",
      "return_date": "2026-01-25",
      "status": "Returned",
      "fine_paid": 12
    }
  ]
}
```

**Example for teacher:**
```
GET /api/v1/admin/library/user-history/uuid?user_type=teacher
```

```json
{
  "user_id": "uuid",
  "user_type": "teacher",
  "user_name": "Dr. Jane Smith",
  "department": "Mathematics",
  "total_books_borrowed": 8,
  "currently_holding": 1,
  "overdue_count": 0,
  "total_fines_paid": 0,
  "results": ["...same structure..."]
}
```

---

### POST /api/v1/admin/library/issue/

Issue a book to a student or teacher.

**Request:**
```json
{
  "book_id": "uuid",
  "user_id": "uuid",
  "user_type": "student",
  "days": 14
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "book_id": "uuid",
  "book_title": "Physics Vol 1",
  "user_type": "student",
  "user_id": "uuid",
  "user_name": "Rahul Sharma",
  "class_section": "10-A",
  "issue_date": "2026-05-23",
  "due_date": "2026-06-06",
  "status": "Active",
  "copies_remaining": 2
}
```

**Response: 400**
```json
{
  "error": "No copies available for this book"
}
```

**Response: 400**
```json
{
  "error": "User already has this book issued"
}
```

---

### POST /api/v1/admin/library/return/

Return a book.

**Request:**
```json
{
  "issue_id": "uuid"
}
```

**Response: 200**
```json
{
  "id": "uuid",
  "book_id": "uuid",
  "book_title": "English Grammar",
  "user_type": "student",
  "user_name": "Priya Patel",
  "return_date": "2026-05-23",
  "overdue_days": 19,
  "fine_amount": 38,
  "fine_rate_per_day": 2,
  "status": "Returned",
  "copies_available_now": 7
}
```

---

### POST /api/v1/admin/library/renew/

Renew (extend due date) for a currently issued book.

**Request:**
```json
{
  "issue_id": "uuid",
  "additional_days": 7
}
```

**Response: 200**
```json
{
  "id": "uuid",
  "book_title": "Physics Vol 1",
  "user_name": "Rahul Sharma",
  "original_due_date": "2026-05-15",
  "new_due_date": "2026-05-22",
  "renewals_count": 1,
  "max_renewals": 2,
  "status": "Active"
}
```

**Response: 400**
```json
{
  "error": "Maximum renewals (2) reached for this issue"
}
```

---

## 9. Fee Management

> **Design:** Fee management tracks student fee payments. Each student has fee records with amounts, payment status, and late fines.
> Features: Record payments (partial/full), apply late fees (fixed or percentage), send reminders, export CSV, filter by status/class.
> KPIs: Total Fees, Collected, Pending, Overdue count + late fine amount, Collection Rate %.

### GET /api/v1/admin/fees/

List fee records with filters and pagination.

**Query Params:** `?search=john&class_name=10&section=A&status=overdue&fee_type=Tuition&due_from=2026-01-01&due_to=2026-06-30&page=1&page_size=20`

- `status` filter: `paid`, `partial`, `pending`, `overdue`
- `fee_type` filter: `Tuition`, `Transport`, `Lab`, etc. (from settings enums)

**Response: 200**
```json
{
  "count": 4,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "uuid",
      "student_id": "uuid",
      "student_name": "John Doe",
      "class_name": "10",
      "section": "A",
      "fee_type": "Tuition Fee",
      "fee_category": "academic",
      "total_amount": 5000,
      "paid": 5000,
      "pending": 0,
      "late_fine": 0,
      "due_date": "2026-04-01",
      "status": "paid",
      "overdue_days": 0,
      "is_active": true,
      "metadata": {}
    },
    {
      "id": "uuid",
      "student_id": "uuid",
      "student_name": "Emma Wilson",
      "class_name": "10",
      "section": "A",
      "fee_type": "Tuition Fee",
      "fee_category": "academic",
      "total_amount": 5000,
      "paid": 3000,
      "pending": 2000,
      "late_fine": 0,
      "due_date": "2026-04-01",
      "status": "partial",
      "overdue_days": 52,
      "is_active": true,
      "metadata": {}
    },
    {
      "id": "uuid",
      "student_id": "uuid",
      "student_name": "Michael Brown",
      "class_name": "10",
      "section": "B",
      "fee_type": "Tuition Fee",
      "fee_category": "academic",
      "total_amount": 5000,
      "paid": 0,
      "pending": 5000,
      "late_fine": 250,
      "due_date": "2026-03-25",
      "status": "overdue",
      "overdue_days": 59,
      "is_active": true,
      "metadata": {}
    },
    {
      "id": "uuid",
      "student_id": "uuid",
      "student_name": "Sophia Garcia",
      "class_name": "9",
      "section": "A",
      "fee_type": "Tuition Fee",
      "fee_category": "academic",
      "total_amount": 4500,
      "paid": 0,
      "pending": 4500,
      "late_fine": 0,
      "due_date": "2026-04-15",
      "status": "pending",
      "overdue_days": 38,
      "is_active": true,
      "metadata": {}
    }
  ],
  "summary": {
    "total_fees": 19500,
    "collected": 8000,
    "pending": 11500,
    "overdue_count": 1,
    "late_fines_total": 250,
    "collection_rate": 41.0
  }
}
```

---

### GET /api/v1/admin/fees/:id/

Get a single fee record with full payment history.

**Response: 200**
```json
{
  "id": "uuid",
  "student_id": "uuid",
  "student_name": "Emma Wilson",
  "class_name": "10",
  "section": "A",
  "fee_type": "Tuition Fee",
  "fee_category": "academic",
  "total_amount": 5000,
  "paid": 3000,
  "pending": 2000,
  "late_fine": 0,
  "due_date": "2026-04-01",
  "status": "partial",
  "overdue_days": 52,
  "payment_history": [
    {
      "id": "uuid",
      "amount": 3000,
      "payment_date": "2026-04-01",
      "method": "Online",
      "reference": "TXN-20260401-001",
      "recorded_by": "Admin Name"
    }
  ],
  "fine_history": [],
  "is_active": true,
  "metadata": {}
}
```

---

### POST /api/v1/admin/fees/

Create a fee record (assign fee to a student).

**Request:**
```json
{
  "student_id": "uuid",
  "fee_type": "Tuition Fee",
  "total_amount": 5000,
  "due_date": "2026-04-01"
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "student_id": "uuid",
  "student_name": "John Doe",
  "class_name": "10",
  "section": "A",
  "fee_type": "Tuition Fee",
  "fee_category": "academic",
  "total_amount": 5000,
  "paid": 0,
  "pending": 5000,
  "late_fine": 0,
  "due_date": "2026-04-01",
  "status": "pending",
  "created_at": "2026-05-23T10:00:00Z",
  "metadata": {}
}
```

---

### POST /api/v1/admin/fees/:id/record-payment/

Record a payment (partial or full) against a fee record.

**Request:**
```json
{
  "amount": 2000,
  "payment_method": "Online",
  "reference": "TXN-20260523-001"
}
```

**Response: 200**
```json
{
  "id": "uuid",
  "fee_id": "uuid",
  "student_name": "Emma Wilson",
  "fee_type": "Tuition Fee",
  "total_amount": 5000,
  "previously_paid": 3000,
  "payment_recorded": 2000,
  "total_paid_now": 5000,
  "pending_now": 0,
  "status": "paid",
  "payment_date": "2026-05-23",
  "payment_method": "Online",
  "reference": "TXN-20260523-001",
  "recorded_by": "Admin Name",
  "message": "Payment of ₹2,000 recorded. Fee fully paid."
}
```

**Response: 400**
```json
{
  "error": "Payment amount (₹6,000) exceeds pending amount (₹2,000)"
}
```

---

### POST /api/v1/admin/fees/:id/apply-late-fee/

Apply a late fee/penalty to a fee record.

**Request:**
```json
{
  "penalty_type": "fixed",
  "amount": 100
}
```

Or percentage-based:
```json
{
  "penalty_type": "percentage",
  "percentage": 5
}
```

**Response: 200**
```json
{
  "id": "uuid",
  "fee_id": "uuid",
  "student_name": "Emma Wilson",
  "pending_amount": 2000,
  "overdue_days": 52,
  "penalty_type": "fixed",
  "penalty_applied": 100,
  "total_late_fine_now": 100,
  "new_pending_with_fine": 2100,
  "applied_on": "2026-05-23",
  "applied_by": "Admin Name",
  "message": "Late fee of ₹100 applied."
}
```

---

### POST /api/v1/admin/fees/bulk-apply-late-fees/

Apply late fees to all overdue records at once (based on configured rules).

**Request:**
```json
{
  "penalty_type": "fixed",
  "amount": 50,
  "apply_to": "all_overdue",
  "class_name": "10"
}
```

**Response: 200**
```json
{
  "applied_to": 3,
  "total_fines_applied": 150,
  "records": [
    { "fee_id": "uuid", "student_name": "Emma Wilson", "fine_applied": 50 },
    { "fee_id": "uuid", "student_name": "Michael Brown", "fine_applied": 50 },
    { "fee_id": "uuid", "student_name": "Sophia Garcia", "fine_applied": 50 }
  ],
  "message": "Late fee of ₹50 applied to 3 overdue records."
}
```

---

### POST /api/v1/admin/fees/send-reminder/

Send fee payment reminders to students/parents.

**Request:**
```json
{
  "target_group": "overdue",
  "class_name": "10",
  "section": "A",
  "message": "This is a reminder that your fee payment is overdue. Please clear the dues at the earliest.",
  "send_via": "email"
}
```

**Response: 200**
```json
{
  "sent_to": 3,
  "target_group": "overdue",
  "send_via": "email",
  "message": "Reminder sent to 3 recipients"
}
```

---

### GET /api/v1/admin/fees/student/:student_id/

Get all fee records for a specific student.

**Query Params:** `?academic_year=2025-2026&status=pending`

**Response: 200**
```json
{
  "student_id": "uuid",
  "student_name": "Emma Wilson",
  "class_section": "10-A",
  "academic_year": "2025-2026",
  "summary": {
    "total_fees": 15000,
    "total_paid": 8000,
    "total_pending": 7000,
    "total_fines": 0
  },
  "records": [
    {
      "id": "uuid",
      "fee_type": "Tuition Fee",
      "fee_category": "academic",
      "total_amount": 5000,
      "paid": 3000,
      "pending": 2000,
      "late_fine": 0,
      "due_date": "2026-04-01",
      "status": "partial"
    },
    {
      "id": "uuid",
      "fee_type": "Lab Fee",
      "fee_category": "academic",
      "total_amount": 5000,
      "paid": 5000,
      "pending": 0,
      "late_fine": 0,
      "due_date": "2026-04-01",
      "status": "paid"
    },
    {
      "id": "uuid",
      "fee_type": "Transport Fee",
      "fee_category": "transport",
      "total_amount": 5000,
      "paid": 0,
      "pending": 5000,
      "late_fine": 0,
      "due_date": "2026-05-01",
      "status": "pending"
    }
  ]
}
```

---

### POST /api/v1/admin/fees/generate-due/

Generate due fee records for students (e.g., at the start of a term, bulk-assign fees to all students in a class).

**Request:**
```json
{
  "fee_type": "Tuition Fee",
  "amount": 5000,
  "due_date": "2026-07-01",
  "class_name": "10",
  "section": "A",
  "academic_year": "2025-2026",
  "term": "Term 2"
}
```

**Response: 201**
```json
{
  "generated": 45,
  "fee_type": "Tuition Fee",
  "amount": 5000,
  "due_date": "2026-07-01",
  "class_section": "10-A",
  "skipped": 0,
  "message": "Due fee of ₹5,000 generated for 45 students in Class 10-A."
}
```

**Response: 409**
```json
{
  "error": "Tuition Fee for Term 2 already generated for Class 10-A",
  "existing_count": 45
}
```

---

### GET /api/v1/admin/fees/:id/receipt/

Generate a payment receipt for a specific fee record (shows all payments made against this fee).

**Response: 200**
```json
{
  "receipt_number": "RCP-2026-00142",
  "generated_on": "2026-05-23",
  "school_name": "ABC International School",
  "school_address": "42, MG Road, Bangalore - 560041",
  "student_name": "Emma Wilson",
  "student_id": "uuid",
  "roll_number": "STU2024002",
  "class_section": "10-A",
  "fee_type": "Tuition Fee",
  "academic_year": "2025-2026",
  "total_amount": 5000,
  "total_paid": 5000,
  "pending": 0,
  "late_fine": 0,
  "status": "paid",
  "payments": [
    {
      "amount": 3000,
      "payment_date": "2026-04-01",
      "method": "Online",
      "reference": "TXN-20260401-001"
    },
    {
      "amount": 2000,
      "payment_date": "2026-05-23",
      "method": "Online",
      "reference": "TXN-20260523-001"
    }
  ],
  "download_url": "/api/v1/admin/fees/receipts/RCP-2026-00142/download/",
  "metadata": {}
}
```

---

### GET /api/v1/admin/fees/student/:student_id/receipt/

Generate a consolidated payment receipt for a student (all fee payments combined).

**Query Params:** `?academic_year=2025-2026&from_date=2026-01-01&to_date=2026-05-23`

**Response: 200**
```json
{
  "receipt_number": "RCP-CONS-2026-00045",
  "generated_on": "2026-05-23",
  "school_name": "ABC International School",
  "school_address": "42, MG Road, Bangalore - 560041",
  "student_name": "Emma Wilson",
  "student_id": "uuid",
  "roll_number": "STU2024002",
  "class_section": "10-A",
  "academic_year": "2025-2026",
  "period": "2026-01-01 to 2026-05-23",
  "fee_summary": {
    "total_fees_assigned": 15000,
    "total_paid": 13000,
    "total_pending": 2000,
    "total_fines": 0
  },
  "payments": [
    {
      "fee_type": "Tuition Fee",
      "amount": 5000,
      "payment_date": "2026-04-01",
      "method": "Online",
      "reference": "TXN-20260401-001"
    },
    {
      "fee_type": "Lab Fee",
      "amount": 5000,
      "payment_date": "2026-04-05",
      "method": "Cash",
      "reference": "CASH-20260405-003"
    },
    {
      "fee_type": "Tuition Fee",
      "amount": 3000,
      "payment_date": "2026-05-23",
      "method": "Online",
      "reference": "TXN-20260523-001"
    }
  ],
  "total_payments_count": 3,
  "total_amount_paid": 13000,
  "download_url": "/api/v1/admin/fees/receipts/RCP-CONS-2026-00045/download/",
  "metadata": {}
}
```

---

### GET /api/v1/admin/fees/export/

Export fee records as CSV.

**Query Params:** `?class_name=10&status=overdue`

**Response: 200** — `Content-Type: text/csv` file download.

---

## 10. Transport

> **Design:** Transport has 3 main areas:
> 1. **Vehicle Inventory** — all vehicles (Bus, Van, Mini-Bus) with capacity, status, maintenance tracking
> 2. **Driver & Staff Directory** — drivers and helpers/attendants with license, experience, assignments
> 3. **Operational Mapping** — route assignments that combine vehicle + driver + helper + route details
>
> KPI cards: Total Vehicles (operational count), Under Maintenance, Total Drivers (active count), Active Routes (assignments count)

---

### GET /api/v1/admin/transport/stats/

Get transport KPI summary.

**Response: 200**
```json
{
  "total_vehicles": 5,
  "operational_vehicles": 3,
  "under_maintenance": 1,
  "out_of_order": 1,
  "total_drivers": 4,
  "active_drivers": 3,
  "available_drivers": 1,
  "total_helpers": 3,
  "active_routes": 3,
  "total_assignments": 3,
  "total_students_transported": 99
}
```

---

### GET /api/v1/admin/transport/vehicles/

List all vehicles in inventory.

**Query Params:** `?search=BUS&type=Bus&status=Operational&page=1&page_size=20`

- `type` filter: `Bus`, `Van`, `Mini-Bus` (configurable)
- `status` filter: `Operational`, `Maintenance`, `Out-Of-Order`

**Response: 200**
```json
{
  "count": 5,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "uuid",
      "vehicle_number": "BUS-001",
      "plate_number": "ABC-1234",
      "type": "Bus",
      "model": "Tata Starbus",
      "year": 2022,
      "fuel_type": "Diesel",
      "capacity": 50,
      "occupied_seats": 45,
      "status": "Operational",
      "driver_id": "uuid",
      "driver_name": "Rajesh Kumar",
      "route_id": "uuid",
      "route_name": "North Zone - Morning",
      "next_service_date": "2024-06-01",
      "insurance_expiry": "2025-12-31",
      "fitness_expiry": "2025-06-30",
      "is_active": true,
      "metadata": {}
    },
    {
      "id": "uuid",
      "vehicle_number": "MINI-001",
      "plate_number": "DEF-9101",
      "type": "Mini-Bus",
      "model": "Tempo Traveller",
      "year": 2023,
      "fuel_type": "Diesel",
      "capacity": 20,
      "occupied_seats": 18,
      "status": "Maintenance",
      "driver_id": null,
      "driver_name": "Unassigned",
      "route_id": null,
      "route_name": "Unassigned",
      "next_service_date": "2024-04-15",
      "insurance_expiry": "2025-08-15",
      "fitness_expiry": "2025-03-20",
      "is_active": true,
      "metadata": {}
    }
  ]
}
```

---

### POST /api/v1/admin/transport/vehicles/

Add a new vehicle.

**Request:**
```json
{
  "vehicle_number": "BUS-004",
  "plate_number": "GHI-5678",
  "type": "Bus",
  "model": "Ashok Leyland",
  "year": 2024,
  "fuel_type": "Diesel",
  "capacity": 50,
  "status": "Operational",
  "insurance_expiry": "2026-12-31",
  "fitness_expiry": "2026-06-30"
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "vehicle_number": "BUS-004",
  "plate_number": "GHI-5678",
  "type": "Bus",
  "model": "Ashok Leyland",
  "year": 2024,
  "fuel_type": "Diesel",
  "capacity": 50,
  "occupied_seats": 0,
  "status": "Operational",
  "driver_id": null,
  "driver_name": "Unassigned",
  "route_id": null,
  "route_name": "Unassigned",
  "next_service_date": null,
  "insurance_expiry": "2026-12-31",
  "fitness_expiry": "2026-06-30",
  "is_active": true,
  "created_at": "2026-05-23T10:00:00Z",
  "metadata": {}
}
```

---

### GET /api/v1/admin/transport/vehicles/:id/

Get vehicle details.

**Response: 200** — Same as list item structure with full details.

---

### PUT /api/v1/admin/transport/vehicles/:id/

Update vehicle details.

**Request:**
```json
{
  "status": "Maintenance",
  "next_service_date": "2026-06-01"
}
```

**Response: 200** — Full vehicle object.

---

### DELETE /api/v1/admin/transport/vehicles/:id/

Soft-delete — sets vehicle to `Inactive`.

**Response: 200**
```json
{
  "id": "uuid",
  "vehicle_number": "BUS-003",
  "status": "Inactive",
  "deactivated_on": "2026-05-23",
  "message": "Vehicle deactivated. Historical records preserved."
}
```

---

### GET /api/v1/admin/transport/drivers/

List all drivers.

**Query Params:** `?search=rajesh&status=Active&license_type=Heavy Vehicle&page=1&page_size=20`

**Response: 200**
```json
{
  "count": 4,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "uuid",
      "driver_id": "DRV001",
      "full_name": "Rajesh Kumar",
      "phone": "+91-9876543210",
      "email": "rajesh.driver@school.com",
      "license_number": "DL-12345678",
      "license_type": "Heavy Vehicle",
      "license_expiry": "2025-06-30",
      "experience_years": 10,
      "join_date": "2020-04-01",
      "status": "Active",
      "assigned_vehicle_id": "uuid",
      "assigned_vehicle": "BUS-001",
      "assigned_route": "North Zone - Morning",
      "emergency_contact_name": "Jane Doe",
      "emergency_contact_phone": "+91-9876543211",
      "is_active": true,
      "metadata": {}
    },
    {
      "id": "uuid",
      "driver_id": "DRV004",
      "full_name": "David Thomas",
      "phone": "+91-9876543240",
      "email": "david.driver@school.com",
      "license_number": "DL-45678901",
      "license_type": "Heavy Vehicle",
      "license_expiry": "2024-08-20",
      "experience_years": 12,
      "join_date": "2018-01-15",
      "status": "Available",
      "assigned_vehicle_id": null,
      "assigned_vehicle": null,
      "assigned_route": null,
      "emergency_contact_name": null,
      "emergency_contact_phone": null,
      "is_active": true,
      "metadata": {}
    }
  ]
}
```

---

### POST /api/v1/admin/transport/drivers/

Add a new driver.

**Request:**
```json
{
  "full_name": "John Driver",
  "phone": "+91-9876543210",
  "email": "driver@school.com",
  "license_number": "DL-12345678",
  "license_type": "Heavy Vehicle",
  "license_expiry": "2027-06-30",
  "experience_years": 10,
  "join_date": "2026-05-01",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "+91-9876543211"
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "driver_id": "DRV005",
  "full_name": "John Driver",
  "phone": "+91-9876543210",
  "email": "driver@school.com",
  "license_number": "DL-12345678",
  "license_type": "Heavy Vehicle",
  "license_expiry": "2027-06-30",
  "experience_years": 10,
  "join_date": "2026-05-01",
  "status": "Available",
  "assigned_vehicle_id": null,
  "assigned_vehicle": null,
  "assigned_route": null,
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "+91-9876543211",
  "is_active": true,
  "created_at": "2026-05-23T10:00:00Z",
  "metadata": {}
}
```

---

### PUT /api/v1/admin/transport/drivers/:id/

Update driver details.

**Response: 200** — Full driver object.

---

### DELETE /api/v1/admin/transport/drivers/:id/

Soft-delete driver.

**Response: 200**
```json
{
  "id": "uuid",
  "driver_id": "DRV004",
  "full_name": "David Thomas",
  "status": "Inactive",
  "deactivated_on": "2026-05-23",
  "message": "Driver deactivated. Historical records preserved."
}
```

---

### GET /api/v1/admin/transport/helpers/

List all helpers/attendants.

**Query Params:** `?search=lakshmi&status=Active&page=1&page_size=20`

**Response: 200**
```json
{
  "count": 3,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "uuid",
      "helper_id": "HLP001",
      "full_name": "Lakshmi Devi",
      "phone": "+91-9876543250",
      "join_date": "2021-04-01",
      "status": "Active",
      "assigned_vehicle_id": "uuid",
      "assigned_vehicle": "BUS-001",
      "assigned_route": "North Zone - Morning",
      "is_active": true,
      "metadata": {}
    },
    {
      "id": "uuid",
      "helper_id": "HLP003",
      "full_name": "Rita Sharma",
      "phone": "+91-9876543270",
      "join_date": "2022-10-01",
      "status": "Available",
      "assigned_vehicle_id": null,
      "assigned_vehicle": null,
      "assigned_route": null,
      "is_active": true,
      "metadata": {}
    }
  ]
}
```

---

### POST /api/v1/admin/transport/helpers/

Add a new helper/attendant.

**Request:**
```json
{
  "full_name": "New Helper",
  "phone": "+91-9876543280",
  "join_date": "2026-05-01"
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "helper_id": "HLP004",
  "full_name": "New Helper",
  "phone": "+91-9876543280",
  "join_date": "2026-05-01",
  "status": "Available",
  "assigned_vehicle_id": null,
  "assigned_vehicle": null,
  "is_active": true,
  "created_at": "2026-05-23T10:00:00Z",
  "metadata": {}
}
```

---

### PUT /api/v1/admin/transport/helpers/:id/

Update helper details.

**Response: 200** — Full helper object.

---

### DELETE /api/v1/admin/transport/helpers/:id/

Soft-delete helper.

**Response: 200**
```json
{
  "id": "uuid",
  "helper_id": "HLP003",
  "full_name": "Rita Sharma",
  "status": "Inactive",
  "deactivated_on": "2026-05-23",
  "message": "Helper deactivated. Historical records preserved."
}
```

---

### GET /api/v1/admin/transport/routes/

List all routes.

**Query Params:** `?search=north&status=Active&page=1&page_size=20`

**Response: 200**
```json
{
  "count": 3,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "uuid",
      "route_code": "R-001",
      "name": "North Zone - Morning",
      "area": "North",
      "shift": "Morning",
      "stops": 4,
      "distance_km": 25,
      "start_time": "07:00",
      "end_time": "09:00",
      "status": "Active",
      "assigned_vehicle": "BUS-001",
      "assigned_driver": "Rajesh Kumar",
      "students_count": 45,
      "is_active": true,
      "metadata": {}
    }
  ]
}
```

---

### POST /api/v1/admin/transport/routes/

Create a new route.

**Request:**
```json
{
  "name": "West Zone - Morning",
  "area": "West",
  "shift": "Morning",
  "stops": 5,
  "distance_km": 18,
  "start_time": "07:00",
  "end_time": "08:30"
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "route_code": "R-004",
  "name": "West Zone - Morning",
  "area": "West",
  "shift": "Morning",
  "stops": 5,
  "distance_km": 18,
  "start_time": "07:00",
  "end_time": "08:30",
  "status": "Active",
  "assigned_vehicle": null,
  "assigned_driver": null,
  "students_count": 0,
  "is_active": true,
  "created_at": "2026-05-23T10:00:00Z",
  "metadata": {}
}
```

---

### PUT /api/v1/admin/transport/routes/:id/

Update route details.

**Response: 200** — Full route object.

---

### DELETE /api/v1/admin/transport/routes/:id/

Soft-delete route.

**Response: 200**
```json
{
  "id": "uuid",
  "name": "West Zone - Morning",
  "status": "Inactive",
  "deactivated_on": "2026-05-23",
  "message": "Route deactivated. Historical records preserved."
}
```

---

### GET /api/v1/admin/transport/assignments/

Get all operational mappings (route assignments). Each assignment ties together: route + vehicle + driver + helper.

**Query Params:** `?status=Active&shift=Morning&page=1&page_size=20`

**Response: 200**
```json
{
  "count": 3,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "uuid",
      "route_id": "uuid",
      "route_name": "North Zone - Morning",
      "route_code": "R-001",
      "area": "North",
      "shift": "Morning",
      "stops": 4,
      "distance_km": 25,
      "start_time": "07:00",
      "end_time": "09:00",
      "vehicle_id": "uuid",
      "vehicle_number": "BUS-001",
      "vehicle_type": "Bus",
      "vehicle_capacity": 50,
      "occupied_seats": 45,
      "driver_id": "uuid",
      "driver_name": "Rajesh Kumar",
      "driver_phone": "+91-9876543210",
      "helper_id": "uuid",
      "helper_name": "Lakshmi Devi",
      "helper_phone": "+91-9876543250",
      "status": "Active",
      "is_active": true,
      "metadata": {}
    },
    {
      "id": "uuid",
      "route_id": "uuid",
      "route_name": "South Zone - Morning",
      "route_code": "R-002",
      "area": "South",
      "shift": "Morning",
      "stops": 4,
      "distance_km": 20,
      "start_time": "07:15",
      "end_time": "09:00",
      "vehicle_id": "uuid",
      "vehicle_number": "BUS-002",
      "vehicle_type": "Bus",
      "vehicle_capacity": 45,
      "occupied_seats": 42,
      "driver_id": "uuid",
      "driver_name": "Mohammed Ali",
      "driver_phone": "+91-9876543220",
      "helper_id": "uuid",
      "helper_name": "Pushpa Singh",
      "helper_phone": "+91-9876543260",
      "status": "Active",
      "is_active": true,
      "metadata": {}
    }
  ]
}
```

---

### POST /api/v1/admin/transport/assignments/

Create a new route assignment (map vehicle + driver + helper to a route).

**Request:**
```json
{
  "route_id": "uuid",
  "vehicle_id": "uuid",
  "driver_id": "uuid",
  "helper_id": "uuid"
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "route_id": "uuid",
  "route_name": "West Zone - Morning",
  "vehicle_id": "uuid",
  "vehicle_number": "BUS-004",
  "driver_id": "uuid",
  "driver_name": "David Thomas",
  "helper_id": "uuid",
  "helper_name": "Rita Sharma",
  "status": "Active",
  "created_at": "2026-05-23T10:00:00Z"
}
```

**Response: 409**
```json
{
  "error": "Vehicle BUS-004 is already assigned to route North Zone - Morning"
}
```

---

### PUT /api/v1/admin/transport/assignments/:id/

Update an assignment (e.g., change driver or vehicle).

**Request:**
```json
{
  "driver_id": "uuid",
  "helper_id": "uuid"
}
```

**Response: 200** — Full assignment object.

---

### DELETE /api/v1/admin/transport/assignments/:id/

Soft-delete an assignment. Frees up the vehicle, driver, and helper for reassignment.

**Response: 200**
```json
{
  "id": "uuid",
  "route_name": "West Zone - Morning",
  "status": "Inactive",
  "deactivated_on": "2026-05-23",
  "message": "Assignment removed. Vehicle, driver, and helper are now available."
}
```

---

### GET /api/v1/admin/transport/vehicles/export/

Export vehicle inventory as CSV.

**Response: 200** — `Content-Type: text/csv` file download.

---

### GET /api/v1/admin/transport/drivers/export/

Export driver directory as CSV.

**Response: 200** — `Content-Type: text/csv` file download.

---

## 11. Staff Management

### GET /api/v1/admin/staff/

List staff members.

**Query Params:** `?search=rajesh&department=Teaching&status=Active&type=Full-time&page=1&page_size=20`

**Response: 200**
```json
{
  "count": 8,
  "results": [
    {
      "id": "uuid",
      "employee_id": "EMP001",
      "full_name": "Rajesh Kumar",
      "email": "rajesh.k@school.edu",
      "phone": "9876543210",
      "department": "Teaching",
      "role": "Mathematics Teacher",
      "employment_type": "Full-time",
      "joining_date": "2021-06-15",
      "salary": 45000,
      "status": "Active"
    }
  ]
}
```

---

### POST /api/v1/admin/staff/

Create a new staff member.

**Request:**
```json
{
  "employee_id": "EMP009",
  "full_name": "New Staff",
  "email": "new.staff@school.edu",
  "phone": "9876543220",
  "department": "Admin",
  "role": "Office Assistant",
  "employment_type": "Full-time",
  "joining_date": "2026-05-01",
  "salary": 25000
}
```

**Response: 201** — Full staff object.

---

### PUT /api/v1/admin/staff/:id/

Update staff details.

**Response: 200** — Full staff object.

---

### DELETE /api/v1/admin/staff/:id/

Soft-delete — sets staff `status` to `Inactive` with a `left_date`. Payroll history, leave records, and salary advance records are preserved.

**Request (optional):**
```json
{
  "reason": "Resigned",
  "left_date": "2026-05-23",
  "notes": "Voluntary resignation"
}
```

**Response: 200**
```json
{
  "id": "uuid",
  "employee_id": "EMP004",
  "full_name": "Sneha Reddy",
  "status": "Inactive",
  "left_date": "2026-05-23",
  "reason": "Resigned",
  "message": "Staff deactivated. Payroll and leave records preserved."
}
```

---

### GET /api/v1/admin/staff/export/

Export staff directory as CSV.

**Response: 200** — `Content-Type: text/csv` file download.

---

## 12. Payroll

### GET /api/v1/admin/payroll/

Get payroll for a given month/year.

**Query Params:** `?month=5&year=2026&status=Pending`

**Response: 200**
```json
{
  "month": "May",
  "year": 2026,
  "results": [
    {
      "id": "uuid",
      "employee_id": "EMP001",
      "employee_name": "Rajesh Kumar",
      "basic_salary": 45000,
      "allowances": 8000,
      "deductions": 5400,
      "net_salary": 47600,
      "status": "Paid",
      "paid_on": "2026-05-01"
    }
  ],
  "summary": {
    "total_staff": 8,
    "total_disbursed": 284000,
    "pending_amount": 44100,
    "pending_count": 1
  }
}
```

---

### POST /api/v1/admin/payroll/run/

Run payroll for a month (generate payslip entries).

**Request:**
```json
{
  "month": 5,
  "year": 2026
}
```

**Response: 200**
```json
{
  "generated": 8,
  "total_amount": 328100,
  "message": "Payroll generated for 8 staff members"
}
```

---

### POST /api/v1/admin/payroll/generate-payslips/

Generate downloadable payslips for all staff.

**Request:**
```json
{
  "month": 5,
  "year": 2026
}
```

**Response: 200**
```json
{
  "generated": 8,
  "download_url": "/api/v1/admin/payroll/payslips/download/?month=5&year=2026"
}
```

---

### GET /api/v1/admin/payroll/salary-structure/:employee_id/

Get salary structure for a specific employee.

**Response: 200**
```json
{
  "employee_id": "EMP001",
  "employee_name": "Rajesh Kumar",
  "basic": 45000,
  "hra": 10000,
  "da": 5000,
  "allowances": {
    "transport": 2000,
    "medical": 1500
  },
  "deductions": {
    "pf": 3600,
    "professional_tax": 200,
    "tds": 1600
  },
  "net_salary": 47600
}
```

---

### GET /api/v1/admin/payroll/salary-revisions/:staff_id/

Get salary revision history for a staff member.

**Response: 200**
```json
{
  "staff_id": "uuid",
  "employee_name": "Rajesh Kumar",
  "current_basic": 50000,
  "revisions": [
    {
      "id": "uuid",
      "previous_basic": 45000,
      "new_basic": 50000,
      "revision_type": "Annual Hike",
      "percentage": 10,
      "increment_amount": 5000,
      "effective_date": "2026-04-01",
      "remarks": "Annual performance hike",
      "created_at": "2026-03-25T10:00:00Z"
    }
  ]
}
```

---

### POST /api/v1/admin/payroll/salary-revisions/

Create a salary revision/hike.

**Request:**
```json
{
  "staff_id": "uuid",
  "new_basic": 50000,
  "revision_type": "Annual Hike",
  "percentage": 10,
  "effective_date": "2026-04-01",
  "remarks": "Annual performance hike"
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "staff_id": "uuid",
  "previous_basic": 45000,
  "new_basic": 50000,
  "revision_type": "Annual Hike",
  "percentage": 10,
  "increment_amount": 5000,
  "effective_date": "2026-04-01"
}
```

---

## 13. Salary Advances

### GET /api/v1/admin/salary-advances/

List salary advance requests.

**Query Params:** `?status=Pending`

**Response: 200**
```json
{
  "results": [
    {
      "id": "uuid",
      "employee_id": "EMP003",
      "employee_name": "Amit Patel",
      "amount": 50000,
      "reason": "Medical emergency",
      "recovery_months": 5,
      "per_month_deduction": 10000,
      "status": "Pending",
      "applied_on": "2026-05-20"
    }
  ]
}
```

---

### POST /api/v1/admin/salary-advances/

Create a new salary advance request.

**Request:**
```json
{
  "employee_id": "EMP003",
  "amount": 50000,
  "reason": "Medical emergency",
  "recovery_months": 5
}
```

**Response: 201** — Full advance object.

---

### POST /api/v1/admin/salary-advances/:id/approve/

**Response: 200**
```json
{
  "id": "uuid",
  "status": "Approved",
  "approved_by": "Admin Name",
  "approved_on": "2026-05-23"
}
```

---

### POST /api/v1/admin/salary-advances/:id/reject/

**Request:**
```json
{
  "remarks": "Budget constraints"
}
```

**Response: 200**
```json
{
  "id": "uuid",
  "status": "Rejected",
  "remarks": "Budget constraints"
}
```

---

### POST /api/v1/admin/salary-advances/:id/disburse/

Mark an approved advance as disbursed.

**Response: 200**
```json
{
  "id": "uuid",
  "status": "Disbursed",
  "disbursed_on": "2026-05-23"
}
```

---

## 14. Notifications

### GET /api/v1/admin/notifications/

List notifications with filters.

**Query Params:** `?search=exam&type=Announcement&status=Sent&page=1&page_size=20`

**Response: 200**
```json
{
  "count": 156,
  "results": [
    {
      "id": "uuid",
      "title": "Mid-term Exam Schedule",
      "message": "Mid-term exams will begin from June 1st.",
      "target": "All Students",
      "type": "Announcement",
      "send_via": "in_app",
      "date": "2026-05-21",
      "status": "Sent",
      "read_rate": "82%",
      "recipients_count": 156,
      "scheduled_at": null
    }
  ],
  "summary": {
    "total_sent": 156,
    "this_month": 24,
    "scheduled": 3,
    "average_read_rate": 78
  }
}
```

---

### POST /api/v1/admin/notifications/

Create and send (or schedule) a notification.

**Request:**
```json
{
  "title": "Parent-Teacher Meeting",
  "message": "PTM scheduled for June 5th. Parents are requested to attend.",
  "type": "Meeting",
  "target_type": "specific_class",
  "target_audience": "class_10a",
  "send_via": "email",
  "schedule_for_later": true,
  "scheduled_at": "2026-05-25T09:00:00Z"
}
```

> `target_type` values: `"all"`, `"students"`, `"teaching_staff"`, `"non_teaching_staff"`, `"parents"`, `"specific_class"`

**Response: 201**
```json
{
  "id": "uuid",
  "title": "Parent-Teacher Meeting",
  "message": "PTM scheduled for June 5th. Parents are requested to attend.",
  "type": "Meeting",
  "target_type": "specific_class",
  "target": "Class 10-A Parents",
  "send_via": "email",
  "status": "Scheduled",
  "scheduled_at": "2026-05-25T09:00:00Z",
  "recipients_count": 45,
  "created_at": "2026-05-23T10:00:00Z"
}
```

---

### GET /api/v1/admin/notifications/:id/

Get notification details.

**Response: 200**
```json
{
  "id": "uuid",
  "title": "Mid-term Exam Schedule",
  "message": "Mid-term exams will begin from June 1st. Please check the detailed schedule on the notice board.",
  "type": "Announcement",
  "target": "All Students",
  "send_via": "in_app",
  "date": "2026-05-21",
  "status": "Sent",
  "read_rate": "82%",
  "recipients_count": 156,
  "scheduled_at": null,
  "created_by": "Admin Name",
  "created_at": "2026-05-21T08:00:00Z"
}
```

---

### PUT /api/v1/admin/notifications/:id/

Update a notification (only if status is Scheduled/Draft).

**Request:**
```json
{
  "title": "Updated Title",
  "message": "Updated message",
  "scheduled_at": "2026-05-26T09:00:00Z"
}
```

**Response: 200** — Full notification object.

---

### DELETE /api/v1/admin/notifications/:id/

Soft-delete — sets notification `status` to `Archived`. Notification history and read receipts are preserved for audit.

**Response: 200**
```json
{
  "id": "uuid",
  "title": "Mid-term Exam Schedule",
  "status": "Archived",
  "archived_on": "2026-05-23",
  "message": "Notification archived. Delivery records preserved."
}
```

---

## 15. Settings

> **Design:** Settings is the central configuration hub for the admin. All configurable parameters across the system (school profile, academic year, enums like fee types, leave types, exam types, departments, designations, etc.) are managed here. This avoids hardcoded values and makes the system fully extensible.

### GET /api/v1/admin/settings/

Get all settings grouped by category.

**Response: 200**
```json
{
  "school_profile": {
    "school_name": "ABC International School",
    "school_code": "SCH001",
    "logo_url": "/uploads/logo.png",
    "address": "42, MG Road, Bangalore - 560041",
    "city": "Bangalore",
    "state": "Karnataka",
    "pin_code": "560041",
    "phone": "+91-80-12345678",
    "email": "admin@abcschool.edu",
    "website": "https://abcschool.edu",
    "principal_name": "Dr. Ramesh Kumar",
    "established_year": 1995,
    "board": "CBSE",
    "metadata": {}
  },
  "academic_year": {
    "current": "2025-2026",
    "start_date": "2025-06-01",
    "end_date": "2026-04-30",
    "terms": [
      { "name": "Term 1", "start_date": "2025-06-01", "end_date": "2025-11-30" },
      { "name": "Term 2", "start_date": "2025-12-01", "end_date": "2026-04-30" }
    ]
  },
  "classes": ["8", "9", "10", "11", "12"],
  "sections": ["A", "B", "C"],
  "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
  "fine_rules": {
    "fee_fine_per_day": 50,
    "fee_max_fine": 2000,
    "fee_grace_period_days": 5,
    "library_fine_per_day": 2,
    "library_max_fine": 100
  },
  "notification_channels": ["in_app", "email", "push"],
  "metadata": {}
}
```

---

### PUT /api/v1/admin/settings/

Update settings (partial update — only send fields to change).

**Request:**
```json
{
  "fine_rules": {
    "fee_fine_per_day": 75,
    "fee_grace_period_days": 3
  },
  "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
}
```

**Response: 200**
```json
{
  "message": "Settings updated successfully",
  "updated_fields": ["fine_rules", "working_days"]
}
```

---

### GET /api/v1/admin/settings/school-profile/

Get school profile details.

**Response: 200**
```json
{
  "school_name": "ABC International School",
  "school_code": "SCH001",
  "logo_url": "/uploads/logo.png",
  "address": "42, MG Road, Bangalore - 560041",
  "city": "Bangalore",
  "state": "Karnataka",
  "pin_code": "560041",
  "phone": "+91-80-12345678",
  "email": "admin@abcschool.edu",
  "website": "https://abcschool.edu",
  "principal_name": "Dr. Ramesh Kumar",
  "established_year": 1995,
  "board": "CBSE",
  "metadata": {}
}
```

---

### PUT /api/v1/admin/settings/school-profile/

Update school profile.

**Request:**
```json
{
  "phone": "+91-80-98765432",
  "principal_name": "Dr. New Principal",
  "logo_url": "/uploads/new-logo.png"
}
```

**Response: 200**
```json
{
  "message": "School profile updated successfully",
  "school_name": "ABC International School",
  "updated_fields": ["phone", "principal_name", "logo_url"]
}
```

---

### GET /api/v1/admin/settings/academic-year/

Get academic year configuration.

**Response: 200**
```json
{
  "current": "2025-2026",
  "start_date": "2025-06-01",
  "end_date": "2026-04-30",
  "terms": [
    { "id": "uuid", "name": "Term 1", "start_date": "2025-06-01", "end_date": "2025-11-30" },
    { "id": "uuid", "name": "Term 2", "start_date": "2025-12-01", "end_date": "2026-04-30" }
  ],
  "previous_years": ["2024-2025", "2023-2024", "2022-2023"]
}
```

---

### PUT /api/v1/admin/settings/academic-year/

Update academic year config (e.g., add new term, change dates).

**Request:**
```json
{
  "current": "2025-2026",
  "start_date": "2025-06-01",
  "end_date": "2026-05-15",
  "terms": [
    { "name": "Term 1", "start_date": "2025-06-01", "end_date": "2025-10-31" },
    { "name": "Term 2", "start_date": "2025-11-01", "end_date": "2026-02-28" },
    { "name": "Term 3", "start_date": "2026-03-01", "end_date": "2026-05-15" }
  ]
}
```

**Response: 200**
```json
{
  "message": "Academic year configuration updated",
  "current": "2025-2026",
  "terms_count": 3
}
```

---

### GET /api/v1/admin/settings/enums/:category/

Get configurable enum values for a specific category. Categories include: `fee_types`, `leave_types`, `exam_types`, `departments`, `designations`, `subjects`, `vehicle_types`, `fuel_types`, `notification_types`, `blood_groups`, `religions`.

**Example:** `GET /api/v1/admin/settings/enums/fee_types/`

**Response: 200**
```json
{
  "category": "fee_types",
  "values": [
    { "id": "uuid", "code": "TUITION", "label": "Tuition Fee", "is_active": true },
    { "id": "uuid", "code": "TRANSPORT", "label": "Transport Fee", "is_active": true },
    { "id": "uuid", "code": "LAB", "label": "Lab Fee", "is_active": true },
    { "id": "uuid", "code": "LIBRARY", "label": "Library Fee", "is_active": true },
    { "id": "uuid", "code": "SPORTS", "label": "Sports Fee", "is_active": true },
    { "id": "uuid", "code": "EXAM", "label": "Exam Fee", "is_active": true }
  ]
}
```

**Example:** `GET /api/v1/admin/settings/enums/departments/`

**Response: 200**
```json
{
  "category": "departments",
  "values": [
    { "id": "uuid", "code": "TEACHING", "label": "Teaching", "is_active": true },
    { "id": "uuid", "code": "ADMIN", "label": "Admin", "is_active": true },
    { "id": "uuid", "code": "SECURITY", "label": "Security", "is_active": true },
    { "id": "uuid", "code": "TRANSPORT", "label": "Transport", "is_active": true },
    { "id": "uuid", "code": "MAINTENANCE", "label": "Maintenance", "is_active": true }
  ]
}
```

---

### PUT /api/v1/admin/settings/enums/:category/

Add or update enum values for a category. Existing values with matching `code` are updated. New codes are added. To deactivate, set `is_active: false` (soft delete — never removes).

**Example:** `PUT /api/v1/admin/settings/enums/fee_types/`

**Request:**
```json
{
  "values": [
    { "code": "HOSTEL", "label": "Hostel Fee" },
    { "code": "LIBRARY", "label": "Library & Reading Fee", "is_active": true }
  ]
}
```

**Response: 200**
```json
{
  "category": "fee_types",
  "added": 1,
  "updated": 1,
  "message": "Fee types updated. Added: HOSTEL. Updated: LIBRARY."
}
```

---

### POST /api/v1/admin/settings/classes/bulk/

Bulk create classes.

**Request:**
```json
{
  "classes": ["8", "9", "10", "11", "12"]
}
```

**Response: 201**
```json
{
  "created": 5,
  "message": "5 classes created"
}
```

---

### POST /api/v1/admin/settings/sections/bulk/

Bulk create sections.

**Request:**
```json
{
  "sections": ["A", "B", "C", "D"]
}
```

**Response: 201**
```json
{
  "created": 4,
  "message": "4 sections created"
}
```

---

### POST /api/v1/admin/settings/subjects/bulk/

Bulk create subjects.

**Request:**
```json
{
  "subjects": [
    { "name": "Mathematics", "code": "MATH" },
    { "name": "Physics", "code": "PHY" }
  ]
}
```

**Response: 201**
```json
{
  "created": 2,
  "message": "2 subjects created"
}
```

---

## Error Response Format

All error responses follow a consistent format:

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {
    "field_name": ["Field-specific error messages"]
  }
}
```

### Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200  | Success |
| 201  | Created |
| 200  | Soft-delete successful (returns deactivated resource) |
| 400  | Bad Request (validation error) |
| 401  | Unauthorized (not logged in / token expired) |
| 403  | Forbidden (insufficient permissions) |
| 404  | Not Found |
| 409  | Conflict (e.g., timetable conflict, duplicate entry) |
| 422  | Unprocessable Entity |
| 500  | Internal Server Error |

---

## Request Headers

| Header | Description | Required |
|--------|-------------|----------|
| `Content-Type` | `application/json` | Yes |
| `X-School-Code` | School tenant identifier | Yes (except /auth/login/) |
| `Cookie` | httpOnly auth cookies (sent automatically) | Yes (after login) |

---

## Pagination Convention

All list endpoints support pagination:

| Param | Default | Description |
|-------|---------|-------------|
| `page` | 1 | Page number |
| `page_size` | 20 | Items per page (max 100) |

Response includes: `count`, `page`, `page_size`, `total_pages`, `results[]`

---

## Recommended Project Structure

```
school-erp-backend/
├── src/
│   ├── config/          # DB, env, constants
│   ├── middleware/       # auth, school-context, error-handler
│   ├── modules/
│   │   ├── auth/        # login, logout, refresh, me
│   │   ├── dashboard/   # aggregation endpoints
│   │   ├── students/    # CRUD + details + exports
│   │   ├── teachers/    # CRUD + assignments
│   │   ├── leaves/      # CRUD + approve/reject
│   │   ├── timetable/   # get/set periods
│   │   ├── examinations/# CRUD + results
│   │   ├── library/     # books + issue/return
│   │   ├── fees/        # assignments + reminders
│   │   ├── transport/   # routes + buses
│   │   ├── staff/       # directory
│   │   ├── payroll/     # salary + payslips + advances
│   │   └── notifications/ # CRUD + send/schedule
│   ├── utils/           # helpers, csv-export, email
│   └── app.js           # Express/FastAPI entry
├── migrations/          # DB migrations
├── tests/
└── package.json / requirements.txt
```

---

## Summary: Total Endpoints

| Module | Endpoints |
|--------|-----------|
| Auth | 7 |
| Dashboard | 6 |
| Students | 9 |
| Teachers | 13 |
| Leaves | 10 |
| Timetable | 12 |
| Examinations | 21 |
| Library | 9 (V2) |
| Fees | 3 |
| Transport | 8 |
| Staff | 5 |
| Payroll | 6 |
| Salary Advances | 5 |
| Notifications | 5 |
| Settings | 11 |
| **V1 Total** | **113** |
| Library (V2) | 9 |
| **Grand Total** | **122** |
