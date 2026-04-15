from typing import Any
from app.proxy.config import MCP_SERVER_NAME
from app.proxy.tool_registry import TOOL_SPECS
from app.proxy.normalizer import normalize_tool_invocation
from app.policy.evaluator import pdp_evaluate_agent_action


def proxy_process_tool_invocation(agent_id: str, tool_name: str, tool_arguments: dict, policy: dict) -> dict[str, Any]:
    """
    Process and route incoming MCP tool calls to the appropriate handlers based on the tool name and arguments.
    Args:
        agent_id (str): The ID of the agent making the request.
        tool_name (str): The name of the tool being called.
        tool_arguments (dict): A dictionary of arguments passed to the tool.
        context (dict): Additional context about the request, such as agent ID, server name, etc.
        policy (dict): The policy to be applied for evaluating the action.
    Returns:
        dict[str, Any]: A dictionary containing the tool name, arguments, metadata, and status of the processed call.
    """ 

    spec = TOOL_SPECS[tool_name]
    derived_context = spec["pre_pdp"](tool_arguments) if "pre_pdp" in spec else {}   

    normalize_request = normalize_tool_invocation(
        agent_id=agent_id,
        server_name=MCP_SERVER_NAME,
        tool_name=tool_name,
        action=spec["action"],
        arguments=tool_arguments,
        resource=spec["resource"], 
        context=derived_context
    )

    evaluation = pdp_evaluate_agent_action(normalize_request, policy)

    if evaluation.decision == "deny":
        return {
            "tool_name": tool_name,
            "arguments": tool_arguments,
            "meta": spec, 
            "status": "denied",
            "decision": evaluation.decision,
            "rationale": evaluation.rationale
        }

    return spec["post_allow"](tool_arguments)

