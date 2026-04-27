# Runtime contract

This document records the current runtime contract for the MCP proxy, PDP invocation model, policy evaluation, and audit path.

## Layer split

The runtime deliberately separates tool execution inputs from PDP decision inputs.

- MCP tool entrypoints receive explicit tool parameters such as `query` or `document_id`.
- Tool entrypoints pass those values to the proxy as `tool_arguments`.
- `tool_arguments` live in the proxy/tool execution layer.
- The proxy uses `tool_arguments` for pre-PDP enrichment and post-allow execution.
- The PDP does not evaluate raw `tool_arguments`.

## PDP invocation request

The PDP receives a normalized `InvocationDecisionRequest`.

Current request shape:

```python
class InvocationDecisionRequest(BaseModel):
    request_id: str
    agent_id: str
    server_name: str
    tool_name: str
    action: str
    resource: str
    decision_context: dict[str, Any]
```

Important contract points:

resource is singular.
decision_context is the PDP decision input.
decision_context is server-prepared.
decision_context may include facts derived from tool arguments, runtime state, authentication, configuration, or database lookups.
Policy constraints evaluate only against decision_context.
Raw caller-supplied tool arguments are not directly evaluated by the PDP.
Policy constraints

## Policy constraints do not declare a source.

Example:

```
constraints:
  - field: document_visibility
    operator: equals
    value: public
```

This means:

```
decision_context["document_visibility"] == "public"
```

The policy engine does not look in a separate parameters object or a separate context object.

## Document example

For docs_tool(document_id):

```
agent supplies document_id
proxy receives tool_arguments = {"document_id": "..."}
proxy derives document_visibility from the document repository
proxy builds decision_context
PDP evaluates decision_context
```

Example decision context:

```
decision_context = {
    "document_visibility": "public",
}
```

The database owns the runtime fact:

```
this document is public/private
```

The policy owns the rule:

```
allow document.read only when document_visibility is public
```

## Decision response

The PDP decision response keeps rationale as a list.

```
rationale: list[str]
```

This allows a stable response shape even if future decisions include multiple rationale codes.

## Audit contract

Every PDP decision is persisted as a PDP audit event.

The PostgreSQL pdp_audit table is the source of truth.

Audit events are also mirrored to stdout through the dedicated pdp_audit logger.

The audit record includes the normalized decision metadata, including:

- request ID
- agent ID
- server name
- tool name
- invocation action
- resource
- decision
- rationale
- policy version
- policy SHA-256
- creation timestamp