# School ERP Backend

A production-ready FastAPI backend for a multi-tenant School ERP system supporting Admin, Teacher, and Student portals.

## Tech Stack

- **FastAPI** (async Python web framework)
- **MySQL 8.0** (database)
- **Redis 7** (token blacklist, caching)
- **SQLAlchemy 2.0** (async ORM with aiomysql)
- **Alembic** (migrations)
- **Pydantic v2** (validation)
- **JWT** (httpOnly cookie auth)

## Prerequisites

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| Python | 3.12+ | `python3 --version` |
| MySQL | 8.0+ | `mysql --version` |
| Redis | 7+ | `redis-cli --version` |
| Node.js | 18+ | `node --version` |
| Docker (optional) | 20+ | `docker --version` |

## Project Structure

```
code/
├── backend/          ← This directory (FastAPI API server)
├── admin/            ← Admin portal (React + Vite, port 5173)
├── teacher/          ← Teacher portal (React + Vite, port 5175)
└── shared/           ← Shared UI component library (@school-erp/ui-shared)
```

---

## Full Setup (Backend + Frontends)

### Step 1: Start MySQL & Redis

```bash
# macOS (Homebrew)
brew services start mysql
brew services start redis

# Or use Docker for just DB + Redis
docker run -d --name school-mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=school_erp mysql:8.0 --default-authentication-plugin=mysql_native_password --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
docker run -d --name school-redis -p 6379:6379 redis:7-alpine
```

### Step 2: Create Database

```bash
mysql -u root -e "CREATE DATABASE IF NOT EXISTS school_erp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### Step 3: Setup Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate    # macOS/Linux
# venv\Scripts\activate     # Windows

# Install dependencies
pip install -e .

# Configure environment (defaults work for local dev with no MySQL password)
# Edit .env if your MySQL has a password:
#   MYSQL_PASSWORD=yourpassword
```

### Step 4: Load Data

You have two options:

#### Option A: Import SQL backup (Fastest — recommended)

```bash
mysql -u root school_erp < school_erp_backup.sql
```

This loads the full database with all demo data in one shot.

#### Option B: Run seed scripts (generates fresh data)

```bash
# 1. Create all database tables
alembic upgrade head

# 2. Create school + admin/teacher/student user accounts
python -m src.seeds.initial

# 3. Seed core demo data (48 students, 10 staff, exams, attendance, assignments, timetable)
python -m src.seeds.demo_data

# 4. Seed expanded admin data (fees, transport, payroll, notifications)
python -m src.seeds.admin_extra_data
```

Or all-in-one:

```bash
python -m src.seeds.seed_all
```

#### Reset and reload from scratch

```bash
mysql -u root -e "DROP DATABASE school_erp; CREATE DATABASE school_erp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Then use Option A or Option B above
```

### Step 5: Start Backend Server

```bash
uvicorn src.main:app --reload --port 8000
```

### Step 6: Start Frontend Portals

> **Important:** The frontend modules depend on a shared UI library at `../shared`. If you see errors like  
> `Failed to resolve import "@school-erp/ui-shared"`, make sure the `shared/` folder exists as a sibling  
> to `admin/` and `teacher/`. The `package.json` in each frontend references it as `"file:../shared"` and  
> `tailwind.config.js` imports from `'../shared/tailwind.shared.js'`.

Open new terminal tabs:

```bash
# Admin portal (http://localhost:5173)
cd admin
npm install
npm run dev

# Teacher portal (http://localhost:5175)
cd teacher
npm install
npm run dev
```

If you get path errors, verify this directory structure:
```
code/
├── admin/          ← package.json has "@school-erp/ui-shared": "file:../shared"
├── teacher/        ← package.json has "@school-erp/ui-shared": "file:../shared"
├── shared/         ← The shared UI component library
│   ├── package.json (name: "@school-erp/ui-shared")
│   ├── src/
│   └── tailwind.shared.js
└── backend/
```

---

## Demo Credentials

| Portal | URL | Email | Password |
|--------|-----|-------|----------|
| Admin | http://localhost:5173 | admin@school.com | password123 |
| Teacher | http://localhost:5175 | jane@teacher.com | password123 |

### Other Teacher Accounts (all use `password123`)

| Name | Email | Subject | Classes |
|------|-------|---------|---------|
| Jane Smith | jane@teacher.com | Mathematics | 8A, 8B, 9A, 9B (Class Teacher of 8A) |
| Robert Brown | robert@teacher.com | English | 8A, 8B, 9A, 9B |
| Priya Sharma | priya@teacher.com | Science | 9A, 9B, 10A, 10B |
| Amit Kumar | amit@teacher.com | Social Studies | 8A, 8B, 10A, 10B |
| Sunita Devi | sunita@teacher.com | Hindi | 8A, 8B, 9A, 9B |
| Rahul Verma | rahul@teacher.com | Computer Science | 9A, 9B, 10A, 10B |

---

## Seeded Data Summary

After running `python -m src.seeds.seed_all`, the database contains:

| Category | Count | Details |
|----------|-------|---------|
| Students | 48 | 8 per section across 8A, 8B, 9A, 9B, 10A, 10B |
| Staff | 10 | 8 teachers + 2 admin staff |
| Attendance | 576 records | 30 days for 8A/8B, 20 days for 9A/9B |
| Assignments | 29 | 24 Math assignments (Jane) + 5 others, with 172 submissions |
| Exams | 18 | Unit tests, mid-terms, pre-finals across all classes, with 120 results |
| Fee Records | 240 | 48 students × 5 months (Jul-Nov), ~75% paid |
| Fee Payments | ~180 | Online, Cash, Cheque, UPI |
| Leave Applications | 24 | 8 staff × 3 each (mix of Approved/Pending/Rejected) |
| Payslips | 48 | 8 staff × 6 months (Jun-Nov) |
| Transport | 6 routes | 6 vehicles, 6 drivers, 4 helpers, 24 students assigned |
| Notifications | 16 | Events, fee reminders, exams, holidays across months |
| Timetable | 36 slots | Full week schedule for Jane + other teachers |
| Activities | 56 | 8 clubs with multiple members |
| Awards | 10 | Academic, Sports, Cultural |
| Parent Meetings | 14 | Spread across multiple students and dates |
| Salary Advances | 4 | Various amounts and recovery plans |

---

## Seed Scripts

| Script | Purpose | Command |
|--------|---------|---------|
| `seed_all.py` | Runs everything below in order | `python -m src.seeds.seed_all` |
| `initial.py` | Creates school + admin/teacher/student users | `python -m src.seeds.initial` |
| `demo_data.py` | Core demo data (students, staff, exams, attendance, assignments, timetable, activities) | `python -m src.seeds.demo_data` |
| `admin_extra_data.py` | Expands admin-facing data (fees ×5 months, transport, payslips, notifications, leaves) | `python -m src.seeds.admin_extra_data` |

### Resetting the Database

To start fresh:

```bash
mysql -u root -e "DROP DATABASE school_erp; CREATE DATABASE school_erp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
python -m src.seeds.seed_all
```

---

## API Documentation

Once the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

### Authentication

All API requests (except login) require:
1. **Cookie**: `access_token` (set automatically on login)
2. **Header**: `X-School-Code: SCH001`

### API Prefix

All endpoints are under `/api/v1/`:
- Admin routes: `/api/v1/admin/...`
- Teacher routes: `/api/v1/teacher/...`
- Auth routes: `/api/v1/auth/...`

---

## Common Issues & Troubleshooting

### 1. `address already in use` (port 8000)

```bash
lsof -i :8000
kill -9 <PID>
```

### 2. `connection refused` (MySQL)

```bash
mysqladmin ping -u root
# If not running:
brew services start mysql            # macOS
sudo systemctl start mysql           # Linux
```

### 3. `connection refused` (Redis)

```bash
redis-cli ping
# If not running:
brew services start redis            # macOS
sudo systemctl start redis           # Linux
```

### 4. `ModuleNotFoundError: No module named 'src'`

```bash
# Make sure you installed in editable mode from the backend/ directory
pip install -e .
```

### 5. Alembic migration errors

```bash
# Reset and re-run
alembic stamp head
alembic upgrade head
```

### 6. Frontend `@school-erp/ui-shared` not found

The shared package must be at `../shared` relative to each frontend. If you see this error:
```bash
cd admin && npm install   # Re-links the shared package
cd teacher && npm install
```

### 7. CORS errors from frontend

Make sure `.env` has your frontend URLs:
```
ALLOWED_ORIGINS=["http://localhost:5173","http://localhost:5174","http://localhost:5175"]
```

### 8. `401 Unauthorized` on every request

- Verify cookies are sent (`withCredentials: true` in Axios)
- Verify `X-School-Code: SCH001` header is present
- Access tokens expire in 15 min — the frontend auto-refreshes them

### 9. `Unknown column 'max_periods'` during seed

Run migrations first: `alembic upgrade head`

---

## Stopping Everything

```bash
# Backend: Ctrl+C in terminal

# Frontend: Ctrl+C in each terminal

# MySQL/Redis:
brew services stop mysql
brew services stop redis

# Or if using Docker:
docker-compose down
```
