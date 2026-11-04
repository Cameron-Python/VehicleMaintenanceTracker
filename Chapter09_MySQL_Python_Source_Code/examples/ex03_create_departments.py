"""§9.3.3: demonstrate DDL and MySQL's implicit DDL commit."""

from db_config import open_connection

SQL = """
CREATE TABLE IF NOT EXISTS Departments (
    DepartmentID VARCHAR(10) PRIMARY KEY,
    DepartmentName VARCHAR(100) NOT NULL
) ENGINE=InnoDB
"""


def main():
    connection = open_connection()
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(SQL)
        # In MySQL, CREATE TABLE causes an implicit commit. This explicit call
        # is harmless, but it cannot make the CREATE TABLE rollback-able.
        connection.commit()
        print("Departments table exists (created if it was missing).")
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
