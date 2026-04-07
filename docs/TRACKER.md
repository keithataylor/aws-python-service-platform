# TRACKER.md

## Current aim
Build a recruiter-facing Python/AWS backend service that is evolving toward an MCP/agent runtime access-control architecture, with proxy / PEP / PDP direction.

The primary system story is agent tool-call control and runtime policy enforcement.
The supporting engineering story is strong backend/platform implementation depth, including schemas, service design, persistence, async/concurrency, observability, and AWS deployment shape.

## Current implemented
- FastAPI service foundation
- health and service-info endpoints
- typed task submission/status example
- externalized YAML policy loading
- agent action evaluation endpoint
- deterministic allow/deny response shape

## Next intended architecture
- richer policy rule model
- parameter/constraint-aware rule evaluation
- policy-as-data validation via Pydantic
- clearer PDP / PEP separation
- future proxy/enforcement module for tool-call mediation
- audit/event model for agent action decisions

## Out of scope for now
- full MCP proxy implementation
- real credential brokerage
- database-backed policy storage
- IdP integration

## Immediate next code goal
Expand policy rules to support constraints and obligations.

## Later-phase backend concerns
- PostgreSQL-backed policy/audit persistence
- typed persistence models for decisions, rules, and execution records
- async/concurrency patterns for evaluation and future proxy/tool mediation
- background task/workflow handling where justified