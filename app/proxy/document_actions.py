"""
Post-allow document tool actions executed after PDP authorization.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.proxy.document_repository import (
    get_document_by_id,
    get_document_metadata,
    search_documents,
)


class DocsToolArguments(BaseModel):
    document_id: str = Field(min_length=1, max_length=100)
    

class ListDocumentsArguments(BaseModel):
    query: str = Field(default="", max_length=200)


class DocumentDecisionContext(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_visibility: str = Field(min_length=1, max_length=50)

    
def build_docs_tool_context(tool_arguments: dict[str, Any]) -> dict[str, Any]:
    metadata = get_document_metadata(tool_arguments["document_id"])

    return DocumentDecisionContext(
        document_visibility=metadata["document_visibility"],
    ).model_dump()
    #return metadata


def process_documents_retrieval_request(arguments: dict) -> dict[str, Any]:
    validated_args = DocsToolArguments.model_validate(arguments)
    document_id = validated_args.document_id
    results = get_document_by_id(document_id)
    return {
        "results": results,
        "total_matches": 1 if results else 0,
        "returned_count": 1 if results else 0
    }

    
def process_list_documents_request(arguments: dict) -> dict[str, Any]:
    validated_args = ListDocumentsArguments.model_validate(arguments)
    query = validated_args.query.strip()

    results = search_documents(query)
    return {
        "results": results,
        "total_matches": len(results),
        "returned_count": len(results)
    }