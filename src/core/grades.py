"""Shared grade system utilities used by admin, teacher, and student modules."""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.examination import GradeScale, GradeSystem


async def get_active_grade_system(db: AsyncSession, school_id: uuid.UUID) -> GradeSystem | None:
    """Get the default/active grade system for a school."""
    result = await db.execute(
        select(GradeSystem).where(
            GradeSystem.school_id == school_id,
            GradeSystem.is_default.is_(True),
            GradeSystem.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


async def get_grade_scales(db: AsyncSession, school_id: uuid.UUID) -> list[dict]:
    """Get grade scales as a list of dicts (for API responses)."""
    grade_system = await get_active_grade_system(db, school_id)
    if not grade_system or not grade_system.scales:
        return []
    return [
        {
            "grade": s.grade,
            "min_percentage": float(s.min_percentage),
            "max_percentage": float(s.max_percentage),
            "grade_point": float(s.grade_point) if s.grade_point else None,
            "description": s.description,
        }
        for s in sorted(grade_system.scales, key=lambda x: float(x.min_percentage), reverse=True)
    ]


def compute_grade(percentage: float, scales: list[GradeScale]) -> str | None:
    """Compute grade letter from percentage using grade scales."""
    for scale in scales:
        if float(scale.min_percentage) <= percentage <= float(scale.max_percentage):
            return scale.grade
    return None
