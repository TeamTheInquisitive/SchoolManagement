from __future__ import annotations

"""
CSV Export Utility

Provides helper functions for generating CSV content from list of dicts.
Used by staff/student/teacher export endpoints.
"""

import csv
from io import StringIO
from typing import Any


def generate_csv(
    data: list[dict[str, Any]],
    columns: list[str] | None = None,
    headers: list[str] | None = None,
) -> str:
    """
    Generate CSV content from a list of dictionaries.

    Args:
        data: List of dictionaries representing rows.
        columns: List of column keys to include. If None, uses all keys from first row.
        headers: Custom header names for the CSV. If None, uses column keys as headers.

    Returns:
        CSV content as a string.
    """
    if not data:
        return ""

    # Determine columns
    if columns is None:
        columns = list(data[0].keys())

    # Determine headers
    if headers is None:
        headers = columns

    output = StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(headers)

    # Write data rows
    for row in data:
        writer.writerow([row.get(col, "") for col in columns])

    return output.getvalue()


def generate_csv_bytes(
    data: list[dict[str, Any]],
    columns: list[str] | None = None,
    headers: list[str] | None = None,
) -> bytes:
    """
    Generate CSV content as bytes (for streaming responses).

    Args:
        data: List of dictionaries representing rows.
        columns: List of column keys to include.
        headers: Custom header names for the CSV.

    Returns:
        CSV content as bytes (UTF-8 encoded).
    """
    csv_str = generate_csv(data, columns, headers)
    return csv_str.encode("utf-8")


def generate_csv_response_headers(filename: str) -> dict[str, str]:
    """
    Generate HTTP headers for a CSV file download response.

    Args:
        filename: The filename for the download.

    Returns:
        Dictionary of HTTP headers.
    """
    return {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "text/csv; charset=utf-8",
    }
