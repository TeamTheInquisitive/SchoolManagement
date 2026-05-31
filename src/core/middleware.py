from __future__ import annotations

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class SchoolContextMiddleware(BaseHTTPMiddleware):
    """Middleware that extracts X-School-Code header and sets it on request state."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        school_code = request.headers.get("X-School-Code")
        request.state.school_code = school_code
        response = await call_next(request)
        return response
