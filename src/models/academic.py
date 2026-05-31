from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import BaseModel, UUIDType


class Class(BaseModel):
    """Class (grade level) definition, e.g., '8', '9', '10', 'LKG'."""

    __tablename__ = "classes"
    __table_args__ = (
        UniqueConstraint("school_id", "name", name="uq_classes_school_name"),
    )

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(100), default=None)
    sort_order: Mapped[int] = mapped_column(default=0)
    max_periods: Mapped[int | None] = mapped_column(Integer, default=None)  # None = all periods apply

    # Relationships
    class_sections: Mapped[list[ClassSection]] = relationship(
        "ClassSection", back_populates="class_", lazy="selectin"
    )


class Section(BaseModel):
    """Section definition, e.g., 'A', 'B', 'C'."""

    __tablename__ = "sections"
    __table_args__ = (
        UniqueConstraint("school_id", "name", name="uq_sections_school_name"),
    )

    name: Mapped[str] = mapped_column(String(10), nullable=False)
    sort_order: Mapped[int] = mapped_column(default=0)

    # Relationships
    class_sections: Mapped[list[ClassSection]] = relationship(
        "ClassSection", back_populates="section", lazy="selectin"
    )


class ClassSection(BaseModel):
    """Composite mapping of class + section for a given academic year."""

    __tablename__ = "class_sections"
    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "class_id",
            "section_id",
            "academic_year_id",
            name="uq_class_sections_school_class_section_year",
        ),
    )

    class_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("classes.id"), nullable=False
    )
    section_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("sections.id"), nullable=False
    )
    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )

    # Relationships
    class_: Mapped[Class] = relationship("Class", back_populates="class_sections", lazy="selectin")
    section: Mapped[Section] = relationship(
        "Section", back_populates="class_sections", lazy="selectin"
    )


class Subject(BaseModel):
    """Subject definition (school-wide)."""

    __tablename__ = "subjects"
    __table_args__ = (
        UniqueConstraint("school_id", "name", name="uq_subjects_school_name"),
        UniqueConstraint("school_id", "code", name="uq_subjects_school_code"),
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str | None] = mapped_column(String(20), default=None)
    description: Mapped[str | None] = mapped_column(Text, default=None)


class ClassSubject(BaseModel):
    """Mapping of subject to class for a given academic year."""

    __tablename__ = "class_subjects"
    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "class_id",
            "subject_id",
            "academic_year_id",
            name="uq_class_subjects",
        ),
    )

    class_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("classes.id"), nullable=False
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("subjects.id"), nullable=False
    )
    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
