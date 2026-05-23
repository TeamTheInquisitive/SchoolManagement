from __future__ import annotations

from src.core.exceptions import AccessDenied, ConflictError


class AttendanceAlreadySubmitted(ConflictError):
    """Raised when attendance for the same class+date already exists."""

    def __init__(self, class_section: str, date: str) -> None:
        super().__init__(
            f"Attendance already submitted for {class_section} on {date}. Use PUT to update.",
            details={"class_section": class_section, "date": date},
        )
        self.code = "ATTENDANCE_EXISTS"


class ClassNotAssigned(AccessDenied):
    """Raised when teacher is not assigned to the class."""

    def __init__(self) -> None:
        super().__init__("You are not assigned to this class")
        self.code = "CLASS_NOT_ASSIGNED"
