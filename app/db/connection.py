"""
Database connection and health-check helpers.
"""

import psycopg

from app.core.config import get_settings
from app.core.logging import app_log_event


def get_active_db_name() -> str:
    return get_settings().db_name


def get_db_connection(db_name: str | None = None) -> psycopg.Connection:
    settings = get_settings()

    target_db = db_name or get_active_db_name()

    conn = psycopg.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=target_db,
        user=settings.db_user,
        password=settings.db_password,
        connect_timeout=3,
    )
    return conn


def check_database_health() -> bool:
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        return True
    except Exception as exc:
        app_log_event(
            event_name="database_health_check_failed",
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        return False
