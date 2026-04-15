# TRACKER.md

## Current aim
Build a recruiter-facing Python/AWS backend service that is evolving toward an MCP-facing agent runtime access-control architecture with clear proxy / PEP / PDP separation.

The primary system story is agent tool-call control and runtime policy enforcement.
The supporting engineering story is backend/platform implementation depth, including schemas, service design, persistence, async/concurrency, observability, and AWS deployment shape.

## Current implemented
- FastAPI service foundation
- health and service-info endpoints
- typed task submission/status example
- externalized YAML policy loading
- agent action evaluation endpoint
- deterministic allow/deny response shape
- mounted FastMCP `/mcp` boundary
- MCP tool discovery and tool invocation tests
- `list_documents` and `docs_tool` MCP tools
- proxy wrapper flow for tool invocation normalization and PDP evaluation
- tool registry/spec pattern with per-tool pre-PDP and post-allow handling
- seeded in-memory document store with public/private visibility metadata
- document search and read flow using shared trusted document data

## Current architecture direction
- MCP-facing proxy as the enforcement path for tool calls
- normalized internal invocation decision requests for PDP evaluation
- semantic action mapping per tool (for example `document.search`, `document.read`)
- trusted pre-PDP context derivation for document-specific policy facts
- post-allow business execution separated from policy evaluation
- clear separation between proxy orchestration, document store helpers, and domain actions

## Out of scope for now
- real credential brokerage
- IdP integration
- database-backed policy storage
- production-grade downstream forwarding to external MCP servers

## Immediate next code goal
Replace the seeded in-memory document store with PostgreSQL-backed document persistence while preserving the current proxy / PDP / tool registry flow.

## Later-phase backend concerns
- PostgreSQL-backed policy/audit persistence
- typed persistence models for decisions, rules, and execution records
- SQLAlchemy and Alembic integration where justified
- auth-derived agent identity passed into the proxy flow
- async/concurrency patterns for evaluation and future proxy/tool mediation
- background task/workflow handling where justified
