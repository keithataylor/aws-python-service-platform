"""
Normalization helpers for building PDP invocation requests from proxy inputs.
"""

from typing import Any
from uuid import uuid4

from app.schemas.invocation import InvocationDecisionRequest


def normalize_tool_invocation(
    *,
    agent_id: str,
    server_name: str,
    tool_name: str,
    action: str,
    resource: str = "unknown",
    decision_context: dict[str, Any] | None = None,
) -> InvocationDecisionRequest:
    """
    Normalizes a tool invocation into a standardized format for PDP evaluation.
    Args:
        agent_id (str): The ID of the agent invoking the tool.
        server_name (str): The name of the server handling the invocation.
        tool_name (str): The name of the tool being invoked.
        action (str): The action being performed with the tool.
        resource (str, optional): The resource being accessed or modified. 
        Defaults to "unknown".
        decision_context (dict[str, Any], optional): Additional context for the PDP evaluation. 
        Defaults to None.
    Returns:
        InvocationDecisionRequest: The normalized tool invocation request.
    """
    return InvocationDecisionRequest(
        request_id=str(uuid4()),
        agent_id=agent_id,
        server_name=server_name,
        tool_name=tool_name,
        action=action,
        resource=resource,
        decision_context=decision_context or {},
    )
