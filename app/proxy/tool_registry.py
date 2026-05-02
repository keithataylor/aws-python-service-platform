"""
Registry mapping MCP tool names to proxy tool specifications.
"""

from app.proxy.document_actions import (
    build_docs_tool_context,
    process_documents_retrieval_request,
    process_list_documents_request,
)
from app.proxy.tool_spec import ToolSpec

TOOL_SPECS: dict[str, ToolSpec] = {
    "list_documents": ToolSpec(
        tool_name="list_documents",
        invocation_action="document.search",
        resource="document",
        pre_pdp=None,
        post_allow=process_list_documents_request,
    ),
    "docs_tool": ToolSpec(
        tool_name="docs_tool",
        invocation_action="document.read",
        resource="document",
        pre_pdp=build_docs_tool_context,
        post_allow=process_documents_retrieval_request,
    ),
}


def get_tool_spec(tool_name: str) -> ToolSpec:
    """
    Return the registered ToolSpec for a tool name.
    """
    try:
        return TOOL_SPECS[tool_name]
    except KeyError as exc:
        raise ValueError(f"Tool spec not found for tool: {tool_name}") from exc