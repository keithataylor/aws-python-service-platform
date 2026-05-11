from pathlib import Path

from app.db.connection import get_db_connection


MIGRATION_FILES = [
    "001_create_documents_table.sql",
    "002_seed_documents.sql",
    "003_create_pdp_audit_table.sql",
    "004_create_registered_agent_credentials.sql",
]


def main() -> None:
    migrations_dir = Path("migrations")

    with get_db_connection() as connection:
        for filename in MIGRATION_FILES:
            migration_path = migrations_dir / filename
            sql = migration_path.read_text(encoding="utf-8")

            print(f"Running migration: {filename}")

            with connection.cursor() as cursor:
                cursor.execute(sql)

            connection.commit()

            print(f"Completed migration: {filename}")

    print("All migrations completed successfully.")


if __name__ == "__main__":
    main()