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
| Docker (optional) | 20+ | `docker --version` |

## Quick Start

### Option 1: Docker (Recommended)

```bash
cd school-erp-backend

# Start all services (MySQL + Redis + App)
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

#### Step 1: Start MySQL & Redis

```bash
# macOS (Homebrew)
brew services start mysql
brew services start redis

# Or use Docker for just DB + Redis
docker run -d --name school-mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=school_erp mysql:8.0 --default-authentication-plugin=mysql_native_password --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
docker run -d --name school-redis -p 6379:6379 redis:7-alpine
```

#### Step 2: Create Database

```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS school_erp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Verify connection
mysql -u root -p school_erp -e "SELECT 1;"
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
# - MYSQL_PASSWORD=password
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

### 2. `connection refused` (MySQL)

```bash
# Check if MySQL is running
mysqladmin ping -u root -p
# → mysqld is alive

# If not running:
brew services start mysql            # macOS
sudo systemctl start mysql           # Linux

# Check connection with your .env settings
mysql -h localhost -u root -p school_erp
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

# If that fails, check DATABASE_URL in .env matches your actual MySQL setup
mysql -u root -p school_erp -e "SHOW TABLES;"
```

---

## Stopping the Server

```bash
# If running in foreground: Ctrl+C

# If running via Docker:
docker-compose down

# Stop MySQL/Redis (local):
brew services stop mysql
brew services stop redis
```
