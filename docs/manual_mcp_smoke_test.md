# Manual MCP smoke test

This document describes a local manual smoke test for the MCP runtime path.

It verifies that a locally running service can authenticate a DB-backed registered-agent credential, route an MCP tool invocation through the proxy/PDP enforcement flow, and persist a PDP audit record.

This is not part of the automated pytest or CI workflow. It is intended as a developer verification path for exercising the runtime end to end with local PostgreSQL state.

## MCP session flow

The mounted `/mcp` endpoint uses the normal MCP session flow.

A manual tool call requires:

1. an initialize request to `/mcp`
2. the returned `Mcp-Session-Id` response header
3. a later `tools/call` request using that session ID
4. the `X-Agent-Api-Key` header for registered-agent identity resolution

A `tools/call` request requires an initialized MCP session. Send an `initialize` request first, then reuse the returned `Mcp-Session-Id` header when calling tools.

## Prerequisites

Run from the project root.

Start PostgreSQL:

```powershell
docker compose up -d
```

Apply migrations:

```powershell
.\scripts\run-migrations.ps1
```

Create or update the local development agent credential:

```powershell
python scripts/create-local-agent-credential.py
```

Expected output includes:

```text
X-Agent-Api-Key: local-dev-agent-key
```

Start the local application:

```powershell
python -m uvicorn app.main:app --reload
```

The smoke test assumes the service is available at:

```text
http://localhost:8000/mcp
```

## 1. Initialize the MCP session

## HTTP command examples

The examples below use real `curl` syntax.

On Windows PowerShell, `curl` may be an alias for `Invoke-WebRequest`. To force the real curl executable, use `curl.exe` instead of `curl`.

Check with:

```powershell
Get-Command curl
```

If it shows `Alias`, use:

```powershell
curl.exe --version
```

Then replace `curl` with `curl.exe` in the examples below.

## 1. Initialize the MCP session

A `tools/call` request requires an initialized MCP session. Send an `initialize` request first, then reuse the returned `Mcp-Session-Id` header when calling tools.

Send the initialize request:

```bash
curl -i -X POST "http://localhost:8000/mcp/" \
  -H "Accept: application/json, text/event-stream" \
  -H "Content-Type: application/json" \
  --data '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "manual-smoke-test",
        "version": "0.1.0"
      }
    }
  }'
```

The response headers should include:

```text
Mcp-Session-Id: <session-id>
```

Copy that value. The following tool calls must include it in the `Mcp-Session-Id` request header.

For convenience, store it in a shell variable:

```bash
SESSION_ID="<session-id-from-response>"
```

## 2. Call `list_documents`

Call the `list_documents` MCP tool using the initialized session and local development API key:

```bash
curl -i -X POST "http://localhost:8000/mcp/" \
  -H "Accept: application/json, text/event-stream" \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -H "X-Agent-Api-Key: local-dev-agent-key" \
  --data '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "list_documents",
      "arguments": {
        "query": ""
      }
    }
  }'
```

Expected result:

- the request should not be rejected as unauthenticated
- the response should contain a successful MCP tool result
- only public documents should be listed

## 3. Call `docs_tool` for a public document

Use one of the public `document_id` values returned by `list_documents`.

For the seeded local data, this is typically:

```text
doc1
```

Call the `docs_tool` MCP tool:

```bash
curl -i -X POST "http://localhost:8000/mcp/" \
  -H "Accept: application/json, text/event-stream" \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -H "X-Agent-Api-Key: local-dev-agent-key" \
  --data '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "docs_tool",
      "arguments": {
        "document_id": "doc1"
      }
    }
  }'
```

Expected result:

- the registered agent identity should resolve from the API-key credential
- the proxy should derive trusted `document_visibility`
- the PDP should allow the public document read
- the response should contain the selected document content

## 4. Verify PDP audit persistence

After the MCP calls, check the latest audit rows:

```bash
docker compose exec -T postgres psql \
  -U app_user \
  -d app_db \
  -c "SELECT request_id, agent_id, tool_name, resource, decision, rationale, policy_sha256, created_at FROM pdp_audit ORDER BY created_at DESC LIMIT 10;"
```

Expected result:

- recent rows should include `agent_id = local-dev-agent`
- `tool_name` should include `docs_tool` for the document read call
- `decision` should show the PDP decision
- `policy_sha256` should be populated

## 5. Optional negative check: invalid API key

Call the same tool with an invalid API key:

```bash
curl -i -X POST "http://localhost:8000/mcp/" \
  -H "Accept: application/json, text/event-stream" \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -H "X-Agent-Api-Key: invalid-local-key" \
  --data '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "docs_tool",
      "arguments": {
        "document_id": "doc1"
      }
    }
  }'
```

Expected result:

- `isError` should be `false`
- `structuredContent.results.document_id` should be `doc1`
- `structuredContent.results.body` should contain the selected document body

## Notes

This smoke test uses the local development credential created by:

```bash
python scripts/create-local-agent-credential.py
```

The pytest suite does not depend on this local credential. Automated tests use the isolated test database or monkeypatched resolver behaviour.