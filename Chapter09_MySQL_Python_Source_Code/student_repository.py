"""Reusable, allowlisted student operations from §§9.6–9.7.

Only fixed SQL statements and fixed optional filters are allowed. User values
are always passed as SQL parameters, never spliced into SQL text.
"""

from contextlib import contextmanager
from datetime import date

from db_config import open_connection


@contextmanager
def db_session(*, dictionary=False, connection_factory=None):
    """Close every cursor/connection; roll back if the operation fails.

    A pooled connection is returned to the pool by connection.close().
    """
    connection = (connection_factory or open_connection)()
    cursor = None
    try:
        cursor = connection.cursor(dictionary=dictionary)
        yield connection, cursor
    except Exception:
        connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def validate_student(first_name, last_name, email, enrollment_date):
    """Check simple classroom rules; UNIQUE(Email) enforces uniqueness."""
    if not all(isinstance(x, str) and x.strip() for x in (first_name, last_name, email)):
        raise ValueError("First name, last name, and email are required.")
    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("Email must look like name@example.com.")
    if any(len(v.strip()) > n for v, n in ((first_name, 50), (last_name, 50), (email, 255))):
        raise ValueError("One of the supplied fields is too long.")
    if isinstance(enrollment_date, str):
        try:
            enrollment_date = date.fromisoformat(enrollment_date)
        except ValueError as exc:
            raise ValueError("Enrollment date must be a valid YYYY-MM-DD date.") from exc
    if not isinstance(enrollment_date, date):
        raise ValueError("Enrollment date must be a date or YYYY-MM-DD string.")
    return enrollment_date


def add_student(first_name, last_name, major, enrollment_date, email, *, connection_factory=None):
    """Insert a student, returning {rowcount, lastrowid}; commit once."""
    enrollment_date = validate_student(first_name, last_name, email, enrollment_date)
    major = (major or "").strip() or None
    if major is not None and len(major) > 100:
        raise ValueError("Major must be at most 100 characters long.")
    with db_session(connection_factory=connection_factory) as (connection, cursor):
        cursor.execute(
            """INSERT INTO Students (FirstName, LastName, Major, EnrollmentDate, Email)
               VALUES (%s, %s, %s, %s, %s)""",
            (first_name.strip(), last_name.strip(), major, enrollment_date, email.strip()),
        )
        result = {"rowcount": cursor.rowcount, "lastrowid": cursor.lastrowid}
        connection.commit()
        return result


def get_student(student_id: int, *, connection_factory=None):
    with db_session(dictionary=True, connection_factory=connection_factory) as (_, cursor):
        cursor.execute(
            """SELECT StudentID, FirstName, LastName, Major, EnrollmentDate, Email
               FROM Students WHERE StudentID = %s""",
            (int(student_id),),
        )
        return cursor.fetchone()


def build_student_filters(major_filter=None, search_text=None, start_date=None, end_date=None):
    """Construct only *allowlisted* SQL fragments; return SQL and values."""
    clauses, params = [], []
    if major_filter and major_filter.strip():
        clauses.append("Major = %s")
        params.append(major_filter.strip())
    if search_text and search_text.strip():
        text = "%" + search_text.strip() + "%"
        clauses.append("(FirstName LIKE %s OR LastName LIKE %s OR Email LIKE %s)")
        params.extend([text, text, text])
    if start_date:
        clauses.append("EnrollmentDate >= %s")
        params.append(start_date)
    if end_date:
        clauses.append("EnrollmentDate <= %s")
        params.append(end_date)
    return (" WHERE " + " AND ".join(clauses)) if clauses else "", tuple(params)


def count_students(major_filter=None, search_text=None, *, connection_factory=None):
    where, params = build_student_filters(major_filter, search_text)
    with db_session(connection_factory=connection_factory) as (_, cursor):
        cursor.execute("SELECT COUNT(*) FROM Students" + where, params)
        return int(cursor.fetchone()[0])


def list_students(major_filter=None, search_text=None, *, limit=25, offset=0,
                  start_date=None, end_date=None, connection_factory=None):
    """Parameterized page of student rows; prevents unbounded dashboard reads."""
    if not 1 <= limit <= 100 or offset < 0:
        raise ValueError("limit must be 1..100; offset must be >= 0")
    where, params = build_student_filters(major_filter, search_text, start_date, end_date)
    sql = (
        "SELECT StudentID, FirstName, LastName, Major, EnrollmentDate, Email "
        "FROM Students" + where + " ORDER BY StudentID DESC LIMIT %s OFFSET %s"
    )
    with db_session(dictionary=True, connection_factory=connection_factory) as (_, cursor):
        cursor.execute(sql, params + (limit, offset))
        return cursor.fetchall()


def update_major(student_id, new_major, *, connection_factory=None):
    major = (new_major or "").strip() or None
    if major is not None and len(major) > 100:
        raise ValueError("Major must be at most 100 characters long.")
    with db_session(connection_factory=connection_factory) as (connection, cursor):
        cursor.execute(
            "UPDATE Students SET Major = %s WHERE StudentID = %s",
            (major, int(student_id)),
        )
        affected = cursor.rowcount
        connection.commit()
        return affected


def delete_student(student_id, *, connection_factory=None):
    with db_session(connection_factory=connection_factory) as (connection, cursor):
        cursor.execute("DELETE FROM Students WHERE StudentID = %s", (int(student_id),))
        affected = cursor.rowcount
        connection.commit()
        return affected
