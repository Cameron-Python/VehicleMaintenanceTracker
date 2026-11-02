"""Optional project question: add student + advisor in ONE transaction."""

from student_repository import db_session, validate_student


def create_student_with_advisor(first, last, email, when, advisor):
    """Both inserts succeed, or neither is saved."""
    when = validate_student(first, last, email, when)
    if not advisor.strip():
        raise ValueError("Advisor name is required.")
    with db_session() as (connection, cursor):
        cursor.execute(
            """INSERT INTO Students (FirstName, LastName, Major, EnrollmentDate, Email)
               VALUES (%s, %s, %s, %s, %s)""",
            (first.strip(), last.strip(), None, when, email.strip()),
        )
        student_id = cursor.lastrowid
        student_rows = cursor.rowcount
        cursor.execute(
            "INSERT INTO AdvisorAssignments (StudentID, AdvisorName) VALUES (%s, %s)",
            (student_id, advisor.strip()),
        )
        advisor_rows = cursor.rowcount
        connection.commit()
        return {"student_id": student_id, "student_rows": student_rows,
                "advisor_rows": advisor_rows}


if __name__ == "__main__":
    print("Import create_student_with_advisor() and supply your own sample values.")
    print("To test a rollback, deliberately violate an AdvisorAssignments constraint.")
