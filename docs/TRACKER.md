# TRACKER.md

## Current aim

Build a recruiter-facing Python/AWS backend service that demonstrates an MCP-facing agent runtime policy decision point (PDP), proxy-style enforcement surface, PostgreSQL-backed persistence, registered-agent identity resolution, auditability, and a working AWS deployment vertical slice.

The primary system story is:

- agent tool-call control
- deterministic runtime policy enforcement
- clear proxy / PEP / PDP separation
- trusted server-prepared decision context
- auditable allow/deny decisions
- DB-backed registered-agent identity resolution
- local and AWS runtime parity through the same application configuration contract

The supporting engineering story is backend/platform implementation depth:

- FastAPI service structure
- FastMCP runtime surface
- typed schemas and validation
- PostgreSQL persistence
- structured runtime logging
- PDP audit logging
- Docker-based local development
- SQL migrations and seed data
- AWS ECS/Fargate deployment
- RDS PostgreSQL runtime configuration
- Secrets Manager runtime secret injection
- CloudWatch log collection
- GitHub Actions CI
- Ruff linting and pytest coverage

The project is intentionally scoped as a small, complete, auditable runtime slice rather than a broad AI governance platform or full SaaS product.

---

## Current implemented state

The current stable implementation includes:

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
- local dev agent credential helper via `scripts/create-local-agent-credential.py`
- isolated test database workflow
- marker-based unit and integration tests
- GitHub Actions CI running:
  - Ruff lint
  - unit tests
  - integration tests
- resolved agent identity boundary
- DB-backed registered-agent credential lookup
- HMAC-SHA256 API-key hashing using `AGENT_CREDENTIAL_HASH_SECRET`
- raw API keys are not stored
- missing, invalid, revoked, or disabled credentials are rejected before PDP/tool execution
- MCP metadata is not used as an authentication source
- proxy receives `ResolvedAgentIdentity` and uses `agent_identity.agent_id` for PDP/audit
- AWS deployment slice using:
  - ECR
  - ECS/Fargate
  - ALB
  - RDS PostgreSQL
  - Secrets Manager
  - IAM execution/task roles
  - IAM Identity Center admin access is configured for normal AWS console work
  - CloudWatch Logs
- one-off ECS task path for RDS migrations
- one-off ECS task path for AWS dev registered-agent credential seeding/rotation
- deployed AWS MCP smoke-test helper for `docs_tool`

---

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
- Tool-specific pre-PDP handlers validate their derived context before it becomes PDP `decision_context`.
- For the document read flow, the derived context is validated as `DocumentDecisionContext` and currently contains `document_visibility`.

The fuller contract is documented in:

- `docs/runtime_contract.md`
- `docs/decision_contract.md`

---

## Current architecture direction

The architecture direction remains intentionally narrow:

- FastMCP owns the raw MCP / JSON-RPC boundary.
- Thin MCP tool functions call the proxy wrapper.
- The proxy wrapper owns orchestration and enforcement.
- The tool registry maps tool names to static policy metadata and handlers.
- Pre-PDP functions derive trusted decision facts.
- The PDP evaluates normalized requests against loaded YAML policy.
- Post-allow functions execute business actions only after an allow decision.
- PDP decisions are persisted for audit.
- Runtime logging and audit logging remain separate.
- AWS deployment should preserve the same application contract used locally.

Current runtime path:

```text
MCP client
-> FastAPI + FastMCP /mcp endpoint
-> thin MCP tool entrypoint
-> registered-agent identity resolution
-> proxy enforcement wrapper
-> trusted pre-PDP context derivation
-> deterministic PDP evaluation
-> allow/deny enforcement
-> PostgreSQL-backed tool action
-> PostgreSQL-backed audit event
```

---

## Current database state

The current PostgreSQL-backed flow includes:

- `documents` table for document search/read examples
- `pdp_audit` table for PDP decision audit events
- `registered_agents` table for stable agent identities
- `agent_api_credentials` table for hashed API-key credentials

Current migration chain:

- `001_create_documents_table.sql`
- `002_seed_documents.sql`
- `003_create_pdp_audit_table.sql`
- `004_create_registered_agent_credentials.sql`

Current schema decisions:

- `pdp_audit.resource` is `TEXT NOT NULL`
- `pdp_audit.rationale` is `TEXT[] NOT NULL`
- `pdp_audit.policy_sha256` is included in the base audit migration
- `registered_agents.status` is constrained to `active` or `disabled`
- `agent_api_credentials.status` is constrained to `active` or `revoked`
- `agent_api_credentials.api_key_hash` is unique
- `agent_api_credentials.agent_id` references `registered_agents.agent_id` with `ON DELETE RESTRICT`
- raw API keys are never stored in PostgreSQL

Current seed document behaviour:

- `doc1` is public
- `doc2` is private
- `doc3` is public

The current policy allows the public document path and default-denies the private document path.

---

## Current AWS deployment state

The AWS vertical slice is live and smoke-tested.

Implemented AWS runtime path:

```text
Internet client / MCP smoke client
-> Application Load Balancer
-> ECS Fargate service
-> FastAPI + FastMCP app
-> RDS PostgreSQL
-> PDP audit persistence
-> CloudWatch logs
```

Implemented AWS infrastructure includes:

- ECR repository for the application image
- ECS Fargate cluster
- ECS task definition
- ECS service
- Application Load Balancer
- HTTP listener
- target group registration for ECS tasks
- VPC
- public subnets
- private app subnets
- private DB subnets
- internet gateway
- public route table
- DB subnet group
- security groups for:
  - ALB
  - ECS app task
  - RDS PostgreSQL
- private RDS PostgreSQL instance
- RDS-managed database password secret
- manually-created Secrets Manager secret for `AGENT_CREDENTIAL_HASH_SECRET`
- ECS task execution role
- ECS task role
- CloudWatch log group
- one-off ECS task path for applying RDS migrations
- one-off ECS task path for creating/rotating the AWS dev agent credential
- deployed MCP smoke-test helper for `docs_tool`

Current AWS configuration contract:

- ECS task definition supplies:
  - `DB_HOST`
  - `DB_PORT`
  - `DB_NAME`
  - `DB_USER`
- ECS task definition injects:
  - `DB_PASSWORD`
  - `AGENT_CREDENTIAL_HASH_SECRET`
- RDS supplies the PostgreSQL database.
- CloudWatch receives application and operational logs.
- The same application settings names are used locally and in AWS.

Verified AWS checks:

- `/health` through the ALB returns healthy.
- RDS migrations run successfully from a one-off ECS task.
- AWS dev registered-agent credential seeding/rotation runs successfully from a one-off ECS task.
- Deployed `docs_tool` returns `doc1` successfully.
- Deployed `docs_tool` denies `doc2` with `DEFAULT_DENY`.

Current intentional AWS development limitation:

- ECS app tasks currently run in public subnets with `assignPublicIp=ENABLED`.
- This avoids adding NAT Gateway or VPC endpoints during the first runnable AWS vertical slice.
- Inbound access is still controlled by security groups:
  - Internet -> ALB on port `80`
  - ALB -> ECS app task on port `8000`
  - ECS app task -> RDS on port `5432`

Deferred AWS hardening:

- HTTPS listener with ACM certificate
- optional HTTP-to-HTTPS redirect
- private ECS task networking without public task IPs
- NAT Gateway or VPC endpoints for outbound AWS service access
- immutable image tags instead of deploying `latest`
- Terraform remote state backend
- migration version tracking
- production-grade credential registration/rotation workflow
- CI/CD deployment workflow

---

## Current operational helper scripts

Local helper:

- `scripts/create-local-agent-credential.py`
  - creates or updates the local dev registered-agent credential in `app_db`
  - prints the local raw API key for manual local MCP calls
  - stores only the HMAC hash in PostgreSQL

AWS helpers:

- `scripts/run-aws-migrations-task.ps1`
  - starts a one-off ECS/Fargate task
  - runs `scripts/run_aws_migrations.py`
  - applies SQL migrations against private RDS

- `scripts/register-aws-dev-agent-task.ps1`
  - starts a one-off ECS/Fargate task
  - runs `scripts/register_aws_dev_agent.py`
  - creates or rotates the AWS dev registered-agent credential
  - prints the raw dev API key once to CloudWatch logs

- `scripts/smoke-aws-docs-tool.ps1`
  - performs the MCP initialize/session flow
  - calls deployed `docs_tool`
  - accepts `-DocumentId` so allow and deny paths can be checked

Raw dev API keys are smoke-test-only material and must not be committed.

---

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
- DB-backed API-key identity adapter
- API-key hashing is deterministic
- API-key hash changes when the API key or HMAC secret changes
- active credential for active registered agent resolves agent identity
- revoked credential does not resolve agent identity
- active credential for disabled registered agent does not resolve agent identity
- missing/invalid API key resolves to unauthenticated identity
- unresolved agent identity rejected before PDP/tool execution
- API-key-resolved agent identity persisted in PDP audit rows

Manual/deployment smoke coverage currently confirms:

- AWS `/health` through ALB
- AWS `docs_tool` allow path for `doc1`
- AWS `docs_tool` deny path for `doc2`

---

## Out of scope for now

The project is not currently trying to implement:

- custom MCP protocol handling
- production credential brokerage
- IdP integration
- multi-tenant SaaS features
- database-backed policy authoring/storage
- Kubernetes deployment
- production-grade downstream forwarding to external MCP servers
- SQLAlchemy/Alembic unless direct SQL becomes a real limitation
- broad AI governance platform features
- production credential registry UI
- production-grade AWS networking hardening

These are deliberate scope boundaries, not forgotten requirements.

The project should continue to favour a small, complete, auditable runtime slice over broad framework expansion.

---

## Engineering roadmap

Next work should be tied to real production-relevant gaps.

Good next candidates:

- document the AWS smoke-test workflow clearly without exposing raw keys or account-specific sensitive values
- keep README, tracker, and AWS deployment docs aligned with the implemented runtime
- move from `latest` image deployments to immutable image tags
- add HTTPS/ACM support for the ALB
- add private ECS task networking using NAT Gateway or VPC endpoints
- add Terraform remote state
- add migration version tracking if migration reruns become harder to reason about
- formalize production-style registered-agent credential registration and rotation
- add CI/CD deployment workflow after the manual AWS path is stable
- keep migration scripts linear and easy to reason about
- avoid speculative wrapper/ToolSpec tests unless a real uncovered failure mode is identified
- role-based Terraform access using IAM Identity Center / SSO temporary credentials
- GitHub Actions OIDC deployment role for ECS application delivery

Avoid adding new infrastructure or abstractions unless they clarify, secure, or harden the current ECS/RDS/proxy/PDP boundary.

---

## Current project status

The current stable implementation demonstrates:

- MCP tool call handling
- proxy orchestration
- server-prepared decision context
- deterministic PDP policy decision
- PostgreSQL-backed business data
- PostgreSQL-backed PDP audit records
- structured runtime/audit logging
- local Docker/PostgreSQL runtime
- AWS ECS/Fargate/RDS/ALB runtime
- RDS-backed registered-agent identity resolution
- HMAC-hashed API-key identity adapter
- one-off ECS operational tasks
- deployed MCP allow/deny smoke tests
- local and CI test coverage
- linted project structure

This is now a credible backend/platform slice for demonstrating agent-runtime policy enforcement, AWS deployment fundamentals, and audit-oriented runtime design.
