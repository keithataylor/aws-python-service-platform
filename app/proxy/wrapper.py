"""
Proxy orchestration for MCP tool invocations and PDP enforcement.
"""

from datetime import datetime, timezone
from typing import Any

from app.audit.pdp_audit_service import record_pdp_audit_event
from app.core.logging import app_log_event
from app.policy.evaluator import pdp_evaluate_agent_action
from app.policy.models import LoadedPolicy
from app.proxy.config import MCP_SERVER_NAME
from app.proxy.identity import ResolvedAgentIdentity
from app.proxy.normalizer import normalize_tool_invocation
from app.proxy.tool_registry import get_tool_spec
from app.schemas.pdp_audit import PDPAuditEvent


def proxy_process_tool_invocation(
        agent_identity: ResolvedAgentIdentity, tool_name: str, 
        tool_arguments: dict, loaded_policy: LoadedPolicy
        ) -> dict[str, Any]:
    """
    Process and route incoming MCP tool calls to the appropriate handlers 
    based on the tool name and arguments.
    Args:
        agent_identity (ResolvedAgentIdentity): The identity of the agent making the request.
        tool_name (str): The name of the tool being called.
        tool_arguments (dict): A dictionary of arguments passed to the tool.
        loaded_policy (LoadedPolicy): The loaded policy to be applied for evaluating the action.
    Returns:
        dict[str, Any]: A dictionary containing the tool name, arguments, 
        metadata, and status of the processed call.
    """ 

    # For unauthenticated identities, we skip PDP evaluation and directly deny access.
    if agent_identity.auth_method == "none":
        app_log_event(
            event_name="agent_identity_unknown",
            request_id="unknown",
            tool_name=tool_name,
        )
        return {
            "tool_name": tool_name,
            "status": "denied",
            "decision": "deny",
            "rationale": ["UNAUTHENTICATED_AGENT_IDENTITY"],
        }
    

    spec = get_tool_spec(tool_name)
    
    derived_context = spec.pre_pdp(tool_arguments) if spec.pre_pdp else {}   

    # Tool-specific pre-PDP handlers return the validated decision_context for this invocation.
    decision_context = derived_context


    normalize_request = normalize_tool_invocation(
        agent_id=agent_identity.agent_id,
        server_name=MCP_SERVER_NAME,
        tool_name=spec.tool_name,
        action=spec.invocation_action,
        resource=spec.resource, 
        decision_context=decision_context
    )

    evaluation = pdp_evaluate_agent_action(normalize_request, loaded_policy.document)

    record_pdp_audit_event(
        event=PDPAuditEvent(
            request_id=normalize_request.request_id,
            agent_id=normalize_request.agent_id,
            server_name=normalize_request.server_name,
            tool_name=normalize_request.tool_name,
            invocation_action=normalize_request.action,
            resource=normalize_request.resource,
            decision=evaluation.decision,
            rationale=evaluation.rationale,
            policy_version=loaded_policy.document.version,
            policy_sha256=loaded_policy.policy_sha256,
            created_at=datetime.now(timezone.utc)
        )
    )
    

    if evaluation.decision == "deny":
        app_log_event(
            event_name="tool_invocation_blocked",
            request_id=normalize_request.request_id,
            tool_name=normalize_request.tool_name,
            decision=evaluation.decision,
        )
        return {
            "tool_name": normalize_request.tool_name,
            "arguments": tool_arguments,
            "meta": spec, 
            "status": "denied",
            "decision": evaluation.decision,
            "rationale": evaluation.rationale
        }

    if spec.post_allow is None:
        raise ValueError(f"Tool spec for '{tool_name}' is missing post_allow")
    

    try:
        result = spec.post_allow(tool_arguments)
    except Exception:
        app_log_event(
            event_name="tool_invocation_failed",
            request_id=normalize_request.request_id,
            tool_name=normalize_request.tool_name,
        )
        raise
    
    app_log_event(
        event_name="tool_invocation_executed",
        request_id=normalize_request.request_id,
        tool_name=normalize_request.tool_name
    )
        
    return result

