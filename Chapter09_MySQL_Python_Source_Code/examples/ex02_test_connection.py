"""Lab 2 / §9.2: connect, handle common errors, and always close."""

import mysql.connector
from mysql.connector import errorcode

from db_config import load_db_config


def main():
    connection = None
    try:
        config = load_db_config()
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            print(f"Connected to {config['database']} on {config['host']}:{config['port']}")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied. Check DB_USER, DB_PASSWORD, and MySQL grants.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist. Check DB_NAME and run the SQL setup.")
        else:
            print(f"Unable to connect to MySQL: {err}")
    finally:
        if connection is not None:
            connection.close()
            print("Connection closed.")


if __name__ == "__main__":
    main()
