# School ERP Backend - Super Admin API Endpoints

## Architecture Overview

```
Super Admin API:
├── Runtime: Python (FastAPI)
├── Database: PostgreSQL
├── Auth: JWT (httpOnly cookies) — role: super_admin
├── Multi-tenancy: Super admin can access ALL schools
├── API Style: RESTful, JSON
├── Base URL: /api/v1
├── Prefix: /api/v1/superadmin/...
└── Shared Auth: /api/v1/auth/...
```

### Super Admin Design Principles

1. **Platform-level access** — Super admin is NOT scoped to a single school. They manage all schools, subscriptions, and platform settings.

2. **No X-School-Code header required** — Unlike admin/teacher/student endpoints, super admin endpoints do not require the school code header.

3. **Destructive operations available** — Hard-delete school (irreversible), user password resets, account unlocking.

4. **Subscription management** — Full lifecycle: create school → assign subscription → record payments → manage renewals.

---

## Endpoints

### 1. Dashboard

| Method | Path | Description |
|--------|------|-------------|
| GET | `/superadmin/dashboard/stats` | Platform-wide dashboard statistics |

**Response: `DashboardStatsResponse`**
```json
{
  "total_schools": 12,
  "total_students": 3500,
  "total_staff": 280,
  "total_income": 1500000.00,
  "active_subscriptions": 10,
  "mrr": 125000.00,
  "expiring_in_7_days": 2,
  "expiring_in_30_days": 4
}
```

---

### 2. Schools

| Method | Path | Description |
|--------|------|-------------|
| GET | `/superadmin/schools` | List all schools |
| POST | `/superadmin/schools` | Create a new school |
| GET | `/superadmin/schools/{school_id}` | Get school details |
| PUT | `/superadmin/schools/{school_id}` | Update school |
| DELETE | `/superadmin/schools/{school_id}/hard-delete` | Permanently delete school (all data) |
| POST | `/superadmin/schools/{school_id}/logo` | Upload school logo |

#### POST `/superadmin/schools` — Create School

**Request: `SchoolCreate`**
```json
{
  "name": "string (required)",
  "code": "string | null (auto-generated if empty)",
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

#### PUT `/superadmin/schools/{school_id}` — Update School

**Request: `SchoolUpdate`**
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

#### GET `/superadmin/schools` — List Schools

**Response: `SchoolListResponse`**
```json
{
  "schools": [
    {
      "id": "uuid",
      "name": "ABC School",
      "code": "SCH001",
      "city": "Bangalore",
      "student_count": 450,
      "staff_count": 35,
      "is_active": true,
      "subscription_status": "active",
      "enrollment_date": "2024-04-01",
      "trial_end_date": null,
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 12
}
```

#### GET `/superadmin/schools/{school_id}` — School Detail

**Response: `SchoolDetailResponse`**
```json
{
  "id": "uuid",
  "name": "ABC School",
  "code": "SCH001",
  "logo_url": "/uploads/logos/school_logo.png",
  "city": "Bangalore",
  "state": "Karnataka",
  "address_line1": "123 Main Street",
  "phone": "9876543210",
  "email": "info@abcschool.com",
  "board_affiliation": "CBSE",
  "principal_name": "Dr. Sharma",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "enrollment_date": "2024-04-01",
  "subscription_status": "active",
  "trial_start_date": null,
  "trial_end_date": null,
  "student_count": 450,
  "staff_count": 35,
  "admin_users": [
    {
      "id": "uuid",
      "email": "admin@abcschool.com",
      "full_name": "School Admin",
      "role": "admin",
      "phone": "9876543211",
      "is_active": true,
      "last_login_at": "2024-06-27T14:00:00"
    }
  ],
  "subscription": {
    "id": "uuid",
    "plan_type": "yearly",
    "amount": 150000.00,
    "start_date": "2024-04-01",
    "end_date": "2025-03-31",
    "auto_renew": true,
    "is_active": true,
    "created_at": "2024-04-01T10:00:00"
  }
}
```

#### DELETE `/superadmin/schools/{school_id}/hard-delete` — Hard Delete

**Response: `HardDeleteResponse`**
```json
{
  "school_id": "uuid",
  "school_name": "ABC School",
  "deleted_tables": {
    "students": 450,
    "staff": 35,
    "users": 12,
    "attendance_sessions": 1200,
    "fee_records": 3400
  },
  "total_records_deleted": 15000
}
```

#### POST `/superadmin/schools/{school_id}/logo` — Upload Logo

**Request:** `multipart/form-data` with `file` field

- Allowed types: `image/png`, `image/jpeg`, `image/jpg`, `image/webp`
- Max size: 2MB

**Response:**
```json
{
  "logo_url": "/uploads/logos/school_id_timestamp.png"
}
```

---

### 3. Subscription Status

| Method | Path | Description |
|--------|------|-------------|
| PUT | `/superadmin/schools/{school_id}/subscription-status` | Update subscription status & trial dates |

**Request: `SubscriptionStatusUpdate`**
```json
{
  "subscription_status": "active | trial | expired | cancelled",
  "trial_start_date": "date | null",
  "trial_end_date": "date | null",
  "enrollment_date": "date | null"
}
```

---

### 4. Subscriptions

| Method | Path | Description |
|--------|------|-------------|
| GET | `/superadmin/schools/{school_id}/subscription` | Get active subscription |
| GET | `/superadmin/schools/{school_id}/subscription-history` | Get all subscriptions |
| POST | `/superadmin/schools/{school_id}/subscription` | Create subscription |
| PUT | `/superadmin/schools/{school_id}/subscription` | Update subscription |

#### POST `/superadmin/schools/{school_id}/subscription` — Create

**Request: `SubscriptionCreate`**
```json
{
  "plan_type": "monthly | yearly (required)",
  "amount": 15000.00,
  "start_date": "2024-04-01",
  "end_date": "2025-03-31",
  "auto_renew": true
}
```

#### PUT `/superadmin/schools/{school_id}/subscription` — Update

**Request: `SubscriptionUpdate`**
```json
{
  "plan_type": "string | null",
  "amount": "decimal | null",
  "start_date": "date | null",
  "end_date": "date | null",
  "auto_renew": "bool | null"
}
```

**Response: `SubscriptionResponse`**
```json
{
  "id": "uuid",
  "plan_type": "yearly",
  "amount": 150000.00,
  "start_date": "2024-04-01",
  "end_date": "2025-03-31",
  "auto_renew": true,
  "is_active": true,
  "created_at": "2024-04-01T10:00:00"
}
```

#### GET `/superadmin/schools/{school_id}/subscription-history`

**Response: `SubscriptionHistoryResponse`**
```json
{
  "subscriptions": [
    { "id": "uuid", "plan_type": "yearly", "amount": 150000.00, "start_date": "2024-04-01", "end_date": "2025-03-31", "auto_renew": true, "is_active": true, "created_at": "..." },
    { "id": "uuid", "plan_type": "monthly", "amount": 15000.00, "start_date": "2023-04-01", "end_date": "2024-03-31", "auto_renew": false, "is_active": false, "created_at": "..." }
  ],
  "total": 2
}
```

---

### 5. Payments

| Method | Path | Description |
|--------|------|-------------|
| GET | `/superadmin/schools/{school_id}/payments` | List payments for a school |
| POST | `/superadmin/schools/{school_id}/payments` | Record a payment |

#### POST `/superadmin/schools/{school_id}/payments` — Record Payment

**Request: `PaymentCreate`**
```json
{
  "amount": 15000.00,
  "payment_date": "2024-06-01",
  "period_start": "2024-06-01",
  "period_end": "2024-06-30",
  "status": "paid",
  "notes": "string | null"
}
```

**Response: `PaymentResponse`**
```json
{
  "id": "uuid",
  "subscription_id": "uuid",
  "amount": 15000.00,
  "payment_date": "2024-06-01",
  "period_start": "2024-06-01",
  "period_end": "2024-06-30",
  "status": "paid",
  "notes": null,
  "created_at": "2024-06-01T10:00:00"
}
```

#### GET `/superadmin/schools/{school_id}/payments`

**Response: `PaymentListResponse`**
```json
{
  "payments": [...],
  "total": 12
}
```

---

### 6. Admin User Management

| Method | Path | Description |
|--------|------|-------------|
| POST | `/superadmin/schools/{school_id}/admin` | Create admin user for a school |

**Request: `AdminCreate`**
```json
{
  "email": "admin@school.com (required, valid email)",
  "full_name": "string (required)",
  "password": "string (required)",
  "phone": "string | null"
}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "admin@school.com",
  "full_name": "Admin Name",
  "role": "admin"
}
```

---

### 7. Platform Settings

| Method | Path | Description |
|--------|------|-------------|
| GET | `/superadmin/settings` | Get all platform settings |
| PUT | `/superadmin/settings` | Update platform settings |

**GET Response:**
```json
{
  "platform_name": "School ERP",
  "max_schools": "50",
  "support_email": "support@erp.com"
}
```

**PUT Request:** (key-value pairs)
```json
{
  "platform_name": "School ERP Pro",
  "support_email": "help@erp.com"
}
```

---

### 8. User Management

| Method | Path | Description |
|--------|------|-------------|
| GET | `/superadmin/users` | List all users (with filters) |
| POST | `/superadmin/users/{user_id}/unlock` | Unlock a locked user |
| POST | `/superadmin/users/{user_id}/reset-password` | Reset user password |

#### GET `/superadmin/users`

**Query Params:**
- `role`: Filter by role (`admin`, `teacher`, `student`, `parent`)
- `school_id`: Filter by school UUID

**Response: `UserListResponse`**
```json
{
  "users": [
    {
      "id": "uuid",
      "email": "user@school.com",
      "full_name": "User Name",
      "role": "admin",
      "phone": "9876543210",
      "is_active": true,
      "school_name": "ABC School",
      "last_login_at": "2024-06-27T14:00:00"
    }
  ],
  "total": 150
}
```

#### POST `/superadmin/users/{user_id}/unlock`

**Response:**
```json
{
  "message": "User admin@school.com unlocked successfully",
  "user_id": "uuid",
  "email": "admin@school.com"
}
```

#### POST `/superadmin/users/{user_id}/reset-password`

**Request:**
```json
{
  "password": "string (min 4 characters)"
}
```

**Response:**
```json
{
  "message": "Password reset for admin@school.com",
  "user_id": "uuid",
  "email": "admin@school.com"
}
```

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized |
| 403 | Forbidden (not super_admin role) |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## Authentication

- Super admin uses the same `/api/v1/auth/login` endpoint
- Token contains `role: "super_admin"`
- All `/superadmin/*` routes require this role; other roles get 403
