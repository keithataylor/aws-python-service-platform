# aws-python-service-platform

Production-style Python backend service portfolio project evolving toward an MCP-facing AI agent runtime policy decision point (PDP) and proxy-style enforcement surface.

This repository is being built to demonstrate practical backend and platform engineering capability relevant to Python/AWS service roles and emerging agent-runtime control-plane work, including:

- Python API/service development
- typed request/response and schema validation
- deterministic policy evaluation
- clean service layering and dependency boundaries
- MCP-facing proxy / PEP / PDP separation
- PostgreSQL-backed persistence design
- Redis-backed state/caching patterns
- async/background execution and concurrency fundamentals
- structured logging, health checks, and operational clarity
- containerised development workflow
- CI and AWS-oriented deployment shape

## Purpose

The aim is to show hands-on engineering work beyond a simple stateless API, with emphasis on service structure, validation, policy control, persistence, reliability, and operational clarity.

The repository’s core application direction is now an MCP-facing agent runtime control surface:

- a remote MCP client calls the mounted `/mcp` endpoint
- FastMCP handles the raw MCP/JSON-RPC boundary
- thin tool entrypoints hand off to a proxy wrapper
- the proxy normalizes a tool invocation into an internal decision request
- the PDP evaluates the normalized request against human-authored YAML policy
- if allowed, the proxy executes the tool-specific business action
- if denied, the proxy returns a denied MCP tool result

This is not intended as a product launch.
It is intended as evidence of implementation capability.

## Current implemented shape

The current implemented slice includes:

- FastAPI application foundation
- mounted FastMCP `/mcp` surface
- externalized YAML policy loading and validation
- normalized internal invocation decision model
- deterministic allow/deny evaluation with rationale and obligations
- proxy wrapper controlling pre-PDP enrichment and post-allow execution
- tool registry/spec mapping tool name to static policy metadata and handlers
- seeded in-memory document store used as the trusted source for current document search/read flow
- MCP tools for:
  - `list_documents`
  - `docs_tool`

## Current MCP proxy flow

The current runtime flow is:

1. MCP client calls `/mcp`
2. FastMCP parses and routes the tool invocation
3. Tool entrypoint passes `tool_name` and `tool_arguments` into the proxy wrapper
4. Proxy resolves static tool policy metadata (`action`, `resource`)
5. Tool-specific pre-PDP enrichment derives trusted context where required
6. Proxy normalizes the invocation into `InvocationDecisionRequest`
7. PDP evaluates against YAML policy
8. On allow, tool-specific post-allow business logic runs
9. On deny, the proxy returns a denied MCP result

## Current policy model

Current policy semantics are intentionally simple:

- rules are evaluated top-to-bottom
- first matching rule wins
- `default_decision` applies if nothing matches
- `parameters` represent caller-supplied tool inputs
- `context` represents trusted derived facts

For the current document example:

- `list_documents(query)` uses caller input in `parameters`
- `docs_tool(document_id)` uses caller input in `parameters`
- trusted `document_visibility` is derived from the document store and supplied in `context`

## Current document example

The current seeded document flow is deliberately small but end-to-end:

- `list_documents(query)` searches title/summary over the in-memory document set
- only public documents are returned in search results
- `docs_tool(document_id)` derives trusted visibility metadata before PDP evaluation
- if allowed, the selected document is returned
- if denied, the tool returns an MCP error result shape

This is intentionally a controlled in-memory implementation so that the mechanism is visible before the data source is replaced with PostgreSQL.

## Planned next phase

The next major step is to replace the in-memory document store with PostgreSQL-backed persistence while keeping the proxy/PDP flow and MCP result shapes stable.

Expected next-phase backend work includes:

- PostgreSQL
- SQLAlchemy
- Alembic
- typed persistence models for documents, policy-relevant metadata, and later audit/event records
- authentication wiring at the FastMCP boundary
- async/concurrency patterns where they support enforcement workflows

## Boundaries

This project is intentionally focused.

It is not currently trying to be:

- a custom MCP framework implementation
- a multi-service system
- a Kubernetes-first project
- a full SaaS product
- a complex multi-tenant platform
- a feature-heavy end-user application

The emphasis is on doing a smaller set of backend/platform concerns properly:

- proxy / PDP separation
- trustworthy policy inputs
- persistence
- authentication
- cache/state handling
- observability
- containerisation
- CI discipline

## Current repository direction

A representative current structure is:

```text
aws-python-service-platform/
├─ app/
│  ├─ main.py
│  ├─ policy/
│  │  ├─ evaluator.py
│  │  ├─ loader.py
│  │  └─ models.py
│  ├─ proxy/
│  │  ├─ config.py
│  │  ├─ wrapper.py
│  │  ├─ normalizer.py
│  │  ├─ tool_registry.py
│  │  ├─ document_store.py
│  │  └─ document_actions.py
│  ├─ schemas/
│  │  └─ invocation.py
│  └─ ...
├─ docs/
├─ tests/
├─ Dockerfile
├─ docker-compose.yml
├─ pyproject.toml
└─ README.md
```

The exact structure may continue to evolve, but the intended separation is now clearer:

- FastMCP boundary in `main.py`
- policy subsystem in `app/policy/`
- proxy orchestration in `app/proxy/wrapper.py`
- tool registry in `app/proxy/tool_registry.py`
- domain data access in `app/proxy/document_store.py`
- post-allow business actions in domain-specific action modules

## Current endpoints and surfaces

- `GET /health` — operational health check
- `GET /api/v1/service-info` — basic service metadata
- mounted MCP surface at `/mcp`
- current MCP tools:
  - `list_documents`
  - `docs_tool`

## Status

This repository is in active build-out as a portfolio project focused on backend/platform depth and MCP-adjacent agent runtime control.
