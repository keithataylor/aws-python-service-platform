rules:
  - rule_id: allow_public_docs_read
    when:
      server_name: docs_mcp
      tool_name: docs_tool
      action: tool.read
      resource: public.docs
      constraints:
        - parameter: document_visibility
          operator: equals
          value: public
    then:
      effect: allow
      rationale: POLICY_ALLOW_PUBLIC_DOCS_READ
      obligations:
        - obligation_type: audit_log
          parameters:
            level: decision

## Field origin and allowed values

| Field | Origin | Allowed values / notes |
|---|---|---|
| `rule_id` | Policy-authored | Free string identifier chosen by policy author |
| `when.server_name` | Runtime-derived, matched by policy | Free string; value comes from normalized invocation request |
| `when.tool_name` | Runtime-derived, matched by policy | Free string; value comes from normalized invocation request |
| `when.action` | Runtime-derived, matched by policy | Free string; value comes from normalized invocation request |
| `when.resource` | Runtime-derived, matched by policy | Free string; value comes from normalized invocation request |
| `constraints.parameter` | Policy-authored | Name of field looked up in request `parameters` or `context` |
| `constraints.operator` | Engine-defined | `equals`, `in`, `not_in` |
| `constraints.value` | Policy-authored | Comparison target; shape depends on operator |
| `then.effect` | Engine-defined | `allow`, `deny` |
| `then.rationale` | Policy-authored | Free string rationale code/message |
| `then.obligations` | Policy-authored | List of obligation objects |
| `then.obligations[].obligation_type` | Policy-authored for now | Free string for now; may become fixed vocabulary later |
| `then.obligations[].parameters` | Policy-authored | Free key/value object |

Note: Engine-defined values require code support; policy-authored values do not.


## Rules behaviour v1

- Rules are evaluated top-to-bottom; the first matching rule wins; if none match, default_decision applies.
- v1 does not yet implement explicit rule priority or deny-overrides behaviour.