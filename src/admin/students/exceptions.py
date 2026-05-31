from __future__ import annotations

from src.core.exceptions import ConflictError, NotFound


class StudentNotFound(NotFound):
    """Student not found."""

    def __init__(self, student_id: str) -> None:
        super().__init__("Student", student_id)


class DuplicateRollNumber(ConflictError):
    """Duplicate roll/admission number within a school."""

    def __init__(self, roll_number: str) -> None:
        super().__init__(
            f"Student with admission number '{roll_number}' already exists",
            details={"admission_number": roll_number},
        )
