from app.db.connection import get_db_connection


def get_active_agent_id_for_api_key_hash(api_key_hash: str) -> str | None:

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT a.agent_id
                FROM agent_api_credentials c
                JOIN registered_agents a
                    ON a.agent_id = c.agent_id
                WHERE c.api_key_hash = %s
                  AND c.status = 'active'
                  AND a.status = 'active';
                """,
                (api_key_hash,),
            )
            result = cursor.fetchone()
   
    if result is None:
        return None

    return result[0]