from typing import Any
from uuid import uuid4
from app.schemas.invocation import InvocationDecisionRequest


def normalize_mcp_request(
    *,
    agent_id: str,
    server_name: str,
    tool_name: str,
    action: str,
    arguments: dict[str, Any] | None = None, 
    resource: str = "unknown",
    context: dict[str, Any] | None = None,
) -> InvocationDecisionRequest:
    return InvocationDecisionRequest(
        request_id=str(uuid4()),
        agent_id=agent_id,
        server_name=server_name,
        tool_name=tool_name,
        action=action,
        resource=resource,
        parameters=arguments or {},
        context=context or {},
    )
