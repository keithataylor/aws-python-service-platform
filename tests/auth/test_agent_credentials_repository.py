import pytest

from app.auth.agent_credentials_repository import (
    get_active_agent_id_for_api_key_hash,
)
from app.db.connection import get_db_connection

pytestmark = pytest.mark.integration


def test_get_active_agent_id_for_api_key_hash_returns_agent_id() -> None:
    api_key_hash = "test-api-key-hash"
    agent_id = "test-agent"

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM agent_api_credentials")
            cursor.execute("DELETE FROM registered_agents")

            cursor.execute(
                """
                INSERT INTO registered_agents (
                    agent_id,
                    display_name,
                    status
                )
                VALUES (%s, %s, %s)
                """,
                (agent_id, "Test Agent", "active"),
            )

            cursor.execute(
                """
                INSERT INTO agent_api_credentials (
                    credential_id,
                    agent_id,
                    api_key_hash,
                    api_key_prefix,
                    status
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    "test-credential",
                    agent_id,
                    api_key_hash,
                    "test",
                    "active",
                ),
            )

            conn.commit()

    resolved_agent_id = get_active_agent_id_for_api_key_hash(api_key_hash)

    assert resolved_agent_id == agent_id



def test_get_active_agent_id_for_api_key_hash_returns_none_for_revoked_credential() -> None:
    api_key_hash = "revoked-api-key-hash"
    agent_id = "test-agent"

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM agent_api_credentials")
            cursor.execute("DELETE FROM registered_agents")

            cursor.execute(
                """
                INSERT INTO registered_agents (
                    agent_id,
                    display_name,
                    status
                )
                VALUES (%s, %s, %s)
                """,
                (agent_id, "Test Agent", "active"),
            )

            cursor.execute(
                """
                INSERT INTO agent_api_credentials (
                    credential_id,
                    agent_id,
                    api_key_hash,
                    api_key_prefix,
                    status
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    "revoked-test-credential",
                    agent_id,
                    api_key_hash,
                    "test",
                    "revoked",
                ),
            )

            conn.commit()

    resolved_agent_id = get_active_agent_id_for_api_key_hash(api_key_hash)

    assert resolved_agent_id is None



def test_get_active_agent_id_for_api_key_hash_returns_none_for_disabled_agent() -> None:
    api_key_hash = "disabled-agent-api-key-hash"
    agent_id = "disabled-test-agent"

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM agent_api_credentials")
            cursor.execute("DELETE FROM registered_agents")

            cursor.execute(
                """
                INSERT INTO registered_agents (
                    agent_id,
                    display_name,
                    status
                )
                VALUES (%s, %s, %s)
                """,
                (agent_id, "Disabled Test Agent", "disabled"),
            )

            cursor.execute(
                """
                INSERT INTO agent_api_credentials (
                    credential_id,
                    agent_id,
                    api_key_hash,
                    api_key_prefix,
                    status
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    "disabled-agent-test-credential",
                    agent_id,
                    api_key_hash,
                    "test",
                    "active",
                ),
            )

            conn.commit()

    resolved_agent_id = get_active_agent_id_for_api_key_hash(api_key_hash)

    assert resolved_agent_id is None