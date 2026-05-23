from __future__ import annotations

"""
PDF Generation Utility

Provides helper functions for generating PDFs (report cards, receipts, payslips).
This module defines the interface/stubs. Actual PDF generation logic can be implemented
using reportlab, weasyprint, or another library.
"""

from io import BytesIO
from typing import Any


def generate_report_card_pdf(
    student_data: dict[str, Any],
    subjects: list[dict[str, Any]],
    overall: dict[str, Any],
    school_info: dict[str, Any],
) -> BytesIO:
    """
    Generate a report card PDF for a student.

    Args:
        student_data: Student info (name, roll_number, class_section, academic_year).
        subjects: List of subject results with marks, grades.
        overall: Overall statistics (gpa, rank, attendance).
        school_info: School name, address, logo_url.

    Returns:
        BytesIO buffer containing the PDF content.
    """
    # Stub implementation - returns empty PDF placeholder
    buffer = BytesIO()
    # In production, use reportlab or weasyprint to generate actual PDF
    content = _build_placeholder_pdf(
        title="Report Card",
        data={
            "student": student_data,
            "subjects": subjects,
            "overall": overall,
            "school": school_info,
        },
    )
    buffer.write(content)
    buffer.seek(0)
    return buffer


def generate_fee_receipt_pdf(
    receipt_data: dict[str, Any],
    payments: list[dict[str, Any]],
    school_info: dict[str, Any],
) -> BytesIO:
    """
    Generate a fee receipt PDF.

    Args:
        receipt_data: Receipt info (receipt_number, student_name, class_section, date).
        payments: List of payment records.
        school_info: School name, address.

    Returns:
        BytesIO buffer containing the PDF content.
    """
    buffer = BytesIO()
    content = _build_placeholder_pdf(
        title="Fee Receipt",
        data={
            "receipt": receipt_data,
            "payments": payments,
            "school": school_info,
        },
    )
    buffer.write(content)
    buffer.seek(0)
    return buffer


def generate_payslip_pdf(
    staff_data: dict[str, Any],
    payslip_data: dict[str, Any],
    earnings: list[dict[str, Any]],
    deductions: list[dict[str, Any]],
    school_info: dict[str, Any],
) -> BytesIO:
    """
    Generate a payslip PDF for a staff member.

    Args:
        staff_data: Staff info (name, employee_id, department, designation).
        payslip_data: Payslip info (month, year, net_salary).
        earnings: List of earning components.
        deductions: List of deduction components.
        school_info: School name, address.

    Returns:
        BytesIO buffer containing the PDF content.
    """
    buffer = BytesIO()
    content = _build_placeholder_pdf(
        title="Payslip",
        data={
            "staff": staff_data,
            "payslip": payslip_data,
            "earnings": earnings,
            "deductions": deductions,
            "school": school_info,
        },
    )
    buffer.write(content)
    buffer.seek(0)
    return buffer


def _build_placeholder_pdf(title: str, data: dict[str, Any]) -> bytes:
    """
    Build a placeholder PDF content.

    In production, replace this with actual PDF generation using:
    - reportlab for programmatic PDF creation
    - weasyprint for HTML-to-PDF conversion

    For now, returns a simple text representation as bytes.
    """
    lines = [
        f"=== {title} ===",
        "",
    ]
    for key, value in data.items():
        lines.append(f"{key}: {value}")
    lines.append("")
    lines.append("--- End of Document ---")
    return "\n".join(lines).encode("utf-8")
