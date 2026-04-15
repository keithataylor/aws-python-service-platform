from app.proxy.ducument_actions import build_docs_tool_context, process_list_documents_request
from app.proxy.ducument_actions import process_documents_retrieval_request


TOOL_SPECS = {
    "list_documents": {
        "action": "document.search",
        "resource": "document",
        "pre_pdp": lambda args: {},
        "post_allow": process_list_documents_request,
    },
    "docs_tool": {
        "action": "document.read",
        "resource": "document",
        "pre_pdp": build_docs_tool_context,
        "post_allow": process_documents_retrieval_request,
    },
}