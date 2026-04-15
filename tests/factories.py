from app.policy.models import (
    PolicyDocument, PolicyRule, PolicyConstraint, 
    PolicyRuleMeta, PolicyThen, PolicyWhen
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
                    action="tool.read",
                    resource="public.docs",
                    constraints=[
                        PolicyConstraint(
                            source="parameters",
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
