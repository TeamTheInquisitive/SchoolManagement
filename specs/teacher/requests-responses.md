# School ERP Backend - Teacher Portal: Requests & Responses

> Detailed request/response documentation for all Teacher Portal API endpoints.
> For quick endpoint reference, see [teacher-endpoints.md](./teacher-endpoints.md).

---

## 1. Authentication (Shared)

> Auth endpoints are identical to the Admin module. The only difference is the `role` field in responses will be `"teacher"`.

### POST /api/v1/auth/login

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
    "avatar_url": null
  }
}
```

---

## 2. Dashboard (`/teacher/dashboard`)

### GET /api/v1/teacher/dashboard/stats

**Response: 200 — `TeacherDashboardStatsResponse`**
```json
{
  "total_students": 120,
  "pending_reviews": 8,
  "upcoming_exams": 3,
  "classes_today": 5
}
```

---

### GET /api/v1/teacher/dashboard/today-schedule

**Response: 200 — `TodayScheduleResponse`**
```json
{
  "date": "2024-01-15",
  "day": "Monday",
  "total_classes": 5,
  "schedule": [
    {
      "period_number": 1,
      "start_time": "08:00",
      "end_time": "08:45",
      "subject": "Mathematics",
      "class_name": "10",
      "section": "A",
      "slot_type": "Lecture"
    }
  ]
}
```

---

### GET /api/v1/teacher/dashboard/pending-reviews

**Response: 200 — `PendingReviewsResponse`**
```json
{
  "total": 8,
  "items": [
    {
      "id": "uuid",
      "title": "Chapter 5 Homework",
      "class_section": "10-A",
      "subject": "Mathematics",
      "due_date": "2024-01-20",
      "submissions_pending": 15
    }
  ]
}
```

---

### GET /api/v1/teacher/dashboard/upcoming-exams

**Response: 200 — `UpcomingExamsResponse`**
```json
{
  "total": 3,
  "items": [
    {
      "id": "uuid",
      "name": "Unit Test 3",
      "class_section": "10-A",
      "subject": "Mathematics",
      "date": "2024-02-01",
      "total_marks": 50.0
    }
  ]
}
```

---

### GET /api/v1/teacher/dashboard/classes-summary

**Response: 200 — `ClassesSummaryResponse`**
```json
{
  "total_classes": 4,
  "classes": [
    {
      "class_name": "10",
      "section": "A",
      "subject": "Mathematics",
      "student_count": 40,
      "is_class_teacher": true
    }
  ]
}
```

---

### GET /api/v1/teacher/dashboard/leave-updates

**Response: 200 — `LeaveUpdatesResponse`**
```json
{
  "items": [
    {
      "id": "uuid",
      "leave_type": "Casual Leave",
      "from_date": "2024-01-20",
      "to_date": "2024-01-21",
      "days": 2.0,
      "status": "Approved"
    }
  ]
}
```

---

### GET /api/v1/teacher/dashboard/mentees-summary

**Response: 200 — `MenteesSummaryResponse`**
```json
{
  "total": 8,
  "mentees": [
    {
      "student_id": "uuid",
      "name": "Rahul Kumar",
      "class_section": "10-A",
      "attendance_percentage": 92.5
    }
  ]
}
```

---

### GET /api/v1/teacher/dashboard/adhoc-classes

**Response: 200 — `AdhocClassesDashboardResponse`**
```json
{
  "total": 2,
  "items": [
    {
      "id": "uuid",
      "class_name": "10",
      "section": "A",
      "subject": "Mathematics",
      "date": "2024-01-16",
      "type": "Extra",
      "status": "Scheduled"
    }
  ]
}
```

---

### GET /api/v1/teacher/dashboard/profile

**Response: 200**
```json
{
  "id": "uuid",
  "full_name": "Jane Smith",
  "email": "jane@teacher.com",
  "phone": "9876543210",
  "department": "Mathematics",
  "designation": "Senior Teacher",
  "qualification": "M.Sc, B.Ed",
  "experience_years": 12,
  "subjects": ["Mathematics"],
  "class_assignments": ["10-A", "10-B", "9-A"],
  "is_class_teacher": true,
  "class_teacher_of": "10-A",
  "avatar_url": null
}
```

---

### PUT /api/v1/teacher/dashboard/profile

**Request:**
```json
{
  "phone": "9876543211",
  "qualification": "M.Sc, B.Ed, PhD",
  "experience_years": 13
}
```

**Response: 200**
```json
{
  "message": "Profile updated successfully",
  "updated_fields": ["phone", "qualification", "experience_years"]
}
```

---

## 3. Attendance (`/teacher/attendance`)

### GET /api/v1/teacher/attendance

**Query Params:** `class_section_id` (uuid, required), `date` (optional)

**Response: 200 — `GetAttendanceResponse`**
```json
{
  "class_section": "10-A",
  "class_name": "10",
  "section": "A",
  "date": "2024-01-15",
  "is_submitted": true,
  "submitted_at": "2024-01-15T08:30:00Z",
  "summary": {
    "total_students": 40,
    "present": 37,
    "absent": 2,
    "late": 1,
    "attendance_rate": 92.5
  },
  "records": [
    {
      "student_id": "uuid",
      "roll_number": "10A-001",
      "full_name": "Rahul Kumar",
      "status": "Present"
    }
  ]
}
```

---

### POST /api/v1/teacher/attendance

**Request: `SubmitAttendanceRequest`**
```json
{
  "class_id": "uuid",
  "date": "2024-01-15",
  "academic_year": "2024-25",
  "records": [
    {"student_id": "uuid", "status": "Present"},
    {"student_id": "uuid", "status": "Absent"},
    {"student_id": "uuid", "status": "Late"}
  ]
}
```

**Response: 201 — `SubmitAttendanceResponse`**
```json
{
  "message": "Attendance submitted successfully",
  "class_section": "10-A",
  "date": "2024-01-15",
  "summary": {
    "total_students": 40,
    "present": 37,
    "absent": 2,
    "late": 1,
    "attendance_rate": 92.5
  },
  "submitted_at": "2024-01-15T08:30:00Z"
}
```

---

### PUT /api/v1/teacher/attendance

**Request: `UpdateAttendanceRequest`**
```json
{
  "class_id": "uuid",
  "date": "2024-01-15",
  "records": [
    {"student_id": "uuid", "status": "Present"},
    {"student_id": "uuid", "status": "Late"}
  ]
}
```

**Response: 200 — `UpdateAttendanceResponse`**
```json
{
  "message": "Attendance updated successfully",
  "class_section": "10-A",
  "date": "2024-01-15",
  "summary": {
    "total_students": 40,
    "present": 38,
    "absent": 1,
    "late": 1,
    "attendance_rate": 95.0
  },
  "updated_at": "2024-01-15T09:00:00Z"
}
```

---

### GET /api/v1/teacher/attendance/history

**Query Params:** `page`, `page_size`, `class_section_id` (optional), `month` (optional)

**Response: 200 — `AttendanceHistoryResponse`**
```json
{
  "count": 25,
  "page": 1,
  "page_size": 20,
  "total_pages": 2,
  "results": [
    {
      "id": "uuid",
      "class_name": "10",
      "section": "A",
      "class_section": "10-A",
      "date": "2024-01-15",
      "status": "Submitted",
      "total_students": 40,
      "present": 37,
      "absent": 2,
      "late": 1,
      "submitted_at": "2024-01-15T08:30:00Z"
    }
  ]
}
```

---

### DELETE /api/v1/teacher/attendance/{session_id}

**Response: 200 — `CancelAttendanceResponse`**
```json
{
  "id": "uuid",
  "class_section": "10-A",
  "date": "2024-01-15",
  "status": "Cancelled",
  "cancelled_on": "2024-01-15",
  "message": "Attendance session cancelled"
}
```

---

### GET /api/v1/teacher/attendance/summary

**Query Params:** `class_section_id` (required), `month` (optional), `year` (optional)

**Response: 200 — `AttendanceSummaryResponse`**
```json
{
  "class_section": "10-A",
  "month": 1,
  "year": 2024,
  "academic_year": "2024-25",
  "working_days": 22,
  "days_marked": 20,
  "average_attendance_percentage": 91.5,
  "students_below_75": [
    {
      "student_id": "uuid",
      "full_name": "Amit Singh",
      "roll_number": "10A-015",
      "attendance_percentage": 68.0
    }
  ]
}
```

---

## 4. Grades (`/teacher/grades`)

### GET /api/v1/teacher/grades

**Query Params:** `class_id` (uuid), `exam_id` (uuid), `page`, `page_size`

**Response: 200 — `GradesListResponse`**
```json
{
  "count": 40,
  "page": 1,
  "page_size": 50,
  "total_pages": 1,
  "class_section": "10-A",
  "exam_name": "Mid-Term",
  "exam_type": "Term Exam",
  "subject": "Mathematics",
  "max_marks": 100.0,
  "is_published": false,
  "stats": {
    "class_average": 72.5,
    "highest_score": 98.0,
    "lowest_score": 35.0,
    "pass_rate": 87.5,
    "total_students": 40,
    "graded_count": 38
  },
  "results": [
    {
      "student_id": "uuid",
      "roll_number": "10A-001",
      "full_name": "Rahul Kumar",
      "marks": 92.0,
      "total_marks": 100.0,
      "percentage": 92.0,
      "grade": "A+",
      "status": "Pass"
    }
  ]
}
```

---

### POST /api/v1/teacher/grades

**Request: `SubmitGradesRequest`**
```json
{
  "class_id": "uuid",
  "exam_id": "uuid",
  "academic_year": "2024-25",
  "grades": [
    {"student_id": "uuid", "marks": 92.0},
    {"student_id": "uuid", "marks": 85.0}
  ]
}
```

**Response: 201 — `SubmitGradesResponse`**
```json
{
  "message": "Grades submitted successfully",
  "class_section": "10-A",
  "exam_name": "Mid-Term",
  "subject": "Mathematics",
  "total_graded": 40,
  "summary": {
    "highest": 98.0,
    "lowest": 35.0,
    "average": 72.5,
    "max_marks": 100.0
  },
  "saved_at": "2024-01-20T14:00:00Z"
}
```

---

### PUT /api/v1/teacher/grades

**Request: `UpdateGradesRequest`**
```json
{
  "class_id": "uuid",
  "exam_id": "uuid",
  "grades": [
    {"student_id": "uuid", "marks": 93.0}
  ]
}
```

**Response: 200 — `UpdateGradesResponse`**
```json
{
  "message": "Grades updated successfully",
  "class_section": "10-A",
  "exam_name": "Mid-Term",
  "updated_count": 1,
  "updated_at": "2024-01-20T15:00:00Z"
}
```

---

### GET /api/v1/teacher/grades/exams

**Query Params:** `class_id` (optional), `academic_year` (optional)

**Response: 200 — `ExamsForGradingResponse`**
```json
{
  "results": [
    {
      "id": "uuid",
      "name": "Mid-Term",
      "exam_type": "Term Exam",
      "class_section": "10-A",
      "subject": "Mathematics",
      "date": "2024-10-15",
      "max_marks": 100.0,
      "is_graded": true,
      "graded_count": 38,
      "total_students": 40
    }
  ]
}
```

---

### GET /api/v1/teacher/grades/report

**Query Params:** `class_id` (uuid), `exam_id` (uuid)

**Response: 200 — `GradeReportResponse`**
```json
{
  "exam_name": "Mid-Term",
  "class_section": "10-A",
  "subject": "Mathematics",
  "max_marks": 100.0,
  "stats": {
    "class_average": 72.5,
    "highest_score": 98.0,
    "lowest_score": 35.0,
    "pass_rate": 87.5,
    "total_students": 40,
    "graded_count": 38
  },
  "marks_distribution": [
    {"range": "90-100", "count": 5},
    {"range": "80-89", "count": 10},
    {"range": "70-79", "count": 12}
  ],
  "grade_distribution": [
    {"grade": "A+", "count": 5, "percentage": 12.5},
    {"grade": "A", "count": 10, "percentage": 25.0}
  ]
}
```

---

### GET /api/v1/teacher/grades/leaderboard

**Query Params:** `class_id` (uuid), `exam_id` (uuid)

**Response: 200 — `LeaderboardResponse`**
```json
{
  "exam_name": "Mid-Term",
  "class_section": "10-A",
  "subject": "Mathematics",
  "max_marks": 100.0,
  "leaderboard": [
    {
      "rank": 1,
      "roll_number": "10A-005",
      "student_name": "Priya S.",
      "marks": 98.0,
      "percentage": 98.0,
      "grade": "A+"
    }
  ]
}
```

---

### POST /api/v1/teacher/grades/import

**Request:** `multipart/form-data` with CSV file

**Response: 200 — `ImportGradesResponse`**
```json
{
  "imported": 35,
  "skipped": 3,
  "errors": [{"row": 12, "message": "Student not found"}],
  "message": "35 grades imported, 3 skipped"
}
```

---

### GET /api/v1/teacher/grades/export

**Query Params:** `class_id` (uuid), `exam_id` (uuid)

**Response:** CSV file download

---

## 5. Assignments (`/teacher/assignments`)

### GET /api/v1/teacher/assignments

**Query Params:** `page`, `page_size`, `class_name` (optional), `section` (optional), `status` (optional), `academic_year` (optional)

**Response: 200 — `AssignmentListResponse`**
```json
{
  "count": 12,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "summary": {
    "total_assignments": 12,
    "active": 8,
    "graded": 3,
    "to_review": 5
  },
  "results": [
    {
      "id": "uuid",
      "title": "Chapter 5 Problems",
      "description": "Solve exercises 1-20",
      "class_name": "10",
      "section": "A",
      "class_section": "10-A",
      "subject": "Mathematics",
      "due_date": "2024-01-20",
      "max_marks": 50.0,
      "total_students": 40,
      "submissions_count": 25,
      "graded_count": 10,
      "status": "Active",
      "created_at": "2024-01-10T08:00:00Z",
      "is_active": true,
      "metadata": {}
    }
  ]
}
```

---

### POST /api/v1/teacher/assignments

**Request: `CreateAssignmentRequest`**
```json
{
  "title": "Chapter 5 Problems",
  "description": "Solve exercises 1-20",
  "class_name": "10",
  "section": "A",
  "due_date": "2024-01-20",
  "max_marks": 50.0,
  "academic_year": "2024-25"
}
```

**Response: 201 — `AssignmentCreateResponse`**
```json
{
  "id": "uuid",
  "title": "Chapter 5 Problems",
  "description": "Solve exercises 1-20",
  "class_name": "10",
  "section": "A",
  "class_section": "10-A",
  "subject": "Mathematics",
  "due_date": "2024-01-20",
  "max_marks": 50.0,
  "total_students": 40,
  "submissions_count": 0,
  "graded_count": 0,
  "status": "Active",
  "created_at": "2024-01-10T08:00:00Z",
  "is_active": true,
  "academic_year": "2024-25",
  "metadata": {}
}
```

---

### GET /api/v1/teacher/assignments/{assignment_id}

**Response: 200 — `AssignmentDetailResponse`**
```json
{
  "id": "uuid",
  "title": "Chapter 5 Problems",
  "description": "Solve exercises 1-20",
  "class_id": "uuid",
  "class_section": "10-A",
  "subject": "Mathematics",
  "due_date": "2024-01-20",
  "max_marks": 50.0,
  "status": "Active",
  "created_at": "2024-01-10T08:00:00Z",
  "updated_at": "2024-01-10T08:00:00Z",
  "is_active": true,
  "academic_year": "2024-25",
  "submission_stats": {
    "total_students": 40,
    "submitted": 25,
    "not_submitted": 15,
    "graded": 10,
    "average_marks": 42.5
  },
  "metadata": {}
}
```

---

### PUT /api/v1/teacher/assignments/{assignment_id}

**Request: `UpdateAssignmentRequest`**
```json
{
  "title": "Chapter 5 & 6 Problems",
  "due_date": "2024-01-25",
  "max_marks": 60.0
}
```

**Response: 200 — `AssignmentUpdateResponse`**
```json
{
  "id": "uuid",
  "title": "Chapter 5 & 6 Problems",
  "description": "Solve exercises 1-20",
  "class_id": "uuid",
  "class_section": "10-A",
  "subject": "Mathematics",
  "due_date": "2024-01-25",
  "max_marks": 60.0,
  "status": "Active",
  "created_at": "2024-01-10T08:00:00Z",
  "updated_at": "2024-01-12T10:00:00Z",
  "is_active": true,
  "academic_year": "2024-25",
  "metadata": {}
}
```

---

### DELETE /api/v1/teacher/assignments/{assignment_id}

**Response: 200 — `AssignmentDeleteResponse`**
```json
{
  "message": "Assignment deactivated",
  "id": "uuid",
  "deactivated_on": "2024-01-12T10:00:00Z"
}
```

---

### GET /api/v1/teacher/assignments/{assignment_id}/submissions

**Query Params:** `page`, `page_size`, `status` (optional)

**Response: 200 — `SubmissionListResponse`**
```json
{
  "count": 25,
  "page": 1,
  "page_size": 20,
  "total_pages": 2,
  "assignment_id": "uuid",
  "assignment_title": "Chapter 5 Problems",
  "class_section": "10-A",
  "total_students": 40,
  "submissions_count": 25,
  "results": [
    {
      "id": "uuid",
      "student_id": "uuid",
      "student_name": "Rahul Kumar",
      "roll_number": "10A-001",
      "submitted_at": "2024-01-18T10:30:00Z",
      "status": "Submitted",
      "marks": null,
      "max_marks": 50.0,
      "graded_at": null
    }
  ]
}
```

---

### POST /api/v1/teacher/assignments/{assignment_id}/submissions/{submission_id}/grade

**Request: `GradeSubmissionRequest`**
```json
{
  "marks": 45.0,
  "feedback": "Excellent work on problems 1-15"
}
```

**Response: 200 — `GradeSubmissionResponse`**
```json
{
  "id": "uuid",
  "student_name": "Rahul Kumar",
  "marks": 45.0,
  "max_marks": 50.0,
  "feedback": "Excellent work on problems 1-15",
  "status": "Graded",
  "graded_at": "2024-01-21T14:00:00Z",
  "message": "Submission graded successfully"
}
```

---

## 6. Adhoc Classes (`/teacher/adhoc-classes`)

### GET /api/v1/teacher/adhoc-classes

**Query Params:** `page`, `page_size`, `type` (optional), `status` (optional), `from_date` (optional), `to_date` (optional)

**Response: 200 — `AdhocClassListResponse`**
```json
{
  "count": 5,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "uuid",
      "staff_id": "uuid",
      "class_name": "10",
      "section": "A",
      "subject": "Mathematics",
      "date": "2024-01-16",
      "start_time": "14:00:00",
      "end_time": "14:45:00",
      "duration_minutes": 45,
      "type": "Extra",
      "reason": "Doubt clearing session",
      "original_staff_id": null,
      "topic": "Quadratic Equations",
      "notes": null,
      "description": null,
      "student_count": 35,
      "status": "Completed",
      "created_at": "2024-01-14T10:00:00Z"
    }
  ]
}
```

---

### POST /api/v1/teacher/adhoc-classes

**Request: `AdhocClassCreateRequest`**
```json
{
  "class_name": "10",
  "section": "A",
  "subject": "Mathematics",
  "date": "2024-01-18",
  "start_time": "14:00:00",
  "end_time": "14:45:00",
  "duration_minutes": 45,
  "type": "Extra",
  "reason": "Doubt clearing session",
  "topic": "Quadratic Equations",
  "student_count": 35
}
```

**Response: 201 — `AdhocClassResponse`** (same structure as list item)

---

### PUT /api/v1/teacher/adhoc-classes/{adhoc_id}

**Request: `AdhocClassUpdateRequest`**
```json
{
  "status": "Completed",
  "student_count": 32,
  "notes": "All doubts cleared"
}
```

**Response: 200 — `AdhocClassResponse`**

---

### DELETE /api/v1/teacher/adhoc-classes/{adhoc_id}

**Response: 200 — `AdhocClassDeleteResponse`**
```json
{
  "id": "uuid",
  "status": "Cancelled",
  "message": "Adhoc class cancelled"
}
```

---

## 7. Leaves (`/teacher/leaves`)

### GET /api/v1/teacher/leaves/balance

**Response: 200 — `LeaveBalanceResponse`**
```json
{
  "academic_year": "2024-25",
  "balances": [
    {
      "leave_type": "Casual Leave",
      "total_allocated": 12,
      "available": 8.0,
      "used": 3.0,
      "pending": 1.0
    },
    {
      "leave_type": "Sick Leave",
      "total_allocated": 10,
      "available": 9.0,
      "used": 1.0,
      "pending": 0.0
    }
  ],
  "summary": {
    "total_leaves": 22,
    "available": 17.0,
    "used": 4.0,
    "pending": 1.0
  }
}
```

---

### GET /api/v1/teacher/leaves/upcoming

**Response: 200 — `UpcomingLeavesResponse`**
```json
{
  "results": [
    {
      "id": "uuid",
      "leave_type": "Casual Leave",
      "from_date": "2024-01-25",
      "to_date": "2024-01-26",
      "duration_days": 2.0,
      "reason": "Family function",
      "status": "Approved",
      "applied_on": "2024-01-15T10:00:00Z",
      "approved_by": "Admin",
      "can_cancel": true
    }
  ]
}
```

---

### GET /api/v1/teacher/leaves

**Query Params:** `page`, `page_size`, `status` (optional), `leave_type` (optional), `academic_year` (optional)

**Response: 200 — `LeaveHistoryResponse`**
```json
{
  "count": 10,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "uuid",
      "leave_type": "Casual Leave",
      "from_date": "2024-01-10",
      "to_date": "2024-01-11",
      "duration_days": 2.0,
      "reason": "Personal work",
      "status": "Approved",
      "applied_on": "2024-01-05T10:00:00Z",
      "approved_by": "Admin",
      "approved_on": "2024-01-06T09:00:00Z",
      "remarks": null,
      "metadata": {}
    }
  ]
}
```

---

### POST /api/v1/teacher/leaves

**Request: `ApplyLeaveRequest`**
```json
{
  "leave_type": "Casual Leave",
  "from_date": "2024-01-25",
  "to_date": "2024-01-26",
  "reason": "Family function",
  "is_half_day": false,
  "academic_year": "2024-25"
}
```

**Response: 201 — `ApplyLeaveResponse`**
```json
{
  "id": "uuid",
  "leave_type": "Casual Leave",
  "from_date": "2024-01-25",
  "to_date": "2024-01-26",
  "duration_days": 2.0,
  "reason": "Family function",
  "status": "Pending",
  "applied_on": "2024-01-15T10:00:00Z",
  "approved_by": null,
  "approved_on": null,
  "remarks": null,
  "academic_year": "2024-25",
  "metadata": {}
}
```

---

### GET /api/v1/teacher/leaves/{leave_id}

**Response: 200 — `LeaveDetailResponse`**
```json
{
  "id": "uuid",
  "leave_type": "Casual Leave",
  "from_date": "2024-01-25",
  "to_date": "2024-01-26",
  "duration_days": 2.0,
  "reason": "Family function",
  "status": "Approved",
  "applied_on": "2024-01-15T10:00:00Z",
  "approved_by": "Admin",
  "approved_on": "2024-01-16T09:00:00Z",
  "remarks": null,
  "substitute_teacher": "Mr. Verma",
  "academic_year": "2024-25",
  "metadata": {}
}
```

---

### DELETE /api/v1/teacher/leaves/{leave_id}

**Response: 200 — `CancelLeaveResponse`**
```json
{
  "message": "Leave cancelled successfully",
  "id": "uuid",
  "status": "Cancelled",
  "cancelled_on": "2024-01-16T10:00:00Z"
}
```

---

## 8. Students (`/teacher/students`)

### GET /api/v1/teacher/students

**Query Params:** `page`, `page_size`, `class_name` (optional), `section` (optional), `search` (optional)

**Response: 200 — `TeacherStudentListResponse`**
```json
{
  "count": 120,
  "page": 1,
  "page_size": 20,
  "total_pages": 6,
  "results": [
    {
      "id": "uuid",
      "roll_number": "10A-001",
      "full_name": "Rahul Kumar",
      "email": "rahul@student.com",
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

### GET /api/v1/teacher/students/mentees

**Response: 200 — `TeacherMenteesResponse`**
```json
{
  "total": 8,
  "mentees": [
    {
      "id": "uuid",
      "roll_number": "10A-001",
      "full_name": "Rahul Kumar",
      "email": "rahul@student.com",
      "phone": "9876543210",
      "class_name": "10",
      "section": "A",
      "class_section": "10-A",
      "avatar_url": null,
      "assigned_date": "2024-04-01"
    }
  ]
}
```

---

### GET /api/v1/teacher/students/{student_id}

**Response: 200 — `TeacherStudentDetailResponse`**
```json
{
  "id": "uuid",
  "roll_number": "10A-001",
  "full_name": "Rahul Kumar",
  "email": "rahul@student.com",
  "phone": "9876543210",
  "class_name": "10",
  "section": "A",
  "class_section": "10-A",
  "date_of_birth": "2008-05-15",
  "gender": "Male",
  "admission_date": "2022-04-01",
  "student_type": "Regular",
  "blood_group": "B+",
  "religion": "Hindu",
  "address": "123 Main St, Gurugram",
  "avatar_url": null,
  "status": "Active",
  "is_active": true,
  "quick_stats": {
    "attendance_percentage": 92.5,
    "average_grade": "A",
    "assignments_submitted": 12,
    "fee_due": 15000.0
  },
  "personal_info": {...},
  "parent_info": {...},
  "medical_info": {...},
  "transport_info": {...},
  "assigned_mentor": {...},
  "academic_summary": {...},
  "behavior_conduct": {...},
  "metadata": {}
}
```

---

### GET /api/v1/teacher/students/{student_id}/exam-results

**Response: 200 — `TeacherStudentExamResultsResponse`**
```json
{
  "student_id": "uuid",
  "student_name": "Rahul Kumar",
  "academic_year": "2024-25",
  "exams": [
    {
      "id": "uuid",
      "exam_name": "Mid-Term",
      "exam_type": "Term Exam",
      "date": "2024-10-15",
      "results": [
        {"subject": "Mathematics", "marks": 92.0, "max_marks": 100.0, "grade": "A+", "percentage": 92.0}
      ],
      "total_marks": 425.0,
      "total_max_marks": 500.0,
      "overall_percentage": 85.0,
      "overall_grade": "A"
    }
  ],
  "performance_analysis": {
    "subject_wise_marks": [],
    "subject_strengths_radar": [],
    "performance_trend_over_time": []
  }
}
```

---

### GET /api/v1/teacher/students/{student_id}/parent-meetings

**Response: 200 — `TeacherStudentMeetingsResponse`**
```json
{
  "count": 3,
  "page": 1,
  "page_size": 10,
  "total_pages": 1,
  "results": [
    {
      "id": "uuid",
      "meeting_type": "PTM",
      "date": "2024-01-10",
      "conducted_by": "Ms. Smith",
      "attendee": "Suresh Kumar (Father)",
      "notes": "Good progress in academics",
      "attendance_status": "Attended",
      "follow_up_required": false,
      "metadata": {}
    }
  ]
}
```

---

### GET /api/v1/teacher/students/{student_id}/activities

**Response: 200 — `TeacherStudentActivitiesResponse`**
```json
{
  "activities": [
    {"id": "uuid", "activity_name": "Chess Club", "year_joined": 2023, "role": "Member", "is_active": true}
  ],
  "awards": [
    {"id": "uuid", "award_name": "Best in Mathematics", "category": "Academic", "year": 2024, "description": "Class topper"}
  ]
}
```

---

### GET /api/v1/teacher/students/{student_id}/fee-summary

**Response: 200 — `TeacherStudentFeeSummaryResponse`**
```json
{
  "student_id": "uuid",
  "student_name": "Rahul Kumar",
  "academic_year": "2024-25",
  "summary": {"total": 75000, "paid": 50000, "due": 25000},
  "fee_structure": [
    {"component": "Tuition", "amount": 50000.0, "frequency": "Quarterly"}
  ],
  "recent_payments": [
    {"date": "2024-01-05", "amount": 15000.0, "method": "Online", "status": "Completed", "reference": "TXN-123"}
  ]
}
```

---

### GET /api/v1/teacher/students/{student_id}/behavior

**Response: 200 — `TeacherStudentBehaviorResponse`**
```json
{
  "student_id": "uuid",
  "student_name": "Rahul Kumar",
  "behavior_summary": {
    "overall_rating": "Good",
    "discipline_percentage": 95.0,
    "punctuality_percentage": 90.0
  },
  "recent_conduct_notes": [
    {"id": "uuid", "note": "Excellent participation", "subject": "Mathematics", "noted_by": "Ms. Smith", "date": "2024-01-12", "type": "Positive"}
  ],
  "disciplinary_records": [],
  "has_clean_record": true,
  "metadata": {}
}
```

---

### GET /api/v1/teacher/students/{student_id}/recent-attendance

**Response: 200 — `TeacherStudentAttendanceResponse`**
```json
{
  "student_id": "uuid",
  "student_name": "Rahul Kumar",
  "records": [
    {"date": "2024-01-15", "subject": "Mathematics", "status": "Present"},
    {"date": "2024-01-14", "subject": "Physics", "status": "Present"}
  ]
}
```

---

### GET /api/v1/teacher/students/{student_id}/assignments

**Query Params:** `page`, `page_size`, `status` (optional)

**Response: 200 — `TeacherStudentAssignmentsResponse`**
```json
{
  "student_id": "uuid",
  "student_name": "Rahul Kumar",
  "count": 12,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [...]
}
```

---

### PUT /api/v1/teacher/students/{student_id}

**Request:** (mentor notes/update)
```json
{
  "mentor_notes": "Needs extra attention in Physics"
}
```

**Response: 200**
```json
{
  "message": "Student updated successfully"
}
```

---

## 9. Notifications (`/teacher/notifications`)

### GET /api/v1/teacher/notifications

**Query Params:** `page`, `page_size`, `type` (optional), `is_read` (optional)

**Response: 200 — `StudentNotificationListResponse` (shared schema)**
```json
{
  "count": 15,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "uuid",
      "notification_id": "uuid",
      "title": "Leave Approved",
      "message": "Your casual leave has been approved",
      "type": "leave",
      "is_read": false,
      "read_at": null,
      "sent_at": "2024-01-16T09:00:00Z",
      "created_at": "2024-01-16T09:00:00Z"
    }
  ],
  "unread_count": 3
}
```

---

### GET /api/v1/teacher/notifications/{notification_id}

**Response: 200 — `StudentNotificationDetailResponse`**
```json
{
  "id": "uuid",
  "notification_id": "uuid",
  "title": "Leave Approved",
  "message": "Your casual leave for 25-26 Jan has been approved by Admin",
  "type": "leave",
  "send_via": "in_app",
  "is_read": true,
  "read_at": "2024-01-16T10:00:00Z",
  "sent_at": "2024-01-16T09:00:00Z",
  "created_at": "2024-01-16T09:00:00Z"
}
```

---

### PUT /api/v1/teacher/notifications/{notification_id}/read

**Response: 200 — `MarkReadResponse`**
```json
{
  "id": "uuid",
  "is_read": true,
  "read_at": "2024-01-16T10:00:00Z",
  "message": "Notification marked as read"
}
```

---

## 10. Timetable (`/teacher/timetable`)

### GET /api/v1/teacher/timetable

**Query Params:** `academic_year` (optional)

**Response: 200 — `TeacherWeeklyTimetableResponse`**
```json
{
  "academic_year": "2024-25",
  "stats": {
    "total_classes_per_week": 25,
    "practical_sessions": 3,
    "free_periods": 10
  },
  "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
  "timetable": {
    "Monday": [
      {
        "id": "uuid",
        "start_time": "08:00",
        "end_time": "08:45",
        "duration_minutes": 45,
        "subject": "Mathematics",
        "type": "Lecture",
        "class_name": "10",
        "section": "A",
        "class_section": "10-A",
        "label": null
      }
    ]
  }
}
```

---

### GET /api/v1/teacher/timetable/today

**Query Params:** `date` (optional, defaults to today)

**Response: 200 — `TeacherTodayResponse`**
```json
{
  "date": "2024-01-15",
  "day": "Monday",
  "stats": {
    "total_classes_today": 5,
    "practical_sessions_today": 1,
    "free_periods_today": 3
  },
  "schedule": [
    {
      "id": "uuid",
      "start_time": "08:00",
      "end_time": "08:45",
      "duration_minutes": 45,
      "subject": "Mathematics",
      "type": "Lecture",
      "class_name": "10",
      "section": "A",
      "class_section": "10-A",
      "label": null
    }
  ]
}
```
