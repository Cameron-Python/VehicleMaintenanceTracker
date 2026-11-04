"""§9.3.4–9.3.5 / Lab 3: safe INSERT -> UPDATE -> DELETE.

Uses the temporary department ID 'CIS_DEMO'; the demo cleans up after itself.
"""

import mysql.connector
from mysql.connector import errorcode

from db_config import open_connection


def run_dml(sql: str, params: tuple, *, label: str) -> dict:
    connection = open_connection()
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        result = {"rowcount": cursor.rowcount, "lastrowid": cursor.lastrowid}
        connection.commit()
        return result
    except Exception:
        connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def main():
    department_id = "CIS_DEMO"
    # The example uses a dedicated demo row. A previous interrupted run can
    # leave it behind; handle a duplicate key rather than deleting user data.
    try:
        result = run_dml(
            "INSERT INTO Departments (DepartmentID, DepartmentName) VALUES (%s, %s)",
            (department_id, "Demo Department"), label="INSERT",
        )
        print(f"INSERT rowcount={result['rowcount']}, lastrowid={result['lastrowid']}")
    except mysql.connector.Error as err:
        if err.errno != errorcode.ER_DUP_ENTRY:
            raise
        print("CIS_DEMO exists already. Remove it manually or continue with this demo.")

    updated = run_dml(
        "UPDATE Departments SET DepartmentName = %s WHERE DepartmentID = %s",
        ("Computer and Information Sciences (Demo)", department_id), label="UPDATE",
    )
    print(f"UPDATE rowcount={updated['rowcount']}")

    # Force a duplicate-key error to demonstrate rollback.
    try:
        run_dml(
            "INSERT INTO Departments (DepartmentID, DepartmentName) VALUES (%s, %s)",
            (department_id, "Duplicate ID"), label="DUPLICATE INSERT",
        )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DUP_ENTRY:
            print("Duplicate primary key rejected: rollback executed as expected.")
        else:
            raise

    deleted = run_dml(
        "DELETE FROM Departments WHERE DepartmentID = %s",
        (department_id,), label="DELETE",
    )
    print(f"DELETE rowcount={deleted['rowcount']}")


if __name__ == "__main__":
    main()
