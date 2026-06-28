# Super Admin API - Request/Response Schemas

**Last Updated: 2026-06-28**

## Dashboard

### DashboardStatsResponse
```json
{
  "total_schools": "int",
  "total_students": "int",
  "total_staff": "int",
  "total_income": "float",
  "active_subscriptions": "int",
  "mrr": "float (Monthly Recurring Revenue)",
  "expiring_in_7_days": "int",
  "expiring_in_30_days": "int"
}
```

---

## Schools

### SchoolCreate (POST /superadmin/schools)
```json
{
  "name": "string (required)",
  "code": "string | null (auto-generated if omitted)",
  "city": "string | null",
  "state": "string | null",
  "address_line1": "string | null",
  "phone": "string | null",
  "email": "string | null",
  "board_affiliation": "string | null",
  "principal_name": "string | null",
  "enrollment_date": "date | null",
  "trial_start_date": "date | null",
  "trial_end_date": "date | null"
}
```

### SchoolUpdate (PUT /superadmin/schools/{id})
```json
{
  "name": "string | null",
  "city": "string | null",
  "state": "string | null",
  "address_line1": "string | null",
  "phone": "string | null",
  "email": "string | null",
  "board_affiliation": "string | null",
  "principal_name": "string | null",
  "is_active": "bool | null"
}
```

### SchoolListResponse
```json
{
  "schools": [
    {
      "id": "UUID",
      "name": "string",
      "code": "string",
      "city": "string | null",
      "student_count": "int",
      "staff_count": "int",
      "is_active": "bool",
      "subscription_status": "string (active|trial|expired|cancelled)",
      "enrollment_date": "date | null",
      "trial_end_date": "date | null",
      "created_at": "datetime | null"
    }
  ],
  "total": "int"
}
```

### SchoolDetailResponse
```json
{
  "id": "UUID",
  "name": "string",
  "code": "string",
  "logo_url": "string | null",
  "city": "string | null",
  "state": "string | null",
  "address_line1": "string | null",
  "phone": "string | null",
  "email": "string | null",
  "board_affiliation": "string | null",
  "principal_name": "string | null",
  "is_active": "bool",
  "created_at": "datetime | null",
  "enrollment_date": "date | null",
  "subscription_status": "string",
  "trial_start_date": "date | null",
  "trial_end_date": "date | null",
  "student_count": "int",
  "staff_count": "int",
  "admin_users": "list[UserItem]",
  "subscription": "SubscriptionResponse | null"
}
```

### HardDeleteResponse
```json
{
  "school_id": "UUID",
  "school_name": "string",
  "deleted_tables": "dict[str, int] (table_name → count deleted)",
  "total_records_deleted": "int"
}
```

---

## Subscription Status

### SubscriptionStatusUpdate (PUT /superadmin/schools/{id}/subscription-status)
```json
{
  "subscription_status": "string | null (active|trial|expired|cancelled)",
  "trial_start_date": "date | null",
  "trial_end_date": "date | null",
  "enrollment_date": "date | null"
}
```

---

## Subscriptions

### SubscriptionCreate (POST /superadmin/schools/{id}/subscription)
```json
{
  "plan_type": "string (required: monthly|yearly)",
  "amount": "decimal (required)",
  "start_date": "date (required)",
  "end_date": "date (required)",
  "auto_renew": "bool (default: true)"
}
```

### SubscriptionUpdate (PUT /superadmin/schools/{id}/subscription)
```json
{
  "plan_type": "string | null",
  "amount": "decimal | null",
  "start_date": "date | null",
  "end_date": "date | null",
  "auto_renew": "bool | null"
}
```

### SubscriptionResponse
```json
{
  "id": "UUID",
  "plan_type": "string",
  "amount": "float",
  "start_date": "date",
  "end_date": "date",
  "auto_renew": "bool",
  "is_active": "bool",
  "created_at": "datetime | null"
}
```

### SubscriptionHistoryResponse
```json
{
  "subscriptions": "list[SubscriptionResponse]",
  "total": "int"
}
```

---

## Payments

### PaymentCreate (POST /superadmin/schools/{id}/payments)
```json
{
  "amount": "decimal (required)",
  "payment_date": "date (required)",
  "period_start": "date (required)",
  "period_end": "date (required)",
  "status": "string (default: paid)",
  "notes": "string | null"
}
```

### PaymentResponse
```json
{
  "id": "UUID",
  "subscription_id": "UUID",
  "amount": "float",
  "payment_date": "date",
  "period_start": "date",
  "period_end": "date",
  "status": "string",
  "notes": "string | null",
  "created_at": "datetime | null"
}
```

### PaymentListResponse
```json
{
  "payments": "list[PaymentResponse]",
  "total": "int"
}
```

---

## Admin User Management

### AdminCreate (POST /superadmin/schools/{id}/admin)
```json
{
  "email": "string (required, valid email)",
  "full_name": "string (required)",
  "password": "string (required)",
  "phone": "string | null"
}
```

### AdminCreate Response
```json
{
  "id": "UUID",
  "email": "string",
  "full_name": "string",
  "role": "admin"
}
```

---

## Platform Settings

### GET /superadmin/settings Response
```json
{
  "key1": "value1",
  "key2": "value2"
}
```

### PUT /superadmin/settings Request
```json
{
  "key1": "new_value1",
  "key2": "new_value2"
}
```

---

## Users

### UserItem
```json
{
  "id": "UUID",
  "email": "string",
  "full_name": "string",
  "role": "string (admin|teacher|student|parent)",
  "phone": "string | null",
  "is_active": "bool",
  "school_name": "string | null",
  "last_login_at": "datetime | null"
}
```

### UserListResponse
```json
{
  "users": "list[UserItem]",
  "total": "int"
}
```

### Unlock User Response (POST /superadmin/users/{id}/unlock)
```json
{
  "message": "User email@school.com unlocked successfully",
  "user_id": "UUID",
  "email": "string"
}
```

### Reset Password Request (POST /superadmin/users/{id}/reset-password)
```json
{
  "password": "string (min 4 chars, required)"
}
```

### Reset Password Response
```json
{
  "message": "Password reset for email@school.com",
  "user_id": "UUID",
  "email": "string"
}
```

---

## Logo Upload

### POST /superadmin/schools/{id}/logo

**Request:** `multipart/form-data`
- Field: `file` (required)
- Allowed MIME: `image/png`, `image/jpeg`, `image/jpg`, `image/webp`
- Allowed extensions: `.png`, `.jpg`, `.jpeg`, `.webp`
- Max size: 2MB

**Response:**
```json
{
  "logo_url": "/uploads/logos/filename.png"
}
```
