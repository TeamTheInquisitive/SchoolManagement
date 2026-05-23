# School ERP Backend

A production-ready FastAPI backend for a multi-tenant School ERP system supporting Admin, Teacher, and Student portals.

## Tech Stack

- **FastAPI** (async Python web framework)
- **PostgreSQL 16** (database)
- **Redis 7** (token blacklist, caching)
- **SQLAlchemy 2.0** (async ORM)
- **Alembic** (migrations)
- **Pydantic v2** (validation)
- **JWT** (httpOnly cookie auth)

## Prerequisites

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| Python | 3.12+ | `python3 --version` |
| PostgreSQL | 16+ | `psql --version` |
| Redis | 7+ | `redis-cli --version` |
| Docker (optional) | 20+ | `docker --version` |

## Quick Start

### Option 1: Docker (Recommended)

```bash
cd school-erp-backend

# Start all services (PostgreSQL + Redis + App)
docker-compose up -d

# Wait for services to be healthy (~10 seconds)
docker-compose ps

# Run database migrations
docker-compose exec app alembic upgrade head

# Seed initial data (creates school + admin user)
docker-compose exec app python -m src.seeds.initial

# Server is running at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### Option 2: Local Development (Step by Step)

#### Step 1: Start PostgreSQL & Redis

```bash
# macOS (Homebrew)
brew services start postgresql@16
brew services start redis

# Or use Docker for just DB + Redis
docker run -d --name school-pg -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:16
docker run -d --name school-redis -p 6379:6379 redis:7-alpine
```

#### Step 2: Create Database

```bash
createdb school_erp

# Verify connection
psql school_erp -c "SELECT 1;"
```

#### Step 3: Setup Python Environment

```bash
cd school-erp-backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate    # macOS/Linux
# venv\Scripts\activate     # Windows

# Install dependencies
pip install -e .
```

#### Step 4: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env if needed (defaults work for local dev)
# - POSTGRES_PASSWORD=password
# - REDIS_URL=redis://localhost:6379/0
# - JWT_SECRET_KEY=change-me-in-production (OK for local)
```

#### Step 5: Run Migrations

```bash
alembic upgrade head
```

#### Step 6: Seed Initial Data

```bash
python -m src.seeds.initial

# This creates:
# - School: "Demo School" (code: SCH001)
# - Admin user: admin@school.com / admin123
```

#### Step 7: Start Server

```bash
uvicorn src.main:app --reload --port 8000

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Started reloader process
```

#### Step 8: Verify

```bash
# Health check
curl http://localhost:8000/health
# → {"status":"healthy","app":"School ERP Backend"}

# Test login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -H "X-School-Code: SCH001" \
  -d '{"email": "admin@school.com", "password": "admin123"}'

# Open Swagger UI in browser
open http://localhost:8000/docs
```

---

## Common Issues & Troubleshooting

### 1. `address already in use` (port 8000)

```bash
# Find what's using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use a different port
uvicorn src.main:app --reload --port 8001
```

### 2. `connection refused` (PostgreSQL)

```bash
# Check if PostgreSQL is running
pg_isready
# → accepting connections

# If not running:
brew services start postgresql@16    # macOS
sudo systemctl start postgresql      # Linux

# Check connection with your .env settings
psql -h localhost -U postgres -d school_erp
```

### 3. `connection refused` (Redis)

```bash
# Check if Redis is running
redis-cli ping
# → PONG

# If not running:
brew services start redis            # macOS
sudo systemctl start redis           # Linux

# If Redis is not installed and you want to skip it for dev:
# The app will start but logout/token blacklist won't work
```

### 4. `ModuleNotFoundError: No module named 'src'`

```bash
# Make sure you installed the package in editable mode
pip install -e .

# Make sure you're in the project root directory
pwd
# → /path/to/school-erp-backend

# Make sure venv is activated
which python
# → /path/to/school-erp-backend/venv/bin/python
```

### 5. `metadata-generation-failed` during pip install

```bash
# This means pyproject.toml has an issue
# Make sure [tool.hatch.build.targets.wheel] section exists:
# packages = ["src"]

pip install -e .
```

### 6. Alembic migration errors

```bash
# If "Target database is not up to date"
alembic upgrade head

# If "Can't locate revision"
alembic stamp head    # Reset alembic state
alembic upgrade head  # Re-run

# If models changed and you need a new migration
alembic revision --autogenerate -m "describe_change"
alembic upgrade head
```

### 7. `TypeError: unsupported operand type(s) for |: 'NoneType' and 'NoneType'`

This happens if `from __future__ import annotations` is in a Pydantic schema file.

```bash
# Fix: remove it from schema files
find src -name "schemas.py" -exec grep -l "from __future__ import annotations" {} \;
# Then remove that line from those files
```

### 8. CORS errors from React frontend

```bash
# Make sure your React dev server URL is in ALLOWED_ORIGINS in .env:
ALLOWED_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# Make sure the React Axios config has:
# withCredentials: true
```

### 9. `401 Unauthorized` on every request

- Check that you're sending the `X-School-Code` header
- Check that cookies are being sent (`withCredentials: true` in Axios)
- Check that the access token hasn't expired (15 min default)
- Try logging in again

### 10. Database tables don't exist

```bash
# Run migrations
alembic upgrade head

# If that fails, check DATABASE_URL in .env matches your actual PostgreSQL setup
echo $DATABASE_URL
psql school_erp -c "\dt"   # List tables
```

---

## Stopping the Server

```bash
# If running in foreground: Ctrl+C

# If running via Docker:
docker-compose down

# Stop PostgreSQL/Redis (local):
brew services stop postgresql@16
brew services stop redis
```

## Reset Everything (Fresh Start)

```bash
# Drop and recreate database
dropdb school_erp
createdb school_erp

# Re-run migrations
alembic upgrade head

# Re-seed
python -m src.seeds.initial
```

## API Documentation

Once running, auto-generated docs are at:

| URL | Description |
|-----|-------------|
| http://localhost:8000/docs | Swagger UI (interactive) |
| http://localhost:8000/redoc | ReDoc (readable) |
| http://localhost:8000/openapi.json | OpenAPI schema |
| http://localhost:8000/health | Health check |

## Default Credentials

| Role | Email | Password | School Code | Frontend Port |
|------|-------|----------|-------------|---------------|
| Admin | admin@school.com | password123 | SCH001 | localhost:5173 |
| Teacher | jane@teacher.com | password123 | SCH001 | localhost:5174 |
| Student | john@student.com | password123 | SCH001 | localhost:5175 |

## API Structure

```
/api/v1/auth/...        → Shared auth (all roles)
/api/v1/admin/...       → Admin portal (role: admin)
/api/v1/teacher/...     → Teacher portal (role: teacher)
/api/v1/student/...     → Student portal (role: student)
```

## Project Structure

```
src/
├── main.py              # App entry point
├── core/                # Shared infrastructure
│   ├── config.py        # Environment settings
│   ├── database.py      # Async DB connection
│   ├── redis.py         # Redis connection
│   ├── base_model.py    # SQLAlchemy base + mixins
│   ├── security.py      # JWT + password hashing
│   ├── dependencies.py  # Annotated type aliases
│   ├── exceptions.py    # Domain exceptions
│   ├── pagination.py    # Generic pagination
│   ├── middleware.py     # School context
│   ├── csv_export.py    # CSV generation
│   └── pdf_generator.py # PDF generation stubs
├── auth/                # Auth domain (7 endpoints)
├── admin/               # Admin portal domains
│   ├── dashboard/       # 7 endpoints
│   ├── students/        # 12 endpoints
│   ├── teachers/        # 12 endpoints
│   ├── staff/           # 5 endpoints
│   ├── leaves/          # 10 endpoints
│   ├── timetable/       # 11 endpoints
│   ├── examinations/    # 16 endpoints
│   ├── fees/            # 12 endpoints
│   ├── transport/       # 24 endpoints
│   ├── notifications/   # 5 endpoints
│   ├── payroll/         # 11 endpoints
│   └── settings/        # 11 endpoints
├── teacher/             # Teacher portal domains
│   ├── dashboard/       # 8 endpoints
│   ├── classes/         # 4 endpoints
│   ├── students/        # 9 endpoints
│   ├── attendance/      # 6 endpoints
│   ├── assignments/     # 8 endpoints
│   ├── grades/          # 8 endpoints
│   ├── notifications/   # 4 endpoints
│   ├── timetable/       # 2 endpoints
│   ├── adhoc_classes/   # 4 endpoints
│   └── leaves/          # 6 endpoints
├── student/             # Student portal domains
│   ├── dashboard/       # 10 endpoints
│   ├── profile/         # 3 endpoints
│   ├── timetable/       # 2 endpoints
│   ├── attendance/      # 3 endpoints
│   ├── assignments/     # 4 endpoints
│   ├── results/         # 5 endpoints
│   ├── fees/            # 6 endpoints
│   ├── library/         # 4 endpoints
│   └── notifications/   # 3 endpoints
└── models/              # SQLAlchemy models (shared)
```

## React UI Integration Guide

### 1. Axios Setup

Create an API service file in your React app:

```javascript
// src/services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,  // REQUIRED: sends httpOnly cookies
});

// Attach school code to every request
api.interceptors.request.use((config) => {
  const schoolCode = localStorage.getItem('school_code');
  if (schoolCode) config.headers['X-School-Code'] = schoolCode;
  return config;
});

// Auto-refresh token on 401
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        await api.post('/auth/refresh-token/');
        return api(original);
      } catch {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 2. Login Flow

```javascript
// Login — cookies are set automatically by the backend
const login = async (email, password) => {
  const { data } = await api.post('/auth/login/', { email, password });
  localStorage.setItem('user', JSON.stringify(data.user));
  localStorage.setItem('school_code', data.user.school_code);
  return data.user;
};

// Logout
const logout = async () => {
  await api.post('/auth/logout/');
  localStorage.removeItem('user');
  localStorage.removeItem('school_code');
};
```

### 3. CORS Configuration

The backend is pre-configured to accept requests from:
- `http://localhost:5173` (Admin portal - Vite)
- `http://localhost:5174` (Teacher portal)
- `http://localhost:5175` (Student portal)

To add more origins, update `.env`:
```
ALLOWED_ORIGINS=["http://localhost:5173","http://localhost:3000","https://yourdomain.com"]
```

### 4. Key Headers

| Header | Value | Purpose |
|--------|-------|---------|
| `Content-Type` | `application/json` | Request body format |
| `X-School-Code` | `SCH001` | Multi-tenant school identifier |
| `Cookie` | (automatic) | Auth tokens — `withCredentials: true` handles this |

### 5. Response Format

All list endpoints return:
```json
{
  "count": 50,
  "page": 1,
  "page_size": 20,
  "total_pages": 3,
  "results": [...]
}
```

All errors return:
```json
{
  "error": "Human-readable message",
  "code": "ERROR_CODE",
  "details": { "field": ["error message"] }
}
```

### 6. File Uploads

For assignment submissions (multipart/form-data):
```javascript
const submitAssignment = async (assignmentId, files, comments) => {
  const formData = new FormData();
  formData.append('comments', comments);
  files.forEach(file => formData.append('files', file));

  return api.post(`/student/assignments/${assignmentId}/submit/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};
```

### 7. Role-Based Routing

```javascript
// After login, route based on role
const user = JSON.parse(localStorage.getItem('user'));
switch (user.role) {
  case 'admin':       navigate('/admin/dashboard'); break;
  case 'teacher':     navigate('/teacher/dashboard'); break;
  case 'student':     navigate('/student/dashboard'); break;
}
```

### 8. Environment Variables (React)

```env
# .env in React app
VITE_API_URL=http://localhost:8000/api/v1
```

## Database

- Multi-tenant via `school_id` on every table
- Academic year scoping on all transactional data
- Soft deletes (is_active flag, never hard delete)
- UUID primary keys
- JSONB metadata field on every entity

### Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description_of_change"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Domain-based structure | Each feature owns its router, schemas, service |
| Teacher = Staff | Same DB table, `is_teacher=true` for teachers |
| httpOnly cookies | Prevents XSS token theft |
| Redis token blacklist | Instant logout without waiting for expiry |
| Academic year scoping | Schools operate in annual cycles |
| Soft deletes everywhere | Full audit trail, no data loss |
| Configurable enums | Admin manages dropdowns via Settings API |
