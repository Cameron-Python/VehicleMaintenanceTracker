"""§9.3.4 and §9.6 GenAI tie-in: fixed, structured tool functions.

This module does NOT call an LLM. No arbitrary/generated SQL is accepted.
"""

from datetime import date

import mysql.connector

from student_repository import add_student, list_students


def add_student_tool(first_name: str, last_name: str, email: str,
                     enrollment_date: str, major: str = "") -> dict:
    """Approved write operation with machine-readable, verified result."""
    try:
        info = add_student(first_name, last_name, major, enrollment_date, email)
        return {"success": True, "rowcount": info["rowcount"],
                "student_id": info["lastrowid"]}
    except (ValueError, mysql.connector.Error):
        # Avoid returning raw SQL error details or credentials to an AI client.
        return {"success": False, "rowcount": 0,
                "message": "Student was not added; check fields or uniqueness."}


def get_students_tool(major: str | None = None, limit: int = 10) -> dict:
    """Approved read operation with explicit max rows for context safety."""
    if not isinstance(limit, int) or not 1 <= limit <= 25:
        return {"success": False, "message": "limit must be between 1 and 25."}
    try:
        rows = list_students(major_filter=major, limit=limit)
        safe_rows = [
            {key: (value.isoformat() if isinstance(value, date) else value)
             for key, value in row.items()}
            for row in rows
        ]
        return {"success": True, "rowcount": len(safe_rows), "students": safe_rows}
    except (ValueError, mysql.connector.Error):
        return {"success": False, "message": "Could not retrieve students."}


if __name__ == "__main__":
    import json
    print(json.dumps(get_students_tool(major="Computer Science", limit=5), indent=2))
