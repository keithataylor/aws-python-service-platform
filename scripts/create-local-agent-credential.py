from app.auth.credential_hashing import hash_agent_api_key
from app.core.config import get_settings
from app.db.connection import get_db_connection

LOCAL_AGENT_ID = "local-dev-agent"
LOCAL_AGENT_DISPLAY_NAME = "Local Dev Agent"
LOCAL_RAW_API_KEY = "local-dev-agent-key"
LOCAL_CREDENTIAL_ID = "local-dev-agent-credential"
LOCAL_API_KEY_PREFIX = "local"


def create_local_agent_credential() -> None:
    settings = get_settings()

    api_key_hash = hash_agent_api_key(
        api_key=LOCAL_RAW_API_KEY,
        secret=settings.agent_credential_hash_secret,
    )

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO registered_agents (
                    agent_id,
                    display_name,
                    status
                )
                VALUES (%s, %s, %s)
                ON CONFLICT (agent_id)
                DO UPDATE SET
                    display_name = EXCLUDED.display_name,
                    status = EXCLUDED.status,
                    updated_at = NOW()
                """,
                (
                    LOCAL_AGENT_ID,
                    LOCAL_AGENT_DISPLAY_NAME,
                    "active",
                ),
            )

            cursor.execute(
                """
                INSERT INTO agent_api_credentials (
                    credential_id,
                    agent_id,
                    api_key_hash,
                    api_key_prefix,
                    status,
                    revoked_at
                )
                VALUES (%s, %s, %s, %s, %s, NULL)
                ON CONFLICT (credential_id)
                DO UPDATE SET
                    agent_id = EXCLUDED.agent_id,
                    api_key_hash = EXCLUDED.api_key_hash,
                    api_key_prefix = EXCLUDED.api_key_prefix,
                    status = EXCLUDED.status,
                    revoked_at = NULL
                """,
                (
                    LOCAL_CREDENTIAL_ID,
                    LOCAL_AGENT_ID,
                    api_key_hash,
                    LOCAL_API_KEY_PREFIX,
                    "active",
                ),
            )

            conn.commit()

    print("Local registered agent credential is ready.")
    print(f"agent_id: {LOCAL_AGENT_ID}")
    print(f"X-Agent-Api-Key: {LOCAL_RAW_API_KEY}")


if __name__ == "__main__":
    create_local_agent_credential()