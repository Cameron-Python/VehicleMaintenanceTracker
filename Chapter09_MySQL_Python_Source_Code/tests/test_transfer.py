"""Mock tests of atomic transfer; do not contact a MySQL server."""

import unittest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from examples.ex06_transfer_funds import transfer_funds


class TestTransfer(unittest.TestCase):
    @patch("examples.ex06_transfer_funds.open_connection")
    def test_two_good_updates_commit_once(self, open_connection):
        connection = MagicMock()
        cursor = connection.cursor.return_value
        cursor.rowcount = 1
        open_connection.return_value = connection
        self.assertTrue(transfer_funds(101, 105, Decimal("10.00")))
        self.assertEqual(cursor.execute.call_count, 2)
        connection.commit.assert_called_once()
        connection.rollback.assert_not_called()
        connection.close.assert_called_once()

    @patch("examples.ex06_transfer_funds.open_connection")
    def test_failed_receiver_rolls_back_debit(self, open_connection):
        connection = MagicMock()
        cursor = connection.cursor.return_value
        open_connection.return_value = connection
        rows_affected = iter((1, 0))

        def execute(sql, params):
            cursor.rowcount = next(rows_affected)

        cursor.execute.side_effect = execute
        self.assertFalse(transfer_funds(101, 999, Decimal("10.00")))
        self.assertEqual(cursor.execute.call_count, 2)
        connection.rollback.assert_called_once()
        connection.commit.assert_not_called()
        cursor.close.assert_called_once()
        connection.close.assert_called_once()

    def test_reject_same_sender_receiver(self):
        with self.assertRaises(ValueError):
            transfer_funds(101, 101, Decimal("10.00"))


if __name__ == "__main__":
    unittest.main()
