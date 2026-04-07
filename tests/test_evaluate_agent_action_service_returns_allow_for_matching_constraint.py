
from app.schemas.agent_action import AgentActionRequest
from app.policy.evaluator import evaluate_agent_action
from tests.factories import build_test_policy   


def test_evaluate_agent_action_service_returns_allow_for_matching_constraint() -> None:
    response = evaluate_agent_action(
        AgentActionRequest(
            agent_id="agent-123",
            tool_name="docs_tool",
            action="tool.read",
            resource="public.docs",
            parameters={"document_visibility": "public"},
        ), 
        build_test_policy()
    )
    assert response.decision == "allow"
    assert response.rationale == ["POLICY_ALLOW_PUBLIC_DOCS_READ"]