# Backend Requirements

## System Requirements
- Python 3.10+
- pip (package manager)
- SQLite 3 (bundled with Python)

## Python Dependencies
- django==5.1.4
- djangorestframework==3.15.2
- djangorestframework-simplejwt==5.4.0
- django-cors-headers==4.6.0
- django-oauth-toolkit==3.0.1
- Pillow==11.1.0 (image handling)

## Architecture Requirements
- Multi-tenant SaaS: Each school is an isolated tenant
- JWT stored in httpOnly cookies (not localStorage) for XSS protection
- OAuth2 provider for Exam Portal SSO
- Role-based access control (Super Admin, Admin, Teacher, Student, Parent)
- Email service for OTP verification and notifications

## Database Models Required
| App | Models |
|-----|--------|
| core | School |
| accounts | User, OTP |
| teachers | TeacherProfile, TeacherClassAssignment, AdhocClass |
| students | StudentProfile, ParentMeeting, StudentActivity |
| leaves | LeaveType, LeaveBalance, LeaveApplication |
| examinations | Exam, ExamResult, ExamAttendance |
| library | Book, BookIssue, LibrarySettings |
| fees | FeeType, FeeAssignment, Payment, LateFineRule, FeeReminder |
| transport | Route, Bus, StaffProfile, SalaryStructure, Payslip |

## Security Requirements
- httpOnly cookie-based JWT authentication
- Password policy: min 8 chars with complexity
- OTP-based email verification
- Tenant isolation via middleware
- CORS restricted to allowed origins
- CSRF protection for cookie-based auth
