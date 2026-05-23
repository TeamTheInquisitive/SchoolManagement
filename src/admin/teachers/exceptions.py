from __future__ import annotations

from src.core.exceptions import AppException, ConflictError, NotFound


class TeacherNotFound(NotFound):
    """Raised when a teacher is not found."""

    def __init__(self, teacher_id: str) -> None:
        super().__init__("Teacher", teacher_id)


class DuplicateAssignment(ConflictError):
    """Raised when a duplicate class assignment is detected."""

    def __init__(self, class_section: str, subject: str) -> None:
        super().__init__(
            f"Teacher is already assigned to {class_section} for {subject}",
            {"class_section": class_section, "subject": subject},
        )


class WorkloadExceeded(AppException):
    """Raised when assignment would exceed max workload hours."""

    def __init__(self, current: int, adding: int, max_hours: int) -> None:
        super().__init__(
            status_code=422,
            error=(
                f"Assignment would exceed max workload. "
                f"Current: {current}hrs, Adding: {adding}hrs, Max: {max_hours}hrs"
            ),
            code="WORKLOAD_EXCEEDED",
            details={"current": current, "adding": adding, "max": max_hours},
        )


class SubjectNotQualified(AppException):
    """Raised when a teacher is not qualified for the given subject."""

    def __init__(self, subject: str, qualified_subjects: list[str]) -> None:
        super().__init__(
            status_code=400,
            error=(
                f"Teacher is not qualified to teach {subject}. "
                f"Qualified subjects: {qualified_subjects}"
            ),
            code="SUBJECT_NOT_QUALIFIED",
            details={"subject": subject, "qualified_subjects": qualified_subjects},
        )
