from app.policy.models import (
    PolicyConstraint, PolicyDocument, PolicyObligation, 
    PolicyRule, PolicyRuleMeta, PolicyThen, PolicyWhen
)
from app.schemas.invocation import InvocationDecisionRequest
from app.policy.evaluator import pdp_evaluate_agent_action
from tests.factories import build_test_policy

def test_evaluate_agent_action_service_returns_allow_for_matching_constraint() -> None:
    
    response = pdp_evaluate_agent_action(
        InvocationDecisionRequest(
            request_id="request-123",
            agent_id="agent-123",
            server_name="docs_mcp",
            tool_name="docs_tool",
            action="document.read",
            resource="document",
            parameters={"document_id": "doc3"},
            context={
                "document_visibility": "public",
                "user_role": "reader"
            },
        ),
        build_test_policy()
    )
    assert response.decision == "allow"
    assert response.rationale == ["POLICY_ALLOW_PUBLIC_DOCS_READ"]


def test_evaluate_agent_action_service_returns_deny_for_non_matching_constraint() -> None:
  
    response = pdp_evaluate_agent_action(
        InvocationDecisionRequest(
            request_id="request-123",
            agent_id="agent-123",
            server_name="docs_mcp",
            tool_name="docs_tool",
            action="document.read",
            resource="document",
            parameters={"document_id": "doc3"},
            context={
                "document_visibility": "unknown",
                "user_role": "reader"},
        ),
        build_test_policy()
    )
    assert response.decision == "deny"
    assert response.rationale == ["DEFAULT_DENY"]


def test_evaluate_server_name_participates_in_policy_evaluation() -> None:
    response = pdp_evaluate_agent_action(
        InvocationDecisionRequest(
            request_id="request-123",
            agent_id="agent-123",
            server_name="bad_server_name",
            tool_name="docs_tool",
            action="document.read",
            resource="document",
            parameters={"document_id": "doc3"},
            context={
                "document_visibility": "public",
                "user_role": "reader"
            },
        ),
        build_test_policy()
    )
    assert response.decision == "deny"
    assert response.rationale == ["DEFAULT_DENY"]
    assert response.obligations == []


def test_evaluate_returns_first_matching_policy() -> None:
    response = pdp_evaluate_agent_action(
        InvocationDecisionRequest(
            request_id="request-123",
            agent_id="agent-123",
            server_name="docs_mcp",
            tool_name="docs_tool",
            action="document.read",
            resource="document",
            parameters={"document_id": "doc3"},
            context={
                "document_visibility": "public",
                "user_role": "reader"
            },
        ),
        PolicyDocument(
            version="1.0",
            default_decision="deny",
            rules=[
                # This rule matches and allows
                PolicyRule(
                    rule_id="Rule 1",
                    when=PolicyWhen(
                        tool_name="docs_tool",
                        server_name="docs_mcp",
                        action="document.read",
                        resource="document",
                        constraints=[
                            PolicyConstraint(
                                source="context",
                                field="document_visibility",
                                operator="equals",
                                value="public",
                            )
                        ]
                    ),
                    then=PolicyThen(
                        effect="allow",
                        rationale="POLICY_ALLOW_PUBLIC_DOCS_READ",
                        obligations=[],
                    ),
                    meta=PolicyRuleMeta(description="Allow reading public documents with docs_tool"),
                ),
                # This rule also matches but should not be evaluated because the first rule already matched
                PolicyRule(
                    rule_id="Rule 2",
                    when=PolicyWhen(
                        tool_name="docs_tool",
                        server_name="docs_mcp",
                        action="document.read",
                        resource="document",
                        constraints=[
                            PolicyConstraint(
                                source="context",
                                field="document_visibility",
                                operator="equals",
                                value="public",
                            )
                        ]
                    ),
                    then=PolicyThen(
                        effect="deny",
                        rationale="POLICY_DENY_ALL_DOCS_READ",
                        obligations=[],
                    ),
                    meta=PolicyRuleMeta(description="Deny reading all documents with docs_tool"),
                )
            ],
        )
    )
    assert response.decision == "allow"
    assert response.rationale == ["POLICY_ALLOW_PUBLIC_DOCS_READ"]


def test_evaluate_invokes_context_parameters() -> None:
    invocation_request = InvocationDecisionRequest(
        request_id="request-123",
        agent_id="agent-123",
        server_name="docs_mcp",
        tool_name="docs_tool",
        action="document.read",
        resource="document",
        parameters={},
        context={"user_role": "reader"},
    )
    policy_document =PolicyDocument(
            version="1.0",
            default_decision="deny",
            rules=[
                PolicyRule(
                    rule_id="Rule 1",
                    when=PolicyWhen(
                        tool_name="docs_tool",
                        server_name="docs_mcp",
                        action="document.read",
                        resource="document",
                        constraints=[
                            PolicyConstraint(
                                source="context",
                                field="user_role",
                                operator="equals",
                                value="reader",
                            )
                        ]
                    ),
                    then=PolicyThen(
                        effect="allow",
                        rationale="POLICY_ALLOW_READERS_TO_READ_PUBLIC_DOCS",
                        obligations=[
                            PolicyObligation(
                                obligation_type="audit_log",
                                parameters={"user_role": "reader"},
                            )
                        ],
                    ),
                    meta=PolicyRuleMeta(description="Allow users with reader role to read public documents"),
                )
            ],
        )
    response = pdp_evaluate_agent_action( invocation_request, policy_document)
    
    assert response.decision == "allow"
    assert response.rationale == ["POLICY_ALLOW_READERS_TO_READ_PUBLIC_DOCS"]

    invocation_request = InvocationDecisionRequest(
        request_id="request-123",
        agent_id="agent-123",
        server_name="docs_mcp",
        tool_name="docs_tool",
        action="document.read",
        resource="document",
        parameters={},
        context={"user_role": "writer"},
    )

    response = pdp_evaluate_agent_action( invocation_request, policy_document)

    assert response.decision == "deny"
    assert response.rationale == ["DEFAULT_DENY"]
