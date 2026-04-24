from app.schemas.pdp_audit import PDPAuditEvent
from app.db.connection import get_db_connection
from app.audit.pdp_audit_service import insert_pdp_audit_event
from datetime import datetime, timezone



def test_pdp_audit_repository(use_test_db) -> None:
    
    audit_event = PDPAuditEvent(
        request_id="test_request_id",
        agent_id="test_agent_id",
        server_name="test_server_name",
        tool_name="test_tool_name",
        invocation_action="test_invocation_action",
        resource="test_resource",
        decision="deny",
        rationale=["test_rationale"],
        policy_version="test_policy_version",
        policy_sha256="test_policy_sha256",
        created_at="2024-06-01T12:00:00Z"
    )

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE pdp_audit RESTART IDENTITY;")
    
    insert_pdp_audit_event(audit_event)


    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT request_id, agent_id, server_name, tool_name, 
                invocation_action, resource, decision, rationale, 
                policy_version, policy_sha256, created_at FROM pdp_audit;
                """)
            result = cursor.fetchone()

            assert result is not None

            (
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
                created_at,
            ) = result
    
    assert request_id == "test_request_id"
    assert agent_id == "test_agent_id"
    assert server_name == "test_server_name"
    assert tool_name == "test_tool_name"
    assert invocation_action == "test_invocation_action"    
    assert resource == "test_resource"
    assert decision == "deny"
    assert rationale == ["test_rationale"]
    assert policy_version == "test_policy_version"
    assert policy_sha256 == "test_policy_sha256"
    assert created_at == datetime(2024, 6, 1, 12, 0, tzinfo=timezone.utc)


        

