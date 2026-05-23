# Backend Setup Log — Issues & Fixes

This documents every issue encountered during first-time setup and how it was resolved.

---

## Setup Steps (What Actually Worked)

```bash
cd /Users/nsharsha/Documents/testing/school-erp-backend

# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -e .

# 3. Copy env file
cp .env.example .env

# 4. Edit .env — set your local PostgreSQL user (Homebrew uses your macOS username with no password)
# POSTGRES_USER=nsharsha
# POSTGRES_PASSWORD=

# 5. Install & start PostgreSQL
brew install postgresql@16
brew services start postgresql@16

# 6. Create database
export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"
createdb school_erp

# 7. Create tables (direct, not via Alembic — see Issue #4 below)
python -c "
import asyncio
from src.core.database import engine
from src.core.base_model import Base
from src.models import *
async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
asyncio.run(create_all())
"

# 8. Seed demo users
python -m src.seeds.initial

# 9. Start server
uvicorn src.main:app --reload --port 8000

# 10. Test
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -H "X-School-Code: SCH001" \
  -d '{"email":"admin@school.com","password":"password123"}'
```

---

## Issues Encountered & Fixes Applied

### Issue #1: `metadata-generation-failed` during pip install

**Error:** Hatchling couldn't find packages.

**Fix:** Added `[tool.hatch.build.targets.wheel]` section to `pyproject.toml`:
```toml
[tool.hatch.build.targets.wheel]
packages = ["src"]
```

---

### Issue #2: `from __future__ import annotations` breaks Pydantic v2

**Error:** `TypeError: unsupported operand type(s) for |: 'NoneType' and 'NoneType'` on schema classes.

**Cause:** `from __future__ import annotations` makes all type annotations lazy strings. Pydantic v2 needs to evaluate them at class definition time.

**Fix:** Removed `from __future__ import annotations` from all `schemas.py` files:
```bash
find src -name "schemas.py" -exec sed -i '' '/^from __future__ import annotations$/d' {} \;
```

Also fixed `date: date | None = None` field name collision by using `Optional[date]` where a field is named `date`.

---

### Issue #3: `passlib` incompatible with newer `bcrypt` package

**Error:** `AttributeError: module 'bcrypt' has no attribute '__about__'` and `ValueError: password cannot be longer than 72 bytes`

**Cause:** `passlib` hasn't been updated to work with `bcrypt >= 4.1`. The `CryptContext` wrapper is broken.

**Fix:** Replaced `passlib` with direct `bcrypt` usage in `src/core/security.py`:
```python
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
```

---

### Issue #4: Alembic autogenerate creates tables in wrong order (FK dependency issue)

**Error:** `relation "subjects" does not exist` when creating `staff` table (FK to subjects).

**Cause:** Alembic autogenerate doesn't always resolve cross-table FK ordering correctly.

**Fix:** Used direct `Base.metadata.create_all()` instead of Alembic for initial schema. SQLAlchemy handles dependency ordering internally:
```python
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

Also removed the direct FK from `staff.primary_subject_id → subjects.id` (enforced at app level instead).

---

### Issue #5: `can't subtract offset-naive and offset-aware datetimes`

**Error:** `asyncpg.exceptions.DataError` when updating `last_login_at` with timezone-aware datetime into a `TIMESTAMP WITHOUT TIME ZONE` column.

**Cause:** `datetime.now(timezone.utc)` produces a tz-aware datetime, but PostgreSQL column expects naive.

**Fix:** Changed to `datetime.utcnow()` in `src/auth/service.py`:
```python
# Before (broken):
user.last_login_at = datetime.now(timezone.utc)

# After (works):
user.last_login_at = datetime.utcnow()
```

---

### Issue #6: Redis not running — server crashes on startup

**Error:** `RuntimeError: Redis client not initialized`

**Fix:** Made Redis optional in `src/core/redis.py` — if Redis isn't available, the app starts with a warning but token blacklist is disabled:
```python
async def init_redis() -> None:
    try:
        redis_client = Redis(connection_pool=pool)
        await redis_client.ping()
    except Exception:
        print("WARNING: Redis not available. Token blacklist disabled.")
        redis_client = None
```

---

### Issue #7: `ImportError: cannot import name 'Staff' from 'src.models.core'`

**Error:** `src/admin/notifications/service.py` tried to import `Staff` from wrong module.

**Fix:** Changed import to correct module:
```python
# Before (wrong):
from src.models.core import Staff, User

# After (correct):
from src.models.core import User
from src.models.staff import Staff
```

---

### Issue #8: Port 8000 already in use

**Error:** `[Errno 48] error while attempting to bind on address ('127.0.0.1', 8000): address already in use`

**Fix:**
```bash
lsof -ti :8000 | xargs kill -9
# Then restart
uvicorn src.main:app --reload --port 8000
```

---

## Current Working State

- Server starts and responds to `/health`
- Login works for all 3 roles (admin, teacher, student)
- Redis is optional (disabled gracefully if not running)
- PostgreSQL 16 via Homebrew on macOS
- All 238+ endpoints registered (backend logic ready)
- Frontend login integration working for all 3 React modules

---

## Environment (.env that works on this machine)

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=nsharsha
POSTGRES_PASSWORD=
POSTGRES_DB=school_erp
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=local
JWT_SECRET_KEY=change-me-in-production
```
