"""§9.5.2: atomic transfer between two StudentAccounts rows (demo only)."""

import argparse
from decimal import Decimal, InvalidOperation

from db_config import open_connection


def transfer_funds(sender_id: int, receiver_id: int, amount: Decimal):
    """Debit + credit together; reject invalid receiver or insufficient funds."""
    if not amount.is_finite() or amount <= 0 or amount != amount.quantize(Decimal("0.01")):
        raise ValueError("Amount must be a positive value with at most 2 decimal places.")
    if sender_id == receiver_id:
        raise ValueError("Sender and receiver must be different accounts.")

    connection = open_connection()
    cursor = None
    try:
        connection.start_transaction()
        cursor = connection.cursor()
        # This conditional UPDATE performs the balance check atomically.
        cursor.execute(
            """UPDATE StudentAccounts SET Balance = Balance - %s
               WHERE StudentID = %s AND Balance >= %s""",
            (amount, sender_id, amount),
        )
        if cursor.rowcount != 1:
            raise ValueError("Sender missing or insufficient funds.")

        cursor.execute(
            "UPDATE StudentAccounts SET Balance = Balance + %s WHERE StudentID = %s",
            (amount, receiver_id),
        )
        if cursor.rowcount != 1:
            raise ValueError("Receiver account not found.")

        connection.commit()
        print(f"COMMIT: transferred ${amount:.2f} from {sender_id} to {receiver_id}.")
        return True
    except Exception as err:
        connection.rollback()
        print(f"ROLLBACK: no transfer saved. Reason: {err}")
        return False
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sender", type=int, help="Sender StudentID (seed: 101)")
    parser.add_argument("receiver", type=int, help="Receiver StudentID (seed: 105)")
    parser.add_argument("amount", help="USD amount, e.g. 10.00")
    args = parser.parse_args()
    try:
        amount = Decimal(args.amount)
    except InvalidOperation:
        parser.error("amount must be numeric (e.g. 10.00)")
    if args.sender < 1 or args.receiver < 1:
        parser.error("account IDs must be positive")
    try:
        transfer_funds(args.sender, args.receiver, amount)
    except ValueError as err:
        parser.error(str(err))


if __name__ == "__main__":
    main()
