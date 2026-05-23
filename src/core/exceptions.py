from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        status_code: int,
        error: str,
        code: str,
        details: dict | None = None,
    ) -> None:
        self.status_code = status_code
        self.error = error
        self.code = code
        self.details = details
        super().__init__(error)


class NotFound(AppException):
    """Resource not found."""

    def __init__(self, resource: str, id: str | None = None) -> None:
        details = {"id": id} if id else None
        super().__init__(404, f"{resource} not found", "NOT_FOUND", details)


class AccessDenied(AppException):
    """Access denied / insufficient permissions."""

    def __init__(self, reason: str = "Insufficient permissions") -> None:
        super().__init__(403, reason, "ACCESS_DENIED")


class ConflictError(AppException):
    """Resource conflict (duplicate, already exists, etc.)."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(409, message, "CONFLICT", details)


class ValidationError(AppException):
    """Business validation error."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(422, message, "VALIDATION_ERROR", details)


class AuthenticationError(AppException):
    """Authentication failed."""

    def __init__(self, message: str = "Invalid credentials") -> None:
        super().__init__(401, message, "AUTHENTICATION_ERROR")


class TokenExpiredError(AppException):
    """Token has expired."""

    def __init__(self) -> None:
        super().__init__(401, "Token has expired", "TOKEN_EXPIRED")


class TokenInvalidError(AppException):
    """Token is invalid."""

    def __init__(self) -> None:
        super().__init__(401, "Invalid token", "TOKEN_INVALID")


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Global exception handler for AppException."""
    content: dict = {"error": exc.error, "code": exc.code}
    if exc.details:
        content["details"] = exc.details
    return JSONResponse(status_code=exc.status_code, content=content)
