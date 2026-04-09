# aws-python-service-platform

Production-style Python backend service portfolio project evolving toward an AI agent runtime policy decision point (PDP).

This repository is being built to demonstrate practical backend and platform engineering capability relevant to Python/AWS service roles and emerging agent-runtime control-plane work, including:

- Python API/service development
- typed request/response and schema validation
- deterministic policy evaluation
- clean service layering and dependency boundaries
- PostgreSQL-backed persistence design
- Redis-backed state/caching patterns
- async/background execution and concurrency fundamentals
- structured logging, health checks, and operational clarity
- containerised development workflow
- CI and AWS-oriented deployment shape

## Purpose

The aim is to show hands-on engineering work beyond a simple stateless API, with emphasis on service structure, validation, policy control, persistence, reliability, and operational clarity.

The repository’s core application direction is an AI agent runtime PDP:
it evaluates structured agent action requests against human-owned policy and returns deterministic allow/deny decisions.

At the same time, the project is also intentionally being used to demonstrate broader backend/platform engineering depth, including data modelling, persistence, async workflows, observability, and deployable service structure.

It is not intended as a product launch.  
It is intended as evidence of implementation capability.

## v1 Scope

Version 1 is focused on establishing a credible PDP-style backend service foundation:

- FastAPI service with clean application structure
- typed schemas for agent action requests and responses
- externalised policy loading and validation
- deterministic allow/deny evaluation
- route-layer dependency injection with service-layer separation
- structured error handling and request validation
- health/readiness endpoints
- structured logging
- Docker-based local development
- automated CI checks for tests, linting, type checking, and container build validation

## v1 Service Shape

Version 1 is centered on a policy decision service for agent/runtime actions:

- a caller submits a structured agent action request
- the API validates the request shape
- the route resolves the active policy document
- the policy service evaluates the request against deterministic rules
- the service returns an explicit allow/deny decision with rationale

This design is intended to demonstrate realistic backend concerns such as schema ownership, dependency boundaries, deterministic service logic, policy-as-data validation, and operational discipline.

It also creates the base for later backend expansion where justified, including persistence, audit storage, async enforcement workflows, and proxy-style mediation.

## Planned Tech Stack

This project is currently centered on:

- **FastAPI**
- **Pydantic**
- **YAML-based policy documents**
- **Docker**
- **GitHub Actions**
- **structured application logging**

Later-phase backend/platform expansion may include:

- **PostgreSQL**
- **SQLAlchemy**
- **Alembic**
- **Redis**
- **background worker / queue patterns**
- **metrics / observability tooling**

## Boundaries

This project is intentionally focused.

It is not intended in v1 to be:

- a multi-service system
- a Kubernetes-first project
- a full SaaS product
- a complex multi-tenant platform
- a feature-heavy end-user application

The emphasis is on doing a smaller set of backend/platform concerns properly:
- persistence
- authentication
- background processing
- cache/state handling
- observability
- containerisation
- CI discipline

## Status

This repository is in active build-out as a portfolio project focused on backend and platform engineering depth.

## Current repository structure

```text
aws-python-service-platform/
├─ app/
│  ├─ main.py
│  ├─ api/
│  │  ├─ deps.py
│  │  └─ routes.py
│  ├─ core/
│  │  ├─ config.py
│  │  └─ policy_loader.py
│  ├─ models/
│  ├─ policies/
│  │  └─ agent_policy.yaml
│  ├─ schemas/
│  │  ├─ agent_action.py
│  │  ├─ echo.py
│  │  ├─ policy.py
│  │  ├─ system.py
│  │  └─ task.py
│  ├─ services/
│  │  ├─ agent_policy_service.py
│  │  └─ task_service.py
│  └─ workers/
├─ docker/
├─ docs/
├─ migrations/
├─ tests/
├─ Dockerfile
├─ docker-compose.yml
├─ pyproject.toml
└─ README.md

```

This structure may evolve, but the project is intended to keep application code, database concerns, worker logic, tests, CI, and supporting documentation clearly separated.

## Current endpoints

- `GET /health` — operational health check
- `GET /api/v1/service-info` — basic service metadata
- `POST /api/v1/echo` — typed request/response example with validation
- `POST /api/v1/tasks` — submit a task for asynchronous-style processing
- `GET /api/v1/tasks/{task_id}` — retrieve current task status
- `POST /api/v1/agent-actions/evaluate` — evaluate a structured agent action against deterministic policy



## Architecture direction

This project is evolving toward an AI agent runtime policy decision point (PDP) for tool-call authorization.

Current focus:
- normalized internal decision requests for agent tool invocations
- externalized policy in YAML
- deterministic policy evaluation with explicit rationale and obligations
- clean separation between proxy/PEP concerns and PDP evaluation logic
- policy subsystem structure with dedicated loading, models, and evaluation components

Planned direction:
- remote MCP proxy acting as the execution-path PEP
- interception and normalization of MCP tool calls before PDP evaluation
- audit/event records for decisions and enforcement actions
- backend persistence and async/concurrency patterns where they support enforcement workflows
- future scoped/ephemeral credential brokerage aligned to policy decisions

Proxy boundary:
- The proxy presents as a remote MCP server to standard MCP clients.
- Agents/hosts are configured to call the proxy as their MCP endpoint.
- The proxy intercepts MCP tool invocations and normalizes them.
- The PDP evaluates only normalized internal decision requests, not raw MCP payloads.
- If allowed, the proxy enforces the result and forwards the call onward.
