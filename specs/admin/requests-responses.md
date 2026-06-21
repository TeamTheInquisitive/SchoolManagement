# Admin API Request/Response Schemas

Last Updated: 2026-06-21

## Students Module

### CreateStudentRequest
```json
{
  "roll_number": "string (required)",
  "full_name": "string (required)",
  "email": "string | null",
  "phone": "string | null (validated: Indian 10-digit)",
  "class_name": "string (required)",
  "section": "string (required)",
  "date_of_birth": "date | null",
  "admission_date": "date | null",
  "gender": "string | null",
  "student_type": "string | null",
  "blood_group": "string | null",
  "religion": "string | null",
  "medical_conditions": "string | null",
  "allergies": "string | null",
  "address": "string | null",
  "address_line2": "string | null",
  "city": "string | null",
  "state": "string | null",
  "pincode": "string | null",
  "parent_name": "string | null",
  "parent_phone": "string | null (validated)",
  "parent_email": "string | null",
  "parent_relationship": "string | null (default: Parent/Guardian)",
  "concessions": "dict[str, float] | null",
  "custom_fees": "list[dict] | null",
  "excluded_fee_ids": "list[str] | null",
  "previous_school": "string | null",
  "token_advance": "float | null",
  "token_payment_method": "string | null",
  "parent_occupation": "string | null",
  "status": "string | null"
}
```

### StudentListResponse
```json
{
  "count": "int",
  "page": "int",
  "page_size": "int",
  "total_pages": "int",
  "results": [StudentListItem],
  "summary": {
    "total": "int",
    "active": "int",
    "inactive": "int"
  }
}
```

### StudentResponse (detail)
```json
{
  "id": "UUID",
  "roll_number": "string",
  "full_name": "string",
  "email": "string | null",
  "phone": "string | null",
  "class_name": "string | null",
  "section": "string | null",
  "status": "string",
  "type": "string | null",
  "gender": "string | null",
  "date_of_birth": "date | null",
  "admission_date": "date | null",
  "address": "string | null",
  "city": "string | null",
  "state": "string | null",
  "pincode": "string | null",
  "parent": { "name", "phone", "email", "emergency_contact", "relationship" },
  "parent_name": "string | null",
  "parent_phone": "string | null",
  "parent_email": "string | null",
  "parent_relationship": "string | null",
  "parent_occupation": "string | null",
  "previous_school": "string | null",
  "token_advance": "any | null",
  "medical": { "blood_group", "religion", "conditions", "allergies" },
  "mentor": { "id", "name", "subject", "qualification", "email", "phone" },
  "class_teacher": { "name", "email", "phone" },
  "stats": { "attendance_percentage", "average_grade", "assignments_submitted/total", "fee_due", "class_rank/strength" },
  "behavior": { "overall_rating", "discipline_score", "punctuality_score" },
  "transport": { "enrolled", "route_name", "route_code", "bus_number", "pickup_point", "drop_point" },
  "created_at": "datetime | null"
}
```

## Teachers Module

### CreateTeacherRequest
```json
{
  "employee_id": "string (required)",
  "full_name": "string (required)",
  "email": "string (required)",
  "phone": "string | null (validated: Indian 10-digit)",
  "gender": "string | null",
  "date_of_birth": "date | null",
  "department": "string | null",
  "designation": "string | null",
  "employment_type": "string | null",
  "joining_date": "date | null",
  "qualification": "string | null",
  "experience_years": "float | null",
  "subjects": "list[str] | null (subject names)",
  "primary_subject": "string | null",
  "max_workload_hours": "int | null",
  "address_line1": "string | null",
  "city": "string | null",
  "state": "string | null",
  "pincode": "string | null",
  "blood_group": "string | null",
  "emergency_contact_name": "string | null",
  "emergency_contact_phone": "string | null",
  "bank_name": "string | null",
  "bank_account_number": "string | null",
  "bank_ifsc": "string | null",
  "pan_number": "string | null",
  "aadhar_number": "string | null",
  "salary": "float | null",
  "basic_salary": "float | null",
  "hra": "float | null",
  "da": "float | null",
  "transport_allowance": "float | null",
  "medical_allowance": "float | null",
  "pf_deduction": "float | null",
  "professional_tax": "float | null",
  "tds": "float | null"
}
```

## Fees Module

### CreateFeeRecordRequest
```json
{
  "student_id": "UUID (required)",
  "fee_type": "string (required)",
  "fee_category": "string (default: academic)",
  "total_amount": "float (required)",
  "due_date": "date (required)",
  "description": "string | null"
}
```

### RecordPaymentRequest
```json
{
  "amount": "float (required)",
  "payment_date": "date (required)",
  "payment_method": "string (required)",
  "reference": "string | null"
}
```

### ApplyLateFeeRequest
```json
{
  "penalty_type": "string (required: fixed/percentage)",
  "amount": "float | null",
  "percentage": "float | null"
}
```

### GenerateDueRequest
```json
{
  "class_section_id": "UUID | null",
  "class_name": "string | null",
  "section": "string | null",
  "due_date": "date (required)"
}
```

### SendReminderRequest
```json
{
  "target_group": "string (required)",
  "class_name": "string | null",
  "section": "string | null",
  "message": "string (required)",
  "send_via": "string (required)"
}
```

## Timetable Module

### CreatePeriodRequest
```json
{
  "name": "string | null",
  "start_time": "time (required, HH:MM)",
  "end_time": "time (required, HH:MM)",
  "is_break": "bool (default: false)",
  "sort_order": "int (default: 0)"
}
```

### CreateSlotRequest
```json
{
  "class_section_id": "UUID (required)",
  "period_config_id": "UUID (required)",
  "day_of_week": "string (required)",
  "subject_id": "UUID | null",
  "staff_id": "UUID | null",
  "slot_type": "string (default: Subject)"
}
```

## Leaves Module

### UpdateLeavePolicyRequest
```json
{
  "policies": [
    {
      "leave_type": "string",
      "display_name": "string | null",
      "code": "string | null",
      "total_per_year": "int",
      "carry_forward": "bool",
      "max_carry_forward": "int | null",
      "max_consecutive_days": "int | null",
      "requires_approval": "bool",
      "half_day_allowed": "bool",
      "medical_certificate_required_after_days": "int | null",
      "advance_notice_days": "int | null",
      "applicable_to": "string (default: all)",
      "members": "list | null"
    }
  ]
}
```

### ApproveLeaveRequest
```json
{
  "remarks": "string | null"
}
```

### RejectLeaveRequest
```json
{
  "remarks": "string (required)"
}
```

## Payroll Module

### RunPayrollRequest
```json
{
  "month": "int (required)",
  "year": "int (required)"
}
```

### GeneratePayslipsRequest
```json
{
  "month": "int (required)",
  "year": "int (required)",
  "staff_ids": "list[UUID] | null"
}
```

## Examinations Module

### CreateExamRequest
```json
{
  "name": "string (required)",
  "exam_type": "string (required)",
  "class_section_id": "UUID (required)",
  "subject_id": "UUID (required)",
  "date": "date | null",
  "start_time": "time | null",
  "end_time": "time | null",
  "total_marks": "float (required)",
  "passing_marks": "float | null",
  "term": "string | null"
}
```

### EnterResultsRequest
```json
{
  "results": [
    {
      "student_id": "UUID (required)",
      "marks_obtained": "float | null",
      "attendance": "string (default: Present)",
      "remarks": "string | null"
    }
  ]
}
```

## Transport Module

### VehicleCreateRequest
```json
{
  "vehicle_number": "string (required)",
  "plate_number": "string | null",
  "type": "string (required)",
  "model": "string | null",
  "year": "int | null",
  "fuel_type": "string | null",
  "capacity": "int (required)",
  "status": "string (default: Operational)",
  "next_service_date": "date | null",
  "insurance_expiry": "date | null",
  "fitness_expiry": "date | null"
}
```

### RouteCreateRequest
```json
{
  "route_code": "string (required)",
  "name": "string (required)",
  "area": "string | null",
  "shift": "string | null",
  "stops": "list[dict] (default: [])",
  "distance_km": "float | null",
  "start_time": "time | null",
  "end_time": "time | null"
}
```

### AssignmentCreateRequest (route assignment)
```json
{
  "route_id": "UUID (required)",
  "vehicle_id": "UUID (required)",
  "driver_id": "UUID (required)",
  "helper_id": "UUID | null"
}
```

## Notifications Module

### NotificationCreateRequest
```json
{
  "title": "string (required)",
  "message": "string (required)",
  "type": "string | null",
  "target_type": "string (required, Literal: all_students/all_teachers/class/section/individual)",
  "target_class_name": "string | null",
  "target_section": "string | null",
  "send_via": "string (default: in_app)"
}
```

## Library Module

### BookCreateRequest
```json
{
  "title": "string (required)",
  "author": "string | null",
  "isbn": "string | null",
  "category": "string | null",
  "publisher": "string | null",
  "total_copies": "int (default: 1)",
  "shelf_location": "string | null"
}
```

### IssueBookRequest
```json
{
  "book_id": "UUID (required)",
  "borrower_id": "UUID (required)",
  "borrower_type": "string (default: student)",
  "due_date": "date (required)"
}
```

## Settings Module

### SchoolProfileUpdateRequest
```json
{
  "name": "string | null",
  "code": "string | null",
  "address_line1": "string | null",
  "address_line2": "string | null",
  "city": "string | null",
  "state": "string | null",
  "country": "string | null",
  "pincode": "string | null",
  "phone": "string | null",
  "email": "string | null",
  "website": "string | null",
  "board_affiliation": "string | null",
  "established_year": "int | null",
  "principal_name": "string | null"
}
```

### ClassesBulkRequest
```json
{
  "classes": ["string (class names)"]
}
```

### SectionsBulkRequest
```json
{
  "sections": ["string (section names)"]
}
```

### SubjectsBulkRequest
```json
{
  "subjects": [
    {
      "name": "string (required)",
      "code": "string | null",
      "description": "string | null"
    }
  ]
}
```
