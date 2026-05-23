from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.admin.settings.router import router as admin_settings_router
from src.admin.staff.router import router as admin_staff_router
from src.admin.students.router import router as admin_students_router
from src.admin.teachers.router import router as admin_teachers_router
from src.auth.router import router as auth_router
from src.core.config import settings
from src.core.exceptions import AppException, app_exception_handler
from src.core.middleware import SchoolContextMiddleware
from src.core.redis import close_redis, init_redis
from src.admin.timetable.router import router as admin_timetable_router
from src.student.profile.router import router as student_profile_router
from src.student.assignments.router import router as student_assignments_router
from src.student.attendance.router import router as student_attendance_router
from src.student.timetable.router import router as student_timetable_router
from src.teacher.students.router import router as teacher_students_router
from src.teacher.attendance.router import router as teacher_attendance_router
from src.teacher.assignments.router import router as teacher_assignments_router
from src.teacher.timetable.router import router as teacher_timetable_router
from src.admin.examinations.router import router as admin_examinations_router
from src.admin.leaves.router import router as admin_leaves_router
from src.teacher.grades.router import router as teacher_grades_router
from src.teacher.leaves.router import router as teacher_leaves_router
from src.student.results.router import router as student_results_router
from src.admin.fees.router import router as admin_fees_router
from src.admin.transport.router import router as admin_transport_router
from src.student.fees.router import router as student_fees_router
from src.admin.notifications.router import router as admin_notifications_router
from src.student.notifications.router import router as student_notifications_router
from src.admin.payroll.router import router as admin_payroll_router
from src.admin.dashboard.router import router as admin_dashboard_router
from src.teacher.dashboard.router import router as teacher_dashboard_router
from src.teacher.adhoc_classes.router import router as teacher_adhoc_classes_router
from src.student.dashboard.router import router as student_dashboard_router
from src.student.library.router import router as student_library_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown events."""
    # Startup
    await init_redis()
    yield
    # Shutdown
    await close_redis()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    redirect_slashes=True,
)

# --- Exception handlers ---
app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]

# --- Middleware ---
# CORS (must be added before other middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# School context middleware
app.add_middleware(SchoolContextMiddleware)

# --- Routers ---
app.include_router(auth_router, prefix="/api/v1")
app.include_router(admin_settings_router, prefix="/api/v1")
app.include_router(admin_staff_router, prefix="/api/v1")
app.include_router(admin_students_router, prefix="/api/v1")
app.include_router(admin_teachers_router, prefix="/api/v1")
app.include_router(admin_timetable_router, prefix="/api/v1")
app.include_router(teacher_students_router, prefix="/api/v1")
app.include_router(teacher_attendance_router, prefix="/api/v1")
app.include_router(teacher_assignments_router, prefix="/api/v1")
app.include_router(teacher_timetable_router, prefix="/api/v1")
app.include_router(student_assignments_router, prefix="/api/v1")
app.include_router(student_attendance_router, prefix="/api/v1")
app.include_router(student_profile_router, prefix="/api/v1")
app.include_router(student_timetable_router, prefix="/api/v1")
app.include_router(admin_examinations_router, prefix="/api/v1")
app.include_router(admin_leaves_router, prefix="/api/v1")
app.include_router(teacher_grades_router, prefix="/api/v1")
app.include_router(teacher_leaves_router, prefix="/api/v1")
app.include_router(student_results_router, prefix="/api/v1")
app.include_router(admin_fees_router, prefix="/api/v1")
app.include_router(admin_transport_router, prefix="/api/v1")
app.include_router(student_fees_router, prefix="/api/v1")
app.include_router(admin_notifications_router, prefix="/api/v1")
app.include_router(student_notifications_router, prefix="/api/v1")
app.include_router(admin_payroll_router, prefix="/api/v1")
app.include_router(admin_dashboard_router, prefix="/api/v1")
app.include_router(teacher_dashboard_router, prefix="/api/v1")
app.include_router(teacher_adhoc_classes_router, prefix="/api/v1")
app.include_router(student_dashboard_router, prefix="/api/v1")
app.include_router(student_library_router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "app": settings.APP_NAME}
