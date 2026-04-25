from app.policy.models import (
    PolicyConstraint,
    PolicyDocument,
    PolicyRule,
    PolicyRuleMeta,
    PolicyThen,
    PolicyWhen,
)


def build_test_policy() -> PolicyDocument:
    return PolicyDocument(
        version="1.0",
        default_decision="deny",
        rules=[
            PolicyRule(
                rule_id="allow_public_docs_read",
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
            )
        ],
    )
