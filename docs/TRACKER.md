# TRACKER.md

## Current aim

Build a recruiter-facing Python/AWS backend service that demonstrates an MCP-facing agent runtime policy decision point (PDP), proxy-style enforcement surface, PostgreSQL-backed persistence, and auditability.

The primary system story is:

- agent tool-call control
- deterministic runtime policy enforcement
- clear proxy / PEP / PDP separation
- trusted server-prepared decision context
- auditable allow/deny decisions

The supporting engineering story is backend/platform implementation depth:

- FastAPI service structure
- FastMCP runtime surface
- typed schemas and validation
- PostgreSQL persistence
- structured logging
- Docker-based local development
- GitHub Actions CI
- Ruff linting and pytest coverage

## Current implemented state

The current stable slice includes:

- FastAPI service foundation
- health endpoint
- service-info endpoint
- mounted FastMCP `/mcp` surface
- MCP initialization and tool discovery
- MCP tools:
  - `list_documents`
  - `docs_tool`
- proxy wrapper flow for MCP tool invocation handling
- frozen `ToolSpec` dataclass registry
- per-tool pre-PDP enrichment and post-allow execution
- normalized `InvocationDecisionRequest`
- `decision_context` as the PDP decision input
- deterministic YAML-backed policy evaluation
- PostgreSQL-backed document repository
- PostgreSQL-backed PDP audit table
- dedicated PDP audit service/repository layer
- dedicated PDP audit logger
- local Docker Compose PostgreSQL workflow
- rerunnable SQL migrations
- isolated test database workflow
- marker-based unit and integration tests
- GitHub Actions CI running:
  - Ruff lint
  - unit tests
  - integration tests
- resolved agent identity boundary
- API-key identity adapter with MCP metadata fallback
- proxy receives `ResolvedAgentIdentity` and uses `agent_identity.agent_id` for PDP/audit

## Current runtime contract

The current runtime contract is:

- MCP tools expose explicit caller-supplied arguments such as `query` and `document_id`.
- Tool entrypoints pass those values to the proxy as `tool_arguments`.
- `tool_arguments` remain in the proxy/tool execution layer.
- The proxy uses `tool_arguments` for:
  - pre-PDP enrichment
  - post-allow execution
- The PDP receives `decision_context`.
- `decision_context` is the server-prepared set of facts the PDP is allowed to evaluate.
- Policy constraints evaluate only against `decision_context`.
- The PDP does not evaluate raw caller-supplied tool arguments.
- `resource` is singular.
- `rationale` remains `list[str]`.
- Every PDP decision is persisted as an audit row.
- Tool-specific pre-PDP handlers validate their derived context before it becomes PDP decision_context.
- For the document read flow, the derived context is validated as DocumentDecisionContext and currently contains document_visibility.

The fuller contract is documented in:

- `docs/runtime_contract.md`

## Current architecture direction

The architecture direction is intentionally narrow:

- FastMCP owns the raw MCP / JSON-RPC boundary.
- Thin MCP tool functions call the proxy wrapper.
- The proxy wrapper owns orchestration.
- The tool registry maps tool names to static policy metadata and handlers.
- Pre-PDP functions derive trusted decision facts.
- The PDP evaluates normalized requests against loaded YAML policy.
- Post-allow functions execute business actions only after an allow decision.
- PDP decisions are persisted for audit.
- Runtime logging and audit logging remain separate.

## Current database state

The current PostgreSQL-backed flow includes:

- `documents` table for document search/read examples
- `pdp_audit` table for PDP decision audit events

Current migration chain:

- `001_create_documents_table.sql`
- `002_seed_documents.sql`
- `003_create_pdp_audit_table.sql`

Current schema decisions:

- `pdp_audit.resource` is `TEXT NOT NULL`
- `pdp_audit.rationale` is `TEXT[] NOT NULL`
- `pdp_audit.policy_sha256` is included in the base audit migration

## Current test coverage

The current tests cover:

- tool registry lookup
- invalid tool lookup
- policy evaluation allow/default-deny behaviour
- server-name participation in policy evaluation
- first matching policy rule wins
- decision-context-based constraint evaluation
- health endpoint success
- health endpoint database failure
- service-info endpoint
- `/api/v1/agent-actions/evaluate`
- MCP initialization
- MCP tools/list
- MCP list_documents tool calls
- MCP docs_tool allow path
- MCP docs_tool deny path
- MCP post-allow failure handling
- PDP audit row persistence
- policy SHA-256 audit persistence
- resolved agent identity boundary
- API-key identity adapter
- MCP metadata fallback
- API-key-resolved agent identity persisted in PDP audit rows
- test DB isolation

## Out of scope for now

The project is not currently trying to implement:

- custom MCP protocol handling
- real credential brokerage
- IdP integration
- multi-tenant SaaS features
- database-backed policy authoring/storage
- Kubernetes deployment
- production-grade downstream forwarding to external MCP servers
- SQLAlchemy/Alembic unless direct SQL becomes a real limitation
- broad AI governance platform features

## Immediate next code direction

Do not add new infrastructure yet.

The next backend work should be chosen only where it protects or clarifies the implemented runtime contract.

Good next candidates are:

- keep README and docs aligned with the implemented code
- keep migration scripts linear and easy to reason about
- avoid speculative wrapper/ToolSpec tests unless a real uncovered failure mode is identified

## Current project status

The current stable implementation demonstrates:

- MCP tool call
- proxy orchestration
- server-prepared decision context
- deterministic PDP policy decision
- PostgreSQL-backed business data
- PostgreSQL-backed PDP audit record
- structured runtime/audit logging
- local and CI test coverage
- linted project structure
- resolved agent identity boundary
- API-key identity adapter
- MCP metadata fallback

This is now a credible small backend/platform slice for demonstrating agent-runtime policy enforcement rather than a generic API scaffold.
