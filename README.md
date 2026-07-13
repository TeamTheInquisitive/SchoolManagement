# School Management Platform - API & Architecture Specification

## Overview

**Backend**: Python FastAPI + SQLAlchemy (async) + MySQL  
**Frontend**: React + Vite + Tailwind CSS + React Query  
**Shared UI Library**: school-erp-ui-shared (Vite library mode)  
**Total API Endpoints**: 327  
**Modules**: Admin, Teacher, Student, SuperAdmin, Auth

---

## Architecture

```
SchoolManagement/           # Backend (FastAPI)
├── src/
│   ├── main.py            # App entry, middleware, routers
│   ├── auth/              # Authentication (JWT, cookies)
│   ├── admin/             # Admin module
│   │   ├── attendance/    # Attendance management
│   │   ├── dashboard/     # Dashboard stats & analytics
│   │   ├── examinations/  # Exams, results, grade system
│   │   ├── fees/          # Fee management & payments
│   │   ├── leaves/        # Leave policies & approvals
│   │   ├── library/       # Library management
│   │   ├── mentoring/     # Mentor assignments
│   │   ├── notifications/ # Notifications
│   │   ├── payroll/       # Payroll & salary management
│   │   ├── settings/      # School settings, config
│   │   ├── staff/         # Staff CRUD
│   │   ├── students/      # Student CRUD & sub-resources
│   │   ├── teachers/      # Teacher/Faculty CRUD
│   │   ├── timetable/     # Timetable & periods
│   │   └── transport/     # Transport management
│   ├── teacher/           # Teacher module
│   ├── student/           # Student module
│   ├── superadmin/        # Super admin module
│   ├── core/              # Config, DB, security, middleware
│   ├── models/            # SQLAlchemy models
│   └── scripts/           # Utilities (sync_prod_schema)
├── alembic/               # Database migrations
├── Procfile               # Railway deployment
└── requirements.txt       # Python dependencies
```

---

## Data Models

### Core
- **School** — Multi-tenant, subscription, trial dates
- **User** — Auth (email, password_hash, role, school_id, student_id/staff_id)
- **AcademicYear** — Current year tracking

### Academic
- **Class** — name, display_name, sort_order
- **Section** — name, sort_order
- **ClassSection** — class_id + section_id + academic_year_id
- **Subject** — name, code

### Students
- **Student** — admission_number, personal info, metadata (student_type, token_advance)
- **StudentEnrollment** — student + class_section + academic_year (links student to class)
- **Parent** — parent info, linked via StudentParent join table
- **StudentMentor** — mentor assignment per academic year

### Staff & Teachers
- **Staff** — employee_id, personal/professional info, salary, bank details, is_teacher flag
- **StaffSubject** — staff + subject (with is_primary)
- **ClassAssignment** — staff + class_section + subject + is_class_teacher
- **SalaryStructure** — basic, hra, da, transport, deductions, net_salary

### Fees
- **FeeStructure** — fee_type, amount, frequency, class_id/class_section_id
- **FeeRecord** — per student per fee component (total, paid, pending, status)
- **FeePayment** — individual payment transactions

### Attendance
- **AttendanceSession** — class_section + date + totals
- **AttendanceRecord** — student + status (Present/Absent/Late)

### Examinations
- **Exam** — name, type, class_section, subject, date, marks
- **ExamResult** — student + exam + marks_obtained + grade
- **GradeSystem** / **GradeScale** — grade definitions (A+, A, B+, etc.)

### Leaves
- **LeavePolicy** — type, days, applicable_to, display_name
- **LeaveBalance** — staff + leave_type + allocated/used/pending
- **LeaveApplication** — staff + dates + status

### Payroll
- **SalaryStructure** — detailed components per staff
- **Payslip** — monthly payslip with components + paid_amount + status

### Activities
- **Activity** — extra-curricular activities
- **Award** — student achievements
- **DisciplinaryRecord** — incidents

### Other
- **ParentMeeting** — parent-teacher meetings
- **Timetable** (PeriodConfig, TimetableSlot)
- **Transport** (Vehicle, Driver, Helper, Route, RouteAssignment)
- **Notification** — in-app notifications
- **Settings** — key-value config storage

---

## API Endpoints (327 total)

### Auth (`/api/v1/auth`)
| Method | Path | Description |
|--------|------|-------------|
| POST | /login | Login with email/password |
| POST | /logout | Logout (clear cookies) |
| GET | /me | Current user profile |
| POST | /refresh-token | Refresh access token |
| POST | /change-password | Change own password |
| POST | /forgot-password | Initiate password reset |
| POST | /reset-password | Reset with token |
| GET | /school-profile | School info (any authenticated user) |

### Admin - Students (`/api/v1/admin/students`)
| Method | Path | Description |
|--------|------|-------------|
| GET | / | List students (paginated, filtered) |
| POST | / | Create student + user account |
| POST | /bulk-import | CSV bulk import |
| POST | /bulk-import-json | JSON bulk import |
| GET | /export | Export students CSV |
| GET | /{id} | Student detail with stats |
| PUT | /{id} | Update student |
| DELETE | /{id} | Soft-delete student |
| GET | /{id}/exam-results | Exam results |
| GET | /{id}/fee-history | Fee structure + payments |
| GET | /{id}/activities | Activities + Awards |
| POST | /{id}/activities | Create activity |
| PUT | /{id}/activities/{aid} | Update activity |
| DELETE | /{id}/activities/{aid} | Delete activity |
| POST | /{id}/awards | Create award |
| PUT | /{id}/awards/{aid} | Update award |
| DELETE | /{id}/awards/{aid} | Delete award |
| GET | /{id}/disciplinary-records | Disciplinary records |
| POST | /{id}/disciplinary-records | Create record |
| PUT | /{id}/disciplinary-records/{rid} | Update record |
| DELETE | /{id}/disciplinary-records/{rid} | Delete record |
| GET | /{id}/parent-meetings | Parent meetings |
| POST | /{id}/parent-meetings | Create meeting |
| PUT | /{id}/parent-meetings/{mid} | Update meeting |
| DELETE | /{id}/parent-meetings/{mid} | Delete meeting |
| POST | /{id}/reset-password | Reset/create student password |

### Admin - Teachers (`/api/v1/admin/teachers`)
| Method | Path | Description |
|--------|------|-------------|
| GET | / | List teachers (paginated) |
| POST | / | Create teacher + user + salary |
| POST | /bulk-import | JSON bulk import |
| GET | /by-class | Teachers by class |
| GET | /export | Export CSV |
| GET | /{id} | Teacher detail + leave balances |
| PUT | /{id} | Update teacher |
| DELETE | /{id} | Soft-delete |
| POST | /{id}/assign-class | Assign class/subject/class-teacher |
| GET | /{id}/assignments | Class assignments |
| GET | /{id}/awards | List awards |
| POST | /{id}/awards | Create award |
| PUT | /{id}/awards/{aid} | Update award |
| DELETE | /{id}/awards/{aid} | Delete award |
| POST | /{id}/bulk-assign | Bulk assign classes |
| DELETE | /{id}/class-assignment/{aid} | Remove assignment |
| GET | /{id}/history | Teacher history |
| POST | /{id}/reset-password | Reset teacher password |

### Admin - Fees (`/api/v1/admin/fees`)
| Method | Path | Description |
|--------|------|-------------|
| GET | / | List fees (grouped by student) |
| POST | / | Create fee record |
| GET | /export | Export CSV |
| POST | /generate-due | Generate fee dues |
| POST | /send-reminder | Send reminders |
| POST | /bulk-apply-late-fees | Apply late fees |
| GET | /student/{id} | Student fee records |
| GET | /student/{id}/receipt | Consolidated receipt |
| GET | /{id} | Fee record detail |
| PUT | /{id} | Update fee record |
| POST | /{id}/record-payment | Record payment |
| POST | /{id}/apply-late-fee | Apply late fee |
| GET | /{id}/receipt | Fee receipt |

### Admin - Payroll (`/api/v1/admin/staff/payroll`)
| Method | Path | Description |
|--------|------|-------------|
| GET | / | Get payslips (month/year) |
| POST | /run | Generate payroll |
| POST | /generate-payslips | Generate payslips |
| POST | /mark-all-paid | Bulk mark all paid |
| PUT | /{payslip_id} | Update payslip components |
| POST | /{payslip_id}/pay | Record partial/full payment |
| GET | /salary-structure/{id} | Salary structure |
| PUT | /salary-structure/{id} | Update salary |
| GET | /salary-revisions/{id} | Salary history |
| POST | /salary-revisions | Create revision |

### Admin - Settings (`/api/v1/admin/settings`)
| Method | Path | Description |
|--------|------|-------------|
| GET/PUT | / | General settings |
| GET/PUT | /school-profile | School profile |
| GET/PUT | /academic-year | Current academic year |
| CRUD | /academic-years | Academic years |
| GET | /class-sections | Classes with sections |
| POST | /classes/bulk | Bulk create classes |
| POST | /sections/bulk | Bulk create sections |
| CRUD | /subjects | Subject management |
| GET/PUT | /class-subjects | Class-subject mapping |
| CRUD | /fee-structures | Fee structure config |
| GET/PUT | /id-generation | ID auto-generation config |
| GET | /next-id?type= | Generate next ID |
| POST | /upload-logo | Upload school logo |

### Admin - Examinations (`/api/v1/admin/examinations`)
| Method | Path | Description |
|--------|------|-------------|
| GET | / | List exams (grouped by name, paginated) |
| POST | / | Create exam |
| GET/PUT | /grade-system | Grade system config |
| GET | /{id} | Exam detail |
| PUT | /{id} | Update exam |
| DELETE | /{id} | Delete exam |
| POST | /{id}/publish | Publish results |
| GET/POST | /{id}/results | Exam results |
| POST | /{id}/results/bulk-upload | Bulk upload results |

### Admin - Attendance (`/api/v1/admin/attendance`)
| Method | Path | Description |
|--------|------|-------------|
| GET | / | Get attendance (class_section_id + date) |
| POST | / | Submit attendance |
| PUT | / | Update attendance |

### Admin - Leaves (`/api/v1/admin/leaves`)
| Method | Path | Description |
|--------|------|-------------|
| GET | / | List leave applications |
| GET/PUT | /policy | Leave policy config |
| POST | /allocate | Allocate leaves to staff |
| GET | /balances | All leave balances |
| POST | /{id}/approve | Approve leave |
| POST | /{id}/reject | Reject leave |
| POST | /{id}/cancel | Cancel leave |

### Admin - Transport, Timetable, Library, Notifications
Full CRUD for vehicles, drivers, helpers, routes, assignments, periods, slots, books, issues, notifications.

### Teacher Module (`/api/v1/teacher`)
Attendance, assignments, grades, leaves, students, timetable, dashboard, notifications.

### Student Module (`/api/v1/student`)
Profile, attendance, assignments, fees, results, timetable, library, notifications, dashboard.

---

## Key Features

1. **Multi-tenant** — All data scoped by school_id
2. **Academic Year** — All academic data linked to academic year
3. **Soft Delete** — is_active flag, not hard delete
4. **Auto ID Generation** — Configurable patterns (STU260001, TCH260001)
5. **Bulk Import** — Excel upload with validation for students/teachers
6. **Dynamic Fee Management** — Per-student components, concessions, partial payments
7. **Leave Policy** — Configurable by department with auto-allocation
8. **Payroll** — Monthly generation, editing, partial payments, bulk actions
9. **Grade System** — Configurable grade scales per class
10. **Attendance** — Session-based, admin/teacher can mark
11. **Exam Scheduling** — Multi-class, multi-subject bulk creation
12. **Real-time Stats** — Dynamic attendance %, grade avg, fee due

---

## Deployment

- **Backend**: Railway.app (Procfile: sync schema → stamp alembic → gunicorn)
- **Frontend**: Separate deployment per module (Admin, Student, Teacher, SuperAdmin)
- **Database**: MySQL (Railway managed)
- **Schema Sync**: `python -m src.scripts.sync_prod_schema` auto-creates tables/columns

---

*Last updated: 2026-06-06*
