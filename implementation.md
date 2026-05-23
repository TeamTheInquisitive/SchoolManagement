# School ERP Backend — Implementation Plan

## Tech Stack

| Layer | Technology | Version | Why |
|-------|-----------|---------|-----|
| Framework | FastAPI | 0.115+ | Async, type-safe, auto OpenAPI docs |
| Python | Python | 3.12+ | Latest features, performance |
| Database | PostgreSQL | 16+ | JSONB, UUID, robust |
| ORM | SQLAlchemy (async) | 2.0+ | Mapped columns, async sessions |
| Migrations | Alembic | 1.14+ | Autogenerate, reversible |
| Auth | python-jose (JWT) + httpOnly cookies | — | Secure token-based auth |
| Token Blacklist | Redis | 7+ | Fast logout invalidation |
| Validation | Pydantic v2 | 2.7+ | Request/response schemas |
| Config | pydantic-settings | 2.2+ | Type-safe env loading |
| Password Hashing | passlib[bcrypt] | — | Industry standard |
| Async DB Driver | asyncpg | — | Fastest PostgreSQL driver |
| Async Redis | redis[hiredis] | — | Async Redis client |
| CORS | FastAPI CORSMiddleware | — | Cross-origin |
| Email | fastapi-mail | — | Async email |
| File Storage | aiofiles + Local/S3 | — | Async file I/O |
| Linting | ruff | — | Fast Python linter + formatter |
| Containerization | Docker + docker-compose | — | App + Postgres + Redis |

---

## Project Structure (Domain-Based)

> Following the domain-based pattern from top FastAPI repos (zhanymkanov/fastapi-best-practices).
> Each domain module owns its own router, schemas, models, service, and exceptions.

```
school-erp-backend/
├── specs/                          # API specs (design phase artifacts)
├── alembic/
│   ├── versions/                   # Migration files: YYYY-MM-DD_slug.py
│   └── env.py
├── src/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app, lifespan, include routers
│   │
│   ├── core/                       # Shared infrastructure
│   │   ├── __init__.py
│   │   ├── config.py              # pydantic-settings: Settings(BaseSettings)
│   │   ├── database.py            # Async engine, sessionmaker, get_db
│   │   ├── redis.py               # Redis connection pool
│   │   ├── security.py            # JWT encode/decode, password hash/verify
│   │   ├── dependencies.py        # Annotated type aliases: SessionDep, CurrentUser, SchoolDep
│   │   ├── exceptions.py          # Base domain exceptions + global handlers
│   │   ├── pagination.py          # PaginatedResponse[T], PaginationParams
│   │   ├── middleware.py          # SchoolContext, RequestID, logging
│   │   └── base_model.py         # SQLAlchemy Base, TimestampMixin, SoftDeleteMixin, SchoolMixin
│   │
│   ├── auth/                       # Auth domain (shared across all roles)
│   │   ├── __init__.py
│   │   ├── router.py             # /api/v1/auth/...
│   │   ├── schemas.py            # LoginRequest, TokenResponse, etc.
│   │   ├── service.py            # login, logout, refresh, reset password logic
│   │   ├── dependencies.py       # get_current_user, role_required
│   │   └── exceptions.py         # InvalidCredentials, TokenExpired, etc.
│   │
│   ├── admin/                      # Admin portal domains
│   │   ├── __init__.py
│   │   ├── dashboard/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── students/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   └── exceptions.py
│   │   ├── teachers/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   └── exceptions.py
│   │   ├── leaves/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── timetable/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   └── exceptions.py
│   │   ├── examinations/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── fees/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── transport/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── staff/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── payroll/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── notifications/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   └── settings/
│   │       ├── router.py
│   │       ├── schemas.py
│   │       └── service.py
│   │
│   ├── teacher/                    # Teacher portal domains
│   │   ├── __init__.py
│   │   ├── dashboard/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── classes/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── students/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── attendance/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   └── exceptions.py
│   │   ├── assignments/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── grades/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── notifications/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── timetable/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── adhoc_classes/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   └── leaves/
│   │       ├── router.py
│   │       ├── schemas.py
│   │       └── service.py
│   │
│   ├── student/                    # Student portal domains
│   │   ├── __init__.py
│   │   ├── dashboard/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── timetable/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── attendance/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── assignments/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── results/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── fees/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── library/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── notifications/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   └── profile/
│   │       ├── router.py
│   │       ├── schemas.py
│   │       └── service.py
│   │
│   └── models/                     # SQLAlchemy models (shared across domains)
│       ├── __init__.py             # Import all models (for Alembic autogenerate)
│       ├── core.py                # School, User, AcademicYear, Settings, EnumConfig
│       ├── staff.py               # Staff, StaffSubjects, ClassAssignment
│       ├── student.py             # Student, StudentEnrollment, Parent, StudentParent, StudentMentor
│       ├── academic.py            # Class, Section, ClassSection, Subject
│       ├── timetable.py           # PeriodConfig, TimetableSlot
│       ├── attendance.py          # AttendanceSession, AttendanceRecord
│       ├── assignment.py          # Assignment, AssignmentSubmission
│       ├── examination.py         # Exam, ExamResult, GradeSystem, GradeScale
│       ├── leave.py               # LeavePolicy, LeaveApplication, LeaveBalance
│       ├── fee.py                 # FeeStructure, FeeRecord, FeePayment, FeeReminder, FeePenalty
│       ├── transport.py           # Vehicle, Driver, Helper, Route, RouteAssignment, StudentTransport
│       ├── notification.py        # Notification, NotificationRecipient
│       ├── payroll.py             # SalaryStructure, Payslip, SalaryAdvance, SalaryRevision
│       ├── activity.py            # Activity, Award, DisciplinaryRecord
│       ├── meeting.py             # ParentMeeting
│       └── adhoc_class.py         # AdhocClass
│
│
├── .env.example
├── .gitignore
├── alembic.ini
├── pyproject.toml                  # Project config + dependencies
├── Dockerfile
├── docker-compose.yml              # App + PostgreSQL + Redis
├── implementation.md
└── README.md
```

---

## Key Patterns (from top FastAPI repos research)

### 1. Config — pydantic-settings

```python
from pydantic_settings import BaseSettings
from pydantic import computed_field, model_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    APP_NAME: str = "School ERP Backend"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    DEBUG: bool = True

    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "school_erp"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"]

    # Email
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@school.com"

    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10

    @model_validator(mode="after")
    def validate_non_default_secrets(self):
        if self.ENVIRONMENT != "local" and self.JWT_SECRET_KEY == "change-me-in-production":
            raise ValueError("JWT_SECRET_KEY must be changed in non-local environments")
        return self

settings = Settings()
```

### 2. Annotated Type Aliases (Dependency Injection)

```python
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Database session
SessionDep = Annotated[AsyncSession, Depends(get_db)]

# Current authenticated user
CurrentUser = Annotated[User, Depends(get_current_user)]

# Role-specific users
AdminUser = Annotated[User, Depends(require_admin)]
TeacherUser = Annotated[User, Depends(require_teacher)]
StudentUser = Annotated[User, Depends(require_student)]

# School context
SchoolDep = Annotated[School, Depends(get_current_school)]

# Pagination
PaginationDep = Annotated[PaginationParams, Depends()]
```

Usage in routes:
```python
@router.get("/students/")
async def list_students(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    pagination: PaginationDep,
    class_name: str | None = None,
    status: str | None = None,
):
    return await student_service.list_students(db, school.id, pagination, class_name, status)
```

### 3. Base Model (SQLAlchemy 2.0 with Mixins)

```python
from sqlalchemy import MetaData, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid import uuid4
from datetime import datetime

# Explicit naming conventions for constraints/indexes
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

class SoftDeleteMixin:
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)
    deleted_by: Mapped[uuid4 | None] = mapped_column(UUID, default=None)

class AuditMixin:
    created_by: Mapped[uuid4 | None] = mapped_column(UUID, default=None)
    updated_by: Mapped[uuid4 | None] = mapped_column(UUID, default=None)

class SchoolMixin:
    school_id: Mapped[uuid4] = mapped_column(UUID, ForeignKey("schools.id"), index=True)

class BaseModel(Base, TimestampMixin, SoftDeleteMixin, AuditMixin, SchoolMixin):
    __abstract__ = True
    id: Mapped[uuid4] = mapped_column(UUID, primary_key=True, default=uuid4)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
```

### 4. Domain-Specific Exceptions + Global Handler

```python
# src/core/exceptions.py
class AppException(Exception):
    def __init__(self, status_code: int, error: str, code: str, details: dict | None = None):
        self.status_code = status_code
        self.error = error
        self.code = code
        self.details = details

class NotFound(AppException):
    def __init__(self, resource: str, id: str):
        super().__init__(404, f"{resource} not found", "NOT_FOUND", {"id": id})

class AccessDenied(AppException):
    def __init__(self, reason: str = "Insufficient permissions"):
        super().__init__(403, reason, "ACCESS_DENIED")

class ConflictError(AppException):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(409, message, "CONFLICT", details)

# Domain-specific (in each domain's exceptions.py)
class AttendanceAlreadySubmitted(ConflictError):
    def __init__(self, class_section: str, date: str):
        super().__init__(f"Attendance already submitted for {class_section} on {date}")

# Global handler in main.py
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error, "code": exc.code, "details": exc.details},
    )
```

### 5. Service Layer Pattern

```
Route (HTTP concerns) → Service (business logic) → Database (SQLAlchemy queries)
```

```python
# src/admin/students/router.py — thin, HTTP only
@router.post("/", status_code=201, response_model=StudentResponse)
async def create_student(
    data: CreateStudentRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    return await student_service.create(db, school.id, data, created_by=user.id)


# src/admin/students/service.py — business logic + DB queries
async def create(db: AsyncSession, school_id: UUID, data: CreateStudentRequest, created_by: UUID) -> Student:
    existing = await db.execute(
        select(Student).where(Student.school_id == school_id, Student.roll_number == data.roll_number)
    )
    if existing.scalar_one_or_none():
        raise ConflictError(f"Student with roll number {data.roll_number} already exists")

    student = Student(school_id=school_id, created_by=created_by, **data.model_dump())
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return student
```

### 6. Pagination (Generic, Reusable)

```python
from typing import TypeVar, Generic
from pydantic import BaseModel

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[T]

class PaginationParams:
    def __init__(self, page: int = 1, page_size: int = 20):
        self.page = max(1, page)
        self.page_size = min(100, max(1, page_size))

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

def paginate(items: list, total: int, params: PaginationParams) -> dict:
    return {
        "count": total,
        "page": params.page,
        "page_size": params.page_size,
        "total_pages": (total + params.page_size - 1) // params.page_size,
        "results": items,
    }
```


### 8. Alembic Configuration

```python
# alembic.ini
file_template = %%(year)d-%%(month).2d-%%(day).2d_%%(slug)s

# alembic/env.py — import all models for autogenerate
from src.models import *  # noqa: F401, F403
target_metadata = Base.metadata
```

Migration commands:
```bash
alembic revision --autogenerate -m "add_leave_balances_table"
alembic upgrade head
alembic downgrade -1  # rollback last migration
```

### 9. Redis Token Blacklist

```python
# src/core/redis.py
from redis.asyncio import Redis

redis_client: Redis | None = None

async def get_redis() -> Redis:
    return redis_client

# src/auth/service.py
async def logout(redis: Redis, token_jti: str, expires_in: int):
    await redis.setex(f"blacklist:{token_jti}", expires_in, "1")

async def is_token_blacklisted(redis: Redis, token_jti: str) -> bool:
    return await redis.exists(f"blacklist:{token_jti}")
```

### 10. Middleware Stack

```python
# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="School ERP Backend", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,  # for httpOnly cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# School context middleware
@app.middleware("http")
async def school_context_middleware(request: Request, call_next):
    school_code = request.headers.get("X-School-Code")
    if school_code:
        request.state.school_code = school_code
    response = await call_next(request)
    return response
```

---

## Implementation Order

### Phase 1: Foundation
- [x] 1. Project setup (pyproject.toml, docker-compose)
- [x] 2. `src/core/config.py` — pydantic-settings
- [x] 3. `src/core/database.py` — async SQLAlchemy engine + session
- [x] 4. `src/core/redis.py` — Redis connection
- [x] 5. `src/core/base_model.py` — Base + mixins
- [x] 6. `src/core/exceptions.py` — exception classes + handlers
- [x] 7. `src/core/dependencies.py` — Annotated type aliases
- [x] 8. `src/core/pagination.py` — generic pagination
- [x] 9. `src/core/middleware.py` — school context, request ID
- [x] 10. `src/core/security.py` — JWT + password hashing
- [x] 11. Alembic setup with naming conventions
- [x] 12. `src/models/core.py` — School, User, AcademicYear
- [x] 13. `src/auth/` — full auth domain (login, logout, refresh, me, password reset/change)
- [x] 14. Initial migration + seed script

### Phase 2: Academic Structure
- [x] 15. `src/models/academic.py` — Class, Section, ClassSection, Subject
- [x] 16. `src/models/core.py` — Settings, EnumConfig
- [x] 17. `src/admin/settings/` — CRUD + bulk create (classes, sections, subjects)

### Phase 3: Staff & Teachers
- [x] 18. `src/models/staff.py` — Staff, StaffSubjects, ClassAssignment
- [x] 19. `src/admin/staff/` — CRUD
- [x] 20. `src/admin/teachers/` — CRUD + assign + history

### Phase 4: Students
- [x] 21. `src/models/student.py` — Student, Enrollment, Parent, Mentor
- [x] 22. `src/admin/students/` — CRUD + export/import
- [x] 23. `src/teacher/students/` — read-only (mentor/class teacher)
- [x] 24. `src/student/profile/` — view + edit own

### Phase 5: Timetable
- [x] 25. `src/models/timetable.py` — PeriodConfig, TimetableSlot
- [x] 26. `src/admin/timetable/` — config + slots + bulk + conflicts
- [x] 27. `src/teacher/timetable/` — view own schedule
- [x] 28. `src/student/timetable/` — view class timetable

### Phase 6: Attendance
- [x] 29. `src/models/attendance.py` — Session, Record
- [x] 30. `src/teacher/attendance/` — mark, update, cancel, history
- [x] 31. `src/student/attendance/` — view own

### Phase 7: Assignments
- [x] 32. `src/models/assignment.py` — Assignment, Submission
- [x] 33. `src/teacher/assignments/` — CRUD + grade + export
- [x] 34. `src/student/assignments/` — view + submit

### Phase 8: Examinations & Results
- [x] 35. `src/models/examination.py` — Exam, Result, GradeSystem
- [x] 36. `src/admin/examinations/` — CRUD + results + publish + analytics
- [x] 37. `src/teacher/grades/` — enter + report + leaderboard
- [x] 38. `src/student/results/` — view + download

### Phase 9: Leaves
- [x] 39. `src/models/leave.py` — Policy, Application, Balance
- [x] 40. `src/admin/leaves/` — configure + approve + calendar
- [x] 41. `src/teacher/leaves/` — apply + balance + upcoming

### Phase 10: Fees
- [x] 42. `src/models/fee.py` — Structure, Record, Payment, Penalty, Reminder
- [x] 43. `src/admin/fees/` — generate + record + late fee + reminders
- [x] 44. `src/student/fees/` — view + receipts + reminders

### Phase 11: Transport
- [x] 45. `src/models/transport.py` — Vehicle, Driver, Helper, Route, Assignment, StudentTransport
- [x] 46. `src/admin/transport/` — full CRUD + operational mapping

### Phase 12: Notifications
- [x] 47. `src/models/notification.py` — Notification, Recipient
- [x] 48. `src/admin/notifications/` — create + send (target_type)
- [x] 49. `src/student/notifications/` — view + mark read

### Phase 13: Payroll
- [x] 50. `src/models/payroll.py` — Salary, Payslip, Advance, Revision
- [x] 51. `src/admin/payroll/` — run + generate + revisions

### Phase 14: Remaining
- [x] 52. `src/models/activity.py` — Activity, Award, Disciplinary
- [x] 53. `src/models/meeting.py` — ParentMeeting
- [x] 54. `src/models/adhoc_class.py` — AdhocClass
- [x] 55. `src/teacher/adhoc_classes/` — CRUD
- [x] 56. Dashboard aggregation (all 3 modules)
- [x] 57. PDF generation (report cards, receipts, payslips)
- [x] 58. CSV exports
- [x] 59. `src/student/library/` — view books (reads from admin-managed data)

---

## Environment Variables (.env.example)

```env
# App
APP_NAME=School ERP Backend
ENVIRONMENT=local
DEBUG=true

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=school_erp

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=change-me-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=["http://localhost:5173","http://localhost:5174","http://localhost:5175"]

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=noreply@school.com

# File Upload
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=10
```

---

## Docker Setup

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [db, redis]
    volumes: ["./src:/app/src", "./uploads:/app/uploads"]

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: school_erp
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

volumes:
  pgdata:
```

---

## Running

```bash
# Start services
docker-compose up -d

# Run migrations
alembic upgrade head

# Seed initial data
python -m src.seeds.initial

# Development server
uvicorn src.main:app --reload --port 8000

```

---

## API Documentation

Auto-generated at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
