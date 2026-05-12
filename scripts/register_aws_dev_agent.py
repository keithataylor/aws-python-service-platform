import os

from app.auth.credential_hashing import hash_agent_api_key
from app.core.config import get_settings
from app.db.connection import get_db_connection

DEFAULT_AGENT_ID = "aws-dev-agent"
DEFAULT_AGENT_DISPLAY_NAME = "AWS Dev Agent"
DEFAULT_CREDENTIAL_ID = "aws-dev-agent-credential"


def register_aws_dev_agent() -> None:
    settings = get_settings()

    raw_api_key = os.getenv("AWS_DEV_AGENT_API_KEY")
    if not raw_api_key:
        raw_api_key = f"aws-dev-agent-{os.urandom(24).hex()}"

    agent_id = os.getenv("AWS_DEV_AGENT_ID", DEFAULT_AGENT_ID)
    agent_display_name = os.getenv(
        "AWS_DEV_AGENT_DISPLAY_NAME",
        DEFAULT_AGENT_DISPLAY_NAME,
    )
    credential_id = os.getenv("AWS_DEV_CREDENTIAL_ID", DEFAULT_CREDENTIAL_ID)
    api_key_prefix = raw_api_key[:8]

    api_key_hash = hash_agent_api_key(
        api_key=raw_api_key,
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
                    agent_id,
                    agent_display_name,
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
                    credential_id,
                    agent_id,
                    api_key_hash,
                    api_key_prefix,
                    "active",
                ),
            )

            conn.commit()

    print("AWS registered agent credential is ready.")
    print(f"agent_id: {agent_id}")
    print(f"credential_id: {credential_id}")
    print(f"api_key_prefix: {api_key_prefix}")
    print("Store this raw dev API key locally for MCP smoke tests:")
    print(raw_api_key)


if __name__ == "__main__":
    register_aws_dev_agent()