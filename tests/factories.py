from app.policy.models import AgentPolicyDocument, AgentPolicyRule, PolicyConstraint


def build_test_policy() -> AgentPolicyDocument:
    return AgentPolicyDocument(
        version="1.0",
        default_decision="deny",
        rules=[
            AgentPolicyRule(
                rule_id="allow_public_docs_read",
                effect="allow",
                tool_name="docs_tool",
                action="tool.read",
                resource="public.docs",
                rationale="POLICY_ALLOW_PUBLIC_DOCS_READ",
                constraints=[
                    PolicyConstraint(
                        parameter="document_visibility",
                        operator="equals",
                        value="public",
                    )
                ],
                obligations=[],
            )
        ],
    )
