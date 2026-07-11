# School ERP Backend - Student Portal: Requests & Responses

> Detailed request/response documentation for all Student Portal API endpoints.
> For quick endpoint reference, see [endpoints.md](./endpoints.md).

---

## 1. Authentication (Shared)

> Auth endpoints are identical to the Admin/Teacher modules. The only difference is the `role` field in responses will be `"student"`.

### POST /api/v1/auth/login/

Login with email and password. Sets httpOnly cookies for access + refresh tokens.

**Request:**
```json
{
  "email": "arjun.mehta@student.com",
  "password": "password123"
}
```

**Response: 200**
```json
{
  "user": {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "email": "arjun.mehta@student.com",
    "full_name": "Arjun Mehta",
    "role": "student",
    "school_code": "SCH001",
    "avatar_url": null,
    "roll_number": "STU2024015",
    "class_name": "10",
    "section": "A",
    "class_section": "10-A"
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
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "email": "arjun.mehta@student.com",
  "full_name": "Arjun Mehta",
  "role": "student",
  "school_code": "SCH001",
  "avatar_url": null,
  "phone": "+91 9876501234",
  "roll_number": "STU2024015",
  "class_name": "10",
  "section": "A",
  "class_section": "10-A",
  "admission_date": "2022-04-01",
  "academic_year": "2025-2026",
  "student_type": "Day Scholar",
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
  "email": "arjun.mehta@student.com"
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

### GET /api/v1/student/dashboard/stats/

Get KPI summary cards for the student dashboard.

**Query Params:** `?academic_year=2025-2026` (optional, defaults to current)

**Response: 200**
```json
{
  "attendance": {
    "percentage": 66.7,
    "present_days": 2,
    "absent_days": 1,
    "total_days": 3,
    "label": "2/3 days"
  },
  "rank_score": {
    "percentage": 83.5,
    "grade": "A",
    "label": "83.5%"
  },
  "assignments": {
    "completed": 0,
    "total": 3,
    "pending": 3,
    "overdue": 0,
    "label": "3 pending"
  },
  "fee_status": {
    "total_fees": 85000,
    "paid_amount": 60000,
    "due_amount": 25000,
    "pending_count": 3,
    "late_fines": 500,
    "currency": "INR",
    "status": "Pending",
    "label": "3 pending"
  },
  "academic_year": "2025-2026",
  "metadata": {}
}
```

---

### GET /api/v1/student/dashboard/today-schedule/

Get today's class schedule for the authenticated student.

**Query Params:** `?date=2026-05-21` (optional, defaults to today)

**Response: 200**
```json
{
  "date": "2026-05-21",
  "day": "Thursday",
  "class_section": "10-A",
  "schedule": [
    {
      "id": "uuid",
      "start_time": "08:00",
      "end_time": "08:45",
      "subject": "Mathematics",
      "teacher": "Dr. Jane Smith",
      "type": "class"
    },
    {
      "id": "uuid",
      "start_time": "09:00",
      "end_time": "09:45",
      "subject": "English",
      "teacher": "Ms. Emily Davis",
      "type": "class"
    },
    {
      "id": "uuid",
      "start_time": "10:00",
      "end_time": "10:45",
      "subject": "Physics",
      "teacher": "Prof. Robert Johnson",
      "type": "class"
    },
    {
      "id": "uuid",
      "start_time": "11:00",
      "end_time": "11:45",
      "subject": "Chemistry",
      "teacher": "Mr. William Anderson",
      "type": "class"
    },
    {
      "id": "uuid",
      "start_time": "12:00",
      "end_time": "12:45",
      "subject": "Hindi",
      "teacher": "Mrs. Priya Sharma",
      "type": "class"
    },
    {
      "id": "uuid",
      "start_time": "13:30",
      "end_time": "14:15",
      "subject": "Computer",
      "teacher": "Mr. Rajesh Kumar",
      "type": "class"
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/dashboard/pending-assignments/

Get the student's pending assignments for dashboard display.

**Query Params:** `?limit=5` (optional, defaults to 5)

**Response: 200**
```json
{
  "results": [
    {
      "id": "a1b2c3d4-5678-9abc-def0-123456789abc",
      "title": "Quadratic Equations Problem Set",
      "subject": "Mathematics",
      "due_date": "2026-04-15",
      "days_left": 2,
      "max_marks": 25,
      "status": "pending",
      "metadata": {}
    },
    {
      "id": "c3d4e5f6-789a-bcde-f012-3456789abcde",
      "title": "Newton's Laws Essay",
      "subject": "Physics",
      "due_date": "2026-04-23",
      "days_left": 10,
      "max_marks": 30,
      "status": "pending",
      "metadata": {}
    },
    {
      "id": "d4e5f6a7-89ab-cdef-0123-456789abcde0",
      "title": "Shakespeare Analysis",
      "subject": "English",
      "due_date": "2026-04-25",
      "days_left": 12,
      "max_marks": 20,
      "status": "pending",
      "metadata": {}
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/dashboard/upcoming-exams/

Get upcoming exams for the student's class.

**Query Params:** `?limit=5` (optional, defaults to 5)

**Response: 200**
```json
{
  "results": [
    {
      "id": "d4e5f6a7-89ab-cdef-0123-456789abcdef",
      "name": "Unit Test 3",
      "date": "2026-06-05",
      "exam_type": "Unit Test",
      "subjects_count": 5
    },
    {
      "id": "e5f6a7b8-9abc-def0-1234-56789abcdef0",
      "name": "Mid-Term Examination",
      "date": "2026-06-15",
      "exam_type": "Mid-Term",
      "subjects_count": 9
    },
    {
      "id": "f6a7b8c9-abcd-ef01-2345-6789abcdef01",
      "name": "Physics Practical",
      "date": "2026-06-02",
      "exam_type": "Practical",
      "subjects_count": 1
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/dashboard/subject-attendance/

Get per-subject attendance breakdown with color coding.

**Query Params:** `?academic_year=2025-2026` (optional, defaults to current)

**Response: 200**
```json
{
  "academic_year": "2025-2026",
  "threshold": 75,
  "subjects": [
    {
      "subject": "Mathematics",
      "percentage": 95,
      "present": 19,
      "total": 20,
      "color": "green"
    },
    {
      "subject": "English",
      "percentage": 88,
      "present": 15,
      "total": 17,
      "color": "green"
    },
    {
      "subject": "Physics",
      "percentage": 80,
      "present": 16,
      "total": 20,
      "color": "green"
    },
    {
      "subject": "Chemistry",
      "percentage": 92,
      "present": 12,
      "total": 13,
      "color": "green"
    },
    {
      "subject": "Biology",
      "percentage": 72,
      "present": 13,
      "total": 18,
      "color": "red"
    },
    {
      "subject": "Hindi",
      "percentage": 94,
      "present": 15,
      "total": 16,
      "color": "green"
    },
    {
      "subject": "Computer",
      "percentage": 100,
      "present": 10,
      "total": 10,
      "color": "green"
    },
    {
      "subject": "Art",
      "percentage": 90,
      "present": 9,
      "total": 10,
      "color": "green"
    },
    {
      "subject": "PE",
      "percentage": 78,
      "present": 7,
      "total": 9,
      "color": "green"
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/dashboard/recent-results/

Get the most recent exam results for the student.

**Query Params:** `?limit=3` (optional, defaults to 3)

**Response: 200**
```json
{
  "results": [
    {
      "id": "11111111-aaaa-bbbb-cccc-111111111111",
      "exam_name": "Unit Test 2",
      "marks_obtained": 412,
      "total_marks": 500,
      "percentage": 82.4,
      "grade": "A",
      "date": "2026-04-15"
    },
    {
      "id": "22222222-bbbb-cccc-dddd-222222222222",
      "exam_name": "Quarterly Exam",
      "marks_obtained": 438,
      "total_marks": 500,
      "percentage": 87.6,
      "grade": "A+",
      "date": "2026-03-01"
    },
    {
      "id": "33333333-cccc-dddd-eeee-333333333333",
      "exam_name": "Unit Test 1",
      "marks_obtained": 198,
      "total_marks": 250,
      "percentage": 79.2,
      "grade": "B+",
      "date": "2026-02-10"
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/dashboard/announcements/

Get recent school announcements.

**Query Params:** `?limit=3` (optional, defaults to 3)

**Response: 200**
```json
{
  "results": [
    {
      "id": "44444444-dddd-eeee-ffff-444444444444",
      "title": "Annual Sports Day - Registration Open",
      "date": "2026-05-20",
      "source": "Admin",
      "excerpt": "Register for events by May 25th. Track, field, and team events available."
    },
    {
      "id": "55555555-eeee-ffff-aaaa-555555555555",
      "title": "New Books Added to Library",
      "date": "2026-05-18",
      "source": "Library",
      "excerpt": "50 new books added in Science and Literature sections. Visit the library to explore."
    },
    {
      "id": "66666666-ffff-aaaa-bbbb-666666666666",
      "title": "Parent-Teacher Meeting Schedule",
      "date": "2026-05-15",
      "source": "Admin",
      "excerpt": "PTM scheduled for June 1st. All parents are requested to attend."
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/dashboard/notifications/

Get recent notifications for the student dashboard.

**Query Params:** `?limit=5` (optional, defaults to 5)

**Response: 200**
```json
{
  "results": [
    {
      "id": "notif-11111111-aaaa-bbbb-cccc-111111111111",
      "type": "assignment",
      "title": "New Assignment Posted",
      "message": "The Mathematics assignment has been posted. Due date: April 15, 2026.",
      "timestamp": "2026-04-10T09:00:00Z",
      "is_read": false,
      "action_url": "/student/assignments/a1b2c3d4-5678-9abc-def0-123456789abc/",
      "metadata": {}
    },
    {
      "id": "notif-22222222-bbbb-cccc-dddd-222222222222",
      "type": "fee",
      "title": "Fee Payment Reminder",
      "message": "Your tuition fee payment is due on April 15. Please make the payment to avoid late fees.",
      "timestamp": "2026-04-08T08:00:00Z",
      "is_read": false,
      "action_url": "/student/fees/",
      "metadata": {}
    },
    {
      "id": "notif-33333333-cccc-dddd-eeee-333333333333",
      "type": "library",
      "title": "Library Book Overdue",
      "message": "Your book \"Advanced Mathematics\" is overdue. Please return it to avoid fines.",
      "timestamp": "2026-04-05T08:00:00Z",
      "is_read": true,
      "action_url": "/student/library/",
      "metadata": {}
    }
  ],
  "unread_count": 2,
  "metadata": {}
}
```

---

### GET /api/v1/student/dashboard/fee-status/

Get fee status overview for dashboard display.

**Query Params:** `?academic_year=2025-2026` (optional, defaults to current)

**Response: 200**
```json
{
  "academic_year": "2025-2026",
  "upcoming_dues": [
    {
      "id": "due-11111111-aaaa-bbbb-cccc-111111111111",
      "fee_type": "Tuition Fee",
      "fee_category": "academic",
      "amount": 25000,
      "currency": "INR",
      "due_date": "2026-04-01",
      "status": "overdue",
      "is_overdue": true,
      "days_overdue": 22,
      "metadata": {}
    }
  ],
  "summary": {
    "total_fees": 85000,
    "paid": 60000,
    "pending": 25000,
    "late_fines": 500,
    "currency": "INR"
  },
  "metadata": {}
}
```

---

### GET /api/v1/student/dashboard/parent-meetings/

Get parent meeting history with attendance status for the dashboard.

**Query Params:** `?academic_year=2025-2026&limit=5` (both optional)

**Response: 200**
```json
{
  "academic_year": "2025-2026",
  "total_attended": 2,
  "total_meetings": 3,
  "results": [
    {
      "id": "meeting-11111111-aaaa-bbbb-cccc-111111111111",
      "title": "Parent Teacher Meeting",
      "date": "2026-04-15",
      "time": "09:00 - 13:00",
      "venue": "School Auditorium",
      "status": "attended",
      "conducted_by": "Dr. Jane Smith",
      "attended_by": "Mr. Vikram Mehta",
      "remarks": null,
      "metadata": {}
    },
    {
      "id": "meeting-22222222-bbbb-cccc-dddd-222222222222",
      "title": "Parent Teacher Meeting",
      "date": "2026-06-15",
      "time": "09:00 - 13:00",
      "venue": "School Auditorium",
      "status": "attended",
      "conducted_by": "Ms. Emily Davis",
      "attended_by": "Mr. Vikram Mehta",
      "remarks": null,
      "metadata": {}
    },
    {
      "id": "meeting-33333333-cccc-dddd-eeee-333333333333",
      "title": "Special Meeting",
      "date": "2025-10-15",
      "time": "10:00 - 12:00",
      "venue": "Conference Room",
      "status": "not_attended",
      "conducted_by": "Dr. Jane Smith",
      "attended_by": null,
      "remarks": "Parent was unavailable due to travel",
      "metadata": {}
    }
  ],
  "metadata": {}
}
```

---

## 3. Timetable

### GET /api/v1/student/timetable/

Get the weekly timetable grid for the student's class, including the weekly overview grid and subject summary.

**Query Params:** `?academic_year=2025-2026` (optional, defaults to current)

**Response: 200**
```json
{
  "class_info": {
    "class_name": "Class 10",
    "section": "Section A",
    "display_label": "Class 10 - Section A"
  },
  "academic_year": "2025-2026",
  "current_day": "Monday",
  "is_today_holiday": false,
  "total_periods": 8,
  "periods": [
    { "id": "uuid", "start_time": "08:00", "end_time": "08:45", "duration_minutes": 45 },
    { "id": "uuid", "start_time": "08:59", "end_time": "09:35", "duration_minutes": 45 },
    { "id": "uuid", "start_time": "09:45", "end_time": "10:28", "duration_minutes": 45 },
    { "id": "uuid", "start_time": "10:45", "end_time": "11:30", "duration_minutes": 45 },
    { "id": "uuid", "start_time": "11:45", "end_time": "12:30", "duration_minutes": 45 },
    { "id": "uuid", "start_time": "13:00", "end_time": "13:45", "duration_minutes": 45 },
    { "id": "uuid", "start_time": "13:50", "end_time": "14:35", "duration_minutes": 45 },
    { "id": "uuid", "start_time": "14:40", "end_time": "15:25", "duration_minutes": 45 }
  ],
  "timetable": {
    "Monday": [
      { "id": "uuid", "subject": "Mathematics", "teacher": "Dr. Jane Smith", "type": "class", "duration_minutes": 45 },
      { "id": "uuid", "subject": "Physics", "teacher": "Prof. Robert Johnson", "type": "lab", "duration_minutes": 45 },
      { "id": "uuid", "subject": "English", "teacher": "Ms. Emily Davis", "type": "class", "duration_minutes": 45 },
      { "id": "uuid", "subject": "Chemistry", "teacher": "Mr. William Anderson", "type": "lab", "duration_minutes": 45 },
      { "id": "uuid", "subject": null, "teacher": null, "type": "free", "duration_minutes": 45 },
      { "id": "uuid", "subject": null, "teacher": null, "type": "free", "duration_minutes": 45 },
      { "id": "uuid", "subject": null, "teacher": null, "type": "free", "duration_minutes": 45 },
      { "id": "uuid", "subject": null, "teacher": null, "type": "free", "duration_minutes": 45 }
    ],
    "Tuesday": [
      { "id": "uuid", "subject": "English", "teacher": "Ms. Emily Davis", "type": "class", "duration_minutes": 45 },
      { "id": "uuid", "subject": "Mathematics", "teacher": "Dr. Jane Smith", "type": "class", "duration_minutes": 45 },
      { "id": "uuid", "subject": "Biology", "teacher": "Dr. Anita Verma", "type": "lab", "duration_minutes": 45 },
      { "id": "uuid", "subject": "Hindi", "teacher": "Mrs. Priya Sharma", "type": "class", "duration_minutes": 45 },
      { "id": "uuid", "subject": "Computer", "teacher": "Mr. Rajesh Kumar", "type": "lab", "duration_minutes": 45 },
      { "id": "uuid", "subject": "PE", "teacher": "Mr. Suresh Yadav", "type": "class", "duration_minutes": 45 },
      { "id": "uuid", "subject": null, "teacher": null, "type": "free", "duration_minutes": 45 },
      { "id": "uuid", "subject": null, "teacher": null, "type": "free", "duration_minutes": 45 }
    ],
    "Wednesday": [
      { "id": "uuid", "subject": "Physics", "teacher": "Prof. Robert Johnson", "type": "lab", "duration_minutes": 45 },
      { "id": "uuid", "subject": "Mathematics", "teacher": "Dr. Jane Smith", "type": "class", "duration_minutes": 45 },
      { "id": "uuid", "subject": "Hindi", "teacher": "Mrs. Priya Sharma", "type": "class", "duration_minutes": 45 },
      { "id": "uuid", "subject": "English", "teacher": "Ms. Emily Davis", "type": "class", "duration_minutes": 45 },
      { "id": "uuid", "subject": "Art", "teacher": "Ms. Kavita Nair", "type": "class", "duration_minutes": 45 },
      { "id": "uuid", "subject": null, "teacher": null, "type": "free", "duration_minutes": 45 },
      { "id": "uuid", "subject": null, "teacher": null, "type": "free", "duration_minutes": 45 },
      { "id": "uuid", "subject": null, "teacher": null, "type": "free", "duration_minutes": 45 }
    ],
    "Thursday": [
      { "id": "uuid", "subject": "Mathematics", "teacher": "Dr. Jane Smith", "type": "class", "duration_minutes": 45 },
      { "id": "uuid", "subject": "English", "teacher": "Ms. Emily Davis", "type": "class", "duration_minutes": 45 },
      { "id": "uuid", "subject": "Physics", "teacher": "Prof. Robert Johnson", "type": "lab", "duration_minutes": 45 },
      { "id": "uuid", "subject": "Chemistry", "teacher": "Mr. William Anderson", "type": "lab", "duration_minutes": 45 },
      { "id": "uuid", "subject": "Hindi", "teacher": "Mrs. Priya Sharma", "type": "class", "duration_minutes": 45 },
      { "id": "uuid", "subject": "Computer", "teacher": "Mr. Rajesh Kumar", "type": "lab", "duration_minutes": 45 },
      { "id": "uuid", "subject": null, "teacher": null, "type": "free", "duration_minutes": 45 },
      { "id": "uuid", "subject": null, "teacher": null, "type": "free", "duration_minutes": 45 }
    ],
    "Friday": [
      { "id": "uuid", "subject": "Chemistry", "teacher": "Mr. William Anderson", "type": "lab", "duration_minutes": 45 },
      { "id": "uuid", "subject": "Biology", "teacher": "Dr. Anita Verma", "type": "lab", "duration_minutes": 45 },
      { "id": "uuid", "subject": "Mathematics", "teacher": "Dr. Jane Smith", "type": "class", "duration_minutes": 45 },
      { "id": "uuid", "subject": "English", "teacher": "Ms. Emily Davis", "type": "class", "duration_minutes": 45 },
      { "id": "uuid", "subject": "Library", "teacher": "Ms. Deepa Iyer", "type": "class", "duration_minutes": 45 },
      { "id": "uuid", "subject": null, "teacher": null, "type": "free", "duration_minutes": 45 },
      { "id": "uuid", "subject": null, "teacher": null, "type": "free", "duration_minutes": 45 },
      { "id": "uuid", "subject": null, "teacher": null, "type": "free", "duration_minutes": 45 }
    ],
    "Saturday": [
      { "id": "uuid", "subject": "Biology", "teacher": "Dr. Anita Verma", "type": "lab", "duration_minutes": 45 },
      { "id": "uuid", "subject": "Hindi", "teacher": "Mrs. Priya Sharma", "type": "class", "duration_minutes": 45 },
      { "id": "uuid", "subject": "PE", "teacher": "Mr. Suresh Yadav", "type": "class", "duration_minutes": 45 },
      { "id": "uuid", "subject": "Art", "teacher": "Ms. Kavita Nair", "type": "class", "duration_minutes": 45 },
      { "id": "uuid", "subject": null, "teacher": null, "type": "free", "duration_minutes": 45 },
      { "id": "uuid", "subject": null, "teacher": null, "type": "free", "duration_minutes": 45 },
      { "id": "uuid", "subject": null, "teacher": null, "type": "free", "duration_minutes": 45 },
      { "id": "uuid", "subject": null, "teacher": null, "type": "free", "duration_minutes": 45 }
    ]
  },
  "subject_summary": [
    {
      "subject": "Mathematics",
      "teacher": "Dr. Jane Smith",
      "sessions_per_week": 3,
      "type": "class"
    },
    {
      "subject": "English",
      "teacher": "Ms. Emily Davis",
      "sessions_per_week": 3,
      "type": "class"
    },
    {
      "subject": "Physics",
      "teacher": "Prof. Robert Johnson",
      "sessions_per_week": 1,
      "type": "lab"
    },
    {
      "subject": "Chemistry",
      "teacher": "Mr. William Anderson",
      "sessions_per_week": 1,
      "type": "lab"
    },
    {
      "subject": "Biology",
      "teacher": "Dr. Anita Verma",
      "sessions_per_week": 2,
      "type": "lab"
    },
    {
      "subject": "Hindi",
      "teacher": "Mrs. Priya Sharma",
      "sessions_per_week": 2,
      "type": "class"
    },
    {
      "subject": "Computer",
      "teacher": "Mr. Rajesh Kumar",
      "sessions_per_week": 2,
      "type": "lab"
    },
    {
      "subject": "PE",
      "teacher": "Mr. Suresh Yadav",
      "sessions_per_week": 1,
      "type": "class"
    },
    {
      "subject": "Art",
      "teacher": "Ms. Kavita Nair",
      "sessions_per_week": 1,
      "type": "class"
    },
    {
      "subject": "Library",
      "teacher": "Ms. Deepa Iyer",
      "sessions_per_week": 1,
      "type": "class"
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/timetable/day/

Get the schedule for a specific day with detailed period cards. Defaults to today.

**Query Params:** `?date=2026-05-19` (optional, defaults to today)

**Response: 200**
```json
{
  "class_info": {
    "class_name": "Class 10",
    "section": "Section A",
    "display_label": "Class 10 - Section A"
  },
  "date": "2026-05-19",
  "day": "Monday",
  "is_today": true,
  "is_holiday": false,
  "periods": [
    {
      "id": "uuid",
      "subject": "Mathematics",
      "teacher": "Dr. Jane Smith",
      "start_time": "08:00",
      "end_time": "08:45",
      "duration_minutes": 45,
      "type": "class"
    },
    {
      "id": "uuid",
      "subject": "Physics",
      "teacher": "Prof. Robert Johnson",
      "start_time": "08:59",
      "end_time": "09:35",
      "duration_minutes": 45,
      "type": "lab"
    },
    {
      "id": "uuid",
      "subject": "English",
      "teacher": "Ms. Emily Davis",
      "start_time": "09:45",
      "end_time": "10:28",
      "duration_minutes": 45,
      "type": "class"
    },
    {
      "id": "uuid",
      "subject": "Chemistry",
      "teacher": "Mr. William Anderson",
      "start_time": "10:45",
      "end_time": "11:30",
      "duration_minutes": 45,
      "type": "lab"
    }
  ],
  "metadata": {}
}
```

---

## 4. Attendance

### GET /api/v1/student/attendance/

Get overall attendance summary with KPI stats, distribution chart data, subject-wise breakdown, recent records, and inline warning.

**Query Params:** `?academic_year=2025-2026&month=2026-04` (both optional, month filters stats and recent records)

**Response: 200**
```json
{
  "academic_year": "2025-2026",
  "overall": {
    "percentage": 66.7,
    "present_days": 2,
    "absent_days": 1,
    "late_days": 0,
    "excused_days": 0,
    "total_days": 3,
    "threshold": 75,
    "status": "below_threshold"
  },
  "stats": {
    "present": 2,
    "absent": 1,
    "late": 0,
    "excused": 0
  },
  "distribution": {
    "present": 2,
    "absent": 1,
    "late": 0,
    "excused": 0
  },
  "warning": {
    "active": true,
    "type": "low_attendance",
    "message": "Your attendance is below 75%. You need to maintain at least 75% attendance to be eligible for exams.",
    "severity": "critical"
  },
  "subject_wise": [
    {
      "subject": "Mathematics",
      "percentage": 95,
      "present": 19,
      "total": 20,
      "color": "green",
      "metadata": {}
    },
    {
      "subject": "English",
      "percentage": 88,
      "present": 15,
      "total": 17,
      "color": "green",
      "metadata": {}
    },
    {
      "subject": "Physics",
      "percentage": 80,
      "present": 16,
      "total": 20,
      "color": "green",
      "metadata": {}
    },
    {
      "subject": "Chemistry",
      "percentage": 92,
      "present": 12,
      "total": 13,
      "color": "green",
      "metadata": {}
    },
    {
      "subject": "Biology",
      "percentage": 72,
      "present": 13,
      "total": 18,
      "color": "red",
      "metadata": {}
    },
    {
      "subject": "Hindi",
      "percentage": 94,
      "present": 15,
      "total": 16,
      "color": "green",
      "metadata": {}
    },
    {
      "subject": "Computer",
      "percentage": 100,
      "present": 10,
      "total": 10,
      "color": "green",
      "metadata": {}
    },
    {
      "subject": "Art",
      "percentage": 90,
      "present": 9,
      "total": 10,
      "color": "green",
      "metadata": {}
    },
    {
      "subject": "PE",
      "percentage": 78,
      "present": 7,
      "total": 9,
      "color": "green",
      "metadata": {}
    }
  ],
  "recent_records": [
    {
      "date": "2026-04-05",
      "subject": "Mathematics",
      "status": "present",
      "period": 1,
      "metadata": {}
    },
    {
      "date": "2026-04-06",
      "subject": "Mathematics",
      "status": "present",
      "period": 1,
      "metadata": {}
    },
    {
      "date": "2026-04-07",
      "subject": "Mathematics",
      "status": "present",
      "period": 1,
      "metadata": {}
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/attendance/history/

Get detailed attendance history (paginated, filterable).

**Query Params:** `?page=1&page_size=20&subject=Mathematics&month=2026-04&status=absent`

**Response: 200**
```json
{
  "count": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3,
  "filters": {
    "subject": "Mathematics",
    "month": "2026-04",
    "status": "absent"
  },
  "results": [
    {
      "id": "a1111111-1111-1111-1111-111111111111",
      "date": "2026-04-20",
      "subject": "Mathematics",
      "period": 1,
      "status": "absent",
      "marked_by": "Dr. Jane Smith",
      "remarks": null,
      "metadata": {}
    },
    {
      "id": "a2222222-2222-2222-2222-222222222222",
      "date": "2026-04-15",
      "subject": "Mathematics",
      "period": 1,
      "status": "absent",
      "marked_by": "Dr. Jane Smith",
      "remarks": "Medical leave",
      "metadata": {}
    },
    {
      "id": "a3333333-3333-3333-3333-333333333333",
      "date": "2026-04-08",
      "subject": "Mathematics",
      "period": 1,
      "status": "present",
      "marked_by": "Dr. Jane Smith",
      "remarks": null,
      "metadata": {}
    },
    {
      "id": "a4444444-4444-4444-4444-444444444444",
      "date": "2026-04-06",
      "subject": "Mathematics",
      "period": 1,
      "status": "present",
      "marked_by": "Dr. Jane Smith",
      "remarks": null,
      "metadata": {}
    },
    {
      "id": "a5555555-5555-5555-5555-555555555555",
      "date": "2026-04-01",
      "subject": "Mathematics",
      "period": 1,
      "status": "present",
      "marked_by": "Dr. Jane Smith",
      "remarks": null,
      "metadata": {}
    }
  ],
  "metadata": {}
}
```

**Response: 400**
```json
{
  "error": "Invalid month format. Use YYYY-MM.",
  "code": "VALIDATION_ERROR"
}
```

---

### GET /api/v1/student/attendance/warnings/

Get attendance warnings and compliance status.

**Query Params:** `?academic_year=2025-2026` (optional, defaults to current)

**Response: 200**
```json
{
  "academic_year": "2025-2026",
  "threshold": 75,
  "current_percentage": 66.7,
  "status": "below_threshold",
  "warnings": [
    {
      "id": "warn-11111111-aaaa-bbbb-cccc-111111111111",
      "type": "low_attendance",
      "severity": "critical",
      "message": "Your attendance is below 75%. You need to maintain at least 75% attendance to be eligible for exams.",
      "issued_date": "2026-04-01",
      "active": true,
      "acknowledged": false,
      "metadata": {}
    }
  ],
  "subjects_at_risk": [
    {
      "subject": "Biology",
      "percentage": 72,
      "present": 13,
      "total": 18,
      "deficit": 1,
      "message": "1 more absence will drop you below 70%",
      "metadata": {}
    }
  ],
  "metadata": {}
}
```

---

## 5. Assignments

### GET /api/v1/student/assignments/

List assignments with summary and filtering.

**Query Params:** `?page=1&page_size=20&status=pending&subject=Mathematics&academic_year=2025-2026`

**Response: 200**
```json
{
  "count": 14,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "summary": {
    "total": 14,
    "pending": 3,
    "overdue": 3,
    "submitted": 3,
    "graded": 6,
    "late": 2
  },
  "results": [
    {
      "id": "a1b2c3d4-5678-9abc-def0-123456789abc",
      "title": "Quadratic Equations Problem Set",
      "subject": "Mathematics",
      "teacher": "Dr. Jane Smith",
      "description": "Solve all problems from Chapter 4 - Quadratic Equations",
      "assigned_date": "2026-04-01",
      "due_date": "2026-04-15",
      "max_marks": 50,
      "marks_obtained": null,
      "status": "pending",
      "is_overdue": true,
      "metadata": {}
    },
    {
      "id": "b2c3d4e5-6789-abcd-ef01-23456789abcd",
      "title": "Newton's Laws Essay",
      "subject": "Physics",
      "teacher": "Prof. Robert Johnson",
      "description": "Write a detailed essay on Newton's Three Laws of Motion with real-world examples",
      "assigned_date": "2026-04-05",
      "due_date": "2026-04-20",
      "max_marks": 30,
      "marks_obtained": null,
      "status": "pending",
      "is_overdue": true,
      "metadata": {}
    },
    {
      "id": "f6a7b8c9-abcd-ef01-2345-6789abcdef01",
      "title": "Shakespeare Analysis",
      "subject": "English",
      "teacher": "Ms. Emily Davis",
      "description": "Analysis on Romeo and Juliet - Act 3",
      "assigned_date": "2026-04-10",
      "due_date": "2026-04-25",
      "max_marks": 40,
      "marks_obtained": null,
      "status": "pending",
      "is_overdue": true,
      "metadata": {}
    },
    {
      "id": "d4e5f6a7-89ab-cdef-0123-456789abcdef",
      "title": "Periodic Table Worksheet",
      "subject": "Chemistry",
      "teacher": "Mr. William Anderson",
      "description": "Complete the periodic table worksheet",
      "assigned_date": "2026-05-10",
      "due_date": "2026-05-18",
      "max_marks": 20,
      "marks_obtained": null,
      "status": "submitted",
      "is_overdue": false,
      "metadata": {}
    },
    {
      "id": "e5f6a7b8-9abc-def0-1234-56789abcdef0",
      "title": "Trigonometry Problem Set",
      "subject": "Mathematics",
      "teacher": "Dr. Jane Smith",
      "description": "Solve all trigonometry problems",
      "assigned_date": "2026-05-01",
      "due_date": "2026-05-10",
      "max_marks": 30,
      "marks_obtained": 27,
      "status": "graded",
      "is_overdue": false,
      "metadata": {}
    },
    {
      "id": "11aabb22-ccdd-eeff-1122-334455667788",
      "title": "Light and Optics Lab Report",
      "subject": "Physics",
      "teacher": "Prof. Robert Johnson",
      "description": "Lab report for light and optics experiment",
      "assigned_date": "2026-04-20",
      "due_date": "2026-04-30",
      "max_marks": 25,
      "marks_obtained": 18,
      "status": "late",
      "is_overdue": false,
      "metadata": {}
    }
  ]
}
```

---

### GET /api/v1/student/assignments/:id/

Get detailed assignment information.

**Response: 200**
```json
{
  "id": "a1b2c3d4-5678-9abc-def0-123456789abc",
  "title": "Quadratic Equations Practice Set",
  "subject": "Mathematics",
  "teacher": "Dr. Jane Smith",
  "description": "Solve the following 10 problems on quadratic equations. Show complete working for each problem. Use the quadratic formula where applicable and verify roots by substitution.",
  "assigned_date": "2026-05-15",
  "due_date": "2026-05-23",
  "max_marks": 25,
  "marks_obtained": null,
  "status": "pending",
  "is_overdue": false,
  "submission_status": "not_submitted",
  "attachments": [
    {
      "id": "att-001",
      "filename": "quadratic_equations_worksheet.pdf",
      "url": "/api/v1/student/assignments/a1b2c3d4-5678-9abc-def0-123456789abc/attachment/att-001/",
      "size_bytes": 245760,
      "type": "application/pdf"
    }
  ],
  "instructions": "Submit as PDF. Handwritten solutions are acceptable if scanned clearly.",
  "class_section": "10-A",
  "academic_year": "2025-2026",
  "created_at": "2026-05-15T09:00:00Z",
  "updated_at": "2026-05-15T09:00:00Z",
  "metadata": {}
}
```

**Response: 404**
```json
{
  "error": "Assignment not found",
  "code": "NOT_FOUND"
}
```

---

### POST /api/v1/student/assignments/:id/submit/

Submit an assignment. Multipart form data with comments and files.

**Request:** `Content-Type: multipart/form-data`
```json
{
  "comments": "Completed all 10 problems. Used the quadratic formula for questions 7-10.",
  "files": ["quadratic_solutions.pdf"]
}
```

> **Constraints:**
> - Max file size: 10MB per file
> - Max files: 5
> - Allowed types: PDF, JPEG, PNG, DOC, DOCX

**Response: 201**
```json
{
  "id": "sub-11111111-aaaa-bbbb-cccc-111111111111",
  "assignment_id": "a1b2c3d4-5678-9abc-def0-123456789abc",
  "status": "submitted",
  "comments": "Completed all 10 problems. Used the quadratic formula for questions 7-10.",
  "files": [
    {
      "id": "file-001",
      "filename": "quadratic_solutions.pdf",
      "url": "/api/v1/student/assignments/a1b2c3d4-5678-9abc-def0-123456789abc/submission/files/file-001/",
      "size_bytes": 1048576,
      "type": "application/pdf",
      "uploaded_at": "2026-05-22T14:30:00Z"
    }
  ],
  "submitted_at": "2026-05-22T14:30:00Z",
  "is_late": false,
  "metadata": {}
}
```

**Response: 400**
```json
{
  "error": "File size exceeds maximum limit of 10MB",
  "code": "FILE_TOO_LARGE",
  "details": {
    "max_size_bytes": 10485760,
    "uploaded_size_bytes": 15728640,
    "filename": "large_file.pdf"
  }
}
```

**Response: 400 (Invalid file type)**
```json
{
  "error": "File type not allowed. Accepted: PDF, JPEG, PNG, DOC, DOCX",
  "code": "INVALID_FILE_TYPE",
  "details": {
    "filename": "solution.exe",
    "type": "application/x-msdownload"
  }
}
```

**Response: 400 (Too many files)**
```json
{
  "error": "Maximum 5 files allowed per submission",
  "code": "TOO_MANY_FILES",
  "details": {
    "max_files": 5,
    "uploaded_count": 7
  }
}
```

**Response: 409**
```json
{
  "error": "Assignment already submitted. Use resubmit endpoint if allowed.",
  "code": "ALREADY_SUBMITTED",
  "details": {
    "submitted_at": "2026-05-20T10:15:00Z"
  }
}
```

**Response: 403**
```json
{
  "error": "Assignment submission deadline has passed and late submission is not allowed",
  "code": "DEADLINE_PASSED"
}
```

---

### GET /api/v1/student/assignments/:id/submission/

View the student's own submission details including grade and feedback.

**Response: 200**
```json
{
  "id": "sub-22222222-bbbb-cccc-dddd-222222222222",
  "assignment_id": "e5f6a7b8-9abc-def0-1234-56789abcdef0",
  "assignment_title": "Trigonometry Problem Set",
  "subject": "Mathematics",
  "status": "graded",
  "comments": "Solved all problems with detailed working.",
  "files": [
    {
      "id": "file-002",
      "filename": "trigonometry_solutions.pdf",
      "url": "/api/v1/student/assignments/e5f6a7b8-9abc-def0-1234-56789abcdef0/submission/files/file-002/",
      "size_bytes": 2097152,
      "type": "application/pdf",
      "uploaded_at": "2026-05-08T16:45:00Z"
    }
  ],
  "submitted_at": "2026-05-08T16:45:00Z",
  "is_late": false,
  "grade": {
    "marks_obtained": 27,
    "max_marks": 30,
    "percentage": 90.0,
    "grade": "A+",
    "graded_by": "Dr. Jane Smith",
    "graded_at": "2026-05-12T10:30:00Z",
    "feedback": "Excellent work! Clear presentation and correct application of identities. Minor calculation error in Q8."
  },
  "metadata": {}
}
```

**Response: 404**
```json
{
  "error": "No submission found for this assignment",
  "code": "SUBMISSION_NOT_FOUND"
}
```

---

## 6. Results

### GET /api/v1/student/results/

Get overall results summary with performance trend, subject-wise performance bar chart, and radar chart data.

**Query Params:** `?academic_year=2025-2026&year=all&month=all&subject=all`

**Response: 200**
```json
{
  "academic_year": "2025-2026",
  "summary": {
    "average_score": 83.5,
    "highest_score": 93,
    "lowest_score": 68,
    "avg_rank": 2.7
  },
  "filters": {
    "year": ["All Years", "2024-2025", "2025-2026"],
    "month": ["All Months", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "subject": ["All Subjects", "Mathematics", "Physics", "English", "Chemistry"]
  },
  "performance_trend": [
    {
      "exam_name": "Unit Test 1",
      "exam_type": "Unit Test",
      "date": "2026-02-10",
      "percentage": 79.2,
      "subjects": {
        "Mathematics": 85,
        "Physics": 78,
        "English": 80,
        "Chemistry": 76
      }
    },
    {
      "exam_name": "Mid-Term",
      "exam_type": "Mid-Term",
      "date": "2026-03-01",
      "percentage": 87.6,
      "subjects": {
        "Mathematics": 85,
        "Physics": 78,
        "English": 90,
        "Chemistry": 82
      }
    },
    {
      "exam_name": "Unit Test 2",
      "exam_type": "Unit Test",
      "date": "2026-04-15",
      "percentage": 82.4,
      "subjects": {
        "Mathematics": 85,
        "Physics": 78,
        "English": 80,
        "Chemistry": 82
      }
    },
    {
      "exam_name": "Quarterly",
      "exam_type": "Quarterly",
      "date": "2026-05-10",
      "percentage": 80.0,
      "subjects": {
        "Mathematics": 85,
        "Physics": 78,
        "English": 80,
        "Chemistry": 76
      }
    }
  ],
  "subject_wise_performance": [
    {
      "subject": "Physics",
      "student_percentage": 79.0,
      "max_marks": 100
    },
    {
      "subject": "English",
      "student_percentage": 90.0,
      "max_marks": 100
    },
    {
      "subject": "Chemistry",
      "student_percentage": 82.0,
      "max_marks": 100
    },
    {
      "subject": "Physics",
      "student_percentage": 79.0,
      "max_marks": 100
    },
    {
      "subject": "English",
      "student_percentage": 90.0,
      "max_marks": 100
    },
    {
      "subject": "Mathematics",
      "student_percentage": 85.0,
      "max_marks": 100
    }
  ],
  "performance_radar": {
    "subjects": ["Physics", "Mathematics", "English", "Chemistry"],
    "student_scores": [79, 85, 90, 82],
    "max_marks": 100
  },
  "metadata": {}
}
```

---

### GET /api/v1/student/results/exam/:exam_id/

Get detailed result for a specific exam with subject-wise breakdown including per-subject rank.

**Response: 200**
```json
{
  "exam_id": "11111111-aaaa-bbbb-cccc-111111111111",
  "exam_name": "Mid-Term Examination",
  "exam_type": "Mid-Term",
  "date": "2026-03-15",
  "class_section": "10-A",
  "academic_year": "2025-2026",
  "total_marks_obtained": 336,
  "total_max_marks": 400,
  "overall_percentage": 83.8,
  "overall_grade": "A",
  "class_rank": 3,
  "total_students": 45,
  "subjects": [
    {
      "subject": "Mathematics",
      "marks_obtained": 85,
      "max_marks": 100,
      "percentage": 85.0,
      "grade": "A",
      "class_average": 72.0,
      "highest_in_class": 92,
      "rank": 3,
      "status": "pass",
      "pass_marks": 40
    },
    {
      "subject": "Physics",
      "marks_obtained": 79,
      "max_marks": 100,
      "percentage": 79.0,
      "grade": "B+",
      "class_average": 68.0,
      "highest_in_class": 88,
      "rank": 3,
      "status": "pass",
      "pass_marks": 40
    },
    {
      "subject": "English",
      "marks_obtained": 90,
      "max_marks": 100,
      "percentage": 90.0,
      "grade": "A+",
      "class_average": 74.0,
      "highest_in_class": 93,
      "rank": 1,
      "status": "pass",
      "pass_marks": 40
    },
    {
      "subject": "Chemistry",
      "marks_obtained": 82,
      "max_marks": 100,
      "percentage": 82.0,
      "grade": "A",
      "class_average": 70.0,
      "highest_in_class": 89,
      "rank": 3,
      "status": "pass",
      "pass_marks": 40
    }
  ],
  "metadata": {}
}
```

**Response: 404**
```json
{
  "error": "Exam result not found",
  "code": "NOT_FOUND"
}
```

---

### GET /api/v1/student/results/exams/

List all exams with results. Supports expandable subject-wise details with per-subject rank and leaderboard link.

**Query Params:** `?page=1&page_size=10&exam_type=Mid-Term&academic_year=2025-2026&month=03&subject=all`

**Response: 200**
```json
{
  "count": 4,
  "page": 1,
  "page_size": 10,
  "total_pages": 1,
  "results": [
    {
      "id": "11111111-aaaa-bbbb-cccc-111111111111",
      "exam_name": "Mid-Term Examination",
      "exam_type": "Mid-Term",
      "date": "2026-03-15",
      "total_marks_obtained": 336,
      "total_max_marks": 400,
      "percentage": 83.8,
      "grade": "A",
      "class_rank": 3,
      "total_students": 45,
      "subjects_count": 4,
      "subjects": [
        {
          "subject": "Mathematics",
          "marks_obtained": 85,
          "max_marks": 100,
          "percentage": 85.0,
          "grade": "A",
          "rank": 3,
          "status": "pass",
          "pass_marks": 40,
          "leaderboard_url": "/api/v1/student/results/exam/11111111-aaaa-bbbb-cccc-111111111111/leaderboard/?subject=Mathematics"
        },
        {
          "subject": "Physics",
          "marks_obtained": 79,
          "max_marks": 100,
          "percentage": 79.0,
          "grade": "B+",
          "rank": 3,
          "status": "pass",
          "pass_marks": 40,
          "leaderboard_url": "/api/v1/student/results/exam/11111111-aaaa-bbbb-cccc-111111111111/leaderboard/?subject=Physics"
        },
        {
          "subject": "English",
          "marks_obtained": 90,
          "max_marks": 100,
          "percentage": 90.0,
          "grade": "A+",
          "rank": 1,
          "status": "pass",
          "pass_marks": 40,
          "leaderboard_url": "/api/v1/student/results/exam/11111111-aaaa-bbbb-cccc-111111111111/leaderboard/?subject=English"
        },
        {
          "subject": "Chemistry",
          "marks_obtained": 82,
          "max_marks": 100,
          "percentage": 82.0,
          "grade": "A",
          "rank": 3,
          "status": "pass",
          "pass_marks": 40,
          "leaderboard_url": "/api/v1/student/results/exam/11111111-aaaa-bbbb-cccc-111111111111/leaderboard/?subject=Chemistry"
        }
      ],
      "metadata": {}
    },
    {
      "id": "22222222-bbbb-cccc-dddd-222222222222",
      "exam_name": "Quarterly Examination",
      "exam_type": "Quarterly",
      "date": "2026-04-20",
      "total_marks_obtained": 228,
      "total_max_marks": 300,
      "percentage": 76.0,
      "grade": "B+",
      "class_rank": 5,
      "total_students": 45,
      "subjects_count": 3,
      "subjects": [],
      "metadata": {}
    },
    {
      "id": "33333333-cccc-dddd-eeee-333333333333",
      "exam_name": "Annual Examination",
      "exam_type": "Annual",
      "date": "2026-05-10",
      "total_marks_obtained": 339,
      "total_max_marks": 400,
      "percentage": 84.8,
      "grade": "A",
      "class_rank": 2,
      "total_students": 45,
      "subjects_count": 4,
      "subjects": [],
      "metadata": {}
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/results/exam/:exam_id/leaderboard/

Get leaderboard for a specific exam, optionally filtered by subject. Shows top performers with podium display.

**Query Params:** `?subject=Mathematics`

**Response: 200**
```json
{
  "exam_id": "11111111-aaaa-bbbb-cccc-111111111111",
  "exam_name": "Mid-Term Examination",
  "subject": "Mathematics",
  "academic_year": "2025-2026",
  "student_rank": 2,
  "student_score": 85,
  "max_marks": 100,
  "percentile": 85.0,
  "top_performers": [
    {
      "rank": 1,
      "student_name": "Emma Wilson",
      "marks_obtained": 92,
      "max_marks": 100,
      "percentage": 92.0,
      "grade": "A+",
      "is_current_student": false
    },
    {
      "rank": 2,
      "student_name": "John Doe",
      "marks_obtained": 85,
      "max_marks": 100,
      "percentage": 85.0,
      "grade": "A",
      "is_current_student": true
    },
    {
      "rank": 3,
      "student_name": "Michael Brown",
      "marks_obtained": 79,
      "max_marks": 100,
      "percentage": 78.0,
      "grade": "B+",
      "is_current_student": false
    }
  ],
  "metadata": {}
}
```

**Response: 404**
```json
{
  "error": "Leaderboard not available for this exam",
  "code": "NOT_FOUND"
}
```

---

### GET /api/v1/student/results/download-report/

Download consolidated results report as PDF.

**Query Params:** `?academic_year=2025-2026&exam_id=11111111-aaaa-bbbb-cccc-111111111111` (exam_id optional; omit for full year report)

**Response: 200**
```json
{
  "download_url": "/api/v1/student/results/download-report/file/",
  "file_name": "Results_Report_John_Doe_2025-2026.pdf",
  "content_type": "application/pdf",
  "generated_at": "2026-05-23T10:30:00Z",
  "report_scope": "all_exams",
  "academic_year": "2025-2026",
  "metadata": {}
}
```

**Response: 404**
```json
{
  "error": "No results available to generate report",
  "code": "NO_DATA"
}
```

---

## 7. Exams

### GET /api/v1/student/exams/upcoming/

Get upcoming exams with schedule and hall ticket info.

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
      "id": "d4e5f6a7-89ab-cdef-0123-456789abcdef",
      "name": "Unit Test 3",
      "exam_type": "Unit Test",
      "start_date": "2026-06-05",
      "end_date": "2026-06-07",
      "time": "09:00 - 11:00",
      "venue": "Examination Hall A",
      "duration_minutes": 120,
      "subjects": ["Mathematics", "English", "Physics", "Chemistry", "Biology"],
      "hall_ticket_available": true,
      "hall_ticket_url": "/api/v1/student/exams/d4e5f6a7-89ab-cdef-0123-456789abcdef/hall-ticket/",
      "metadata": {}
    },
    {
      "id": "e5f6a7b8-9abc-def0-1234-56789abcdef0",
      "name": "Mid-Term Examination",
      "exam_type": "Mid-Term",
      "start_date": "2026-06-15",
      "end_date": "2026-06-25",
      "time": "09:00 - 12:00",
      "venue": "Examination Hall A & B",
      "duration_minutes": 180,
      "subjects": ["Mathematics", "English", "Physics", "Chemistry", "Biology", "Hindi", "Computer", "Art", "PE"],
      "hall_ticket_available": true,
      "hall_ticket_url": "/api/v1/student/exams/e5f6a7b8-9abc-def0-1234-56789abcdef0/hall-ticket/",
      "metadata": {}
    },
    {
      "id": "f6a7b8c9-abcd-ef01-2345-6789abcdef01",
      "name": "Physics Practical",
      "exam_type": "Practical",
      "start_date": "2026-06-02",
      "end_date": "2026-06-02",
      "time": "10:00 - 12:00",
      "venue": "Physics Lab 1",
      "duration_minutes": 120,
      "subjects": ["Physics"],
      "hall_ticket_available": false,
      "hall_ticket_url": null,
      "metadata": {}
    }
  ]
}
```

---

### GET /api/v1/student/exams/past/

Get past exam results in table format.

**Query Params:** `?page=1&page_size=10&academic_year=2025-2026`

**Response: 200**
```json
{
  "count": 4,
  "page": 1,
  "page_size": 10,
  "total_pages": 1,
  "results": [
    {
      "id": "11111111-aaaa-bbbb-cccc-111111111111",
      "exam_name": "Unit Test 2",
      "exam_type": "Unit Test",
      "date": "2026-04-15",
      "marks_obtained": 412,
      "total_marks": 500,
      "percentage": 82.4,
      "grade": "A",
      "class_rank": 5
    },
    {
      "id": "22222222-bbbb-cccc-dddd-222222222222",
      "exam_name": "Quarterly Exam",
      "exam_type": "Quarterly",
      "date": "2026-03-01",
      "marks_obtained": 438,
      "total_marks": 500,
      "percentage": 87.6,
      "grade": "A+",
      "class_rank": 3
    },
    {
      "id": "33333333-cccc-dddd-eeee-333333333333",
      "exam_name": "Unit Test 1",
      "exam_type": "Unit Test",
      "date": "2026-02-10",
      "marks_obtained": 198,
      "total_marks": 250,
      "percentage": 79.2,
      "grade": "B+",
      "class_rank": 8
    },
    {
      "id": "77777777-aaaa-bbbb-cccc-777777777777",
      "exam_name": "Half-Yearly Exam",
      "exam_type": "Mid-Term",
      "date": "2025-10-15",
      "marks_obtained": 680,
      "total_marks": 800,
      "percentage": 85.0,
      "grade": "A",
      "class_rank": 4
    }
  ]
}
```

---

### GET /api/v1/student/exams/:id/hall-ticket/

Get hall ticket download URL for a specific exam.

**Response: 200**
```json
{
  "exam_id": "d4e5f6a7-89ab-cdef-0123-456789abcdef",
  "exam_name": "Unit Test 3",
  "student_name": "Arjun Mehta",
  "roll_number": "STU2024015",
  "class_section": "10-A",
  "exam_dates": "2026-06-05 to 2026-06-07",
  "venue": "Examination Hall A",
  "seat_number": "A-15",
  "download_url": "/api/v1/student/exams/d4e5f6a7-89ab-cdef-0123-456789abcdef/hall-ticket/download/",
  "content_type": "application/pdf",
  "generated_at": "2026-05-28T10:00:00Z",
  "metadata": {}
}
```

**Response: 404**
```json
{
  "error": "Hall ticket not available for this exam",
  "code": "HALL_TICKET_NOT_AVAILABLE"
}
```

---

## 8. Fees

### GET /api/v1/student/fees/

Get fee summary with current dues and recent payment history. Provides summary cards (Total Fees, Paid Amount, Pending Amount, Late Fines) and quick access to current dues and recent payments.

**Query Params:** `?academic_year=2025-2026`

**Response: 200**
```json
{
  "academic_year": "2025-2026",
  "summary": {
    "total_fees": 68700,
    "paid": 5000,
    "due": 0,
    "overdue": 0,
    "late_fines": 0,
    "currency": "INR"
  },
  "current_dues": [],
  "recent_payments": [
    {
      "id": "pay-11111111-aaaa-bbbb-cccc-111111111111",
      "fee_type": "Tuition Fee",
      "fee_category": "academic",
      "amount": 5000,
      "currency": "INR",
      "paid_date": "2026-05-01",
      "method": "UPI",
      "receipt_id": "RCP-2026-045",
      "status": "Paid"
    },
    {
      "id": "pay-22222222-bbbb-cccc-dddd-222222222222",
      "fee_type": "Lab Fee",
      "fee_category": "academic",
      "amount": 600,
      "currency": "INR",
      "paid_date": "2026-04-05",
      "method": "UPI",
      "receipt_id": "RCP-2026-046",
      "status": "Paid"
    },
    {
      "id": "pay-33333333-cccc-dddd-eeee-333333333333",
      "fee_type": "Tuition Fee",
      "fee_category": "academic",
      "amount": 5000,
      "currency": "INR",
      "paid_date": "2026-04-01",
      "method": "Bank Transfer",
      "receipt_id": "RCP-2026-012",
      "status": "Paid"
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/fees/structure/

Get fee structure breakdown with components and frequency. Shows all fee components applicable to the student with individual amounts and billing frequency, plus total annual fee. Supports academic year selector.

**Query Params:** `?academic_year=2025-2026`

**Response: 200**
```json
{
  "academic_year": "2025-2026",
  "components": [
    {
      "id": "comp-11111111-aaaa-bbbb-cccc-111111111111",
      "fee_component": "Tuition Fee",
      "fee_category": "academic",
      "amount": 5000,
      "currency": "INR",
      "frequency": "Monthly",
      "metadata": {}
    },
    {
      "id": "comp-22222222-bbbb-cccc-dddd-222222222222",
      "fee_component": "Lab Fee",
      "fee_category": "academic",
      "amount": 600,
      "currency": "INR",
      "frequency": "Quarterly",
      "metadata": {}
    },
    {
      "id": "comp-33333333-cccc-dddd-eeee-333333333333",
      "fee_component": "Library Fee",
      "fee_category": "academic",
      "amount": 300,
      "currency": "INR",
      "frequency": "Annually",
      "metadata": {}
    },
    {
      "id": "comp-44444444-dddd-eeee-ffff-444444444444",
      "fee_component": "Activity Fee",
      "fee_category": "other",
      "amount": 250,
      "currency": "INR",
      "frequency": "Monthly",
      "metadata": {}
    },
    {
      "id": "comp-55555555-eeee-ffff-aaaa-555555555555",
      "fee_component": "Exam Fee",
      "fee_category": "academic",
      "amount": 1200,
      "currency": "INR",
      "frequency": "Semi-Annually",
      "metadata": {}
    }
  ],
  "total_annual_fee": 68700,
  "currency": "INR",
  "metadata": {}
}
```

---

### GET /api/v1/student/fees/dues/

Get list of current fee dues (Fee Details section). Each due shows total amount, paid amount, balance, due date, status, and either a pay now action for Pending/Overdue items or receipt access for Paid items.

**Query Params:** `?academic_year=2025-2026`

**Response: 200 (with dues)**
```json
{
  "count": 2,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "total_due": 12500,
  "currency": "INR",
  "results": [
    {
      "id": "due-11111111-aaaa-bbbb-cccc-111111111111",
      "fee_type": "Exam Fee",
      "fee_category": "academic",
      "description": "Mid-Term Examination Fee - June 2026",
      "amount": 2500,
      "total_amount": 2500,
      "paid_amount": 0,
      "balance": 2500,
      "currency": "INR",
      "due_date": "2026-06-01",
      "status": "Pending",
      "is_overdue": false,
      "days_until_due": 9,
      "pay_now_url": "/api/v1/student/fees/pay/due-11111111-aaaa-bbbb-cccc-111111111111/",
      "metadata": {}
    },
    {
      "id": "due-22222222-bbbb-cccc-dddd-222222222222",
      "fee_type": "Transport Fee",
      "fee_category": "transport",
      "description": "Transport Fee - Q2 (Apr-Jun 2026)",
      "amount": 10000,
      "total_amount": 10000,
      "paid_amount": 0,
      "balance": 10000,
      "currency": "INR",
      "due_date": "2026-05-15",
      "status": "Overdue",
      "is_overdue": true,
      "days_overdue": 8,
      "pay_now_url": "/api/v1/student/fees/pay/due-22222222-bbbb-cccc-dddd-222222222222/",
      "metadata": {}
    }
  ]
}
```

**Response: 200 (all paid - Fee Details with paid items)**
```json
{
  "count": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "total_due": 0,
  "currency": "INR",
  "results": [
    {
      "id": "due-33333333-cccc-dddd-eeee-333333333333",
      "fee_type": "Tuition Fee",
      "fee_category": "academic",
      "description": "Tuition Fee - May 2026",
      "amount": 5000,
      "total_amount": 5000,
      "paid_amount": 5000,
      "balance": 0,
      "currency": "INR",
      "due_date": "2026-06-01",
      "status": "Paid",
      "is_overdue": false,
      "receipt_url": "/api/v1/student/fees/receipt/pay-11111111-aaaa-bbbb-cccc-111111111111/",
      "metadata": {}
    }
  ]
}
```

**Response: 200 (no dues)**
```json
{
  "count": 0,
  "page": 1,
  "page_size": 20,
  "total_pages": 0,
  "total_due": 0,
  "currency": "INR",
  "results": []
}
```

---

### GET /api/v1/student/fees/history/

Get payment history (Payment History tab). Shows all past payments with date, fee type, amount, paid date, payment method, status, and receipt download action.

**Query Params:** `?page=1&page_size=20&academic_year=2025-2026`

**Response: 200**
```json
{
  "count": 5,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "pay-11111111-aaaa-bbbb-cccc-111111111111",
      "fee_type": "Tuition Fee",
      "fee_category": "academic",
      "description": "Tuition Fee - May 2026",
      "amount": 5000,
      "currency": "INR",
      "paid_date": "2026-05-01",
      "method": "UPI",
      "transaction_id": "UPI-2026050112345",
      "receipt_id": "RCP-2026-045",
      "receipt_url": "/api/v1/student/fees/receipt/pay-11111111-aaaa-bbbb-cccc-111111111111/",
      "status": "Paid",
      "metadata": {}
    },
    {
      "id": "pay-22222222-bbbb-cccc-dddd-222222222222",
      "fee_type": "Lab Fee",
      "fee_category": "academic",
      "description": "Lab Fee - Q1 (Apr-Jun 2026)",
      "amount": 600,
      "currency": "INR",
      "paid_date": "2026-04-05",
      "method": "UPI",
      "transaction_id": "UPI-2026040512346",
      "receipt_id": "RCP-2026-046",
      "receipt_url": "/api/v1/student/fees/receipt/pay-22222222-bbbb-cccc-dddd-222222222222/",
      "status": "Paid",
      "metadata": {}
    },
    {
      "id": "pay-33333333-cccc-dddd-eeee-333333333333",
      "fee_type": "Tuition Fee",
      "fee_category": "academic",
      "description": "Tuition Fee - April 2026",
      "amount": 5000,
      "currency": "INR",
      "paid_date": "2026-04-01",
      "method": "Bank Transfer",
      "transaction_id": "NEFT-20260401789012",
      "receipt_id": "RCP-2026-012",
      "receipt_url": "/api/v1/student/fees/receipt/pay-33333333-cccc-dddd-eeee-333333333333/",
      "status": "Paid",
      "metadata": {}
    },
    {
      "id": "pay-44444444-dddd-eeee-ffff-444444444444",
      "fee_type": "Tuition Fee",
      "fee_category": "academic",
      "description": "Tuition Fee - March 2026",
      "amount": 5000,
      "currency": "INR",
      "paid_date": "2026-03-01",
      "method": "Cash",
      "transaction_id": null,
      "receipt_id": "RCP-2025-089",
      "receipt_url": "/api/v1/student/fees/receipt/pay-44444444-dddd-eeee-ffff-444444444444/",
      "status": "Paid",
      "metadata": {}
    },
    {
      "id": "pay-55555555-eeee-ffff-aaaa-555555555555",
      "fee_type": "Activity Fee",
      "fee_category": "other",
      "description": "Activity Fee - March 2026",
      "amount": 250,
      "currency": "INR",
      "paid_date": "2026-03-01",
      "method": "Bank Transfer",
      "transaction_id": "NEFT-20260301456789",
      "receipt_id": "RCP-2025-072",
      "receipt_url": "/api/v1/student/fees/receipt/pay-55555555-eeee-ffff-aaaa-555555555555/",
      "status": "Paid",
      "metadata": {}
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/fees/receipt/:payment_id/

Get payment receipt details with download URL. Supports receipt download as PDF.

**Response: 200**
```json
{
  "payment_id": "pay-11111111-aaaa-bbbb-cccc-111111111111",
  "receipt_id": "RCP-2026-045",
  "student_name": "John Doe",
  "roll_number": "STU2024015",
  "class_section": "10-A",
  "fee_type": "Tuition Fee",
  "description": "Tuition Fee - May 2026",
  "amount": 5000,
  "currency": "INR",
  "paid_date": "2026-05-01",
  "method": "UPI",
  "transaction_id": "UPI-2026050112345",
  "school_name": "Delhi Public School",
  "school_address": "Sector 24, Gurugram, Haryana 122017",
  "download_url": "/api/v1/student/fees/receipt/pay-11111111-aaaa-bbbb-cccc-111111111111/download/",
  "content_type": "application/pdf",
  "generated_at": "2026-05-01T12:30:00Z",
  "metadata": {}
}
```

**Response: 404**
```json
{
  "error": "Payment receipt not found",
  "code": "NOT_FOUND"
}
```

---

## 9. Library

### GET /api/v1/student/library/

Get library summary with currently issued books, overdue indicators, and fine information.

**Response: 200**
```json
{
  "summary": {
    "books_issued": 1,
    "overdue_books": 1,
    "max_allowed": 3,
    "total_fine": 195,
    "currency": "INR",
    "fine_per_day": 5,
    "books_returned": 0
  },
  "fine_policy": {
    "rate": 5,
    "currency": "INR",
    "unit": "per_day",
    "message": "Late return penalty: INR 5/day for overdue books. You have 1 overdue book with INR 195 in pending fines."
  },
  "my_books": [
    {
      "id": "borrow-11111111-aaaa-bbbb-cccc-111111111111",
      "book_id": "book-001",
      "title": "Advanced Mathematics",
      "author": "John Smith",
      "isbn": "978-0262033848",
      "issue_date": "2026-03-16",
      "due_date": "2026-04-14",
      "days_remaining": null,
      "days_overdue": 39,
      "status": "Overdue",
      "fine": 195,
      "fine_per_day": 5,
      "currency": "INR",
      "overdue_message": "This book is 39 days overdue. Fine: INR 5/day. Current penalty: INR 195. Please return it to avoid further fines.",
      "metadata": {}
    }
  ],
  "metadata": {}
}
```

**Notes:**
- `status` values: `Issued`, `Overdue`, `Returned`
- `days_remaining`: number of days until due date (null if overdue)
- `days_overdue`: number of days past due date (null if not overdue)
- `fine_per_day`: INR charged per day for overdue books
- `overdue_message`: human-readable warning shown on overdue book cards
- Summary card "Books Issued" counts currently held (non-returned) books
- Summary card "Books Returned" counts books returned in current academic year
- Max allowed books per student: 3

---

### GET /api/v1/student/library/catalog/

Search and browse the book catalog (Browse Catalog tab).

**Query Params:** `?page=1&page_size=20&search=physics&category=Physics`

**Response: 200**
```json
{
  "count": 45,
  "page": 1,
  "page_size": 20,
  "total_pages": 3,
  "results": [
    {
      "id": "book-101",
      "title": "Concepts of Physics Vol. 1",
      "author": "H.C. Verma",
      "isbn": "978-8177091878",
      "category": "Physics",
      "publisher": "Bharati Bhawan",
      "edition": "2024",
      "total_copies": 5,
      "available_copies": 3,
      "is_available": true,
      "metadata": {}
    },
    {
      "id": "book-102",
      "title": "Fundamentals of Physics",
      "author": "Halliday, Resnick & Walker",
      "isbn": "978-1119460138",
      "category": "Physics",
      "publisher": "Wiley",
      "edition": "2023",
      "total_copies": 3,
      "available_copies": 0,
      "is_available": false,
      "metadata": {}
    },
    {
      "id": "book-103",
      "title": "Problems in General Physics",
      "author": "I.E. Irodov",
      "isbn": "978-8183552158",
      "category": "Physics",
      "publisher": "G.K. Publishers",
      "edition": "2022",
      "total_copies": 4,
      "available_copies": 2,
      "is_available": true,
      "metadata": {}
    },
    {
      "id": "book-104",
      "title": "University Physics",
      "author": "Young & Freedman",
      "isbn": "978-0135216118",
      "category": "Physics",
      "publisher": "Pearson",
      "edition": "2024",
      "total_copies": 2,
      "available_copies": 1,
      "is_available": true,
      "metadata": {}
    },
    {
      "id": "book-105",
      "title": "The Feynman Lectures on Physics",
      "author": "Richard P. Feynman",
      "isbn": "978-0465024940",
      "category": "Physics",
      "publisher": "Basic Books",
      "edition": "2011",
      "total_copies": 3,
      "available_copies": 2,
      "is_available": true,
      "metadata": {}
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/library/history/

Get borrowing history (History tab).

**Query Params:** `?page=1&page_size=20`

**Response: 200**
```json
{
  "count": 12,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "history-001",
      "book_id": "book-050",
      "title": "To Kill a Mockingbird",
      "author": "Harper Lee",
      "category": "English",
      "issue_date": "2026-04-01",
      "return_date": "2026-04-14",
      "fine": 0,
      "currency": "INR",
      "status": "Returned",
      "metadata": {}
    },
    {
      "id": "history-002",
      "book_id": "book-030",
      "title": "R.D. Sharma Mathematics Class 10",
      "author": "R.D. Sharma",
      "category": "Mathematics",
      "issue_date": "2026-03-10",
      "return_date": "2026-03-28",
      "fine": 40,
      "currency": "INR",
      "status": "Returned",
      "metadata": {}
    },
    {
      "id": "history-003",
      "book_id": "book-075",
      "title": "Organic Chemistry",
      "author": "Morrison & Boyd",
      "category": "Chemistry",
      "issue_date": "2026-02-15",
      "return_date": "2026-02-28",
      "fine": 0,
      "currency": "INR",
      "status": "Returned",
      "metadata": {}
    },
    {
      "id": "history-004",
      "book_id": "book-012",
      "title": "Computer Science with Python",
      "author": "Sumita Arora",
      "category": "Computer Science",
      "issue_date": "2026-01-20",
      "return_date": "2026-02-03",
      "fine": 0,
      "currency": "INR",
      "status": "Returned",
      "metadata": {}
    },
    {
      "id": "history-005",
      "book_id": "book-088",
      "title": "The Story of My Experiments with Truth",
      "author": "Mahatma Gandhi",
      "category": "Hindi",
      "issue_date": "2025-12-01",
      "return_date": "2025-12-15",
      "fine": 0,
      "currency": "INR",
      "status": "Returned",
      "metadata": {}
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/library/fines/

Get fine details and penalty information.

**Response: 200**
```json
{
  "summary": {
    "total_pending_fines": 195,
    "total_paid_fines": 40,
    "currency": "INR",
    "fine_rate": 5,
    "fine_unit": "per_day"
  },
  "pending_fines": [
    {
      "id": "fine-001",
      "borrow_id": "borrow-11111111-aaaa-bbbb-cccc-111111111111",
      "book_id": "book-001",
      "title": "Advanced Mathematics",
      "author": "John Smith",
      "issue_date": "2026-03-16",
      "due_date": "2026-04-14",
      "days_overdue": 39,
      "fine_per_day": 5,
      "total_fine": 195,
      "currency": "INR",
      "status": "Overdue",
      "metadata": {}
    }
  ],
  "paid_fines": [
    {
      "id": "fine-002",
      "borrow_id": "history-002",
      "book_id": "book-030",
      "title": "R.D. Sharma Mathematics Class 10",
      "author": "R.D. Sharma",
      "issue_date": "2026-03-10",
      "return_date": "2026-03-28",
      "days_overdue": 4,
      "fine_per_day": 5,
      "total_fine": 40,
      "paid_date": "2026-03-28",
      "currency": "INR",
      "status": "Returned",
      "metadata": {}
    }
  ],
  "metadata": {}
}
```

---

## 10. Messages

### GET /api/v1/student/messages/teachers/

List teachers available to chat with (the student's class teachers).

**Response: 200**
```json
{
  "results": [
    {
      "teacher_id": "t-11111111-aaaa-bbbb-cccc-111111111111",
      "name": "Dr. Jane Smith",
      "subject": "Mathematics",
      "avatar_url": null,
      "avatar_initials": "JS",
      "last_message": "Sure, I'll explain that in tomorrow's class.",
      "last_message_time": "2026-05-21T15:30:00Z",
      "unread_count": 0,
      "is_online": false
    },
    {
      "teacher_id": "t-22222222-bbbb-cccc-dddd-222222222222",
      "name": "Ms. Emily Davis",
      "subject": "English",
      "avatar_url": null,
      "avatar_initials": "ED",
      "last_message": "Good effort on the essay. Keep practicing.",
      "last_message_time": "2026-05-20T10:15:00Z",
      "unread_count": 1,
      "is_online": true
    },
    {
      "teacher_id": "t-33333333-cccc-dddd-eeee-333333333333",
      "name": "Prof. Robert Johnson",
      "subject": "Physics",
      "avatar_url": null,
      "avatar_initials": "RJ",
      "last_message": "Refer to chapter 5 for the derivation.",
      "last_message_time": "2026-05-19T14:00:00Z",
      "unread_count": 0,
      "is_online": false
    },
    {
      "teacher_id": "t-44444444-dddd-eeee-ffff-444444444444",
      "name": "Mr. William Anderson",
      "subject": "Chemistry",
      "avatar_url": null,
      "avatar_initials": "WA",
      "last_message": null,
      "last_message_time": null,
      "unread_count": 0,
      "is_online": false
    },
    {
      "teacher_id": "t-55555555-eeee-ffff-aaaa-555555555555",
      "name": "Mrs. Priya Sharma",
      "subject": "Hindi",
      "avatar_url": null,
      "avatar_initials": "PS",
      "last_message": "Submit the poem recitation audio by Friday.",
      "last_message_time": "2026-05-18T09:45:00Z",
      "unread_count": 0,
      "is_online": false
    },
    {
      "teacher_id": "t-66666666-ffff-aaaa-bbbb-666666666666",
      "name": "Mr. Rajesh Kumar",
      "subject": "Computer",
      "avatar_url": null,
      "avatar_initials": "RK",
      "last_message": "Your Python project submission looks good.",
      "last_message_time": "2026-05-17T16:20:00Z",
      "unread_count": 0,
      "is_online": true
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/messages/:teacher_id/

Get chat history with a specific teacher.

**Query Params:** `?page=1&page_size=50&before=2026-05-21T15:30:00Z` (cursor-based optional)

**Response: 200**
```json
{
  "teacher_id": "t-11111111-aaaa-bbbb-cccc-111111111111",
  "teacher_name": "Dr. Jane Smith",
  "subject": "Mathematics",
  "count": 25,
  "page": 1,
  "page_size": 50,
  "total_pages": 1,
  "results": [
    {
      "id": "msg-001",
      "sender": "student",
      "sender_name": "Arjun Mehta",
      "content": "Ma'am, I have a doubt in the quadratic equations assignment. Can you explain question 7?",
      "timestamp": "2026-05-21T14:00:00Z",
      "is_read": true
    },
    {
      "id": "msg-002",
      "sender": "teacher",
      "sender_name": "Dr. Jane Smith",
      "content": "Hi Arjun, for question 7 you need to use the discriminant method first. Check if b^2 - 4ac is positive, negative, or zero.",
      "timestamp": "2026-05-21T14:15:00Z",
      "is_read": true
    },
    {
      "id": "msg-003",
      "sender": "student",
      "sender_name": "Arjun Mehta",
      "content": "I got the discriminant as negative. Does that mean the roots are imaginary?",
      "timestamp": "2026-05-21T14:30:00Z",
      "is_read": true
    },
    {
      "id": "msg-004",
      "sender": "teacher",
      "sender_name": "Dr. Jane Smith",
      "content": "Correct! When the discriminant is negative, the equation has no real roots. For this class, just state that the roots are not real. We'll cover complex numbers in class 11.",
      "timestamp": "2026-05-21T15:00:00Z",
      "is_read": true
    },
    {
      "id": "msg-005",
      "sender": "student",
      "sender_name": "Arjun Mehta",
      "content": "Thank you ma'am! Can you also explain the graphical method for solving these?",
      "timestamp": "2026-05-21T15:15:00Z",
      "is_read": true
    },
    {
      "id": "msg-006",
      "sender": "teacher",
      "sender_name": "Dr. Jane Smith",
      "content": "Sure, I'll explain that in tomorrow's class.",
      "timestamp": "2026-05-21T15:30:00Z",
      "is_read": true
    }
  ],
  "metadata": {}
}
```

**Response: 403**
```json
{
  "error": "You can only message teachers assigned to your class",
  "code": "TEACHER_NOT_ASSIGNED"
}
```

---

### POST /api/v1/student/messages/:teacher_id/

Send a message to a teacher.

**Request:**
```json
{
  "content": "Ma'am, I won't be able to attend tomorrow's class due to a doctor's appointment. Can I get the notes?"
}
```

**Response: 201**
```json
{
  "id": "msg-007",
  "sender": "student",
  "sender_name": "Arjun Mehta",
  "content": "Ma'am, I won't be able to attend tomorrow's class due to a doctor's appointment. Can I get the notes?",
  "timestamp": "2026-05-22T08:00:00Z",
  "is_read": false,
  "teacher_id": "t-11111111-aaaa-bbbb-cccc-111111111111",
  "metadata": {}
}
```

**Response: 400**
```json
{
  "error": "Message content cannot be empty",
  "code": "VALIDATION_ERROR"
}
```

**Response: 403**
```json
{
  "error": "You can only message teachers assigned to your class",
  "code": "TEACHER_NOT_ASSIGNED"
}
```

---

### GET /api/v1/student/messages/announcements/

List school announcements.

**Query Params:** `?page=1&page_size=20&source=Admin`

**Response: 200**
```json
{
  "count": 8,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "44444444-dddd-eeee-ffff-444444444444",
      "title": "Annual Sports Day - Registration Open",
      "source": "Admin",
      "content": "We are excited to announce the Annual Sports Day on June 15, 2026. All students are encouraged to participate. Registration forms are available at the sports office. Events include: 100m, 200m, 400m, long jump, shot put, cricket, football, and basketball. Last date for registration: May 25, 2026.",
      "date": "2026-05-20",
      "author": "Principal Office",
      "is_important": true,
      "metadata": {}
    },
    {
      "id": "55555555-eeee-ffff-aaaa-555555555555",
      "title": "New Books Added to Library",
      "source": "Library",
      "content": "50 new books have been added to the library in the Science and Literature sections. Some notable additions include latest editions of HC Verma, RD Sharma, and a new collection of Shakespeare's works. Visit the library to explore and borrow.",
      "date": "2026-05-18",
      "author": "Librarian",
      "is_important": false,
      "metadata": {}
    },
    {
      "id": "66666666-ffff-aaaa-bbbb-666666666666",
      "title": "Parent-Teacher Meeting Schedule",
      "source": "Admin",
      "content": "Parent-Teacher Meeting is scheduled for June 1, 2026 from 9:00 AM to 1:00 PM. All parents are requested to attend. Individual time slots will be communicated via SMS. Please carry the student's progress report.",
      "date": "2026-05-15",
      "author": "Vice Principal",
      "is_important": true,
      "metadata": {}
    },
    {
      "id": "77777777-aaaa-bbbb-cccc-888888888888",
      "title": "Holiday Notice - Eid-ul-Adha",
      "source": "Admin",
      "content": "The school will remain closed on June 7, 2026 (Saturday) on account of Eid-ul-Adha. Regular classes will resume on Monday, June 9, 2026.",
      "date": "2026-05-12",
      "author": "Principal Office",
      "is_important": false,
      "metadata": {}
    },
    {
      "id": "88888888-bbbb-cccc-dddd-999999999999",
      "title": "Science Exhibition 2026",
      "source": "Admin",
      "content": "Inter-house Science Exhibition will be held on June 20, 2026. Students interested in participating should submit their project proposals to respective science teachers by May 30, 2026. Prizes for top 3 in each category.",
      "date": "2026-05-10",
      "author": "Science Department",
      "is_important": false,
      "metadata": {}
    }
  ]
}
```

---

### GET /api/v1/student/messages/announcements/:id/

Get a single announcement with full details.

**Response: 200**
```json
{
  "id": "44444444-dddd-eeee-ffff-444444444444",
  "title": "Annual Sports Day - Registration Open",
  "source": "Admin",
  "content": "We are excited to announce the Annual Sports Day on June 15, 2026. All students are encouraged to participate. Registration forms are available at the sports office. Events include: 100m, 200m, 400m, long jump, shot put, cricket, football, and basketball. Last date for registration: May 25, 2026.",
  "date": "2026-05-20",
  "author": "Principal Office",
  "is_important": true,
  "attachments": [
    {
      "id": "att-ann-001",
      "filename": "sports_day_schedule.pdf",
      "url": "/api/v1/student/messages/announcements/44444444-dddd-eeee-ffff-444444444444/attachments/att-ann-001/",
      "size_bytes": 512000,
      "type": "application/pdf"
    }
  ],
  "target_audience": ["all_students"],
  "created_at": "2026-05-20T08:00:00Z",
  "metadata": {}
}
```

**Response: 404**
```json
{
  "error": "Announcement not found",
  "code": "NOT_FOUND"
}
```

---

## 11. Quiz Portal

### GET /api/v1/student/quizzes/

List available and completed quizzes with summary stats.

**Query Params:** `?page=1&page_size=20&subject=Mathematics&academic_year=2025-2026`

**Response: 200**
```json
{
  "summary": {
    "available": 3,
    "completed": 5,
    "average_score": 88,
    "average_rank": 4
  },
  "available_quizzes": {
    "count": 3,
    "page": 1,
    "page_size": 20,
    "total_pages": 1,
    "results": [
      {
        "id": "quiz-11111111-aaaa-bbbb-cccc-111111111111",
        "title": "Quadratic Equations Quiz",
        "subject": "Mathematics",
        "questions_count": 10,
        "duration_minutes": 30,
        "attempts_used": 0,
        "max_attempts": 3,
        "best_score": null,
        "status": "available",
        "created_by": "Dr. Jane Smith",
        "available_from": "2026-05-20T00:00:00Z",
        "available_until": "2026-05-30T23:59:59Z",
        "metadata": {}
      },
      {
        "id": "quiz-22222222-bbbb-cccc-dddd-222222222222",
        "title": "Light and Optics MCQ",
        "subject": "Physics",
        "questions_count": 15,
        "duration_minutes": 20,
        "attempts_used": 1,
        "max_attempts": 3,
        "best_score": 60,
        "status": "available",
        "created_by": "Prof. Robert Johnson",
        "available_from": "2026-05-18T00:00:00Z",
        "available_until": "2026-05-28T23:59:59Z",
        "metadata": {}
      },
      {
        "id": "quiz-33333333-cccc-dddd-eeee-333333333333",
        "title": "Hindi Grammar Test",
        "subject": "Hindi",
        "questions_count": 20,
        "duration_minutes": 25,
        "attempts_used": 0,
        "max_attempts": 2,
        "best_score": null,
        "status": "available",
        "created_by": "Mrs. Priya Sharma",
        "available_from": "2026-05-19T00:00:00Z",
        "available_until": "2026-05-29T23:59:59Z",
        "metadata": {}
      }
    ]
  },
  "completed_quizzes": {
    "count": 5,
    "page": 1,
    "page_size": 20,
    "total_pages": 1,
    "results": [
      {
        "id": "quiz-44444444-dddd-eeee-ffff-444444444444",
        "title": "Trigonometry Basics",
        "subject": "Mathematics",
        "score": 9,
        "total_questions": 10,
        "percentage": 90,
        "rank": 3,
        "total_participants": 42,
        "completed_at": "2026-05-15T10:30:00Z"
      },
      {
        "id": "quiz-55555555-eeee-ffff-aaaa-555555555555",
        "title": "English Grammar Quiz",
        "subject": "English",
        "score": 14,
        "total_questions": 15,
        "percentage": 93,
        "rank": 2,
        "total_participants": 44,
        "completed_at": "2026-05-12T11:00:00Z"
      },
      {
        "id": "quiz-66666666-ffff-aaaa-bbbb-666666666666",
        "title": "Periodic Table Challenge",
        "subject": "Chemistry",
        "score": 8,
        "total_questions": 10,
        "percentage": 80,
        "rank": 7,
        "total_participants": 43,
        "completed_at": "2026-05-08T14:15:00Z"
      }
    ]
  },
  "metadata": {}
}
```

---

### GET /api/v1/student/quizzes/:id/

Get quiz details including attempt information.

**Response: 200**
```json
{
  "id": "quiz-11111111-aaaa-bbbb-cccc-111111111111",
  "title": "Quadratic Equations Quiz",
  "subject": "Mathematics",
  "description": "Test your understanding of quadratic equations, discriminant, nature of roots, and graphical representation.",
  "questions_count": 10,
  "duration_minutes": 30,
  "max_attempts": 3,
  "attempts_used": 0,
  "best_score": null,
  "passing_score": 60,
  "created_by": "Dr. Jane Smith",
  "available_from": "2026-05-20T00:00:00Z",
  "available_until": "2026-05-30T23:59:59Z",
  "instructions": "Each question carries 1 mark. No negative marking. You must complete the quiz within the time limit.",
  "class_section": "10-A",
  "status": "available",
  "metadata": {}
}
```

**Response: 404**
```json
{
  "error": "Quiz not found",
  "code": "NOT_FOUND"
}
```

---

### POST /api/v1/student/quizzes/:id/start/

Start a quiz attempt. Returns questions with options.

**Request:**
```json
{}
```

**Response: 200**
```json
{
  "attempt_id": "attempt-11111111-aaaa-bbbb-cccc-111111111111",
  "quiz_id": "quiz-11111111-aaaa-bbbb-cccc-111111111111",
  "quiz_title": "Quadratic Equations Quiz",
  "started_at": "2026-05-22T10:00:00Z",
  "expires_at": "2026-05-22T10:30:00Z",
  "duration_minutes": 30,
  "total_questions": 10,
  "questions": [
    {
      "id": "q-001",
      "question_number": 1,
      "text": "What is the standard form of a quadratic equation?",
      "options": [
        { "id": "opt-a", "label": "A", "text": "ax + b = 0" },
        { "id": "opt-b", "label": "B", "text": "ax^2 + bx + c = 0" },
        { "id": "opt-c", "label": "C", "text": "ax^3 + bx^2 + cx + d = 0" },
        { "id": "opt-d", "label": "D", "text": "ax^2 + b = 0" }
      ],
      "marks": 1
    },
    {
      "id": "q-002",
      "question_number": 2,
      "text": "The discriminant of a quadratic equation ax^2 + bx + c = 0 is:",
      "options": [
        { "id": "opt-a", "label": "A", "text": "b^2 + 4ac" },
        { "id": "opt-b", "label": "B", "text": "b^2 - 4ac" },
        { "id": "opt-c", "label": "C", "text": "4ac - b^2" },
        { "id": "opt-d", "label": "D", "text": "b^2 - 2ac" }
      ],
      "marks": 1
    },
    {
      "id": "q-003",
      "question_number": 3,
      "text": "If the discriminant is zero, the quadratic equation has:",
      "options": [
        { "id": "opt-a", "label": "A", "text": "Two distinct real roots" },
        { "id": "opt-b", "label": "B", "text": "Two equal real roots" },
        { "id": "opt-c", "label": "C", "text": "No real roots" },
        { "id": "opt-d", "label": "D", "text": "One real and one imaginary root" }
      ],
      "marks": 1
    },
    {
      "id": "q-004",
      "question_number": 4,
      "text": "The roots of x^2 - 5x + 6 = 0 are:",
      "options": [
        { "id": "opt-a", "label": "A", "text": "2 and 3" },
        { "id": "opt-b", "label": "B", "text": "-2 and -3" },
        { "id": "opt-c", "label": "C", "text": "1 and 6" },
        { "id": "opt-d", "label": "D", "text": "-1 and -6" }
      ],
      "marks": 1
    },
    {
      "id": "q-005",
      "question_number": 5,
      "text": "The sum of the roots of ax^2 + bx + c = 0 is:",
      "options": [
        { "id": "opt-a", "label": "A", "text": "b/a" },
        { "id": "opt-b", "label": "B", "text": "-b/a" },
        { "id": "opt-c", "label": "C", "text": "c/a" },
        { "id": "opt-d", "label": "D", "text": "-c/a" }
      ],
      "marks": 1
    },
    {
      "id": "q-006",
      "question_number": 6,
      "text": "The product of the roots of ax^2 + bx + c = 0 is:",
      "options": [
        { "id": "opt-a", "label": "A", "text": "b/a" },
        { "id": "opt-b", "label": "B", "text": "-b/a" },
        { "id": "opt-c", "label": "C", "text": "c/a" },
        { "id": "opt-d", "label": "D", "text": "-c/a" }
      ],
      "marks": 1
    },
    {
      "id": "q-007",
      "question_number": 7,
      "text": "Which method is used to solve x^2 + 6x + 9 = 0?",
      "options": [
        { "id": "opt-a", "label": "A", "text": "Factorisation" },
        { "id": "opt-b", "label": "B", "text": "Completing the square" },
        { "id": "opt-c", "label": "C", "text": "Quadratic formula" },
        { "id": "opt-d", "label": "D", "text": "All of the above" }
      ],
      "marks": 1
    },
    {
      "id": "q-008",
      "question_number": 8,
      "text": "The quadratic formula gives roots as:",
      "options": [
        { "id": "opt-a", "label": "A", "text": "x = (-b +/- sqrt(b^2-4ac)) / 2a" },
        { "id": "opt-b", "label": "B", "text": "x = (-b +/- sqrt(b^2+4ac)) / 2a" },
        { "id": "opt-c", "label": "C", "text": "x = (b +/- sqrt(b^2-4ac)) / 2a" },
        { "id": "opt-d", "label": "D", "text": "x = (-b +/- sqrt(b^2-4ac)) / a" }
      ],
      "marks": 1
    },
    {
      "id": "q-009",
      "question_number": 9,
      "text": "If one root of x^2 - 7x + k = 0 is 3, then k is:",
      "options": [
        { "id": "opt-a", "label": "A", "text": "10" },
        { "id": "opt-b", "label": "B", "text": "12" },
        { "id": "opt-c", "label": "C", "text": "14" },
        { "id": "opt-d", "label": "D", "text": "21" }
      ],
      "marks": 1
    },
    {
      "id": "q-010",
      "question_number": 10,
      "text": "The graph of a quadratic equation is a:",
      "options": [
        { "id": "opt-a", "label": "A", "text": "Straight line" },
        { "id": "opt-b", "label": "B", "text": "Circle" },
        { "id": "opt-c", "label": "C", "text": "Parabola" },
        { "id": "opt-d", "label": "D", "text": "Hyperbola" }
      ],
      "marks": 1
    }
  ],
  "metadata": {}
}
```

**Response: 400**
```json
{
  "error": "Maximum attempts reached for this quiz",
  "code": "MAX_ATTEMPTS_REACHED",
  "details": {
    "max_attempts": 3,
    "attempts_used": 3
  }
}
```

**Response: 400 (Quiz expired)**
```json
{
  "error": "This quiz is no longer available",
  "code": "QUIZ_EXPIRED",
  "details": {
    "available_until": "2026-05-20T23:59:59Z"
  }
}
```

---

### POST /api/v1/student/quizzes/:id/submit/

Submit quiz answers.

**Request:**
```json
{
  "attempt_id": "attempt-11111111-aaaa-bbbb-cccc-111111111111",
  "answers": [
    { "question_id": "q-001", "selected_option": "opt-b" },
    { "question_id": "q-002", "selected_option": "opt-b" },
    { "question_id": "q-003", "selected_option": "opt-b" },
    { "question_id": "q-004", "selected_option": "opt-a" },
    { "question_id": "q-005", "selected_option": "opt-b" },
    { "question_id": "q-006", "selected_option": "opt-c" },
    { "question_id": "q-007", "selected_option": "opt-d" },
    { "question_id": "q-008", "selected_option": "opt-a" },
    { "question_id": "q-009", "selected_option": "opt-b" },
    { "question_id": "q-010", "selected_option": "opt-c" }
  ]
}
```

**Response: 200**
```json
{
  "attempt_id": "attempt-11111111-aaaa-bbbb-cccc-111111111111",
  "quiz_id": "quiz-11111111-aaaa-bbbb-cccc-111111111111",
  "quiz_title": "Quadratic Equations Quiz",
  "score": 9,
  "total_questions": 10,
  "percentage": 90,
  "passed": true,
  "passing_score": 60,
  "submitted_at": "2026-05-22T10:25:00Z",
  "time_taken_seconds": 1500,
  "metadata": {}
}
```

**Response: 400**
```json
{
  "error": "Quiz attempt has already been submitted",
  "code": "ALREADY_SUBMITTED"
}
```

**Response: 400 (Time expired)**
```json
{
  "error": "Quiz time has expired. Auto-submitted with answered questions.",
  "code": "TIME_EXPIRED",
  "details": {
    "score": 7,
    "total_questions": 10,
    "answered": 8,
    "unanswered": 2
  }
}
```

---

### GET /api/v1/student/quizzes/:id/result/

Get quiz result details.

**Response: 200**
```json
{
  "quiz_id": "quiz-11111111-aaaa-bbbb-cccc-111111111111",
  "quiz_title": "Quadratic Equations Quiz",
  "subject": "Mathematics",
  "attempt_id": "attempt-11111111-aaaa-bbbb-cccc-111111111111",
  "score": 9,
  "total_questions": 10,
  "percentage": 90,
  "rank": 4,
  "total_participants": 42,
  "passed": true,
  "passing_score": 60,
  "time_taken_seconds": 1500,
  "completed_at": "2026-05-22T10:25:00Z",
  "attempts_used": 1,
  "max_attempts": 3,
  "best_score": 90,
  "metadata": {}
}
```

**Response: 404**
```json
{
  "error": "No result found. Quiz not yet attempted.",
  "code": "NOT_ATTEMPTED"
}
```

---

### GET /api/v1/student/quizzes/completed/

List all completed quizzes with scores.

**Query Params:** `?page=1&page_size=20&subject=Mathematics`

**Response: 200**
```json
{
  "count": 5,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "quiz-44444444-dddd-eeee-ffff-444444444444",
      "title": "Trigonometry Basics",
      "subject": "Mathematics",
      "score": 9,
      "total_questions": 10,
      "percentage": 90,
      "rank": 3,
      "total_participants": 42,
      "completed_at": "2026-05-15T10:30:00Z",
      "metadata": {}
    },
    {
      "id": "quiz-55555555-eeee-ffff-aaaa-555555555555",
      "title": "English Grammar Quiz",
      "subject": "English",
      "score": 14,
      "total_questions": 15,
      "percentage": 93,
      "rank": 2,
      "total_participants": 44,
      "completed_at": "2026-05-12T11:00:00Z",
      "metadata": {}
    },
    {
      "id": "quiz-66666666-ffff-aaaa-bbbb-666666666666",
      "title": "Periodic Table Challenge",
      "subject": "Chemistry",
      "score": 8,
      "total_questions": 10,
      "percentage": 80,
      "rank": 7,
      "total_participants": 43,
      "completed_at": "2026-05-08T14:15:00Z",
      "metadata": {}
    },
    {
      "id": "quiz-77777777-aaaa-bbbb-cccc-777777777777",
      "title": "Hindi Sahitya MCQ",
      "subject": "Hindi",
      "score": 17,
      "total_questions": 20,
      "percentage": 85,
      "rank": 5,
      "total_participants": 44,
      "completed_at": "2026-04-28T09:45:00Z",
      "metadata": {}
    },
    {
      "id": "quiz-88888888-bbbb-cccc-dddd-888888888888",
      "title": "Biology Cell Structure",
      "subject": "Biology",
      "score": 11,
      "total_questions": 12,
      "percentage": 92,
      "rank": 4,
      "total_participants": 43,
      "completed_at": "2026-04-20T13:00:00Z",
      "metadata": {}
    }
  ]
}
```

---

## 12. My Profile (10 endpoints)

### GET /api/v1/student/profile/

Get the full student profile including personal, parent/guardian, medical, transport, mentor information, and recent attendance. The profile header displays avatar, name, roll number, class, email, phone, and student type badge (Day Scholar / Hostler). Quick stats (KPI cards) for attendance, average grade, assignments, and fee due are included.

**Response: 200**
```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "roll_number": "STU2024001",
  "full_name": "John Doe",
  "email": "john@student.com",
  "phone": "+1-555-0101",
  "class_name": "10",
  "section": "A",
  "class_section": "10-A",
  "academic_year": "2025-2026",
  "student_type": "Day Scholar",
  "avatar_url": null,
  "avatar_initials": "JD",
  "quick_stats": {
    "attendance_percentage": 67,
    "avg_grade": 83.5,
    "pending_assignments": 0,
    "fee_due": 0
  },
  "personal": {
    "date_of_birth": "2010-05-10",
    "gender": "Male",
    "admission_date": "2024-01-04",
    "blood_group": "O+",
    "religion": null,
    "nationality": "Indian",
    "student_type": "Day Scholar",
    "address": {
      "street": "123 Main St",
      "city": "City",
      "state": "State",
      "pincode": "12345",
      "country": "India"
    },
    "phone": "+1-555-0101",
    "alternate_phone": null
  },
  "parent": {
    "parent_name": "Robert Doe",
    "relationship": "Parent/Guardian",
    "phone": "+1-555-0102",
    "email": "robert@parent.com",
    "occupation": null,
    "emergency_contact": "+1-555-0102",
    "address": {
      "street": "123 Main St",
      "city": "City",
      "state": "State",
      "pincode": "12345",
      "country": "India"
    }
  },
  "medical": {
    "blood_group": "O+",
    "gender": "Male",
    "religion": null,
    "conditions": "None reported",
    "allergies": "None reported",
    "medications": null,
    "doctor_name": null,
    "doctor_phone": null,
    "insurance_id": null
  },
  "transport": {
    "enrolled": true,
    "route_name": "Route 5 - Downtown",
    "bus_number": "BUS-005",
    "pickup_point": "Main Street Corner",
    "pickup_time": "07:15",
    "drop_time": "15:00",
    "driver_name": null,
    "driver_phone": null
  },
  "mentor": {
    "teacher_id": "t-11111111-aaaa-bbbb-cccc-111111111111",
    "name": "Dr. Jane Smith",
    "subject": "Mathematics",
    "qualification": "Ph.D. in Mathematics",
    "email": "jane.smith@school.com",
    "phone": "+1-555-1001"
  },
  "recent_attendance": [
    {
      "id": "att-001",
      "subject": "Mathematics",
      "date": "2026-04-07",
      "status": "present",
      "metadata": {}
    },
    {
      "id": "att-002",
      "subject": "Mathematics",
      "date": "2026-04-06",
      "status": "present",
      "metadata": {}
    },
    {
      "id": "att-003",
      "subject": "Mathematics",
      "date": "2026-04-05",
      "status": "absent",
      "metadata": {}
    }
  ],
  "created_at": "2024-01-04T10:00:00Z",
  "updated_at": "2026-05-10T14:30:00Z",
  "metadata": {}
}
```

---

### PUT /api/v1/student/profile/

Update editable profile fields. Only phone, alternate_phone, address, and emergency contact are student-editable. Non-editable fields: full_name, date_of_birth, gender, blood_group, roll_number, class, admission_date.

**Request:**
```json
{
  "phone": "+1-555-0101",
  "alternate_phone": "+1-555-0199",
  "address": {
    "street": "456 Oak Avenue",
    "city": "City",
    "state": "State",
    "pincode": "12346",
    "country": "India"
  },
  "emergency_contact": "+1-555-0103"
}
```

**Response: 200**
```json
{
  "message": "Profile updated successfully",
  "updated_fields": ["phone", "alternate_phone", "address", "emergency_contact"],
  "updated_at": "2026-05-22T16:00:00Z",
  "metadata": {}
}
```

**Response: 400**
```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "phone": "Invalid phone number format.",
    "pincode": "Pincode must be a valid format."
  }
}
```

**Response: 403**
```json
{
  "error": "You can only update phone, address, and emergency contact. Contact admin for other changes.",
  "code": "FIELD_NOT_EDITABLE",
  "details": {
    "non_editable_fields": ["full_name", "date_of_birth", "gender", "blood_group"]
  }
}
```

---

### GET /api/v1/student/profile/mentor/

Get assigned mentor details including subject, qualification, contact information, and designation.

**Response: 200**
```json
{
  "teacher_id": "t-11111111-aaaa-bbbb-cccc-111111111111",
  "name": "Dr. Jane Smith",
  "subject": "Mathematics",
  "qualification": "Ph.D. in Mathematics",
  "email": "jane.smith@school.com",
  "phone": "+1-555-1001",
  "avatar_url": null,
  "avatar_initials": "JS",
  "designation": "Mentor",
  "experience_years": 7,
  "assigned_since": "2025-06-15",
  "total_mentees": 8,
  "available_hours": "Mon-Fri 3:00 PM - 4:00 PM",
  "metadata": {}
}
```

**Response: 404**
```json
{
  "error": "No mentor assigned. Contact your class teacher.",
  "code": "MENTOR_NOT_ASSIGNED"
}
```

---

### GET /api/v1/student/profile/parent-meetings/

Get parent-teacher meeting history with attendance status, conducted by, attended by, and discussion notes.

**Response: 200**
```json
{
  "count": 4,
  "summary": { "total_meetings": 4, "attended": 3, "not_attended": 1 },
  "meetings": [
    { "id": "mtg-001", "title": "Parent-Teacher Meeting", "date": "2026-04-23", "status": "Attended", "attended_by": "Robert Doe", "conducted_by": "Dr. Jane Smith", "notes": "Discussed academic progress. Student performing well in Mathematics.", "metadata": {} },
    { "id": "mtg-002", "title": "Parent-Teacher Meeting", "date": "2026-01-15", "status": "Attended", "attended_by": "Robert Doe", "conducted_by": "Ms. Emily Davis", "notes": "Quarterly review. Good improvement in English and Science.", "metadata": {} },
    { "id": "mtg-003", "title": "Special Meeting", "date": "2025-10-10", "status": "Not Attended", "attended_by": null, "conducted_by": "Dr. Jane Smith", "notes": "Parent could not attend due to personal reasons.", "metadata": {} },
    { "id": "mtg-004", "title": "Parent-Teacher Meeting", "date": "2025-07-25", "status": "Attended", "attended_by": "Robert Doe", "conducted_by": "Prof. Robert Johnson", "notes": "Initial orientation meeting. Discussed student goals and expectations.", "metadata": {} }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/profile/behavior/

Get behavior and conduct information including overall rating, discipline score, punctuality score, and recent conduct notes.

**Response: 200**
```json
{
  "overall_rating": "A",
  "overall_label": "Excellent",
  "discipline": { "score": 95, "label": "Very Good" },
  "punctuality": { "score": 98, "label": "Excellent" },
  "recent_conduct_notes": [
    { "id": "cn-001", "type": "positive", "note": "Excellent class participation", "subject": "Mathematics", "teacher": "Ms. Smith", "date": "2026-04-15", "metadata": {} },
    { "id": "cn-002", "type": "positive", "note": "Helped classmates with group project", "subject": "Science", "teacher": "Mr. Johnson", "date": "2026-04-03", "metadata": {} }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/profile/activities/

Get extra-curricular activities and club memberships with role, membership date, and status.

**Response: 200**
```json
{
  "count": 3,
  "activities": [
    { "id": "act-001", "name": "School Basketball Team", "role": "Point Guard", "member_since": "2024", "status": "Active", "achievements": null, "metadata": {} },
    { "id": "act-002", "name": "Science Club", "role": null, "member_since": "2024", "status": "Active", "achievements": "Participated in 3 competitions", "metadata": {} },
    { "id": "act-003", "name": "Drama Society", "role": null, "member_since": "2025", "status": "Active", "achievements": "Performed in Annual Play 2025", "metadata": {} }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/profile/awards/

Get awards and achievements list.

**Response: 200**
```json
{
  "count": 1,
  "awards": [
    { "id": "awd-001", "title": "Best Student Award", "category": "Academic Excellence", "year": "2025", "description": "Recognized for outstanding performance in Mathematics", "metadata": {} }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/profile/academic-summary/

Get academic performance summary including overall attendance, overall grade, assignments submitted, and class rank.

**Response: 200**
```json
{
  "overall_attendance": { "percentage": 67, "present_days": 2, "total_days": 3 },
  "overall_grade": { "percentage": 83.5, "based_on_exams": 11 },
  "assignments_submitted": { "count": 0, "total": 0 },
  "class_rank": { "rank": 5, "total_students": 45 },
  "metadata": {}
}
```

---

### GET /api/v1/student/profile/print/

Get print-friendly full profile data formatted for printing.

**Response: 200**
```json
{
  "student": { "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479", "roll_number": "STU2024001", "full_name": "John Doe", "class_section": "10-A", "academic_year": "2025-2026", "student_type": "Day Scholar", "avatar_url": null },
  "personal": { "date_of_birth": "2010-05-10", "gender": "Male", "admission_date": "2024-01-04", "blood_group": "O+", "religion": null, "address": "123 Main St, City, State 12345" },
  "parent": { "name": "Robert Doe", "relationship": "Parent/Guardian", "phone": "+1-555-0102", "email": "robert@parent.com", "emergency_contact": "+1-555-0102" },
  "medical": { "blood_group": "O+", "conditions": "None reported", "allergies": "None reported" },
  "transport": { "enrolled": true, "route_name": "Route 5 - Downtown", "bus_number": "BUS-005", "pickup_point": "Main Street Corner" },
  "mentor": { "name": "Dr. Jane Smith", "subject": "Mathematics", "qualification": "Ph.D. in Mathematics", "email": "jane.smith@school.com", "phone": "+1-555-1001" },
  "academic_summary": { "overall_attendance": 67, "overall_grade": 83.5, "class_rank": 5, "total_students": 45 },
  "generated_at": "2026-05-23T12:44:00Z",
  "metadata": {}
}
```

---

### GET /api/v1/student/profile/export-pdf/

Export the full student profile as a downloadable PDF document.

**Response: 200** (binary PDF with Content-Type: application/pdf)

**Response: 503**
```json
{
  "error": "PDF generation service is temporarily unavailable. Please try again later.",
  "code": "PDF_SERVICE_UNAVAILABLE"
}
```

---

## Error Responses (Common)

### 401 Unauthorized

Returned when the request lacks valid authentication.

```json
{
  "error": "Authentication required. Please login.",
  "code": "UNAUTHORIZED"
}
```

### 403 Forbidden

Returned when a non-student role tries to access student endpoints.

```json
{
  "error": "Access denied. Student role required.",
  "code": "FORBIDDEN"
}
```

### 400 Bad Request

Returned for validation errors.

```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "academic_year": "Invalid format. Use YYYY-YYYY (e.g., 2025-2026).",
    "page": "Must be a positive integer."
  }
}
```

### 500 Internal Server Error

Returned for unexpected server errors.

```json
{
  "error": "An unexpected error occurred. Please try again later.",
  "code": "INTERNAL_ERROR",
  "request_id": "req-abc123def456"
}
```

---

## Summary

| Section | Endpoints | Methods |
|---------|-----------|---------|
| Auth (shared) | 7 | POST, GET |
| Dashboard | 10 | GET |
| Timetable | 2 | GET |
| Attendance | 3 | GET |
| Assignments | 4 | GET, POST |
| Results | 5 | GET |
| Exams | 3 | GET |
| Fees | 5 | GET |
| Library | 4 | GET |
| Messages | 5 | GET, POST |
| Quiz Portal | 6 | GET, POST |
| My Profile | 10 | GET, PUT |
| **Total** | **57 student + 7 auth = 64** | |
