"""Chapter 9: one place to load local settings and open a MySQL connection."""

import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent


def load_db_config() -> dict:
    """Load a local .env; OS environment variables take precedence."""
    load_dotenv(PROJECT_ROOT / ".env")
    missing = [
        key for key in ("DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME")
        if not os.getenv(key)
    ]
    if missing:
        raise RuntimeError(
            "Missing database setting(s): " + ", ".join(missing)
            + ". Copy .env.example to .env and fill in your own settings."
        )

    try:
        port = int(os.getenv("DB_PORT") or "3306")
    except ValueError as exc:
        raise ValueError("DB_PORT must be a valid integer, usually 3306.") from exc
    if not 1 <= port <= 65535:
        raise ValueError("DB_PORT must be between 1 and 65535.")

    return {
        "host": os.environ["DB_HOST"],
        "port": port,
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
        "database": os.environ["DB_NAME"],
        "autocommit": False,
        "connection_timeout": 10,
    }


def open_connection():
    """Return a new connection; the caller must close it."""
    return mysql.connector.connect(**load_db_config())
