"""§9.4 / Lab 4: fetchone(), fetchmany(), fetchall(), and dict cursors."""

import argparse
import json

from db_config import open_connection


def show_one(student_id: int):
    connection = open_connection()
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT FirstName, LastName FROM Students WHERE StudentID = %s",
            (student_id,),
        )
        row = cursor.fetchone()
        print(f"fetchone({student_id}): {row if row else 'no matching student'}")
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def show_batches(batch_size: int):
    connection = open_connection()
    cursor = None
    try:
        cursor = connection.cursor()  # unbuffered cursor, good for batching
        cursor.execute("SELECT StudentID, FirstName, LastName FROM Students ORDER BY StudentID")
        batch_number = 0
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            batch_number += 1
            print(f"fetchmany batch #{batch_number}: {batch}")
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def show_all_as_dicts():
    connection = open_connection()
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT StudentID, FirstName, LastName, Major FROM Students ORDER BY StudentID LIMIT 25")
        rows = cursor.fetchall()
        print("fetchall() dictionary rows (capped at 25 for this demonstration):")
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", type=int, default=2001, help="StudentID for fetchone")
    parser.add_argument("--batch-size", type=int, default=2)
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error("--batch-size must be positive")
    show_one(args.id)
    show_batches(args.batch_size)
    show_all_as_dicts()


if __name__ == "__main__":
    main()
