"""§9.6.1 / Lab 5: console-based student input with validation."""

import mysql.connector
from mysql.connector import errorcode

from student_repository import add_student


def main():
    while True:
        print("\n--- Add New Student ---")
        first = input("First name: ").strip()
        last = input("Last name: ").strip()
        major = input("Major (optional): ").strip()
        when = input("Enrollment date (YYYY-MM-DD): ").strip()
        email = input("Email: ").strip()
        try:
            result = add_student(first, last, major, when, email)
            print(f"Student added. StudentID: {result['lastrowid']}; rowcount={result['rowcount']}")
        except ValueError as err:
            print(f"Invalid input: {err}")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                print("This email is already in use. No student was added.")
            else:
                print(f"Database operation failed: {err}")
        again = input("Add another student? (y/n): ").lower().strip()
        if again not in ("y", "yes"):
            break


if __name__ == "__main__":
    main()
