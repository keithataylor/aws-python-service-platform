from typing import Any

from app.proxy.ducument_actions import build_docs_tool_context, process_list_documents_request
from app.proxy.ducument_actions import process_documents_retrieval_request


TOOL_SPECS = {
    "list_documents": {
        "action": "document.search",
        "resource": "document",
        "post_allow": process_list_documents_request,
    },
    "docs_tool": {
        "action": "document.read",
        "resource": "document",
        "pre_pdp": build_docs_tool_context,
        "post_allow": process_documents_retrieval_request,
    },
}

def get_tool_spec(tool_name: str) -> dict[str, Any]:
    return TOOL_SPECS[tool_name]