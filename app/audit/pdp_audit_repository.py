
from app.db.connection import get_db_connection
from app.schemas.pdp_audit import PDPAuditEvent


def insert_pdp_audit_event(event: PDPAuditEvent) -> None:
    """
    Insert a PDP audit event into the database.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO pdp_audit (
                    request_id,
                    agent_id,
                    server_name,
                    tool_name,
                    invocation_action,
                    resource,
                    decision,
                    rationale,
                    policy_version,
                    policy_sha256,
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    event.request_id,
                    event.agent_id,
                    event.server_name,
                    event.tool_name,
                    event.invocation_action,
                    event.resource,
                    event.decision,
                    event.rationale,
                    event.policy_version,
                    event.policy_sha256,
                    event.created_at,
                ),
            )
