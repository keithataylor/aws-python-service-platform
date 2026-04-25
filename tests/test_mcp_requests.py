from dataclasses import replace
from typing import Any

import pytest

from app.db.connection import get_db_connection
from app.proxy.normalizer import normalize_tool_invocation
from app.proxy.tool_registry import TOOL_SPECS
from app.schemas.invocation import InvocationDecisionRequest

pytestmark = pytest.mark.integration

init_request = {
    "url":"/mcp",
    "json": {
       "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "0.1.0"},
        },
    },
    "headers":{"Accept": "application/json, text/event-stream"},
}

test_url = init_request["url"]
test_json = init_request["json"]
test_headers = init_request["headers"]
    

def test_normalize_tool_invocation() -> None:

    invocation_request = normalize_tool_invocation(
        agent_id="agent_123",
        server_name="test_server",
        tool_name="docs_tool",
        action="tools/call",
        arguments={"arg1": "value1", "arg2": 2},
        resource="test_resource",
        context={"key": "value"},
    )

    assert isinstance(invocation_request, InvocationDecisionRequest)
    assert invocation_request.agent_id == "agent_123"
    assert invocation_request.server_name == "test_server"
    assert invocation_request.resource == "test_resource"
    assert invocation_request.tool_name == "docs_tool"
    assert invocation_request.action == "tools/call"
    assert invocation_request.parameters == {"arg1": "value1", "arg2": 2}
    assert invocation_request.context == {"key": "value"}
    

def test_mcp_initialization(client) -> None:
   
    response = client.post(test_url, json=test_json, headers=test_headers)

    assert response.status_code == 200
    assert '"jsonrpc":"2.0"' in response.text
    assert '"id":1' in response.text
    assert '"result":{"protocolVersion":"2025-06-18"' in response.text


def test_mcp_returns_tools_list(client) -> None:

    init_response = client.post(test_url, json=test_json, headers=test_headers)

    session_id = init_response.headers.get("Mcp-Session-Id")

    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        },
        headers={
           "Accept": "application/json, text/event-stream",
           "Content-Type": "application/json",
           "Mcp-Session-Id": session_id
        },
    )

    assert response.status_code == 200
    json_out = response.json()
    assert json_out["jsonrpc"] == "2.0" 
    assert json_out["id"] == 1
    assert "tools" in json_out["result"]
    tool_list = [tool["name"] for tool in json_out["result"]["tools"]]
    assert "docs_tool" in tool_list
    assert "list_documents" in tool_list
          

def test_list_documents_with_query_param_returns_document(client) -> None:
    init_response = client.post(test_url, json=test_json, headers=test_headers)

    session_id = init_response.headers.get("Mcp-Session-Id")

    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "list_documents", 
                "arguments": {"query": "Document 1"}
            }
        },
        headers={
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "Mcp-Session-Id": session_id
        },
    )

    assert response.status_code == 200
    json_out = response.json()
    my_list = json_out["result"]["structuredContent"]["results"]
    assert isinstance(my_list, list)

    for doc in my_list:
        assert "document_id" in doc
        assert isinstance(doc["document_id"], str)
        assert doc["document_id"]

    total_match = json_out["result"]["structuredContent"]["total_matches"]
    assert isinstance(total_match, int)
    returned_count = json_out["result"]["structuredContent"]["returned_count"]
    assert isinstance(returned_count, int) and returned_count == 1


def test_list_documents_with_empty_query_returns_all_public_documents(client) -> None:
  
    init_response = client.post(test_url, json=test_json, headers=test_headers)

    session_id = init_response.headers.get("Mcp-Session-Id")

    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "list_documents", 
                "arguments": {"query": ""}
            }
        },
        headers={
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "Mcp-Session-Id": session_id
        },
    )

    assert response.status_code == 200

    json_out = response.json()
    my_list = json_out["result"]["structuredContent"]["results"]
    assert isinstance(my_list, list)

    for doc in my_list:
        assert "document_id" in doc
        assert isinstance(doc["document_id"], str)
        assert doc["document_id"]

    total_match = json_out["result"]["structuredContent"]["total_matches"]
    assert isinstance(total_match, int)
    returned_count = json_out["result"]["structuredContent"]["returned_count"]
    assert isinstance(returned_count, int) and returned_count >= 1
   

def test_docs_tool_with_document_id_returns_correct_document(client) -> None:
    
    init_response = client.post(test_url, json=test_json, headers=test_headers)

    session_id = init_response.headers.get("Mcp-Session-Id")

    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "docs_tool", 
                "arguments": {"document_id": "test_doc_public_1"}
            }
        },
        headers={
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "Mcp-Session-Id": session_id
        },
    )

    assert response.status_code == 200
    json_out = response.json()["result"]["structuredContent"]
    assert "body" in json_out["results"]
    assert "title" in json_out["results"]
    assert "document_id" in json_out["results"]
    assert isinstance(json_out["total_matches"], int)
    assert isinstance(json_out["returned_count"], int)
   


def test_mcp_tool_call_and_audit_record(client) -> None:
    init_response = client.post(test_url, json=test_json, headers=test_headers)

    session_id = init_response.headers.get("Mcp-Session-Id")

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE pdp_audit RESTART IDENTITY;")

    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "docs_tool", 
                "arguments": {"document_id": "test_doc_public_1"}
            }
        },
        headers={
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "Mcp-Session-Id": session_id
        },
    )

    assert response.status_code == 200
  
    # Now query the test_db for the audit record
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT tool_name, decision, policy_version, policy_sha256
                FROM pdp_audit
                ORDER BY id DESC
                LIMIT 1
                """
            )
            audit_record = cursor.fetchone()

    tool_name, decision, policy_version, policy_sha256 = audit_record

    assert audit_record is not None
    assert tool_name == "docs_tool"
    assert decision == "allow"
    assert policy_version == "1.0"
    assert policy_sha256 is not None and len(policy_sha256) == 64  # Assuming it's a SHA-256 hash
   
    

def test_mcp_tool_call_with_decision_denied(client, override_loaded_policy) -> None:
    
    init_response = client.post(test_url, json=test_json, headers=test_headers)

    session_id = init_response.headers.get("Mcp-Session-Id")

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE pdp_audit RESTART IDENTITY;")

    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "docs_tool", 
                "arguments": {"document_id": "test_doc_private_1"}
            }
        },
        headers={
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "Mcp-Session-Id": session_id
        },
    )

    assert response.status_code == 200

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT tool_name, decision, policy_version, policy_sha256
                FROM pdp_audit
                ORDER BY id DESC
                LIMIT 1
                """
            )
            audit_record = cursor.fetchone()

    tool_name, decision, policy_version, policy_sha256 = audit_record

    assert audit_record is not None
    assert tool_name == "docs_tool"
    assert decision == "deny"
    assert policy_version == "1.0"
    assert policy_sha256 is not None and len(policy_sha256) == 64  # Assuming it's a SHA-256 hash


#overrides the tool spec or post_allow function to raise an exception
# performs the MCP request
# asserts the returned error shape is correct
def test_mcp_tool_call_logs_failure_when_post_allow_raises(client) -> None:

    init_response = client.post(test_url, json=test_json, headers=test_headers)

    session_id = init_response.headers.get("Mcp-Session-Id")

    original_spec = TOOL_SPECS["docs_tool"]
   
    def post_allow_exception(arguments: dict[str, Any]) -> dict[str, Any]:
        raise Exception("Simulated post_allow failure")

    try:
        TOOL_SPECS["docs_tool"] = replace(original_spec, post_allow=post_allow_exception,)
        
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 99,
                "method": "tools/call",
                "params": {
                    "name": "docs_tool",
                    "arguments": {"document_id": "test_doc_public_1"},
                },
            },
            headers={
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json",
                "Mcp-Session-Id": session_id, 
            },
        )
    finally:
        TOOL_SPECS["docs_tool"] = original_spec
        
   
    assert response.status_code == 200
    json_out = response.json()
    assert json_out["result"]["isError"] is True
    assert "Simulated post_allow failure" in json_out["result"]["content"][0]["text"]
    
