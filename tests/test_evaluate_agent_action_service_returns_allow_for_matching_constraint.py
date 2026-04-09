
from app.schemas.invocation import InvocationDecisionRequest
from app.policy.evaluator import evaluate_agent_action
from tests.factories import build_test_policy   


def test_evaluate_agent_action_service_returns_allow_for_matching_constraint() -> None:
    response = evaluate_agent_action(
        InvocationDecisionRequest(
            request_id="request-123",
            agent_id="agent-123",
            server_name="docs_mcp",
            tool_name="docs_tool",
            action="tool.read",
            resource="public.docs",
            parameters={"document_visibility": "public"},
            context={},
        ), 
        build_test_policy()
    )
    assert response.decision == "allow"
    assert response.rationale == ["POLICY_ALLOW_PUBLIC_DOCS_READ"]

  