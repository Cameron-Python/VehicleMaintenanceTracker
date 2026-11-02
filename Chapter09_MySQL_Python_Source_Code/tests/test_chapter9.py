"""Run: python -m unittest discover -s tests -v (no database needed)."""

import unittest
from datetime import date
from unittest.mock import MagicMock, patch

from student_repository import (
    add_student, build_student_filters, list_students, validate_student,
)


class TestStudentInput(unittest.TestCase):
    def test_valid_iso_date(self):
        self.assertEqual(
            validate_student("A", "B", "a@example.com", "2026-02-01"),
            date(2026, 2, 1),
        )

    def test_invalid_date_rejected(self):
        with self.assertRaises(ValueError):
            validate_student("A", "B", "a@example.com", "2026-02-30")

    def test_missing_name_rejected(self):
        with self.assertRaises(ValueError):
            validate_student(" ", "B", "a@example.com", "2026-01-01")

    def test_filters_parameterized_even_for_malicious_input(self):
        injection = "' OR 1=1 --"
        sql, params = build_student_filters(major_filter=injection, search_text="Alice")
        self.assertNotIn(injection, sql)
        self.assertEqual(sql.count("%s"), 4)
        self.assertEqual(params, (injection, "%Alice%", "%Alice%", "%Alice%"))

    def test_page_limit_checked(self):
        with self.assertRaises(ValueError):
            list_students(limit=10000)


class TestTransactionPatterns(unittest.TestCase):
    @patch("student_repository.open_connection")
    def test_success_commits_and_closes(self, mock_connect):
        connection = MagicMock()
        cursor = connection.cursor.return_value
        cursor.rowcount = 1
        cursor.lastrowid = 2020
        mock_connect.return_value = connection
        result = add_student("Alice", "B", "CS", "2026-02-01", "a@example.com")
        self.assertEqual(result, {"rowcount": 1, "lastrowid": 2020})
        connection.commit.assert_called_once()
        connection.rollback.assert_not_called()
        cursor.close.assert_called_once()
        connection.close.assert_called_once()
        self.assertIn("%s", cursor.execute.call_args.args[0])

    @patch("student_repository.open_connection")
    def test_error_rolls_back_and_closes(self, mock_connect):
        connection = MagicMock()
        cursor = connection.cursor.return_value
        cursor.execute.side_effect = RuntimeError("simulated statement failure")
        mock_connect.return_value = connection
        with self.assertRaisesRegex(RuntimeError, "simulated statement failure"):
            add_student("Alice", "B", "CS", "2026-02-01", "a@example.com")
        connection.commit.assert_not_called()
        connection.rollback.assert_called_once()
        cursor.close.assert_called_once()
        connection.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
