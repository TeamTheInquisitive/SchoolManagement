from __future__ import annotations

from src.core.exceptions import ConflictError


class TeacherConflict(ConflictError):
    """Teacher is already assigned to another class at the same time."""

    def __init__(
        self,
        teacher_name: str,
        existing_class: str,
        existing_subject: str,
        day: str,
        period_start_time: str,
    ) -> None:
        super().__init__(
            "Conflict: Teacher already assigned to another class at this time.",
            details={
                "teacher_name": teacher_name,
                "existing_class": existing_class,
                "existing_subject": existing_subject,
                "day": day,
                "period_start_time": period_start_time,
            },
        )


class SlotAlreadyOccupied(ConflictError):
    """Slot is already occupied by another assignment."""

    def __init__(self, day: str, period_start_time: str, class_section: str) -> None:
        super().__init__(
            f"Slot already occupied for {class_section} on {day} at {period_start_time}",
            details={
                "day": day,
                "period_start_time": period_start_time,
                "class_section": class_section,
            },
        )


class TimeOverlap(ConflictError):
    """Period time overlaps with an existing period."""

    def __init__(self, existing_name: str, existing_start: str, existing_end: str) -> None:
        super().__init__(
            f"Time overlap with {existing_name} ({existing_start} - {existing_end})",
            details={
                "existing_period": existing_name,
                "existing_start_time": existing_start,
                "existing_end_time": existing_end,
            },
        )
