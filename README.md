# School Management Portal - Backend API

Django REST Framework backend serving all frontend clients (Admin Portal, Student/Teacher Portal, Exam Portal).

## Tech Stack
- Python 3.12, Django 5.1.4, Django REST Framework 3.15
- SQLite (development), PostgreSQL (production)
- JWT Authentication (httpOnly cookies) + OAuth2 (Exam Portal SSO)
- Redis + Celery (planned for background tasks)

## Setup

```bash
# Clone and enter directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed demo data
python manage.py seed_demo

# Run server
python manage.py runserver
```

Server runs at `http://localhost:8000`

## Demo Credentials
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@school.com | password123 |
| Teacher | jane@teacher.com | password123 |
| Student | john@student.com | password123 |

## Project Structure
```
backend/
├── config/          # Django settings, URLs, WSGI
├── apps/
│   ├── core/        # School (tenant) model, middleware, permissions
│   ├── accounts/    # User model, auth views, JWT cookie auth
│   ├── teachers/    # TeacherProfile, privileges, adhoc classes
│   ├── students/    # StudentProfile, parent meetings, activities
│   ├── leaves/      # Leave types, balances, applications
│   ├── examinations/# Exams, results, attendance
│   ├── library/     # Books, issues, fines
│   ├── fees/        # Fee types, assignments, payments, reminders
│   ├── transport/   # Routes, buses, staff, payroll
│   └── staff/       # Non-teaching staff management
├── requirements.txt
└── manage.py
```

## Environment Variables
```
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174
```

## API Base URL
All endpoints prefixed with `/api/v1/`

## Multi-Tenancy
Each request must include `X-School-Code` header or use subdomain-based routing.
