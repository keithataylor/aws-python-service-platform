# Production Secret and Terraform State Security

## Purpose

This document defines the production security approach for Terraform state and runtime secrets in `aws-python-service-platform`.

The project rule is:

> Terraform manages infrastructure.
> Secret values are created, owned, rotated, and administered outside Terraform.

This keeps the infrastructure-as-code layer separate from the sensitive runtime credential layer.

---

## Core security position

Terraform should be responsible for:

- VPC, subnets, route tables, security groups, and VPC endpoints
- ECR repositories
- ECS clusters, services, and task definitions
- ALB, listeners, and target groups
- RDS infrastructure
- IAM roles and permissions
- CloudWatch log groups
- references to existing Secrets Manager secrets
- private AWS-service access paths needed by ECS tasks

Terraform should not be responsible for:

- generating production database passwords
- generating production agent credential hash secrets
- storing secret values in `.tfvars`
- storing secret values in Terraform state
- reading secret values through Terraform data sources
- outputting secret values
- passing secret values directly into ECS task definitions

---

## Why this matters

Terraform state can contain sensitive values.

Marking a Terraform variable as `sensitive` helps hide values from CLI output, but it does not guarantee that those values are absent from state or plan files.

Therefore, for production use, the safest approach is:

```text
Do not let Terraform see secret values in the first place.
```

---

## Production secret ownership model

Secret values should be created by an administrator or controlled secret-provisioning process.

For this project, production secrets include:

| Secret | Purpose | Production owner |
|---|---|---|
| `DB_PASSWORD` | Password used by the app to connect to RDS PostgreSQL | Admin / secrets owner |
| `AGENT_CREDENTIAL_HASH_SECRET` | HMAC secret used to hash presented agent API keys | Admin / secrets owner |

The values should be stored in AWS Secrets Manager.

Terraform may reference the secret ARNs or names, but should not read the secret values.

---

## Correct production flow

```text
Admin / security owner
  -> creates secret values in AWS Secrets Manager
  -> controls rotation and access policy

Terraform
  -> creates infrastructure
  -> creates ECS task role permissions
  -> wires ECS task definition to existing secret ARNs
  -> never reads the secret values

ECS/Fargate
  -> injects secrets into the running container at startup

Application
  -> reads DB_PASSWORD and AGENT_CREDENTIAL_HASH_SECRET from environment variables
```

---

## ECS secret injection model

The ECS task definition should use the ECS `secrets` mechanism.

Conceptually:

```text
container environment variable:
  DB_PASSWORD

source:
  Secrets Manager secret ARN
```

The container receives the value at runtime.

Terraform only needs to know:

```text
secret name or ARN
environment variable name
```

Terraform does not need to know:

```text
actual database password
actual agent credential hash secret
```

---

## Terraform state backend policy

Production Terraform state should use a remote backend.

Recommended backend:

```text
S3 backend
  -> encrypted bucket
  -> versioning enabled
  -> state locking enabled
  -> restricted IAM access
```

State files must be treated as sensitive infrastructure records.

They may contain:

- resource IDs
- network details
- IAM role names
- ARNs
- RDS endpoints
- secret ARNs
- generated metadata
- dependency information

Even without secret values, state should not be public or committed to Git.

### Current project boundary

Remote Terraform state is documented here as the production recommendation, but it is not currently implemented for this portfolio/dev environment.

The current project remains a single-operator deployment using local Terraform state, with the strict rule that local state files must not be committed to Git.

Remote state should be added if the project moves beyond single-developer demonstration into shared infrastructure management, client handover, or a more production-like multi-environment workflow.

---

## Repository rules

The following must never be committed:

```text
terraform.tfstate
terraform.tfstate.*
.terraform/
*.tfvars
.env
.env.docker
```

Example files may be committed:

```text
terraform.tfvars.example
.env.example
.env.docker.example
```

Example files must not contain real credentials.

---

## Terraform variable rule

Production Terraform variables may include non-secret references such as:

```text
db_password_secret_arn
agent_credential_hash_secret_arn
```

They must not include secret values such as:

```text
db_password
agent_credential_hash_secret
```

Good:

```hcl
variable "db_password_secret_arn" {
  description = "ARN of the existing Secrets Manager secret containing the RDS app password."
  type        = string
}
```

Avoid:

```hcl
variable "db_password" {
  description = "Database password."
  type        = string
  sensitive   = true
}
```

The avoided form may hide CLI output, but still risks Terraform handling and storing the secret value.

---

## RDS password handling

For production, the preferred approach is:

```text
Admin creates RDS password secret in Secrets Manager.
Terraform receives only the secret ARN or name.
Terraform configures ECS to use the secret.
Application reads DB_PASSWORD at runtime.
```

If Terraform must create the RDS instance, the password handling must be decided carefully before implementation.

Preferred strict-security posture:

```text
Terraform creates the RDS infrastructure shape.
Secret values are provisioned separately by an admin-controlled workflow.
Terraform does not generate or store the password.
```

For a portfolio/dev environment, Terraform-generated disposable secrets may be acceptable, but this should be explicitly marked as non-production.

---

## Agent credential hash secret handling

`AGENT_CREDENTIAL_HASH_SECRET` is security-critical.

It controls how raw agent API keys are HMAC-hashed before database lookup.

Production rules:

- create the secret outside Terraform
- store it in Secrets Manager
- restrict read access to the ECS task role
- do not print it
- do not place it in `.tfvars`
- do not store it in Terraform state
- rotate only with a planned credential migration strategy

---

## IAM access model

For ECS secret injection, the ECS task execution role should have least-privilege access to the specific Secrets Manager secrets injected into the container.

In this project, the execution role reads the configured secret values before the app container starts and injects them as environment variables.

The running application should not need direct Secrets Manager read access unless the app code explicitly calls AWS Secrets Manager at runtime.

Example permission intent:

```text
Allow ECS task execution role to read:
  DB password secret
  agent credential hash secret
```

It should not have broad access such as:

```text
secretsmanager:GetSecretValue on *
```

---

## Operational separation

Production responsibilities should be separated:

| Responsibility | Owner |
|---|---|
| Infrastructure definition | Terraform |
| Secret value creation | Admin / security owner |
| Secret rotation | Admin / security owner |
| Runtime secret access | ECS task role |
| Application config reading | FastAPI app settings |
| State storage security | AWS account/platform owner |

This separation reduces the chance that infrastructure automation becomes a secret-handling layer.

---

## Production checklist

Before production deployment:

- [ ] Terraform remote state is configured.
- [ ] S3 state bucket is encrypted.
- [ ] S3 state bucket has versioning enabled.
- [ ] State locking is enabled.
- [x] Terraform state files are not committed to Git.
- [x] `.tfvars` files containing real values are not committed.
- [x] `AGENT_CREDENTIAL_HASH_SECRET` is created in Secrets Manager outside Terraform.
- [ ] Production secrets are created in Secrets Manager outside Terraform.
- [x] Terraform references only secret ARNs/names for `AGENT_CREDENTIAL_HASH_SECRET`.
- [x] ECS task definition declares `DB_PASSWORD` and `AGENT_CREDENTIAL_HASH_SECRET` in its `secrets` block so ECS injects them into the app container environment.
- [x] ECS task execution role has `secretsmanager:GetSecretValue` permission only for the specific Secrets Manager secrets referenced by that task definition.
- [x] Secret values are not output by Terraform.
- [x] Secret values are not read through Terraform data sources.
- [ ] RDS password handling is documented before production use.
- [ ] `AGENT_CREDENTIAL_HASH_SECRET` rotation strategy is documented before production use.

---

## Project decision

For this project:

```text
Development/portfolio environment:
  Terraform may be used pragmatically, but no local state or tfvars file may be committed.

Production-grade recommendation:
  Terraform manages infrastructure only.
  Secrets Manager stores secret values.
  Secret values are created/administered outside Terraform.
  Terraform references secret ARNs/names only.
  ECS injects secrets at runtime.
```

This is the recommended security posture for client-facing or production work.