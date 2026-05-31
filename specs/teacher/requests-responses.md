# School ERP Backend - Teacher Portal: Requests & Responses

> Detailed request/response documentation for all Teacher Portal API endpoints.
> For quick endpoint reference, see [endpoints.md](./endpoints.md).

---

## 1. Authentication (Shared)

> Auth endpoints are identical to the Admin module. The only difference is the `role` field in responses will be `"teacher"`.

### POST /api/v1/auth/login/

Login with email and password. Sets httpOnly cookies for access + refresh tokens.

**Request:**
```json
{
  "email": "jane@teacher.com",
  "password": "password123"
}
```

**Response: 200**
```json
{
  "user": {
    "id": "b2c4e6f8-1a3b-4c5d-9e7f-0a1b2c3d4e5f",
    "email": "jane@teacher.com",
    "full_name": "Jane Smith",
    "role": "teacher",
    "school_code": "SCH001",
    "avatar_url": null,
    "staff_id": "EMP012",
    "department": "Teaching",
    "primary_subject": "Mathematics"
  }
}
```

**Response: 401**
```json
{
  "error": "Invalid email or password",
  "code": "INVALID_CREDENTIALS"
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
  "error": "Invalid or expired refresh token",
  "code": "TOKEN_EXPIRED"
}
```

---

### GET /api/v1/auth/me/

Get the current authenticated user's profile.

**Response: 200**
```json
{
  "id": "b2c4e6f8-1a3b-4c5d-9e7f-0a1b2c3d4e5f",
  "email": "jane@teacher.com",
  "full_name": "Jane Smith",
  "role": "teacher",
  "school_code": "SCH001",
  "avatar_url": null,
  "phone": "+91 9876543210",
  "staff_id": "EMP012",
  "employee_id": "EMP012",
  "department": "Teaching",
  "designation": "Senior Teacher",
  "primary_subject": "Mathematics",
  "subjects": ["Mathematics", "Statistics"],
  "qualification": "M.Sc. Mathematics, B.Ed.",
  "joining_date": "2019-06-15",
  "metadata": {}
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
  "email": "jane@teacher.com"
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
  "error": "No account found with this email",
  "code": "USER_NOT_FOUND"
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
  "error": "Invalid or expired reset token",
  "code": "INVALID_TOKEN"
}
```

---

### POST /api/v1/auth/change-password/

Change password for the currently authenticated user.

**Request:**
```json
{
  "current_password": "password123",
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
  "error": "Current password is incorrect",
  "code": "INVALID_PASSWORD"
}
```

---

## 2. Dashboard

### GET /api/v1/teacher/dashboard/stats/

Get KPI summary cards for the teacher dashboard.

**Query Params:** `?academic_year=2025-2026` (optional, defaults to current)

**Response: 200**
```json
{
  "total_students": 145,
  "pending_reviews": 8,
  "upcoming_exams": 3,
  "classes_today": 4,
  "academic_year": "2025-2026"
}
```

---

### GET /api/v1/teacher/dashboard/today-schedule/

Get today's class schedule for the authenticated teacher.

**Query Params:** `?date=2026-05-23` (optional, defaults to today)

**Response: 200**
```json
{
  "date": "2026-05-23",
  "day": "Friday",
  "schedule": [
    {
      "id": "uuid",
      "start_time": "08:00",
      "end_time": "08:45",
      "class_name": "10",
      "section": "A",
      "class_section": "10-A",
      "subject": "Mathematics"
    },
    {
      "id": "uuid",
      "start_time": "09:00",
      "end_time": "09:45",
      "class_name": "10",
      "section": "B",
      "class_section": "10-B",
      "subject": "Mathematics"
    },
    {
      "id": "uuid",
      "start_time": "11:00",
      "end_time": "11:45",
      "class_name": "11",
      "section": "A",
      "class_section": "11-A",
      "subject": "Statistics"
    },
    {
      "id": "uuid",
      "start_time": "13:30",
      "end_time": "14:15",
      "class_name": "10",
      "section": "A",
      "class_section": "10-A",
      "subject": "Mathematics"
    }
  ]
}
```

---

### GET /api/v1/teacher/dashboard/pending-reviews/

Get assignments that have submissions pending teacher review.

**Query Params:** `?page=1&page_size=10`

**Response: 200**
```json
{
  "count": 8,
  "page": 1,
  "page_size": 10,
  "total_pages": 1,
  "results": [
    {
      "id": "a1b2c3d4-5678-9abc-def0-123456789abc",
      "title": "Quadratic Equations Practice",
      "class_section": "10-A",
      "subject": "Mathematics",
      "due_date": "2026-05-20",
      "submissions_count": 38,
      "total_students": 45,
      "pending_review_count": 38,
      "status": "Active"
    },
    {
      "id": "b2c3d4e5-6789-abcd-ef01-23456789abcd",
      "title": "Trigonometry Worksheet",
      "class_section": "10-B",
      "subject": "Mathematics",
      "due_date": "2026-05-22",
      "submissions_count": 32,
      "total_students": 42,
      "pending_review_count": 32,
      "status": "Active"
    },
    {
      "id": "c3d4e5f6-789a-bcde-f012-3456789abcde",
      "title": "Statistics Data Analysis",
      "class_section": "11-A",
      "subject": "Statistics",
      "due_date": "2026-05-21",
      "submissions_count": 35,
      "total_students": 38,
      "pending_review_count": 35,
      "status": "Active"
    }
  ]
}
```

---

### GET /api/v1/teacher/dashboard/upcoming-exams/

Get upcoming exams for classes assigned to the teacher.

**Query Params:** `?limit=5`

**Response: 200**
```json
{
  "results": [
    {
      "id": "d4e5f6a7-89ab-cdef-0123-456789abcdef",
      "name": "Unit Test 3",
      "class_section": "10-A",
      "subject": "Mathematics",
      "date": "2026-06-05",
      "exam_type": "Unit Test",
      "max_marks": 50,
      "duration_minutes": 60
    },
    {
      "id": "e5f6a7b8-9abc-def0-1234-56789abcdef0",
      "name": "Mid-Term Examination",
      "class_section": "10-B",
      "subject": "Mathematics",
      "date": "2026-06-15",
      "exam_type": "Mid-Term",
      "max_marks": 100,
      "duration_minutes": 180
    },
    {
      "id": "f6a7b8c9-abcd-ef01-2345-6789abcdef01",
      "name": "Statistics Practical",
      "class_section": "11-A",
      "subject": "Statistics",
      "date": "2026-06-20",
      "exam_type": "Practical",
      "max_marks": 30,
      "duration_minutes": 90
    }
  ]
}
```

---

### GET /api/v1/teacher/dashboard/classes-summary/

Get the teacher's assigned classes with quick progress stats (attendance %, assignment completion %).

**Response: 200**
```json
{
  "classes": [
    {
      "class_id": "uuid",
      "class_name": "10",
      "section": "A",
      "subject": "Mathematics",
      "student_count": 5,
      "attendance_percentage": 78,
      "assignment_completion_percentage": 65
    },
    {
      "class_id": "uuid",
      "class_name": "10",
      "section": "B",
      "subject": "Mathematics",
      "student_count": 5,
      "attendance_percentage": 82,
      "assignment_completion_percentage": 70
    },
    {
      "class_id": "uuid",
      "class_name": "11",
      "section": "A",
      "subject": "Mathematics",
      "student_count": 8,
      "attendance_percentage": 90,
      "assignment_completion_percentage": 80
    }
  ]
}
```

---

### GET /api/v1/teacher/dashboard/leave-updates/

Get recent leave applications and their current status.

**Query Params:** `?limit=5`

**Response: 200**
```json
{
  "pending_count": 1,
  "recent": [
    {
      "id": "uuid",
      "leave_type": "Casual",
      "from_date": "2026-05-23",
      "to_date": "2026-05-27",
      "days": 3,
      "status": "Pending"
    },
    {
      "id": "uuid",
      "leave_type": "Sick",
      "from_date": "2026-05-10",
      "to_date": "2026-05-11",
      "days": 2,
      "status": "Approved"
    },
    {
      "id": "uuid",
      "leave_type": "Earned",
      "from_date": "2025-12-22",
      "to_date": "2025-12-25",
      "days": 4,
      "status": "Approved"
    }
  ]
}
```

---

### GET /api/v1/teacher/dashboard/mentees-summary/

Get the teacher's assigned mentees (quick summary for dashboard).

**Response: 200**
```json
{
  "mentees": [
    {
      "student_id": "uuid",
      "name": "John Doe",
      "class_section": "10-A",
      "avatar_initials": "JD"
    },
    {
      "student_id": "uuid",
      "name": "Sophia Garcia",
      "class_section": "9-A",
      "avatar_initials": "SG"
    }
  ]
}
```

---

### GET /api/v1/teacher/dashboard/adhoc-classes/

Get teacher's adhoc/substitute classes (past and upcoming).

**Query Params:** `?status=all&limit=5`

**Response: 200**
```json
{
  "adhoc_classes": [
    {
      "id": "uuid",
      "class_name": "11",
      "section": "A",
      "subject": "Advanced Calculus",
      "description": "Extra class for PIMT aspirants",
      "date": "2026-05-10",
      "status": "Done"
    },
    {
      "id": "uuid",
      "class_name": "9",
      "section": "B",
      "subject": "Mathematics",
      "description": "Substitute for Mr. Amit (on leave)",
      "date": "2026-06-29",
      "status": "Done"
    }
  ]
}
```

---

## 2.5. Adhoc Classes

### GET /api/v1/teacher/adhoc-classes/

List all adhoc/substitute classes for the teacher.

**Query Params:** `?status=Done&from_date=2026-01-01&to_date=2026-06-30&page=1&page_size=20`

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
      "class_name": "11",
      "section": "A",
      "subject": "Advanced Calculus",
      "description": "Extra class for PIMT aspirants",
      "date": "2026-05-10",
      "time": "14:00",
      "duration_minutes": 60,
      "student_count": 8,
      "status": "Done",
      "type": "Extra",
      "is_active": true,
      "metadata": {}
    },
    {
      "id": "uuid",
      "class_name": "9",
      "section": "B",
      "subject": "Mathematics",
      "description": "Substitute for Mr. Amit (on leave)",
      "date": "2026-06-29",
      "time": "10:00",
      "duration_minutes": 45,
      "student_count": 35,
      "status": "Done",
      "type": "Substitute",
      "is_active": true,
      "metadata": {}
    }
  ]
}
```

---

### POST /api/v1/teacher/adhoc-classes/

Create/log an adhoc class (substitute or extra class).

**Request:**
```json
{
  "class_name": "10",
  "section": "A",
  "subject": "Mathematics",
  "description": "Doubt clearing session before exams",
  "date": "2026-06-15",
  "time": "15:00",
  "duration_minutes": 60,
  "type": "Extra"
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "class_name": "10",
  "section": "A",
  "subject": "Mathematics",
  "description": "Doubt clearing session before exams",
  "date": "2026-06-15",
  "time": "15:00",
  "duration_minutes": 60,
  "student_count": 0,
  "status": "Scheduled",
  "type": "Extra",
  "created_at": "2026-05-23T10:00:00Z",
  "metadata": {}
}
```

---

### PUT /api/v1/teacher/adhoc-classes/:id/

Update an adhoc class (mark as done, add notes, update timing).

**Request:**
```json
{
  "status": "Done",
  "student_count": 38,
  "notes": "Covered quadratic equations revision"
}
```

**Response: 200**
```json
{
  "id": "uuid",
  "class_name": "10",
  "section": "A",
  "subject": "Mathematics",
  "status": "Done",
  "student_count": 38,
  "notes": "Covered quadratic equations revision",
  "updated_at": "2026-06-15T16:00:00Z"
}
```

---

### DELETE /api/v1/teacher/adhoc-classes/:id/

Soft-delete an adhoc class.

**Response: 200**
```json
{
  "id": "uuid",
  "status": "Cancelled",
  "deactivated_on": "2026-05-23",
  "message": "Adhoc class cancelled."
}
```

---

## 3. My Classes

### GET /api/v1/teacher/classes/

List all classes assigned to the authenticated teacher. Each class card shows student count and average score.

**Query Params:** `?academic_year=2025-2026`

**Response: 200**
```json
{
  "academic_year": "2025-2026",
  "results": [
    {
      "id": "uuid",
      "class_name": "10",
      "section": "A",
      "class_section": "10-A",
      "subject": "Mathematics",
      "student_count": 44,
      "avg_score": 78,
      "avg_attendance": 92,
      "is_class_teacher": true,
      "academic_year": "2025-2026",
      "metadata": {}
    },
    {
      "id": "uuid",
      "class_name": "10",
      "section": "B",
      "class_section": "10-B",
      "subject": "Mathematics",
      "student_count": 48,
      "avg_score": 73,
      "avg_attendance": 88,
      "is_class_teacher": false,
      "academic_year": "2025-2026",
      "metadata": {}
    },
    {
      "id": "uuid",
      "class_name": "11",
      "section": "A",
      "class_section": "11-A",
      "subject": "Mathematics",
      "student_count": 40,
      "avg_score": 86,
      "avg_attendance": 94,
      "is_class_teacher": false,
      "academic_year": "2025-2026",
      "metadata": {}
    }
  ]
}
```

---

### GET /api/v1/teacher/classes/:class_id/students/

List students in a specific class. Teacher must be assigned to this class. Returns per-student stats visible on the class page.

**Query Params:** `?search=john&page=1&page_size=20&sort_by=roll_number&order=asc`

**Response: 200**
```json
{
  "count": 44,
  "page": 1,
  "page_size": 20,
  "total_pages": 3,
  "class_section": "10-A",
  "subject": "Mathematics",
  "class_stats": {
    "total_students": 44,
    "class_average": 78,
    "need_attention": 5,
    "avg_attendance": 92
  },
  "results": [
    {
      "id": "uuid",
      "roll_number": "STU2024001",
      "full_name": "John Doe",
      "email": "john@student.com",
      "phone": "+1-555-0101",
      "type": "Day Scholar",
      "attendance_percentage": 95,
      "avg_score": 89,
      "assignments_completed": 41,
      "avatar_url": null,
      "status": "Active",
      "metadata": {}
    },
    {
      "id": "uuid",
      "roll_number": "STU2024002",
      "full_name": "Emma Wilson",
      "email": "emma@student.com",
      "phone": "+1-555-0201",
      "type": "Hostler",
      "attendance_percentage": 92,
      "avg_score": 85,
      "assignments_completed": 43,
      "avatar_url": null,
      "status": "Active",
      "metadata": {}
    }
  ]
}
```

**Response: 403**
```json
{
  "error": "You are not assigned to this class",
  "code": "CLASS_NOT_ASSIGNED"
}
```

---

### GET /api/v1/teacher/mentees/

List students assigned as mentees to the authenticated teacher.

**Query Params:** `?page=1&page_size=20&status=Active`

**Response: 200**
```json
{
  "count": 8,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "s1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6",
      "full_name": "Aarav Patel",
      "roll_number": "1001",
      "class_section": "10-A",
      "attendance_percentage": 92.5,
      "current_grade": "A",
      "last_meeting_date": "2026-05-15",
      "mentoring_status": "Good",
      "avatar_url": null,
      "metadata": {}
    },
    {
      "id": "s4d5e6f7-a8b9-c0d1-e2f3-a4b5c6d7e8f9",
      "full_name": "Priya Verma",
      "roll_number": "1015",
      "class_section": "10-A",
      "attendance_percentage": 68.2,
      "current_grade": "C",
      "last_meeting_date": "2026-05-10",
      "mentoring_status": "Needs Attention",
      "avatar_url": null,
      "metadata": {}
    },
    {
      "id": "s5e6f7a8-b9c0-d1e2-f3a4-b5c6d7e8f9a0",
      "full_name": "Rohan Gupta",
      "roll_number": "1108",
      "class_section": "11-A",
      "attendance_percentage": 85.0,
      "current_grade": "B",
      "last_meeting_date": "2026-05-18",
      "mentoring_status": "Good",
      "avatar_url": null,
      "metadata": {}
    }
  ]
}
```

---

### GET /api/v1/teacher/mentees/:student_id/

Get detailed mentoring info for a specific mentee.

**Response: 200**
```json
{
  "id": "s4d5e6f7-a8b9-c0d1-e2f3-a4b5c6d7e8f9",
  "full_name": "Priya Verma",
  "roll_number": "1015",
  "class_section": "10-A",
  "email": "priya.verma@student.com",
  "phone": "+91 9876543215",
  "attendance_percentage": 68.2,
  "current_grade": "C",
  "mentoring_status": "Needs Attention",
  "assigned_since": "2025-06-01",
  "meetings": [
    {
      "id": "m1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6",
      "date": "2026-05-10",
      "type": "One-on-One",
      "notes": "Discussed poor attendance. Student facing health issues. Advised to get medical certificate.",
      "follow_up_date": "2026-05-24"
    },
    {
      "id": "m2b3c4d5-e6f7-a8b9-c0d1-e2f3a4b5c6d7",
      "date": "2026-04-20",
      "type": "Parent Meeting",
      "notes": "Met with father. Discussed academic performance drop. Agreed on extra coaching.",
      "follow_up_date": "2026-05-10"
    }
  ],
  "parent_info": {
    "name": "Rajesh Verma",
    "phone": "+91 9876543400",
    "email": "rajesh.verma@email.com",
    "relationship": "Father"
  },
  "metadata": {}
}
```

---

## 4. Student Details

### GET /api/v1/teacher/students/

List students across all of the teacher's assigned classes.

**Query Params:** `?search=aarav&class_name=10&section=A&page=1&page_size=20`

**Response: 200**
```json
{
  "count": 125,
  "page": 1,
  "page_size": 20,
  "total_pages": 7,
  "results": [
    {
      "id": "s1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6",
      "roll_number": "1001",
      "full_name": "Aarav Patel",
      "email": "aarav.patel@student.com",
      "class_name": "10",
      "section": "A",
      "class_section": "10-A",
      "avatar_url": null,
      "status": "Active"
    }
  ]
}
```

---

### GET /api/v1/teacher/students/:id/

Get full student profile. Teacher can only view students in their assigned classes.

**Response: 200**
```json
{
  "id": "s1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6",
  "roll_number": "1001",
  "full_name": "Aarav Patel",
  "email": "aarav.patel@student.com",
  "phone": "+91 9876543201",
  "class_name": "10",
  "section": "A",
  "class_section": "10-A",
  "date_of_birth": "2011-03-15",
  "gender": "Male",
  "admission_date": "2023-04-01",
  "student_type": "Day Scholar",
  "blood_group": "B+",
  "religion": "Hindu",
  "address": "45, MG Road, Bangalore, Karnataka 560001",
  "avatar_url": null,
  "status": "Active",
  "is_active": true,
  "quick_stats": {
    "attendance_percentage": 92.5,
    "average_grade": "A",
    "assignments_submitted": 24,
    "fee_due": 15000
  },
  "personal_info": {
    "date_of_birth": "2011-03-15",
    "admission_date": "2023-04-01",
    "address": "45, MG Road, Bangalore, Karnataka 560001",
    "nationality": "Indian"
  },
  "parent_info": {
    "father_name": "Vikram Patel",
    "father_phone": "+91 9876543301",
    "father_email": "vikram.patel@email.com",
    "mother_name": "Meera Patel",
    "mother_phone": "+91 9876543302",
    "mother_email": "meera.patel@email.com",
    "emergency_contact": "+91 9876543301",
    "relationship": "Father"
  },
  "medical_info": {
    "blood_group": "B+",
    "gender": "Male",
    "religion": "Hindu",
    "medical_conditions": "None",
    "allergies": null
  },
  "transport_info": {
    "transport_service": "Dr - Shuttle",
    "route": "Route 5 - Downtown",
    "bus_number": "BUS-005",
    "pickup_point": "Main Street Corner"
  },
  "assigned_mentor": {
    "id": "uuid",
    "full_name": "Dr. Jane Smith",
    "subject": "Mathematics",
    "qualification": "Ph.D in Mathematics",
    "email": "jane.smith@school.com",
    "phone": "+91-555-1001"
  },
  "academic_summary": {
    "overall_attendance": 67,
    "overall_grade": 83.5,
    "assignments_submitted": 0,
    "assignments_total": 0,
    "class_rank": 5,
    "class_strength": 45
  },
  "behavior_conduct": {
    "overall_rating": "A",
    "discipline_percentage": 95,
    "punctuality_percentage": 98
  },
  "metadata": {}
}
```

**Response: 403 (Not mentor or class teacher)**
```json
{
  "error": "Access denied. Student details are only accessible to the student's assigned mentor or class teacher.",
  "code": "ACCESS_DENIED",
  "details": {
    "required_role": "mentor or class_teacher",
    "your_role": "subject_teacher"
  }
}
```

---

### GET /api/v1/teacher/students/:id/exam-results/

Get a student's exam results and performance trends.

**Query Params:** `?academic_year=2025-2026`

**Response: 200**
```json
{
  "student_id": "s1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6",
  "student_name": "Aarav Patel",
  "academic_year": "2025-2026",
  "exams": [
    {
      "id": "ex1a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
      "exam_name": "Unit Test 1",
      "exam_type": "Unit Test",
      "date": "2025-08-15",
      "results": [
        { "subject": "Mathematics", "marks": 45, "max_marks": 50, "grade": "A+", "percentage": 90.0 },
        { "subject": "English", "marks": 38, "max_marks": 50, "grade": "A", "percentage": 76.0 },
        { "subject": "Science", "marks": 42, "max_marks": 50, "grade": "A", "percentage": 84.0 },
        { "subject": "Social Studies", "marks": 40, "max_marks": 50, "grade": "A", "percentage": 80.0 },
        { "subject": "Hindi", "marks": 35, "max_marks": 50, "grade": "B+", "percentage": 70.0 }
      ],
      "total_marks": 200,
      "total_max_marks": 250,
      "overall_percentage": 80.0,
      "overall_grade": "A"
    },
    {
      "id": "ex2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
      "exam_name": "Mid-Term",
      "exam_type": "Mid-Term",
      "date": "2025-11-10",
      "results": [
        { "subject": "Mathematics", "marks": 88, "max_marks": 100, "grade": "A+", "percentage": 88.0 },
        { "subject": "English", "marks": 72, "max_marks": 100, "grade": "B+", "percentage": 72.0 },
        { "subject": "Science", "marks": 85, "max_marks": 100, "grade": "A", "percentage": 85.0 },
        { "subject": "Social Studies", "marks": 78, "max_marks": 100, "grade": "A", "percentage": 78.0 },
        { "subject": "Hindi", "marks": 68, "max_marks": 100, "grade": "B", "percentage": 68.0 }
      ],
      "total_marks": 391,
      "total_max_marks": 500,
      "overall_percentage": 78.2,
      "overall_grade": "A"
    }
  ],
  "performance_analysis": {
    "subject_wise_marks": [
      { "subject": "Mathematics", "marks_obtained": 88, "class_average": 72 },
      { "subject": "Physics", "marks_obtained": 78, "class_average": 68 },
      { "subject": "Chemistry", "marks_obtained": 82, "class_average": 70 },
      { "subject": "English", "marks_obtained": 80, "class_average": 74 },
      { "subject": "Biology", "marks_obtained": 75, "class_average": 65 }
    ],
    "subject_strengths_radar": [
      { "subject": "Mathematics", "score": 88 },
      { "subject": "Physics", "score": 78 },
      { "subject": "Chemistry", "score": 82 },
      { "subject": "English", "score": 80 },
      { "subject": "Biology", "score": 75 }
    ],
    "performance_trend_over_time": [
      { "exam_name": "Sep 2025", "Mathematics": 70, "Physics": 65, "English": 72, "Chemistry": 68 },
      { "exam_name": "Dec 2025", "Mathematics": 82, "Physics": 70, "English": 75, "Chemistry": 74 },
      { "exam_name": "Mar 2026", "Mathematics": 88, "Physics": 78, "English": 80, "Chemistry": 82 }
    ]
  }
}
```

---

### GET /api/v1/teacher/students/:id/parent-meetings/

Get parent meeting history for a student.

**Query Params:** `?page=1&page_size=10`

**Response: 200**
```json
{
  "count": 3,
  "page": 1,
  "page_size": 10,
  "total_pages": 1,
  "results": [
    {
      "id": "pm1a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
      "meeting_type": "Parent-Teacher Meeting",
      "date": "2026-04-15",
      "conducted_by": "Jane Smith",
      "attendee": "Vikram Patel (Father)",
      "notes": "Discussed overall academic progress. Student performing well in Mathematics. Need improvement in Hindi.",
      "attendance_status": "Attended",
      "follow_up_required": false,
      "metadata": {}
    },
    {
      "id": "pm2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
      "meeting_type": "Scheduled Meeting",
      "date": "2026-02-10",
      "conducted_by": "Jane Smith",
      "attendee": "Meera Patel (Mother)",
      "notes": "Discussed attendance improvement plan. Student was absent for a week due to illness.",
      "attendance_status": "Attended",
      "follow_up_required": true,
      "metadata": {}
    }
  ]
}
```

---

### GET /api/v1/teacher/students/:id/activities/

Get extra-curricular activities and awards for a student.

**Response: 200**
```json
{
  "activities": [
    {
      "id": "act1a2b3-c4d5-e6f7-a8b9-c0d1e2f3a4b5",
      "activity_name": "Science Club",
      "year_joined": 2024,
      "role": "Member",
      "is_active": true,
      "metadata": {}
    },
    {
      "id": "act2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6",
      "activity_name": "Mathematics Olympiad",
      "year_joined": 2025,
      "role": "Participant",
      "is_active": true,
      "metadata": {}
    }
  ],
  "awards": [
    {
      "id": "awd1a2b3-c4d5-e6f7-a8b9-c0d1e2f3a4b5",
      "award_name": "Best in Mathematics",
      "category": "Academic",
      "year": 2025,
      "description": "Scored highest in class in Mathematics annual exam",
      "metadata": {}
    },
    {
      "id": "awd2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6",
      "award_name": "Science Quiz Winner",
      "category": "Competition",
      "year": 2025,
      "description": "Won inter-school science quiz competition",
      "metadata": {}
    }
  ]
}
```

---

### GET /api/v1/teacher/students/:id/fee-summary/

Get fee overview for a student (read-only, limited details).

**Query Params:** `?academic_year=2025-2026`

**Response: 200**
```json
{
  "student_id": "s1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6",
  "student_name": "Aarav Patel",
  "academic_year": "2025-2026",
  "summary": {
    "total_fee": 120000,
    "total_paid": 105000,
    "total_due": 15000,
    "payment_status": "Partial"
  },
  "fee_structure": [
    { "component": "Tuition Fee", "amount": 60000, "frequency": "Annual" },
    { "component": "Lab Fee", "amount": 15000, "frequency": "Annual" },
    { "component": "Library Fee", "amount": 5000, "frequency": "Annual" },
    { "component": "Sports Fee", "amount": 10000, "frequency": "Annual" },
    { "component": "Transport Fee", "amount": 30000, "frequency": "Annual" }
  ],
  "recent_payments": [
    {
      "date": "2026-04-05",
      "amount": 30000,
      "method": "Online",
      "status": "Completed",
      "reference": "PAY-2026-04-1234"
    },
    {
      "date": "2026-01-10",
      "amount": 30000,
      "method": "Cheque",
      "status": "Completed",
      "reference": "PAY-2026-01-0987"
    }
  ]
}
```

---

### GET /api/v1/teacher/students/:id/behavior/

Get behavior, conduct, disciplinary records, and recent conduct notes for a student.

**Response: 200**
```json
{
  "student_id": "uuid",
  "student_name": "John Doe",
  "behavior_summary": {
    "overall_rating": "A",
    "discipline_percentage": 95,
    "punctuality_percentage": 98
  },
  "recent_conduct_notes": [
    {
      "id": "uuid",
      "note": "Excellent class participation",
      "subject": "Mathematics",
      "noted_by": "Ms. Smith",
      "date": "2026-04-03",
      "type": "Positive"
    },
    {
      "id": "uuid",
      "note": "Helped classmates with group project",
      "subject": "Science",
      "noted_by": "Mr. Johnson",
      "date": "2026-03-18",
      "type": "Positive"
    }
  ],
  "disciplinary_records": [],
  "has_clean_record": true,
  "metadata": {}
}
```

---

### GET /api/v1/teacher/students/:id/recent-attendance/

Get recent attendance records for a student (shown in the student detail page).

**Query Params:** `?limit=10`

**Response: 200**
```json
{
  "student_id": "uuid",
  "student_name": "John Doe",
  "records": [
    { "date": "2026-05-23", "subject": "Mathematics", "status": "Present" },
    { "date": "2026-05-22", "subject": "Mathematics", "status": "Present" },
    { "date": "2026-05-21", "subject": "Mathematics", "status": "Absent" }
  ]
}
```

---

### GET /api/v1/teacher/students/:id/assignments/

Get assignment submissions for a specific student (teacher's subject only).

**Query Params:** `?academic_year=2025-2026&status=all&page=1&page_size=20`

**Response: 200**
```json
{
  "student_id": "uuid",
  "student_name": "John Doe",
  "count": 0,
  "page": 1,
  "page_size": 20,
  "total_pages": 0,
  "results": []
}
```

---

## 5. Attendance

> **Status values:** `Present`, `Absent`, `Late` (3 states per student per day)

### GET /api/v1/teacher/attendance/

Get attendance records for a specific class and date. Used to render the mark attendance form.

**Query Params:** `?class_id=uuid&date=2026-05-23`

**Response: 200 (already submitted)**
```json
{
  "class_section": "10-A",
  "class_name": "10",
  "section": "A",
  "date": "2026-05-23",
  "is_submitted": true,
  "submitted_at": "2026-05-23T08:45:00Z",
  "summary": {
    "total_students": 2,
    "present": 2,
    "absent": 0,
    "late": 0,
    "attendance_rate": 100.0
  },
  "records": [
    {
      "student_id": "uuid",
      "roll_number": "STU2024001",
      "full_name": "John Doe",
      "status": "Present"
    },
    {
      "student_id": "uuid",
      "roll_number": "STU2024002",
      "full_name": "Emma Wilson",
      "status": "Present"
    }
  ]
}
```

**Response: 200 (not yet submitted — blank form)**
```json
{
  "class_section": "10-A",
  "class_name": "10",
  "section": "A",
  "date": "2026-05-23",
  "is_submitted": false,
  "submitted_at": null,
  "summary": null,
  "records": [
    {
      "student_id": "uuid",
      "roll_number": "STU2024001",
      "full_name": "John Doe",
      "status": "Not Marked"
    },
    {
      "student_id": "uuid",
      "roll_number": "STU2024002",
      "full_name": "Emma Wilson",
      "status": "Not Marked"
    }
  ]
}
```

---

### POST /api/v1/teacher/attendance/

Submit attendance for a class on a specific date. Each student's status is one of: `Present`, `Absent`, `Late`.

**Request:**
```json
{
  "class_id": "uuid",
  "date": "2026-05-23",
  "academic_year": "2025-2026",
  "records": [
    { "student_id": "uuid", "status": "Present" },
    { "student_id": "uuid", "status": "Present" }
  ]
}
```

**Response: 201**
```json
{
  "message": "Attendance submitted successfully",
  "class_section": "10-A",
  "date": "2026-05-23",
  "summary": {
    "total_students": 2,
    "present": 2,
    "absent": 0,
    "late": 0,
    "attendance_rate": 100.0
  },
  "submitted_at": "2026-05-23T08:45:00Z"
}
```

**Response: 403**
```json
{
  "error": "You are not assigned to this class",
  "code": "CLASS_NOT_ASSIGNED"
}
```

**Response: 409**
```json
{
  "error": "Attendance already submitted for this class and date. Use PUT to update.",
  "code": "ATTENDANCE_EXISTS"
}
```

---

### PUT /api/v1/teacher/attendance/

Update attendance for a class on a specific date (correction — e.g., marking someone late who was absent).

**Request:**
```json
{
  "class_id": "uuid",
  "date": "2026-05-23",
  "records": [
    { "student_id": "uuid", "status": "Late" },
    { "student_id": "uuid", "status": "Absent" }
  ]
}
```

**Response: 200**
```json
{
  "message": "Attendance updated successfully",
  "class_section": "10-A",
  "date": "2026-05-23",
  "summary": {
    "total_students": 2,
    "present": 0,
    "absent": 1,
    "late": 1,
    "attendance_rate": 50.0
  },
  "updated_at": "2026-05-23T09:30:00Z"
}
```

---

### GET /api/v1/teacher/attendance/history/

Get attendance history — past submissions by the teacher. Shown in the "Attendance History" section below the form.

**Query Params:** `?class_id=uuid&from_date=2026-04-01&to_date=2026-05-23&page=1&page_size=20`

**Response: 200**
```json
{
  "count": 15,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "uuid",
      "class_name": "10",
      "section": "A",
      "class_section": "10-A",
      "date": "2026-05-23",
      "status": "Submitted",
      "total_students": 42,
      "present": 42,
      "absent": 2,
      "late": 1,
      "submitted_at": "2026-05-23T08:45:00Z"
    },
    {
      "id": "uuid",
      "class_name": "10",
      "section": "A",
      "class_section": "10-A",
      "date": "2026-04-08",
      "status": "Submitted",
      "total_students": 43,
      "present": 40,
      "absent": 1,
      "late": 2,
      "submitted_at": "2026-04-08T08:30:00Z"
    },
    {
      "id": "uuid",
      "class_name": "10",
      "section": "B",
      "class_section": "10-B",
      "date": "2026-04-05",
      "status": "Submitted",
      "total_students": 48,
      "present": 45,
      "absent": 0,
      "late": 3,
      "submitted_at": "2026-04-05T09:15:00Z"
    }
  ]
}
```

---

### DELETE /api/v1/teacher/attendance/:id/

Soft-delete an attendance record (e.g., submitted in error).

**Response: 200**
```json
{
  "id": "uuid",
  "class_section": "10-A",
  "date": "2026-04-05",
  "status": "Cancelled",
  "cancelled_on": "2026-05-23",
  "message": "Attendance record cancelled."
}
```

---

### GET /api/v1/teacher/attendance/summary/

Get attendance summary/statistics for a class over a period.

**Query Params:** `?class_id=uuid&month=5&year=2026&academic_year=2025-2026`

**Response: 200**
```json
{
  "class_section": "10-A",
  "month": 5,
  "year": 2026,
  "academic_year": "2025-2026",
  "working_days": 22,
  "days_marked": 18,
  "average_attendance_percentage": 91.5,
  "students_below_75": [
    {
      "student_id": "uuid",
      "full_name": "Priya Verma",
      "roll_number": "STU2024015",
      "attendance_percentage": 68.2
    }
  ]
}
```

---

## 6. Assignments

### GET /api/v1/teacher/assignments/

List teacher's assignments with filters and pagination. Includes KPI summary.

**Query Params:** `?class_id=uuid&status=Active&search=quadratic&page=1&page_size=20&academic_year=2025-2026`

**Response: 200**
```json
{
  "count": 3,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "summary": {
    "total_assignments": 3,
    "active": 2,
    "graded": 98,
    "to_review": 35
  },
  "results": [
    {
      "id": "uuid",
      "title": "Quadratic Equations Worksheet",
      "description": "Solve problems from Chapter 4",
      "class_name": "10",
      "section": "A",
      "class_section": "10-A",
      "subject": "Mathematics",
      "due_date": "2026-04-12",
      "max_marks": 100,
      "total_students": 51,
      "submissions_count": 42,
      "graded_count": 34,
      "status": "Past Due",
      "created_at": "2026-04-01T09:00:00Z",
      "is_active": true,
      "metadata": {}
    },
    {
      "id": "uuid",
      "title": "Trigonometry Problem Set",
      "description": "Complete trigonometry exercises",
      "class_name": "10",
      "section": "B",
      "class_section": "10-B",
      "subject": "Mathematics",
      "due_date": "2026-04-20",
      "max_marks": 100,
      "total_students": 50,
      "submissions_count": 30,
      "graded_count": 25,
      "status": "Past Due",
      "created_at": "2026-04-10T09:00:00Z",
      "is_active": true,
      "metadata": {}
    },
    {
      "id": "uuid",
      "title": "Calculus Assignment",
      "description": "Calculus fundamentals practice",
      "class_name": "11",
      "section": "A",
      "class_section": "11-A",
      "subject": "Mathematics",
      "due_date": "2026-04-25",
      "max_marks": 75,
      "total_students": 48,
      "submissions_count": 40,
      "graded_count": 40,
      "status": "Past Due",
      "created_at": "2026-04-15T09:00:00Z",
      "is_active": true,
      "metadata": {}
    }
  ]
}
```

---

### POST /api/v1/teacher/assignments/

Create a new assignment.

**Request:**
```json
{
  "title": "Chapter 5 Problem Set",
  "description": "Enter assignment instructions and details.",
  "class_name": "10",
  "section": "A",
  "due_date": "2026-06-01",
  "max_marks": 100,
  "academic_year": "2025-2026"
}
```

**Response: 201**
```json
{
  "id": "uuid",
  "title": "Chapter 5 Problem Set",
  "description": "Enter assignment instructions and details.",
  "class_name": "10",
  "section": "A",
  "class_section": "10-A",
  "subject": "Mathematics",
  "due_date": "2026-06-01",
  "max_marks": 100,
  "total_students": 44,
  "submissions_count": 0,
  "graded_count": 0,
  "status": "Active",
  "created_at": "2026-05-23T10:00:00Z",
  "is_active": true,
  "academic_year": "2025-2026",
  "metadata": {}
}
```

**Response: 400**
```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "title": ["Title is required"],
    "due_date": ["Due date must be in the future"]
  }
}
```

---

### GET /api/v1/teacher/assignments/:id/

Get assignment details with submission statistics.

**Response: 200**
```json
{
  "id": "a1b2c3d4-5678-9abc-def0-123456789abc",
  "title": "Quadratic Equations Practice",
  "description": "Solve problems 1-20 from Chapter 4",
  "class_id": "c1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6",
  "class_section": "10-A",
  "subject": "Mathematics",
  "due_date": "2026-05-20",
  "max_marks": 50,
  "status": "Active",
  "created_at": "2026-05-10T09:00:00Z",
  "updated_at": "2026-05-10T09:00:00Z",
  "is_active": true,
  "academic_year": "2025-2026",
  "submission_stats": {
    "total_students": 45,
    "submitted": 38,
    "not_submitted": 7,
    "graded": 0,
    "average_marks": null
  },
  "metadata": {}
}
```

---

### PUT /api/v1/teacher/assignments/:id/

Update an existing assignment.

**Request:**
```json
{
  "title": "Quadratic Equations Practice (Updated)",
  "description": "Solve problems 1-25 from Chapter 4. Additional 5 problems added.",
  "due_date": "2026-05-25",
  "max_marks": 60
}
```

**Response: 200**
```json
{
  "id": "a1b2c3d4-5678-9abc-def0-123456789abc",
  "title": "Quadratic Equations Practice (Updated)",
  "description": "Solve problems 1-25 from Chapter 4. Additional 5 problems added.",
  "class_id": "c1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6",
  "class_section": "10-A",
  "subject": "Mathematics",
  "due_date": "2026-05-25",
  "max_marks": 60,
  "status": "Active",
  "created_at": "2026-05-10T09:00:00Z",
  "updated_at": "2026-05-23T11:00:00Z",
  "is_active": true,
  "academic_year": "2025-2026",
  "metadata": {}
}
```

---

### DELETE /api/v1/teacher/assignments/:id/

Soft-delete an assignment.

**Response: 200**
```json
{
  "message": "Assignment deleted successfully",
  "id": "a1b2c3d4-5678-9abc-def0-123456789abc",
  "deactivated_on": "2026-05-23T11:30:00Z"
}
```

---

### GET /api/v1/teacher/assignments/:id/submissions/

List student submissions for a specific assignment. Shows graded/pending review status per student.

**Query Params:** `?status=pending_review&page=1&page_size=50`

- `status` filter: `all`, `submitted`, `pending_review`, `graded`, `not_submitted`

**Response: 200**
```json
{
  "count": 42,
  "page": 1,
  "page_size": 50,
  "total_pages": 1,
  "assignment_id": "uuid",
  "assignment_title": "Quadratic Equations Worksheet",
  "class_section": "10-A",
  "total_students": 45,
  "submissions_count": 42,
  "results": [
    {
      "id": "uuid",
      "student_id": "uuid",
      "student_name": "John Doe",
      "roll_number": "STU2024001",
      "submitted_at": "2026-04-04T10:30:00Z",
      "status": "Graded",
      "marks": 43,
      "max_marks": 50,
      "graded_at": "2026-04-06T14:00:00Z"
    },
    {
      "id": "uuid",
      "student_id": "uuid",
      "student_name": "Jane Smith",
      "roll_number": "STU2024003",
      "submitted_at": "2026-04-04T12:30:15Z",
      "status": "Graded",
      "marks": 38,
      "max_marks": 50,
      "graded_at": "2026-04-06T14:10:00Z"
    },
    {
      "id": "uuid",
      "student_id": "uuid",
      "student_name": "Mike Johnson",
      "roll_number": "STU2024005",
      "submitted_at": "2026-04-04T13:09:00Z",
      "status": "Pending Review",
      "marks": null,
      "max_marks": 50,
      "graded_at": null
    },
    {
      "id": "uuid",
      "student_id": "uuid",
      "student_name": "Sarah Williams",
      "roll_number": "STU2024008",
      "submitted_at": "2026-04-04T10:11:45Z",
      "status": "Pending Review",
      "marks": null,
      "max_marks": 50,
      "graded_at": null
    }
  ]
}
```

---

### POST /api/v1/teacher/assignments/:id/submissions/:submission_id/grade/

Grade a student's submission.

**Request:**
```json
{
  "marks": 43,
  "feedback": "Good work on Q1-Q5. Need improvement on integration problems."
}
```

**Response: 200**
```json
{
  "id": "uuid",
  "student_name": "Mike Johnson",
  "marks": 43,
  "max_marks": 50,
  "feedback": "Good work on Q1-Q5. Need improvement on integration problems.",
  "status": "Graded",
  "graded_at": "2026-05-23T10:00:00Z",
  "message": "Submission graded successfully."
}
```

**Response: 400**
```json
{
  "error": "Marks (55) cannot exceed max marks (50)"
}
```

---

### GET /api/v1/teacher/assignments/:id/submissions/export/

Export all submissions for an assignment as CSV.

**Response: 200** — `Content-Type: text/csv` file download.

Columns: Roll Number, Student Name, Submitted At, Status, Marks, Max Marks, Feedback

---

## 7. Grades

### GET /api/v1/teacher/grades/

Get grades/marks for a specific class and exam. Includes KPI stats.

**Query Params:** `?class_id=uuid&exam_id=uuid&page=1&page_size=50`

**Response: 200**
```json
{
  "count": 2,
  "page": 1,
  "page_size": 50,
  "total_pages": 1,
  "class_section": "10-A",
  "exam_name": "Mid-term Mathematics",
  "exam_type": "Mid-Term",
  "subject": "Mathematics",
  "max_marks": 100,
  "is_published": false,
  "stats": {
    "class_average": 0,
    "highest_score": 0,
    "lowest_score": 0,
    "pass_rate": 0,
    "total_students": 2,
    "graded_count": 0
  },
  "results": [
    {
      "student_id": "uuid",
      "roll_number": "STU2024001",
      "full_name": "John Doe",
      "marks": null,
      "total_marks": 100,
      "percentage": null,
      "grade": "Pending",
      "status": "Pending"
    },
    {
      "student_id": "uuid",
      "roll_number": "STU2024002",
      "full_name": "Emma Wilson",
      "marks": null,
      "total_marks": 100,
      "percentage": null,
      "grade": "Pending",
      "status": "Pending"
    }
  ]
}
```

---

### POST /api/v1/teacher/grades/

Submit grades (bulk) for a class and exam.

**Request:**
```json
{
  "class_id": "c1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6",
  "exam_id": "d4e5f6a7-89ab-cdef-0123-456789abcdef",
  "academic_year": "2025-2026",
  "grades": [
    { "student_id": "s1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6", "marks": 45 },
    { "student_id": "s2b3c4d5-e6f7-a8b9-c0d1-e2f3a4b5c6d7", "marks": 38 },
    { "student_id": "s3c4d5e6-f7a8-b9c0-d1e2-f3a4b5c6d7e8", "marks": 48 },
    { "student_id": "s4d5e6f7-a8b9-c0d1-e2f3-a4b5c6d7e8f9", "marks": 29 },
    { "student_id": "s5e6f7a8-b9c0-d1e2-f3a4-b5c6d7e8f9a0", "marks": 32 }
  ]
}
```

**Response: 201**
```json
{
  "message": "Grades saved successfully",
  "class_section": "10-A",
  "exam_name": "Unit Test 3",
  "subject": "Mathematics",
  "total_graded": 5,
  "summary": {
    "highest": 48,
    "lowest": 29,
    "average": 38.4,
    "max_marks": 50
  },
  "saved_at": "2026-05-23T14:00:00Z"
}
```

**Response: 403**
```json
{
  "error": "You are not assigned to teach this subject in this class",
  "code": "SUBJECT_NOT_ASSIGNED"
}
```

**Response: 400**
```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "grades[3].marks": ["Marks cannot exceed max_marks (50)"]
  }
}
```

---

### PUT /api/v1/teacher/grades/

Update existing grades for a class and exam.

**Request:**
```json
{
  "class_id": "c1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6",
  "exam_id": "d4e5f6a7-89ab-cdef-0123-456789abcdef",
  "grades": [
    { "student_id": "s4d5e6f7-a8b9-c0d1-e2f3-a4b5c6d7e8f9", "marks": 31 },
    { "student_id": "s5e6f7a8-b9c0-d1e2-f3a4-b5c6d7e8f9a0", "marks": 34 }
  ]
}
```

**Response: 200**
```json
{
  "message": "Grades updated successfully",
  "class_section": "10-A",
  "exam_name": "Unit Test 3",
  "updated_count": 2,
  "updated_at": "2026-05-23T15:30:00Z"
}
```

---

### GET /api/v1/teacher/grades/exams/

List available exams that the teacher can grade (for their assigned classes/subjects).

**Query Params:** `?class_id=c1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6&academic_year=2025-2026`

**Response: 200**
```json
{
  "results": [
    {
      "id": "d4e5f6a7-89ab-cdef-0123-456789abcdef",
      "name": "Unit Test 3",
      "exam_type": "Unit Test",
      "class_section": "10-A",
      "subject": "Mathematics",
      "date": "2026-06-05",
      "max_marks": 50,
      "is_graded": false,
      "graded_count": 0,
      "total_students": 45
    },
    {
      "id": "e5f6a7b8-9abc-def0-1234-56789abcdef0",
      "name": "Mid-Term Examination",
      "exam_type": "Mid-Term",
      "class_section": "10-A",
      "subject": "Mathematics",
      "date": "2026-06-15",
      "max_marks": 100,
      "is_graded": false,
      "graded_count": 0,
      "total_students": 45
    },
    {
      "id": "ex1a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
      "name": "Unit Test 2",
      "exam_type": "Unit Test",
      "class_section": "10-A",
      "subject": "Mathematics",
      "date": "2026-03-10",
      "max_marks": 50,
      "is_graded": true,
      "graded_count": 45,
      "total_students": 45
    }
  ]
}
```

---

### GET /api/v1/teacher/grades/report/

Get exam report with marks distribution and grade distribution (for the Report dialog).

**Query Params:** `?class_id=uuid&exam_id=uuid`

**Response: 200**
```json
{
  "exam_name": "Mid-term Mathematics",
  "class_section": "10-A",
  "subject": "Mathematics",
  "max_marks": 100,
  "stats": {
    "class_average": 72.4,
    "highest_score": 98,
    "lowest_score": 22,
    "graded_count": 42,
    "total_students": 45,
    "pass_rate": 88
  },
  "marks_distribution": [
    { "range": "0-20", "count": 1 },
    { "range": "21-40", "count": 4 },
    { "range": "41-60", "count": 8 },
    { "range": "61-80", "count": 18 },
    { "range": "81-100", "count": 11 }
  ],
  "grade_distribution": [
    { "grade": "A+", "count": 5, "percentage": 11.9 },
    { "grade": "A", "count": 8, "percentage": 19.0 },
    { "grade": "B+", "count": 10, "percentage": 23.8 },
    { "grade": "B", "count": 8, "percentage": 19.0 },
    { "grade": "C", "count": 6, "percentage": 14.3 },
    { "grade": "F", "count": 5, "percentage": 11.9 }
  ]
}
```

---

### GET /api/v1/teacher/grades/leaderboard/

Get ranked leaderboard for a specific exam and class.

**Query Params:** `?class_id=uuid&exam_id=uuid&limit=20`

**Response: 200**
```json
{
  "exam_name": "Unit Test - Algebra",
  "class_section": "10-A",
  "subject": "Mathematics",
  "max_marks": 50,
  "leaderboard": [
    { "rank": 1, "roll_number": "STU2024003", "student_name": "Ishaan Kumar", "marks": 48, "percentage": 96.0, "grade": "A+" },
    { "rank": 2, "roll_number": "STU2024001", "student_name": "John Doe", "marks": 45, "percentage": 90.0, "grade": "A+" },
    { "rank": 3, "roll_number": "STU2024002", "student_name": "Emma Wilson", "marks": 42, "percentage": 84.0, "grade": "A" },
    { "rank": 4, "roll_number": "STU2024005", "student_name": "Rohan Gupta", "marks": 38, "percentage": 76.0, "grade": "B+" },
    { "rank": 5, "roll_number": "STU2024004", "student_name": "Priya Verma", "marks": 32, "percentage": 64.0, "grade": "B" }
  ]
}
```

---

### POST /api/v1/teacher/grades/import/

Import grades from CSV file.

**Request:** `Content-Type: multipart/form-data`
- `file`: CSV with columns — `roll_number, marks`
- `class_id`: uuid
- `exam_id`: uuid

**Response: 200**
```json
{
  "imported": 42,
  "skipped": 1,
  "errors": [
    { "row": 15, "roll_number": "STU2024099", "error": "Student not found in class 10-A" }
  ],
  "message": "42 grades imported. Grades auto-computed."
}
```

---

### GET /api/v1/teacher/grades/export/

Export grades report as CSV/PDF.

**Query Params:** `?class_id=uuid&exam_id=uuid&format=csv`

- `format`: `csv` or `pdf`

**Response: 200** — File download (`Content-Type: text/csv` or `application/pdf`)

Columns (CSV): Roll Number, Student Name, Marks Obtained, Total Marks, Percentage, Grade

---

## 8. Quizzes

### GET /api/v1/teacher/quizzes/

List teacher's quizzes with filters and pagination.

**Query Params:** `?class_id=c1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6&status=Published&search=algebra&page=1&page_size=20`

**Response: 200**
```json
{
  "count": 6,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "q1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6",
      "title": "Algebra Basics Quiz",
      "class_id": "c1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6",
      "class_section": "10-A",
      "subject": "Mathematics",
      "total_questions": 20,
      "duration_minutes": 30,
      "passing_marks": 12,
      "total_marks": 20,
      "attempts_count": 40,
      "total_students": 45,
      "status": "Published",
      "created_at": "2026-05-01T09:00:00Z",
      "published_at": "2026-05-02T08:00:00Z",
      "is_active": true,
      "metadata": {}
    },
    {
      "id": "q2b3c4d5-e6f7-a8b9-c0d1-e2f3a4b5c6d7",
      "title": "Geometry Fundamentals",
      "class_id": "c1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6",
      "class_section": "10-A",
      "subject": "Mathematics",
      "total_questions": 15,
      "duration_minutes": 20,
      "passing_marks": 9,
      "total_marks": 15,
      "attempts_count": 0,
      "total_students": 45,
      "status": "Draft",
      "created_at": "2026-05-20T10:00:00Z",
      "published_at": null,
      "is_active": true,
      "metadata": {}
    }
  ]
}
```

---

### POST /api/v1/teacher/quizzes/

Create a new quiz.

**Request:**
```json
{
  "title": "Trigonometry Quick Test",
  "class_id": "c1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6",
  "duration_minutes": 25,
  "total_questions": 15,
  "passing_marks": 9,
  "questions": [
    {
      "question_text": "What is the value of sin(30)?",
      "options": ["0", "0.5", "1", "0.707"],
      "correct_option": 1,
      "marks": 1
    },
    {
      "question_text": "Which trigonometric ratio is equal to opposite/hypotenuse?",
      "options": ["cos", "tan", "sin", "cot"],
      "correct_option": 2,
      "marks": 1
    },
    {
      "question_text": "What is cos(0)?",
      "options": ["0", "0.5", "1", "-1"],
      "correct_option": 2,
      "marks": 1
    }
  ],
  "academic_year": "2025-2026",
  "metadata": {}
}
```

**Response: 201**
```json
{
  "id": "q3c4d5e6-f7a8-b9c0-d1e2-f3a4b5c6d7e8",
  "title": "Trigonometry Quick Test",
  "class_id": "c1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6",
  "class_section": "10-A",
  "subject": "Mathematics",
  "total_questions": 15,
  "duration_minutes": 25,
  "passing_marks": 9,
  "total_marks": 15,
  "attempts_count": 0,
  "status": "Draft",
  "created_at": "2026-05-23T12:00:00Z",
  "published_at": null,
  "is_active": true,
  "academic_year": "2025-2026",
  "metadata": {}
}
```

**Response: 400**
```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "title": ["Title is required"],
    "duration_minutes": ["Duration must be at least 5 minutes"]
  }
}
```

---

### GET /api/v1/teacher/quizzes/:id/

Get quiz details including questions and attempt statistics.

**Response: 200**
```json
{
  "id": "q1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6",
  "title": "Algebra Basics Quiz",
  "class_id": "c1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6",
  "class_section": "10-A",
  "subject": "Mathematics",
  "total_questions": 20,
  "duration_minutes": 30,
  "passing_marks": 12,
  "total_marks": 20,
  "status": "Published",
  "created_at": "2026-05-01T09:00:00Z",
  "published_at": "2026-05-02T08:00:00Z",
  "is_active": true,
  "academic_year": "2025-2026",
  "questions": [
    {
      "id": "qn1a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
      "question_number": 1,
      "question_text": "Simplify: 2x + 3x",
      "options": ["5x", "6x", "5x^2", "6"],
      "correct_option": 0,
      "marks": 1
    },
    {
      "id": "qn2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
      "question_number": 2,
      "question_text": "Solve for x: 2x = 10",
      "options": ["2", "5", "10", "20"],
      "correct_option": 1,
      "marks": 1
    }
  ],
  "attempt_stats": {
    "total_students": 45,
    "attempted": 40,
    "not_attempted": 5,
    "passed": 35,
    "failed": 5,
    "average_score": 15.2,
    "highest_score": 20,
    "lowest_score": 8
  },
  "metadata": {}
}
```

---

### PUT /api/v1/teacher/quizzes/:id/

Update a quiz. Can only update if status is "Draft" or no attempts have been made.

**Request:**
```json
{
  "title": "Geometry Fundamentals (Revised)",
  "duration_minutes": 25,
  "total_questions": 18,
  "passing_marks": 11,
  "questions": [
    {
      "question_text": "How many sides does a hexagon have?",
      "options": ["4", "5", "6", "8"],
      "correct_option": 2,
      "marks": 1
    },
    {
      "question_text": "What is the sum of angles in a triangle?",
      "options": ["90", "180", "270", "360"],
      "correct_option": 1,
      "marks": 1
    }
  ]
}
```

**Response: 200**
```json
{
  "id": "q2b3c4d5-e6f7-a8b9-c0d1-e2f3a4b5c6d7",
  "title": "Geometry Fundamentals (Revised)",
  "class_id": "c1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6",
  "class_section": "10-A",
  "subject": "Mathematics",
  "total_questions": 18,
  "duration_minutes": 25,
  "passing_marks": 11,
  "total_marks": 18,
  "status": "Draft",
  "created_at": "2026-05-20T10:00:00Z",
  "updated_at": "2026-05-23T13:00:00Z",
  "is_active": true,
  "metadata": {}
}
```

**Response: 409**
```json
{
  "error": "Cannot modify a published quiz that has student attempts",
  "code": "QUIZ_HAS_ATTEMPTS"
}
```

---

### DELETE /api/v1/teacher/quizzes/:id/

Soft-delete a quiz.

**Response: 200**
```json
{
  "message": "Quiz deleted successfully",
  "id": "q2b3c4d5-e6f7-a8b9-c0d1-e2f3a4b5c6d7",
  "deactivated_on": "2026-05-23T13:30:00Z"
}
```

**Response: 409**
```json
{
  "error": "Cannot delete a published quiz with active attempts. Archive it instead.",
  "code": "QUIZ_HAS_ATTEMPTS"
}
```

---

### POST /api/v1/teacher/quizzes/:id/publish/

Publish a draft quiz, making it available to students.

**Response: 200**
```json
{
  "message": "Quiz published successfully",
  "id": "q2b3c4d5-e6f7-a8b9-c0d1-e2f3a4b5c6d7",
  "title": "Geometry Fundamentals (Revised)",
  "status": "Published",
  "published_at": "2026-05-23T14:00:00Z"
}
```

**Response: 400**
```json
{
  "error": "Quiz must have at least one question to publish",
  "code": "QUIZ_EMPTY"
}
```

---

## 9. Notifications & Messaging

> **Channel:** Messages are sent via WhatsApp Business API.
> Teacher can only message students/parents in their assigned classes.

### GET /api/v1/teacher/notifications/

List notifications/messages sent by the teacher. Includes KPI stats.

**Query Params:** `?recipient_type=Students&class_id=uuid&page=1&page_size=20`

**Response: 200**
```json
{
  "count": 5,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "stats": {
    "my_students": 2,
    "my_classes": 3,
    "messages_sent": 5,
    "parents_delivered": 3
  },
  "results": [
    {
      "id": "uuid",
      "title": "Assignment Reminder",
      "message": "This is a reminder that the Mathematics assignment is due tomorrow. Please ensure timely submission.",
      "recipient_group": "Students",
      "class_section": "10-A",
      "recipients_count": 2,
      "sent_at": "2026-05-19T08:00:00Z",
      "delivery_count": 2,
      "read_count": 2,
      "channel": "whatsapp",
      "status": "Delivered",
      "metadata": {}
    },
    {
      "id": "uuid",
      "title": "Parent Teacher Meeting",
      "message": "PTM scheduled for 25th May. Please ensure attendance.",
      "recipient_group": "Parents",
      "class_section": "10-A",
      "recipients_count": 2,
      "sent_at": "2026-05-18T10:00:00Z",
      "delivery_count": 2,
      "read_count": 1,
      "channel": "whatsapp",
      "status": "Delivered",
      "metadata": {}
    }
  ]
}
```

---

### POST /api/v1/teacher/notifications/

Send a WhatsApp message to students or parents. Supports optional scheduling.

**Request:**
```json
{
  "title": "Assignment Reminder",
  "message": "This is a reminder that the Mathematics assignment is due tomorrow. Please ensure timely submission.",
  "recipient_group": "Students",
  "class_name": "10",
  "section": "A",
  "scheduled_date": null,
  "scheduled_time": null
}
```

- `recipient_group`: `Students` or `Parents`
- `class_name` + `section`: filter recipients to specific class (omit both to send to all assigned classes)
- `scheduled_date` + `scheduled_time`: optional — leave null to send immediately

**Response: 201**
```json
{
  "id": "uuid",
  "title": "Assignment Reminder",
  "message": "This is a reminder that the Mathematics assignment is due tomorrow. Please ensure timely submission.",
  "recipient_group": "Students",
  "class_section": "10-A",
  "recipients_count": 2,
  "channel": "whatsapp",
  "status": "Sent",
  "sent_at": "2026-05-23T15:00:00Z",
  "scheduled_at": null,
  "message": "WhatsApp message sent to 2 recipients."
}
```

**Scheduled message response:**
```json
{
  "id": "uuid",
  "title": "Parent Teacher Meeting",
  "recipient_group": "Parents",
  "class_section": "10-A",
  "recipients_count": 2,
  "channel": "whatsapp",
  "status": "Scheduled",
  "sent_at": null,
  "scheduled_at": "2026-05-25T09:00:00Z",
  "message": "Message scheduled for 2026-05-25 at 09:00."
}
```

**Response: 400**
```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "message": ["Message content is required"],
    "title": ["Message title is required"]
  }
}
```

---

### GET /api/v1/teacher/notifications/:id/

Get notification details including delivery status.

**Response: 200**
```json
{
  "id": "uuid",
  "title": "Assignment Reminder",
  "message": "This is a reminder that the Mathematics assignment is due tomorrow. Please ensure timely submission.",
  "recipient_group": "Students",
  "class_section": "10-A",
  "channel": "whatsapp",
  "sent_at": "2026-05-19T08:00:00Z",
  "scheduled_at": null,
  "status": "Delivered",
  "delivery_stats": {
    "total_recipients": 2,
    "delivered": 2,
    "read": 2,
    "failed": 0
  },
  "metadata": {}
}
```

---

### GET /api/v1/teacher/notifications/recipients/

Get available recipient groups with counts. Used to populate the "Select Recipients" section.

**Query Params:** `?class_name=10&section=A`

**Response: 200**
```json
{
  "assigned_classes": [
    { "class_name": "10", "section": "A", "student_count": 2, "status": "Active" },
    { "class_name": "10", "section": "B", "student_count": 3, "status": "Active" },
    { "class_name": "11", "section": "A", "student_count": 5, "status": "Active" }
  ],
  "recipient_groups": [
    { "key": "Students", "label": "Students", "description": "Send to students directly" },
    { "key": "Parents", "label": "Parents", "description": "Send to parents" }
  ],
  "filtered_recipients": {
    "class_name": "10",
    "section": "A",
    "total_recipients": 2,
    "group": "Students"
  }
}
```

---

## 10. Timetable

### GET /api/v1/teacher/timetable/

Get the teacher's weekly timetable with KPI stats. Supports day filtering.

**Query Params:** `?academic_year=2025-2026&day=Tuesday`

- `day`: optional — if provided, returns only that day's schedule. If omitted, returns all days.

**Response: 200**
```json
{
  "academic_year": "2025-2026",
  "stats": {
    "total_classes_per_week": 18,
    "practical_sessions": 5,
    "free_periods": 10
  },
  "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
  "timetable": {
    "Tuesday": [
      {
        "id": "uuid",
        "start_time": "08:00",
        "end_time": "08:50",
        "duration_minutes": 50,
        "subject": "Mathematics",
        "type": "Lecture",
        "class_name": "11",
        "section": "A",
        "class_section": "11-A"
      },
      {
        "id": "uuid",
        "start_time": "09:00",
        "end_time": "09:50",
        "duration_minutes": 50,
        "subject": "Mathematics",
        "type": "Lecture",
        "class_name": "10",
        "section": "A",
        "class_section": "10-A"
      },
      {
        "id": "uuid",
        "start_time": "10:00",
        "end_time": "10:50",
        "duration_minutes": 50,
        "subject": "Mathematics",
        "type": "Lecture",
        "class_name": "10",
        "section": "B",
        "class_section": "10-B"
      },
      {
        "id": "uuid",
        "start_time": "11:00",
        "end_time": "11:00",
        "duration_minutes": 0,
        "subject": null,
        "type": "Free",
        "class_name": null,
        "section": null,
        "class_section": null
      },
      {
        "id": "uuid",
        "start_time": "12:00",
        "end_time": "12:50",
        "duration_minutes": 50,
        "subject": null,
        "type": "Break",
        "class_name": null,
        "section": null,
        "class_section": null,
        "label": "Lunch Break"
      },
      {
        "id": "uuid",
        "start_time": "13:00",
        "end_time": "13:50",
        "duration_minutes": 50,
        "subject": "Mathematics",
        "type": "Lecture",
        "class_name": "11",
        "section": "A",
        "class_section": "11-A"
      },
      {
        "id": "uuid",
        "start_time": "14:00",
        "end_time": "14:50",
        "duration_minutes": 50,
        "subject": "Tutorial",
        "type": "Practical",
        "class_name": "10",
        "section": "A",
        "class_section": "10-A"
      }
    ]
  }
}
```

---

### GET /api/v1/teacher/timetable/today/

Get today's schedule (same structure as single-day from above, convenience endpoint).

**Query Params:** `?date=2026-05-23` (optional, defaults to today)

**Response: 200**
```json
{
  "date": "2026-05-23",
  "day": "Tuesday",
  "stats": {
    "total_classes_today": 5,
    "practical_sessions_today": 1,
    "free_periods_today": 1
  },
  "schedule": [
    {
      "id": "uuid",
      "start_time": "08:00",
      "end_time": "08:50",
      "duration_minutes": 50,
      "subject": "Mathematics",
      "type": "Lecture",
      "class_name": "11",
      "section": "A",
      "class_section": "11-A"
    },
    {
      "id": "uuid",
      "start_time": "09:00",
      "end_time": "09:50",
      "duration_minutes": 50,
      "subject": "Mathematics",
      "type": "Lecture",
      "class_name": "10",
      "section": "A",
      "class_section": "10-A"
    },
    {
      "id": "uuid",
      "start_time": "10:00",
      "end_time": "10:50",
      "duration_minutes": 50,
      "subject": "Mathematics",
      "type": "Lecture",
      "class_name": "10",
      "section": "B",
      "class_section": "10-B"
    },
    {
      "id": "uuid",
      "start_time": "11:00",
      "end_time": "11:00",
      "duration_minutes": 0,
      "subject": null,
      "type": "Free",
      "class_section": null
    },
    {
      "id": "uuid",
      "start_time": "12:00",
      "end_time": "12:50",
      "duration_minutes": 50,
      "subject": null,
      "type": "Break",
      "class_section": null,
      "label": "Lunch Break"
    },
    {
      "id": "uuid",
      "start_time": "13:00",
      "end_time": "13:50",
      "duration_minutes": 50,
      "subject": "Mathematics",
      "type": "Lecture",
      "class_name": "11",
      "section": "A",
      "class_section": "11-A"
    },
    {
      "id": "uuid",
      "start_time": "14:00",
      "end_time": "14:50",
      "duration_minutes": 50,
      "subject": "Tutorial",
      "type": "Practical",
      "class_name": "10",
      "section": "A",
      "class_section": "10-A"
    }
  ]
}
```

---

## 11. Leaves

> **3 tabs:** Leave Balance, Leave History, Upcoming / Planned

### GET /api/v1/teacher/leaves/balance/

Get the authenticated teacher's leave balance with per-type breakdown and overall summary.

**Query Params:** `?academic_year=2025-2026`

**Response: 200**
```json
{
  "academic_year": "2025-2026",
  "balances": [
    {
      "leave_type": "Casual Leave",
      "total_allocated": 12,
      "available": 9,
      "used": 3,
      "pending": 1
    },
    {
      "leave_type": "Sick Leave",
      "total_allocated": 15,
      "available": 13,
      "used": 2,
      "pending": 0
    },
    {
      "leave_type": "Earned Leave",
      "total_allocated": 20,
      "available": 12,
      "used": 8,
      "pending": 0
    }
  ],
  "summary": {
    "total_leaves": 47,
    "available": 33,
    "used": 13,
    "pending": 1
  }
}
```

---

### GET /api/v1/teacher/leaves/

List leave history for the authenticated teacher.

**Query Params:** `?status=Approved&leave_type=Casual Leave&academic_year=2025-2026&page=1&page_size=20`

**Response: 200**
```json
{
  "count": 7,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "lv1a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
      "leave_type": "Casual Leave",
      "from_date": "2026-05-26",
      "to_date": "2026-05-26",
      "duration_days": 1,
      "reason": "Personal work - bank visit",
      "status": "Pending",
      "applied_on": "2026-05-23T09:00:00Z",
      "approved_by": null,
      "approved_on": null,
      "remarks": null,
      "metadata": {}
    },
    {
      "id": "lv2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
      "leave_type": "Casual Leave",
      "from_date": "2026-05-12",
      "to_date": "2026-05-13",
      "duration_days": 2,
      "reason": "Family function",
      "status": "Approved",
      "applied_on": "2026-05-08T10:00:00Z",
      "approved_by": "Admin User",
      "approved_on": "2026-05-09T11:00:00Z",
      "remarks": "Approved. Please ensure pending assignments are covered.",
      "metadata": {}
    },
    {
      "id": "lv3c4d5e-6f7a-8b9c-0d1e-2f3a4b5c6d7e",
      "leave_type": "Sick Leave",
      "from_date": "2026-04-20",
      "to_date": "2026-04-21",
      "duration_days": 2,
      "reason": "Fever and body ache",
      "status": "Approved",
      "applied_on": "2026-04-20T07:30:00Z",
      "approved_by": "Admin User",
      "approved_on": "2026-04-20T08:00:00Z",
      "remarks": "Get well soon. Medical certificate submitted.",
      "metadata": {}
    },
    {
      "id": "lv4d5e6f-7a8b-9c0d-1e2f-3a4b5c6d7e8f",
      "leave_type": "Earned Leave",
      "from_date": "2026-03-25",
      "to_date": "2026-03-27",
      "duration_days": 3,
      "reason": "Travel plans - family vacation",
      "status": "Approved",
      "applied_on": "2026-03-15T09:00:00Z",
      "approved_by": "Admin User",
      "approved_on": "2026-03-16T10:30:00Z",
      "remarks": "Approved.",
      "metadata": {}
    }
  ]
}
```

---

### GET /api/v1/teacher/leaves/upcoming/

Get upcoming/planned leaves (approved or pending, with future dates). This is the "Upcoming / Planned" tab.

**Response: 200**
```json
{
  "results": [
    {
      "id": "uuid",
      "leave_type": "Casual Leave",
      "from_date": "2026-05-25",
      "to_date": "2026-05-27",
      "duration_days": 3,
      "reason": "Personal family event",
      "status": "Approved",
      "applied_on": "2026-05-10",
      "approved_by": "Admin User",
      "can_cancel": false
    },
    {
      "id": "uuid",
      "leave_type": "Casual Leave",
      "from_date": "2026-06-16",
      "to_date": "2026-06-16",
      "duration_days": 1,
      "reason": "Doctor appointment",
      "status": "Pending",
      "applied_on": "2026-05-20",
      "approved_by": null,
      "can_cancel": true
    }
  ]
}
```

---

### POST /api/v1/teacher/leaves/

Apply for leave.

**Request:**
```json
{
  "leave_type": "Casual Leave",
  "from_date": "2026-05-28",
  "to_date": "2026-05-28",
  "reason": "Need to attend a family function in the afternoon",
  "academic_year": "2025-2026",
  "metadata": {}
}
```

**Response: 201**
```json
{
  "id": "lv5e6f7a-8b9c-0d1e-2f3a-4b5c6d7e8f9a",
  "leave_type": "Casual Leave",
  "from_date": "2026-05-28",
  "to_date": "2026-05-28",
  "duration_days": 1,
  "reason": "Need to attend a family function in the afternoon",
  "status": "Pending",
  "applied_on": "2026-05-23T16:00:00Z",
  "approved_by": null,
  "approved_on": null,
  "remarks": null,
  "academic_year": "2025-2026",
  "metadata": {}
}
```

**Response: 400**
```json
{
  "error": "Insufficient leave balance",
  "code": "INSUFFICIENT_BALANCE",
  "details": {
    "leave_type": "Casual Leave",
    "remaining": 0,
    "requested": 1
  }
}
```

**Response: 409**
```json
{
  "error": "You already have a leave application for overlapping dates",
  "code": "LEAVE_OVERLAP"
}
```

---

### GET /api/v1/teacher/leaves/:id/

Get details of a specific leave application.

**Response: 200**
```json
{
  "id": "lv2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
  "leave_type": "Casual Leave",
  "from_date": "2026-05-12",
  "to_date": "2026-05-13",
  "duration_days": 2,
  "reason": "Family function",
  "status": "Approved",
  "applied_on": "2026-05-08T10:00:00Z",
  "approved_by": "Admin User",
  "approved_on": "2026-05-09T11:00:00Z",
  "remarks": "Approved. Please ensure pending assignments are covered.",
  "substitute_teacher": "Rahul Verma",
  "academic_year": "2025-2026",
  "metadata": {}
}
```

---

### DELETE /api/v1/teacher/leaves/:id/

Cancel a pending leave application. Only works if status is "Pending".

**Response: 200**
```json
{
  "message": "Leave application cancelled successfully",
  "id": "lv1a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
  "status": "Cancelled",
  "cancelled_on": "2026-05-23T17:00:00Z"
}
```

**Response: 400**
```json
{
  "error": "Cannot cancel a leave that has already been approved or rejected",
  "code": "LEAVE_NOT_CANCELLABLE"
}
```

---

## Common Error Responses

### 401 Unauthorized

Returned when the auth token is missing or expired.

```json
{
  "error": "Authentication required",
  "code": "UNAUTHORIZED"
}
```

### 403 Forbidden

Returned when the teacher tries to access resources outside their scope.

```json
{
  "error": "You do not have permission to access this resource",
  "code": "FORBIDDEN"
}
```

### 404 Not Found

Returned when the requested resource does not exist.

```json
{
  "error": "Resource not found",
  "code": "NOT_FOUND"
}
```

### 500 Internal Server Error

```json
{
  "error": "An unexpected error occurred. Please try again later.",
  "code": "INTERNAL_ERROR"
}
```
