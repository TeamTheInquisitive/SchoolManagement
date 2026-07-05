from __future__ import annotations

from fastapi import Request, Response
from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse

from src.core.security import decode_token

# Maps URL path prefixes to module keys (list means any of those modules grants access).
ADMIN_ROUTE_MODULE_MAP = {
    "/api/v1/admin/dashboard": ["dashboard"],
    "/api/v1/admin/students": ["students", "admissions"],
    "/api/v1/admin/staff": ["staff"],
    "/api/v1/admin/teachers": ["staff"],
    "/api/v1/admin/timetable": ["timetable"],
    "/api/v1/admin/attendance": ["attendance"],
    "/api/v1/admin/examinations": ["examinations"],
    "/api/v1/admin/fees": ["fees"],
    "/api/v1/admin/transport": ["transport"],
    "/api/v1/admin/leaves": ["leaves"],
    "/api/v1/admin/mentoring": ["mentoring"],
    "/api/v1/admin/notifications": ["notifications"],
    "/api/v1/admin/library": ["library"],
    "/api/v1/admin/settings": ["settings"],
}


class ModuleAccessMiddleware(BaseHTTPMiddleware):
    """Middleware that enforces module-level access for admin users.

    GET requests are always allowed (read-only access for data fetching).
    Only write operations (POST, PUT, DELETE, PATCH) are restricted
    based on the admin's allowed_modules.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        path = request.url.path

        if not path.startswith("/api/v1/admin/"):
            return await call_next(request)

        if request.method == "GET":
            return await call_next(request)

        access_token = request.cookies.get("access_token")
        if not access_token:
            return await call_next(request)

        try:
            payload = decode_token(access_token)
        except (JWTError, Exception):
            return await call_next(request)

        if payload.get("type") != "access":
            return await call_next(request)

        if payload.get("role") != "admin":
            return await call_next(request)

        allowed_modules = payload.get("allowed_modules")
        if allowed_modules is None:
            return await call_next(request)

        required_modules = None
        for route_prefix, modules in ADMIN_ROUTE_MODULE_MAP.items():
            if path.startswith(route_prefix):
                required_modules = modules
                break

        if required_modules and not any(m in allowed_modules for m in required_modules):
            return JSONResponse(
                status_code=404,
                content={"detail": "Not found"},
            )

        return await call_next(request)


class SchoolContextMiddleware(BaseHTTPMiddleware):
    """Middleware that extracts X-School-Code header and sets it on request state."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        school_code = request.headers.get("X-School-Code")
        request.state.school_code = school_code
        response = await call_next(request)
        return response


class AuditContextMiddleware(BaseHTTPMiddleware):
    """Middleware that extracts user ID from the access token and stores it on request state.

    The DB session dependency uses this to SET @current_user_id so MySQL triggers
    can populate created_by / updated_by automatically.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        user_id: str | None = None
        access_token = request.cookies.get("access_token")
        if access_token:
            try:
                payload = decode_token(access_token)
                if payload.get("type") == "access":
                    user_id = payload.get("sub")
            except (JWTError, Exception):
                pass
        request.state.audit_user_id = user_id
        response = await call_next(request)
        return response
