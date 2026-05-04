# Decision contract

This document records the current runtime contract for MCP tool calls, proxy enforcement, PDP invocation, policy evaluation, identity resolution, and PDP audit persistence.

## Runtime flow

The current MCP runtime flow is:

```text
MCP client
→ FastMCP tool entrypoint
→ agent identity resolution
→ proxy wrapper
→ tool-specific argument validation
→ tool-specific derived context validation
→ PDP invocation request
→ PDP policy evaluation
→ PDP audit persistence
→ post-allow tool action, if allowed
```

The proxy is the enforcement boundary for MCP tool invocations.

## Layer split

The runtime deliberately separates caller-supplied tool input from PDP decision input.

- MCP tool entrypoints receive explicit tool parameters such as `query` or `document_id`.
- Tool entrypoints pass those values to the proxy as `tool_arguments`.
- `tool_arguments` remain in the proxy/tool execution layer.
- The proxy uses `tool_arguments` for pre-PDP enrichment and post-allow execution.
- The PDP does not evaluate raw `tool_arguments`.

The PDP evaluates a server-prepared `decision_context`, not raw MCP JSON and not arbitrary caller-supplied argument dictionaries.

## Agent identity resolution

MCP tool execution uses DB-backed API-key identity resolution.

Current identity flow:

- The request must provide `X-Agent-Api-Key`.
- The raw API key is never stored.
- The presented API key is HMAC-SHA256 hashed using `AGENT_CREDENTIAL_HASH_SECRET`.
- The resulting hash is looked up against `agent_api_credentials.api_key_hash`.
- The credential must have `status = 'active'`.
- The owning registered agent must have `status = 'active'`.
- If both checks pass, the runtime resolves the registered agent's `agent_id` as the trusted agent identity.
- Missing, invalid, revoked, or disabled credentials resolve to `auth_method="none"`.
- `auth_method="none"` is rejected by the proxy before:
  - tool lookup
  - pre-PDP enrichment
  - PDP evaluation
  - PDP audit persistence
  - post-allow execution
- MCP request metadata is not used as an authentication source.

The resolver returns `ResolvedAgentIdentity`, currently containing:

- `agent_id`
- `auth_method`
- optional `tenant_id`
- optional `roles`

The proxy receives the resolved identity object and currently uses `agent_identity.agent_id` for:

- `InvocationDecisionRequest.agent_id`
- PDP audit event `agent_id`
- runtime logging where agent identity is needed

Credential implementation details are not passed into the PDP. The PDP does not receive:

- raw API keys
- API-key hashes
- credential IDs
- API-key prefixes
- credential status values

`policy.yaml` authorizes the resolved identity. It may match on `agent_id`, but it should not contain or evaluate credential material.

Additional identity facts such as `roles`, `tenant_id`, or `auth_method` should only be added to `decision_context` when policy rules actually need to evaluate them.

## Tool argument validation

Tool arguments are caller supplied, so tool action handlers validate the argument shape before using those values.

Current document tool argument validation:

- `list_documents` validates `query`
- `docs_tool` validates `document_id`

This keeps caller-supplied tool input explicit and bounded before it is used for repository access, pre-PDP enrichment, or post-allow execution.

## Derived decision context

Tool-specific pre-PDP handlers derive trusted tool/domain facts for policy evaluation.

Current document read flow:

```text
docs_tool(document_id)
→ validate document_id
→ look up document metadata
→ derive document_visibility
→ validate DocumentDecisionContext
→ return dict for PDP decision_context
```

For the document read flow, the derived context is validated as `DocumentDecisionContext`.

Current document decision context:

```python
{
    "document_visibility": "public",
}
```

The document pre-PDP handler owns document-derived policy facts.

The identity resolver owns agent identity facts.

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

- `resource` is singular.
- `agent_id` is top-level request metadata for audit and traceability.
- `decision_context` is the PDP decision input.
- `decision_context` is server-prepared.
- Current document policy uses `decision_context.document_visibility`.
- Policy constraints evaluate only against `decision_context`.
- Raw caller-supplied tool arguments are not directly evaluated by the PDP.
- Tool-specific pre-PDP handlers validate their derived context before it becomes PDP `decision_context`.
- Unauthenticated agent identity is rejected before a PDP request is built.

## Policy matching

Policy rules are evaluated top-to-bottom.

The first matching rule wins.

If no rule matches, `default_decision` applies.

Rule matching currently uses top-level invocation metadata:

- `server_name`
- `tool_name`
- `action`
- `resource`

Policy constraints evaluate only against `decision_context`.

## Policy constraints

Policy constraints do not declare a source.

Example:

```yaml
constraints:
  - field: document_visibility
    operator: equals
    value: public
```

This means:

```python
decision_context["document_visibility"] == "public"
```

The policy engine does not look in a separate `parameters` object or a separate `context` object.

Supported operators are currently:

- `equals`
- `in`
- `not_in`

Constraint matching fails closed when the referenced field is missing from `decision_context`.

## Document example

For `docs_tool(document_id)`:

```text
agent supplies document_id
proxy receives tool_arguments = {"document_id": "..."}
document argument model validates document_id
proxy derives document_visibility from the document repository
DocumentDecisionContext validates the derived document context
proxy builds InvocationDecisionRequest with decision_context
PDP evaluates decision_context
```

The database owns the runtime fact:

```text
this document is public/private
```

The policy owns the rule:

```text
allow document.read only when document_visibility is public
```

So the allow path is:

```text
document_visibility = public
→ policy constraint matches
→ PDP decision = allow
→ audit row is written
→ post-allow document action executes
```

The deny path is:

```text
document_visibility = private
→ policy constraint does not match
→ default_decision applies
→ PDP decision = deny
→ audit row is written
→ post-allow document action does not execute
```

## Decision response

The PDP decision response keeps rationale as a list.

```python
rationale: list[str]
```

This keeps the response shape stable even if future decisions include multiple rationale codes.

## Audit contract

Every PDP decision is persisted as a PDP audit event.

The PostgreSQL `pdp_audit` table is the source of truth.

Audit events are also mirrored to stdout through the dedicated `pdp_audit` logger.

The audit record includes the normalized decision metadata:

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

Unauthenticated identity failures happen before PDP evaluation and therefore are not PDP audit events.

## Current failure boundaries

The current fail-closed boundaries are:

- missing or invalid API key is rejected before PDP/tool execution
- missing `decision_context` fields cause constraints to fail
- invalid tool argument shapes fail before repository/action use
- invalid document-derived context fails before PDP evaluation
- denied PDP decisions do not execute post-allow tool actions

These boundaries are intended to keep caller input, trusted derived facts, policy decisions, and audit records clearly separated.
