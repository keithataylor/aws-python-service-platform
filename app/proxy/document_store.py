
from typing import Any


DICT_LIST = [
    {"document_id": "doc1", "title": "Document 1", "summary": "Summary of document 1", "metadata": {"document_visibility": "public"}},
    {"document_id": "doc2", "title": "Document 2", "summary": "Summary of document 2", "metadata": {"document_visibility": "private"}},
    {"document_id": "doc3", "title": "Document 3", "summary": "Summary of document 3", "metadata": {"document_visibility": "public"}},
    {"document_id": "doc4", "title": "Document 4", "summary": "Summary of document 4", "metadata": {"document_visibility": "private"}},
]


def get_document_metadata(document_id: str) -> dict:
  # Placeholder for document metadata retrieval logic
  # In a real implementation, this would involve looking up the document's metadata based on its ID
  for doc in DICT_LIST:
    if doc["document_id"] == document_id:
      return doc["metadata"]

  raise ValueError(f"Document with ID {document_id} not found")


def get_document_by_id(document_id: str) -> dict[str, Any]:

  for doc in DICT_LIST:   
    if doc["document_id"] == document_id: 
      return doc
      
  raise ValueError(f"Document with ID {document_id} not found")


def search_documents(query: str) -> list[dict[str, Any]]:
  # Placeholder for document search logic
  # In a real implementation, this would involve searching the document store based on the query

  # If query is empty, return all documents that are publicly visible only
  results = []

  if not query:
    results = [doc for doc in DICT_LIST if doc["metadata"]["document_visibility"] == "public"]
    return results

  for doc in DICT_LIST:
    if query.lower() in doc["title"].lower() or query.lower() in doc["summary"].lower():
      results.append(doc)

  if results:
    return results
  else:
    return [{"error": f"No documents found matching the query: {query}"}]
  
