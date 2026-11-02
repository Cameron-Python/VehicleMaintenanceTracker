"""§9.6.2: dictionary-based student reporting, major filter and paging."""

import argparse

from student_repository import list_students


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--major", help="Optional exact major match")
    parser.add_argument("--from-date", dest="start_date", help="Enrollment on/after YYYY-MM-DD")
    parser.add_argument("--to-date", dest="end_date", help="Enrollment on/before YYYY-MM-DD")
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--page-size", type=int, default=20)
    args = parser.parse_args()
    if args.page < 1 or not 1 <= args.page_size <= 100:
        parser.error("page must be >= 1 and page-size must be 1..100")
    rows = list_students(
        major_filter=args.major,
        start_date=args.start_date,
        end_date=args.end_date,
        limit=args.page_size,
        offset=(args.page - 1) * args.page_size,
    )
    print(f"\nStudent Report, page {args.page} ({len(rows)} row(s))")
    print("-" * 85)
    if not rows:
        print("No matching students on this page.")
    for student in rows:
        print(
            f"{student['StudentID']:>5} | {student['FirstName']:<14} "
            f"{student['LastName']:<14} | {(student['Major'] or 'N/A'):<22} "
            f"| {student['EnrollmentDate']} | {student['Email']}"
        )


if __name__ == "__main__":
    main()
