from typing import Any

from app.proxy.ducument_actions import build_docs_tool_context, process_list_documents_request
from app.proxy.ducument_actions import process_documents_retrieval_request
from app.proxy.tool_spec import ToolSpec


# TOOL_SPECS = {
#     "list_documents": {
#         "action": "document.search",
#         "resource": "document",
#         "post_allow": process_list_documents_request,
#     },
#     "docs_tool": {
#         "action": "document.read",
#         "resource": "document",
#         "pre_pdp": build_docs_tool_context,
#         "post_allow": process_documents_retrieval_request,
#     },
# }

# def get_tool_spec(tool_name: str) -> dict[str, Any]:
#     return TOOL_SPECS[tool_name]

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
    try:
        return TOOL_SPECS[tool_name]
    except KeyError as exc:
        raise ValueError(f"Tool spec not found for tool: {tool_name}") from exc