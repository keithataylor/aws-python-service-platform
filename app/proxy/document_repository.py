"""
PostgreSQL-backed document access for proxy tool actions and policy context.
"""

from typing import Any

from app.db.connection import get_db_connection


def get_document_metadata(document_id: str) -> dict:

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            result = cursor.execute(
                "SELECT document_visibility FROM documents WHERE document_id = %s",
                (document_id,)
            ).fetchone()

    if result:
        return {"document_visibility": result[0]}

    raise ValueError(f"Document with ID {document_id} not found")



def get_document_by_id(document_id: str) -> dict[str, Any]:

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            result = cursor.execute(
                "SELECT document_id, title, body FROM documents WHERE document_id = %s",
                (document_id,)
            ).fetchone()

    if result:
        return {
            "document_id": result[0], 
            "title": result[1], 
            "body": result[2]
            }
      
    raise ValueError(f"Document with ID {document_id} not found")


def search_documents(query: str) -> list[dict[str, Any]]:
    
    results = []

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            if not query:
                results = cursor.execute(
                    """
                    SELECT document_id, title, summary FROM documents 
                        WHERE document_visibility = 'public'
                    """
                ).fetchall()
            else:
                results = cursor.execute(
                    """
                    SELECT document_id, title, summary FROM documents 
                        WHERE document_visibility = 'public' 
                        AND (title ILIKE %s OR summary ILIKE %s)
                    """,
                    (f"%{query}%", f"%{query}%")
                ).fetchall()
            
            results_list = [
                {"document_id": row[0], "title": row[1], "summary": row[2]}
                for row in results
            ]
            return results_list

