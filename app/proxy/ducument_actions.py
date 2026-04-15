from typing import Any

from app.proxy.document_store import get_document_by_id, get_document_metadata, search_documents


def build_docs_tool_context(tool_arguments: dict[str, Any]) -> dict[str, Any]:
    metadata = get_document_metadata(tool_arguments["document_id"])
    return metadata


def process_documents_retrieval_request(arguments: dict) -> dict[str, Any]:
    results = get_document_by_id(arguments["document_id"])
    return {
        "results": results,
        "total_matches": 1 if results else 0,
        "returned_count": 1 if results else 0
    }


def process_list_documents_request(arguments: dict) -> dict[str, Any]:
    results = search_documents(arguments["query"])
    return {
        "results": results,
        "total_matches": len(results),
        "returned_count": len(results)
    }