# School ERP Backend - Student Portal: Requests & Responses

> Detailed request/response documentation for all Student Portal API endpoints.
> For quick endpoint reference, see [student-endpoint.md](./student-endpoint.md).

---

## 1. Authentication (Shared)

> Auth endpoints are identical to the Admin/Teacher modules. The only difference is the `role` field in responses will be `"student"`.

### POST /api/v1/auth/login

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

### POST /api/v1/auth/logout

**Response: 200**
```json
{
  "message": "Logged out successfully"
}
```

---

### POST /api/v1/auth/refresh-token

**Response: 200**
```json
{
  "message": "Token refreshed"
}
```

---

### GET /api/v1/auth/me

**Response: 200**
```json
{
  "id": "uuid",
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
```

---

### POST /api/v1/auth/change-password

**Request:**
```json
{
  "current_password": "oldpass123",
  "new_password": "newpass456"
}
```

**Response: 200**
```json
{
  "message": "Password changed successfully"
}
```

---

## 2. Dashboard (`/student/dashboard`)

### GET /api/v1/student/dashboard/stats

**Response: 200 — `StudentDashboardStatsResponse`**
```json
{
  "attendance_percentage": 92.5,
  "average_grade": "A",
  "pending_assignments": 3,
  "fee_status": "Clear"
}
```

---

### GET /api/v1/student/dashboard/today-schedule

**Response: 200 — `StudentTodayScheduleResponse`**
```json
{
  "date": "2024-01-15",
  "day": "Monday",
  "total_classes": 6,
  "schedule": [
    {
      "period_number": 1,
      "start_time": "08:00",
      "end_time": "08:45",
      "subject": "Mathematics",
      "teacher_name": "Mr. Sharma",
      "slot_type": "Lecture"
    }
  ]
}
```

---

### GET /api/v1/student/dashboard/pending-assignments

**Response: 200 — `StudentPendingAssignmentsResponse`**
```json
{
  "total": 3,
  "items": [
    {
      "id": "uuid",
      "title": "Chapter 5 Problems",
      "subject": "Mathematics",
      "due_date": "2024-01-20",
      "total_marks": 50.0,
      "status": "Pending"
    }
  ]
}
```

---

### GET /api/v1/student/dashboard/upcoming-exams

**Response: 200 — `StudentUpcomingExamsResponse`**
```json
{
  "total": 2,
  "items": [
    {
      "id": "uuid",
      "name": "Unit Test 3",
      "subject": "Physics",
      "date": "2024-02-01",
      "total_marks": 100.0,
      "start_time": "09:00",
      "end_time": "12:00"
    }
  ]
}
```

---

### GET /api/v1/student/dashboard/subject-attendance

**Response: 200 — `SubjectAttendanceResponse`**
```json
{
  "overall_percentage": 92.5,
  "subjects": [
    {
      "subject": "Mathematics",
      "total_classes": 40,
      "attended": 37,
      "percentage": 92.5
    }
  ]
}
```

---

### GET /api/v1/student/dashboard/recent-results

**Response: 200 — `RecentResultsResponse`**
```json
{
  "items": [
    {
      "exam_id": "uuid",
      "exam_name": "Mid-Term",
      "subject": "Mathematics",
      "marks_obtained": 85.0,
      "total_marks": 100.0,
      "grade": "A",
      "percentage": 85.0
    }
  ]
}
```

---

### GET /api/v1/student/dashboard/announcements

**Response: 200 — `AnnouncementsResponse`**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Sports Day",
      "message": "Annual sports day on 25th Jan",
      "date": "2024-01-10",
      "type": "event"
    }
  ]
}
```

---

### GET /api/v1/student/dashboard/notifications

**Response: 200 — `NotificationsResponse`**
```json
{
  "unread_count": 5,
  "items": [
    {
      "id": "uuid",
      "title": "Assignment Due",
      "message": "Math assignment due tomorrow",
      "date": "2024-01-14",
      "is_read": false
    }
  ]
}
```

---

### GET /api/v1/student/dashboard/fee-status

**Response: 200 — `FeeStatusResponse`**
```json
{
  "total_fees": 50000.0,
  "total_paid": 40000.0,
  "total_pending": 10000.0,
  "items": [
    {
      "fee_type": "Tuition",
      "amount": 25000.0,
      "paid": 25000.0,
      "pending": 0.0,
      "due_date": "2024-01-31",
      "status": "Paid"
    }
  ]
}
```

---

### GET /api/v1/student/dashboard/parent-meetings

**Response: 200 — `ParentMeetingsResponse`**
```json
{
  "total": 2,
  "items": [
    {
      "id": "uuid",
      "meeting_type": "PTM",
      "date": "2024-01-10",
      "conducted_by": "Ms. Verma",
      "status": "Completed",
      "notes": "Good progress"
    }
  ]
}
```

---

## 3. Timetable (`/student/timetable`)

### GET /api/v1/student/timetable

**Query Params:** `academic_year` (optional)

**Response: 200 — `StudentWeeklyTimetableResponse`**
```json
{
  "class_info": {
    "class_name": "10",
    "section": "A",
    "display_label": "10-A"
  },
  "academic_year": "2024-25",
  "current_day": "Monday",
  "is_today_holiday": false,
  "total_periods": 8,
  "periods": [
    {
      "id": "uuid",
      "start_time": "08:00",
      "end_time": "08:45",
      "duration_minutes": 45
    }
  ],
  "timetable": {
    "Monday": [
      {
        "id": "uuid",
        "subject": "Mathematics",
        "teacher": "Mr. Sharma",
        "type": "class",
        "duration_minutes": 45
      }
    ]
  },
  "subject_summary": [
    {
      "subject": "Mathematics",
      "teacher": "Mr. Sharma",
      "sessions_per_week": 5,
      "type": "class"
    }
  ]
}
```

---

### GET /api/v1/student/timetable/day

**Query Params:** `date` (optional, defaults to today)

**Response: 200 — `StudentDayResponse`**
```json
{
  "class_info": {
    "class_name": "10",
    "section": "A",
    "display_label": "10-A"
  },
  "date": "2024-01-15",
  "day": "Monday",
  "is_today": true,
  "is_holiday": false,
  "periods": [
    {
      "id": "uuid",
      "subject": "Mathematics",
      "teacher": "Mr. Sharma",
      "start_time": "08:00",
      "end_time": "08:45",
      "duration_minutes": 45,
      "type": "class"
    }
  ]
}
```

---

## 4. Attendance (`/student/attendance`)

### GET /api/v1/student/attendance

**Query Params:** `academic_year` (optional), `month` (optional, YYYY-MM format)

**Response: 200 — `StudentAttendanceOverviewResponse`**
```json
{
  "academic_year": "2024-25",
  "overall": {
    "percentage": 92.5,
    "present_days": 185,
    "absent_days": 10,
    "late_days": 3,
    "excused_days": 2,
    "total_days": 200,
    "threshold": 75,
    "status": "above_threshold"
  },
  "stats": {
    "present": 185,
    "absent": 10,
    "late": 3,
    "excused": 2
  },
  "distribution": {
    "present": 185,
    "absent": 10,
    "late": 3,
    "excused": 2
  },
  "warning": {
    "active": false,
    "type": "none",
    "message": "",
    "severity": "info"
  },
  "subject_wise": [
    {
      "subject": "Mathematics",
      "percentage": 95.0,
      "present": 38,
      "total": 40,
      "color": "#4CAF50",
      "metadata": {}
    }
  ],
  "recent_records": [
    {
      "date": "2024-01-15",
      "subject": "Mathematics",
      "status": "Present",
      "period": 1,
      "metadata": {}
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/attendance/history

**Query Params:** `page`, `page_size`, `subject` (optional), `month` (optional), `status` (optional)

**Response: 200 — `StudentAttendanceHistoryResponse`**
```json
{
  "count": 200,
  "page": 1,
  "page_size": 20,
  "total_pages": 10,
  "filters": {
    "subject": null,
    "month": null,
    "status": null
  },
  "results": [
    {
      "id": "uuid",
      "date": "2024-01-15",
      "subject": "Mathematics",
      "period": 1,
      "status": "Present",
      "marked_by": "Mr. Sharma",
      "remarks": null,
      "metadata": {}
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/attendance/warnings

**Query Params:** `academic_year` (optional)

**Response: 200 — `StudentAttendanceWarningsResponse`**
```json
{
  "academic_year": "2024-25",
  "threshold": 75,
  "current_percentage": 72.0,
  "status": "below_threshold",
  "warnings": [
    {
      "id": "warn-001",
      "type": "low_attendance",
      "severity": "critical",
      "message": "Attendance below 75% threshold",
      "issued_date": "2024-01-10",
      "active": true,
      "acknowledged": false,
      "metadata": {}
    }
  ],
  "subjects_at_risk": [
    {
      "subject": "Physics",
      "percentage": 68.0,
      "present": 17,
      "total": 25,
      "deficit": 2,
      "message": "Need 2 more classes to reach threshold",
      "metadata": {}
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/attendance/summary

Alias for `GET /student/attendance`. Same response schema (`StudentAttendanceOverviewResponse`).

---

### GET /api/v1/student/attendance/monthly

**Query Params:** `month` (optional, YYYY-MM)

Same response schema as overview, scoped to a specific month.

---

## 5. Assignments (`/student/assignments`)

### GET /api/v1/student/assignments

**Query Params:** `page`, `page_size`, `status` (optional), `subject` (optional), `academic_year` (optional)

**Response: 200 — `StudentAssignmentListResponse`**
```json
{
  "count": 15,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "summary": {
    "total": 15,
    "pending": 3,
    "overdue": 1,
    "submitted": 8,
    "graded": 6,
    "late": 2
  },
  "results": [
    {
      "id": "uuid",
      "title": "Chapter 5 Problems",
      "subject": "Mathematics",
      "teacher": "Mr. Sharma",
      "description": "Solve all exercises",
      "assigned_date": "2024-01-10",
      "due_date": "2024-01-20",
      "max_marks": 50.0,
      "marks_obtained": null,
      "status": "Pending",
      "is_overdue": false,
      "metadata": {}
    }
  ]
}
```

---

### GET /api/v1/student/assignments/{assignment_id}

**Response: 200 — `StudentAssignmentDetailResponse`**
```json
{
  "id": "uuid",
  "title": "Chapter 5 Problems",
  "subject": "Mathematics",
  "teacher": "Mr. Sharma",
  "description": "Solve all exercises from chapter 5",
  "assigned_date": "2024-01-10",
  "due_date": "2024-01-20",
  "max_marks": 50.0,
  "marks_obtained": null,
  "status": "Pending",
  "is_overdue": false,
  "submission_status": "Not Submitted",
  "attachments": [
    {
      "id": "att-001",
      "filename": "worksheet.pdf",
      "url": "/uploads/worksheet.pdf",
      "size_bytes": 204800,
      "type": "application/pdf"
    }
  ],
  "class_section": "10-A",
  "academic_year": "2024-25",
  "created_at": "2024-01-10T08:00:00Z",
  "updated_at": "2024-01-10T08:00:00Z",
  "metadata": {}
}
```

---

### POST /api/v1/student/assignments/{assignment_id}/submit/

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `comments` | string | No | Submission comments |
| `files` | File[] | No | File attachments |

**Response: 201 — `SubmitAssignmentResponse`**
```json
{
  "id": "uuid",
  "assignment_id": "uuid",
  "status": "Submitted",
  "comments": "Completed all problems",
  "files": [
    {
      "id": "file-001",
      "filename": "solution.pdf",
      "url": "/uploads/solution.pdf",
      "size_bytes": 102400,
      "type": "application/pdf",
      "uploaded_at": "2024-01-18T10:30:00Z"
    }
  ],
  "submitted_at": "2024-01-18T10:30:00Z",
  "is_late": false,
  "metadata": {}
}
```

---

### GET /api/v1/student/assignments/{assignment_id}/submission/

**Response: 200 — `StudentSubmissionDetailResponse`**
```json
{
  "id": "uuid",
  "assignment_id": "uuid",
  "assignment_title": "Chapter 5 Problems",
  "subject": "Mathematics",
  "status": "Graded",
  "comments": "Completed all problems",
  "files": [
    {
      "id": "file-001",
      "filename": "solution.pdf",
      "url": "/uploads/solution.pdf",
      "size_bytes": 102400,
      "type": "application/pdf",
      "uploaded_at": "2024-01-18T10:30:00Z"
    }
  ],
  "submitted_at": "2024-01-18T10:30:00Z",
  "is_late": false,
  "grade": {
    "marks_obtained": 45.0,
    "max_marks": 50.0,
    "percentage": 90.0,
    "grade": "A+",
    "graded_by": "Mr. Sharma",
    "graded_at": "2024-01-21T14:00:00Z",
    "feedback": "Excellent work!"
  },
  "metadata": {}
}
```

---

## 6. Results (`/student/results`)

### GET /api/v1/student/results

**Query Params:** `academic_year` (optional)

**Response: 200 — `ResultsOverviewResponse`**
```json
{
  "academic_year": "2024-25",
  "summary": {
    "average_score": 82.5,
    "highest_score": 95.0,
    "lowest_score": 68.0,
    "avg_rank": 5.0
  },
  "filters": {},
  "performance_trend": [
    {
      "exam_name": "Unit Test 1",
      "exam_type": "Unit Test",
      "date": "2024-07-15",
      "percentage": 78.0,
      "subjects": {"Mathematics": 85.0, "Physics": 72.0}
    }
  ],
  "subject_wise_performance": [
    {
      "subject": "Mathematics",
      "student_percentage": 88.0,
      "max_marks": 100.0
    }
  ],
  "performance_radar": {
    "subjects": ["Mathematics", "Physics", "Chemistry"],
    "student_scores": [88.0, 75.0, 82.0],
    "max_marks": 100.0
  },
  "metadata": {}
}
```

---

### GET /api/v1/student/results/exams

**Query Params:** `page`, `page_size`, `exam_type` (optional), `academic_year` (optional)

**Response: 200 — `ExamResultsListResponse`**
```json
{
  "count": 5,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "uuid",
      "exam_name": "Mid-Term",
      "exam_type": "Term Exam",
      "date": "2024-10-15",
      "total_marks_obtained": 425.0,
      "total_max_marks": 500.0,
      "percentage": 85.0,
      "grade": "A",
      "class_rank": 5,
      "total_students": 40,
      "subjects_count": 5,
      "subjects": [
        {
          "subject": "Mathematics",
          "marks_obtained": 92.0,
          "max_marks": 100.0,
          "percentage": 92.0,
          "grade": "A+",
          "rank": 3,
          "status": "Pass",
          "pass_marks": 35.0,
          "leaderboard_url": "/api/v1/student/results/exam/uuid/leaderboard?subject=Mathematics"
        }
      ],
      "metadata": {}
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/results/download-report

**Query Params:** `academic_year` (optional), `exam_id` (optional, UUID)

**Response: 200 — `DownloadReportResponse`**
```json
{
  "download_url": "/reports/student-report-2024.pdf",
  "file_name": "Report_Card_2024-25.pdf",
  "content_type": "application/pdf",
  "generated_at": "2024-01-15T10:00:00Z",
  "report_scope": "full_year",
  "academic_year": "2024-25",
  "metadata": {}
}
```

---

### GET /api/v1/student/results/exam/{exam_id}

**Response: 200 — `ExamDetailResponse`**
```json
{
  "exam_id": "uuid",
  "exam_name": "Mid-Term",
  "exam_type": "Term Exam",
  "date": "2024-10-15",
  "class_section": "10-A",
  "academic_year": "2024-25",
  "total_marks_obtained": 425.0,
  "total_max_marks": 500.0,
  "overall_percentage": 85.0,
  "overall_grade": "A",
  "class_rank": 5,
  "total_students": 40,
  "subjects": [
    {
      "subject": "Mathematics",
      "marks_obtained": 92.0,
      "max_marks": 100.0,
      "percentage": 92.0,
      "grade": "A+",
      "class_average": 72.5,
      "highest_in_class": 98.0,
      "rank": 3,
      "status": "Pass",
      "pass_marks": 35.0
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/results/exam/{exam_id}/leaderboard

**Query Params:** `subject` (optional)

**Response: 200 — `LeaderboardResponse`**
```json
{
  "exam_id": "uuid",
  "exam_name": "Mid-Term",
  "subject": "Mathematics",
  "academic_year": "2024-25",
  "student_rank": 3,
  "student_score": 92.0,
  "max_marks": 100.0,
  "percentile": 92.5,
  "top_performers": [
    {
      "rank": 1,
      "student_name": "Rahul K.",
      "marks_obtained": 98.0,
      "max_marks": 100.0,
      "percentage": 98.0,
      "grade": "A+",
      "is_current_student": false
    }
  ],
  "metadata": {}
}
```

---

## 7. Fees (`/student/fees`)

### GET /api/v1/student/fees

**Query Params:** `academic_year` (optional)

**Response: 200 — `FeeSummaryResponse`**
```json
{
  "academic_year": "2024-25",
  "summary": {
    "total_fees": 75000.00,
    "paid": 50000.00,
    "due": 25000.00,
    "overdue": 10000.00,
    "late_fines": 500.00,
    "currency": "INR"
  },
  "current_dues": [
    {
      "id": "uuid",
      "fee_type": "Tuition Fee",
      "fee_category": "Academic",
      "amount": 15000.00,
      "due_date": "2024-02-01",
      "status": "Pending"
    }
  ],
  "recent_payments": [
    {
      "id": "uuid",
      "fee_type": "Tuition Fee",
      "fee_category": "Academic",
      "amount": 25000.00,
      "currency": "INR",
      "paid_date": "2024-01-05",
      "method": "Online",
      "receipt_id": "REC-2024-001",
      "status": "Completed"
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/fees/structure

**Query Params:** `academic_year` (optional)

**Response: 200 — `FeeStructureResponse`**
```json
{
  "academic_year": "2024-25",
  "components": [
    {
      "id": "uuid",
      "fee_component": "Tuition Fee",
      "fee_category": "Academic",
      "amount": 50000.00,
      "currency": "INR",
      "frequency": "Quarterly",
      "metadata": {}
    }
  ],
  "total_annual_fee": 75000.00,
  "currency": "INR",
  "metadata": {}
}
```

---

### GET /api/v1/student/fees/dues

**Query Params:** `page`, `page_size`, `academic_year` (optional)

**Response: 200 — `FeeDuesResponse`**
```json
{
  "count": 3,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "total_due": 25000.00,
  "currency": "INR",
  "results": [
    {
      "id": "uuid",
      "fee_type": "Tuition Fee",
      "fee_category": "Academic",
      "description": "Q3 Tuition",
      "amount": 15000.00,
      "total_amount": 15000.00,
      "paid_amount": 0.00,
      "balance": 15000.00,
      "currency": "INR",
      "due_date": "2024-02-01",
      "status": "Pending",
      "is_overdue": false,
      "days_until_due": 15,
      "days_overdue": null,
      "pay_now_url": null,
      "receipt_url": null,
      "metadata": {}
    }
  ]
}
```

---

### GET /api/v1/student/fees/history

**Query Params:** `page`, `page_size`, `academic_year` (optional)

**Response: 200 — `PaymentHistoryResponse`**
```json
{
  "count": 10,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "uuid",
      "fee_type": "Tuition Fee",
      "fee_category": "Academic",
      "description": "Q2 Tuition",
      "amount": 15000.00,
      "currency": "INR",
      "paid_date": "2024-01-05",
      "method": "Online",
      "transaction_id": "TXN-123456",
      "receipt_id": "REC-2024-001",
      "receipt_url": "/receipts/REC-2024-001.pdf",
      "status": "Completed",
      "metadata": {}
    }
  ],
  "metadata": {}
}
```

---

### GET /api/v1/student/fees/receipt/{payment_id}

**Response: 200 — `FeeReceiptResponse`**
```json
{
  "payment_id": "uuid",
  "receipt_id": "REC-2024-001",
  "student_name": "Arjun Mehta",
  "roll_number": "STU2024015",
  "class_section": "10-A",
  "fee_type": "Tuition Fee",
  "description": "Q2 Tuition",
  "amount": 15000.00,
  "currency": "INR",
  "paid_date": "2024-01-05",
  "method": "Online",
  "transaction_id": "TXN-123456",
  "school_name": "Delhi Public School",
  "school_address": "Sector 24, Gurugram",
  "download_url": "/receipts/REC-2024-001.pdf",
  "content_type": "application/pdf",
  "generated_at": "2024-01-05T10:30:00Z",
  "metadata": {}
}
```

---

### GET /api/v1/student/fees/reminders

**Response: 200 — `RemindersResponse`**
```json
{
  "count": 2,
  "results": [
    {
      "id": "uuid",
      "message": "Fee payment due on 1st Feb",
      "sent_at": "2024-01-25T09:00:00Z",
      "send_via": "notification",
      "target_group": "class_10A"
    }
  ]
}
```

---

## 8. Library (`/student/library`)

### GET /api/v1/student/library

**Response: 200 — `MyBooksResponse`**
```json
{
  "summary": {
    "total_borrowed": 12,
    "currently_holding": 2,
    "overdue": 0,
    "total_fines": 0.0
  },
  "books": [
    {
      "id": "uuid",
      "title": "Physics NCERT Class 10",
      "author": "NCERT",
      "isbn": "978-81-7450-XXX",
      "issue_date": "2024-01-05",
      "due_date": "2024-01-19",
      "status": "Active",
      "is_overdue": false,
      "fine": 0.0
    }
  ]
}
```

---

### GET /api/v1/student/library/catalog

**Query Params:** `page`, `page_size`, `search` (optional), `category` (optional)

**Response: 200 — `CatalogResponse`**
```json
{
  "count": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8,
  "results": [
    {
      "id": "uuid",
      "title": "Physics NCERT Class 10",
      "author": "NCERT",
      "isbn": "978-81-7450-XXX",
      "category": "Textbook",
      "publisher": "NCERT",
      "available_copies": 3,
      "total_copies": 10
    }
  ]
}
```

---

### GET /api/v1/student/library/history

**Query Params:** `page`, `page_size`

**Response: 200 — `BorrowingHistoryResponse`**
```json
{
  "count": 12,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "uuid",
      "title": "Physics NCERT Class 10",
      "author": "NCERT",
      "issue_date": "2024-01-05",
      "due_date": "2024-01-19",
      "return_date": "2024-01-18",
      "status": "Returned",
      "fine_paid": 0.0
    }
  ]
}
```

---

### GET /api/v1/student/library/fines

**Response: 200 — `FinesResponse`**
```json
{
  "total_fines": 100.0,
  "total_paid": 50.0,
  "total_pending": 50.0,
  "items": [
    {
      "id": "uuid",
      "book_title": "Harry Potter",
      "fine_amount": 50.0,
      "reason": "Late return",
      "date": "2024-01-10",
      "status": "Pending"
    }
  ]
}
```

---

## 9. Notifications (`/student/notifications`)

### GET /api/v1/student/notifications

**Query Params:** `page`, `page_size`, `type` (optional), `is_read` (optional, boolean)

**Response: 200 — `StudentNotificationListResponse`**
```json
{
  "count": 25,
  "page": 1,
  "page_size": 20,
  "total_pages": 2,
  "results": [
    {
      "id": "uuid",
      "notification_id": "uuid",
      "title": "Assignment Due",
      "message": "Math assignment due tomorrow",
      "type": "assignment",
      "is_read": false,
      "read_at": null,
      "sent_at": "2024-01-14T08:00:00Z",
      "created_at": "2024-01-14T08:00:00Z"
    }
  ],
  "unread_count": 5
}
```

---

### GET /api/v1/student/notifications/{notification_id}

**Response: 200 — `StudentNotificationDetailResponse`**
```json
{
  "id": "uuid",
  "notification_id": "uuid",
  "title": "Assignment Due",
  "message": "Math assignment due tomorrow. Please submit before 5 PM.",
  "type": "assignment",
  "send_via": "in_app",
  "is_read": true,
  "read_at": "2024-01-14T10:00:00Z",
  "sent_at": "2024-01-14T08:00:00Z",
  "created_at": "2024-01-14T08:00:00Z"
}
```

---

### PUT /api/v1/student/notifications/{notification_id}/read

**Response: 200 — `MarkReadResponse`**
```json
{
  "id": "uuid",
  "is_read": true,
  "read_at": "2024-01-14T10:00:00Z",
  "message": "Notification marked as read"
}
```

---

## 10. Profile (`/student/profile`)

### GET /api/v1/student/profile

**Response: 200 — `StudentProfileResponse`**
```json
{
  "id": "uuid",
  "roll_number": "STU2024015",
  "full_name": "Arjun Mehta",
  "email": "arjun.mehta@student.com",
  "phone": "9876543210",
  "class_name": "10",
  "section": "A",
  "class_section": "10-A",
  "academic_year": "2024-25",
  "student_type": "Regular",
  "avatar_url": "/avatars/arjun.jpg",
  "avatar_initials": "AM",
  "quick_stats": {
    "attendance_percentage": 92.5,
    "avg_grade": 85.0,
    "pending_assignments": 3,
    "fee_due": 15000.0
  },
  "personal": {
    "date_of_birth": "2008-05-15",
    "gender": "Male",
    "admission_date": "2022-04-01",
    "blood_group": "B+",
    "religion": "Hindu",
    "nationality": "Indian",
    "student_type": "Regular",
    "address": {
      "street": "123 Main St",
      "city": "Gurugram",
      "state": "Haryana",
      "pincode": "122001",
      "country": "India"
    },
    "phone": "9876543210",
    "alternate_phone": null
  },
  "parent": {
    "parent_name": "Suresh Mehta",
    "relationship": "Father",
    "phone": "9876543211",
    "email": "suresh@email.com",
    "occupation": "Engineer",
    "emergency_contact": "9876543211",
    "address": null
  },
  "medical": {
    "blood_group": "B+",
    "gender": "Male",
    "religion": "Hindu",
    "conditions": null,
    "allergies": null,
    "medications": null,
    "doctor_name": null,
    "doctor_phone": null,
    "insurance_id": null
  },
  "transport": {
    "enrolled": true,
    "route_name": "Route 5 - Sector 24",
    "bus_number": "HR-26-1234",
    "pickup_point": "Sector 24 Market",
    "pickup_time": "07:30",
    "drop_time": "14:30",
    "driver_name": "Ram Singh",
    "driver_phone": "9876543299"
  },
  "mentor": {
    "teacher_id": "uuid",
    "name": "Ms. Verma",
    "subject": "Mathematics",
    "qualification": "M.Sc, B.Ed",
    "email": "verma@school.edu",
    "phone": "9876543222"
  },
  "recent_attendance": [
    {
      "id": "att-001",
      "subject": "Mathematics",
      "date": "2024-01-15",
      "status": "Present",
      "metadata": {}
    }
  ],
  "created_at": "2022-04-01T08:00:00Z",
  "updated_at": "2024-01-10T14:00:00Z",
  "metadata": {}
}
```

---

### PUT /api/v1/student/profile

**Request: `UpdateProfileRequest`**
```json
{
  "phone": "9876543210",
  "alternate_phone": "9876543211",
  "address": {
    "street": "456 New St",
    "city": "Gurugram",
    "state": "Haryana",
    "pincode": "122002",
    "country": "India"
  },
  "emergency_contact": "9876543211"
}
```

All fields are optional. Only provided fields are updated.

**Response: 200 — `UpdateProfileResponse`**
```json
{
  "message": "Profile updated successfully",
  "updated_fields": ["phone", "address"],
  "updated_at": "2024-01-15T10:00:00Z",
  "metadata": {}
}
```

---

### GET /api/v1/student/profile/mentor

**Response: 200 — `MentorDetailResponse`**
```json
{
  "teacher_id": "uuid",
  "name": "Ms. Verma",
  "subject": "Mathematics",
  "qualification": "M.Sc, B.Ed",
  "email": "verma@school.edu",
  "phone": "9876543222",
  "avatar_url": "/avatars/verma.jpg",
  "avatar_initials": "SV",
  "designation": "Senior Teacher",
  "experience_years": 12.0,
  "assigned_since": "2024-04-01",
  "total_mentees": 8,
  "available_hours": "Mon-Fri 3:00-4:00 PM",
  "metadata": {}
}
```
