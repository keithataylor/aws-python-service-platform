from app.proxy.normalizer import normalize_mcp_request
from app.schemas.invocation import InvocationDecisionRequest


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
    

def test_normalize_mcp_request():

    invocation_request = normalize_mcp_request(
        #mcp_request,
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
    

def test_mcp_initialization(client):
   
    response = client.post(test_url, json=test_json, headers=test_headers)

    assert response.status_code == 200
    assert '"jsonrpc":"2.0"' in response.text
    assert '"id":1' in response.text
    assert '"result":{"protocolVersion":"2025-06-18"' in response.text


def test_mcp_returns_tools_list(client):

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
        headers={"Accept": "application/json, text/event-stream",
                 "Content-Type": "application/json",
                 "Mcp-Session-Id": session_id},
    )

    assert response.status_code == 200
    assert '"jsonrpc":"2.0"' in response.text
    assert '"id":1' in response.text
    assert '"result":{"tools"' in response.text
    assert '"list_documents"' in response.text
    assert '"docs_tool"' in response.text
          

def test_mcp_tools_call(client):
    
  init_response = client.post(test_url, json=test_json, headers=test_headers)

  session_id = init_response.headers.get("Mcp-Session-Id")

  response = client.post(
      "/mcp",
      json={
          "jsonrpc": "2.0",
          "id": 2,
          "method": "tools/call",
          "params": {
              "name": "docs_tool", 
              "arguments": {"document_id": "doc4"}
              }
      },
      headers={"Accept": "application/json, text/event-stream",
                  "Content-Type": "application/json",
                  "Mcp-Session-Id": session_id},
  )

  assert response.status_code == 200
  out = response.json()
  assert "jsonrpc" in out
  assert out["jsonrpc"] == "2.0"
  assert "id" in out
  assert out["id"] == 2


def test_mcp_tool_call_returns_allow_for_document_id(client) -> None:
       
  init_response = client.post(test_url, json=test_json, headers=test_headers)

  session_id = init_response.headers.get("Mcp-Session-Id")

  response = client.post(
      "/mcp",
      json={
          "jsonrpc": "2.0",
          "id": 2,
          "method": "tools/call",
          "params": {
              "name": "docs_tool", 
              "arguments": {"document_id": "doc3"}
              }
      },
      headers={"Accept": "application/json, text/event-stream",
                  "Content-Type": "application/json",
                  "Mcp-Session-Id": session_id},
  )

  assert response.status_code == 200
  out = response.json()
  print(out)
  assert out["result"]["structuredContent"]["results"]["document_id"] == "doc3"
 


def test_list_documents_tool_call_returns_documents_list(client) -> None:
  
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
      headers={"Accept": "application/json, text/event-stream",
                  "Content-Type": "application/json",
                  "Mcp-Session-Id": session_id},
  )

  assert response.status_code == 200

  out = response.json()
  my_list = out["result"]["structuredContent"]["results"]
  assert isinstance(my_list, list)
  
  for doc in my_list:
    assert "document_id" in doc
    assert isinstance(doc["document_id"], str)
    assert doc["document_id"]
  
  total_match = out["result"]["structuredContent"]["total_matches"]
  assert isinstance(total_match, int)
  
  returned_count = out["result"]["structuredContent"]["returned_count"]
  assert isinstance(returned_count, int) and returned_count >= 1
   