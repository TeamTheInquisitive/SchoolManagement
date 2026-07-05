from __future__ import annotations

from fastapi import Request, Response
from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.core.security import decode_token


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
