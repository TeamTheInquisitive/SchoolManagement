# Backend Functionality

## Authentication & Authorization
| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/auth/register/ | POST | Register new user (sends verification OTP) |
| /api/v1/auth/login/ | POST | Login (sets httpOnly JWT cookies) |
| /api/v1/auth/logout/ | POST | Logout (blacklists token, clears cookies) |
| /api/v1/auth/refresh-token/ | POST | Refresh access token via cookie |
| /api/v1/auth/me/ | GET/PUT | Get or update current user profile |
| /api/v1/auth/change-password/ | POST | Change password (requires old password) |
| /api/v1/auth/forgot-password/ | POST | Send password reset OTP to email |
| /api/v1/auth/reset-password/ | POST | Reset password with OTP |
| /api/v1/auth/verify-email/ | POST | Verify email with OTP |
| /api/v1/auth/resend-otp/ | POST | Resend OTP for verification/reset |

## Teacher Management (Admin only)
| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/admin/teachers/ | GET | List all teachers (with filters) |
| /api/v1/admin/teachers/ | POST | Create teacher (creates user + profile) |
| /api/v1/admin/teachers/{id}/ | GET/PUT/DELETE | Teacher CRUD |
| /api/v1/admin/teachers/{id}/assign-class/ | POST | Assign class to teacher |
| /api/v1/admin/teachers/{id}/privileges/{aid}/ | PUT | Update privileges for assignment |
| /api/v1/admin/teachers/{id}/class-assignment/{aid}/ | DELETE | Remove class assignment |
| /api/v1/admin/teachers/{id}/privileges/{aid}/apply-template/ | POST | Apply privilege template |

## Teacher Privilege System
- 10 privilege categories: Attendance, Assignments, Grades, Examinations, Timetable, Student Info, Messaging, Notifications, Quiz Management, Reports
- Each permission is toggleable per class assignment
- Templates: Class Teacher (full access) / Subject Teacher (limited)
- Privileges stored as JSON for flexibility

## Student Management
- StudentProfile with day_scholar/hostler type
- Mentor assignment (FK to TeacherProfile)
- Parent/Guardian information
- Medical details (blood group, conditions, allergies)
- Transport enrollment (route, bus, pickup point)
- Parent meeting tracking (attended/absent)
- Extra-curricular activities and awards

## Leave Management
- Configurable leave types (Casual, Sick, Earned) per school
- Leave balance tracking per academic year
- Application workflow: Apply → Pending → Approved/Rejected
- Applicable to both teachers and students
- Leave history with remarks

## Examinations
- Exam types: Unit Test, Mid-term, Final, Quarterly
- Filters: year, month, subject, class, exam type
- Result tracking with marks, grade, rank
- Exam attendance (present/absent)
- Pass/fail statistics

## Library
- Book catalog with ISBN, category, shelf location
- Issue with configurable number of days
- Due date auto-calculated from issue date + days
- Overdue detection and fine calculation
- Fine per day configurable in LibrarySettings
- Max books per student limit

## Fee Management
- Fee types: Tuition, Transport, Hostel, Lab, Library
- Applicable to: All / Day Scholar / Hostler
- Fee assignment with status tracking (pending/partial/paid/overdue)
- Payment recording (cash/cheque/UPI/bank transfer)
- Late fine rules: fixed per day / percentage / slab-based
- Grace period and max fine cap
- Send reminders to groups (all/class/section/overdue)

## Transport
- Route management with stops list
- Bus assignment with driver details
- Student transport enrollment

## Payroll
- Salary structure: basic + HRA + allowances - deductions
- Monthly payslip generation
- Payment status tracking

## Staff Management
- Non-teaching staff profiles
- Department and designation tracking
- Employee ID management

## Multi-Tenancy
- School model as tenant identifier
- TenantMiddleware extracts school from X-School-Code header or subdomain
- All queries scoped to current tenant
- BaseModel abstract class for tenant-aware models

## Email Service
- OTP generation (6-digit, 10-min expiry)
- Email verification flow
- Password reset flow
- Console backend for development, SMTP for production
