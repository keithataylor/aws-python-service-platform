# AWS Terraform Deployment Sequence

## Purpose

This document records the AWS/Terraform deployment steps taken for `aws-python-service-platform`, in sequence order.

The goal is to make clear:

- what was created
- why each step was required
- which Terraform file contains the relevant infrastructure definition
- where AWS CLI or Docker CLI was used outside Terraform
- how the explicit AWS wiring maps to the final runtime architecture

The Mermaid architecture diagram shows the final shape. This document shows the practical build path used to assemble that shape.

---

## Current Terraform file layout

The Terraform root module currently lives in:

- `infra/terraform/`

Current relevant Terraform files:

- `infra/terraform/providers.tf`
- `infra/terraform/variables.tf`
- `infra/terraform/main.tf`
- `infra/terraform/outputs.tf`
- `infra/terraform/resources.tf`
- `infra/terraform/network.tf`
- `infra/terraform/security_groups.tf`
- `infra/terraform/vpc_endpoints.tf`
- `infra/terraform/load_balancer.tf`
- `infra/terraform/rds.tf`
- `infra/terraform/terraform.tfvars.example`
- local-only `infra/terraform/terraform.tfvars`
- `infra/terraform/.terraform.lock.hcl`

File purposes:

- `providers.tf`
  - Terraform version constraint
  - AWS provider declaration
  - AWS provider region configuration

- `variables.tf`
  - input variables such as AWS region, project name, environment, and externally created secret ARNs

- `main.tf`
  - shared Terraform locals
  - `name_prefix`
  - `short_name_prefix`
  - `common_tags`

- `outputs.tf`
  - useful values exposed after apply
  - ECR repository URL
  - ALB DNS name
  - RDS endpoint
  - RDS-managed secret ARN

- `resources.tf`
  - general AWS resources currently containing:
    - ECR repository
    - ECS cluster

- `network.tf`
  - VPC
  - internet gateway
  - public subnets
  - private app subnets
  - private DB subnets
  - public route table
  - private app route table
  - route table associations
  - RDS DB subnet group

- `security_groups.tf`
  - ALB security group
  - app/ECS task security group
  - AWS service interface endpoint security group
  - DB/RDS security group
  - security group ingress and egress rules

- `vpc_endpoints.tf`
  - interface VPC endpoints for ECR API, ECR Docker registry, CloudWatch Logs, and Secrets Manager
  - S3 gateway endpoint associated with the private app route table

- `load_balancer.tf`
  - Application Load Balancer
  - target group
  - HTTP listener

- `rds.tf`
  - RDS PostgreSQL instance
  - RDS-managed master password setting

- `terraform.tfvars.example`
  - committed example values
  - contains placeholders, not real account-specific values

- `terraform.tfvars`
  - local-only real values
  - ignored by Git

- `.terraform.lock.hcl`
  - provider dependency lock file
  - committed so provider versions/checksums are stable and reviewable

---

## 1. Created Terraform project structure

Files:

- `infra/terraform/providers.tf`
- `infra/terraform/variables.tf`
- `infra/terraform/main.tf`
- `infra/terraform/outputs.tf`
- `infra/terraform/resources.tf`
- `infra/terraform/network.tf`
- `infra/terraform/security_groups.tf`
- `infra/terraform/vpc_endpoints.tf`
- `infra/terraform/load_balancer.tf`
- `infra/terraform/rds.tf`
- `infra/terraform/terraform.tfvars.example`

Why:

- Terraform needs a root module.
- The AWS provider must be declared.
- Common project/environment variables need to be defined once.
- Shared naming/tagging values need to be available to all resources.
- Outputs expose generated values needed during deployment, such as ECR URL, ALB DNS, and RDS endpoint.

Key concept:

- Terraform loads all `.tf` files in the same module directory.
- The filenames are mainly for human organisation.
- The block contents are what Terraform evaluates.

---

## 2. Configured provider, variables, locals, and outputs

Files:

- `infra/terraform/providers.tf`
- `infra/terraform/variables.tf`
- `infra/terraform/main.tf`
- `infra/terraform/outputs.tf`

Why:

- `providers.tf` tells Terraform to use the AWS provider and which region to target.
- `variables.tf` defines configurable deployment inputs.
- `main.tf` defines reusable local values used across resources.
- `outputs.tf` exposes useful generated values after apply.

Important values:

- `var.aws_region`
- `var.project_name`
- `var.environment`
- `var.agent_credential_hash_secret_arn`
- `local.name_prefix`
- `local.short_name_prefix`
- `local.common_tags`

Important distinction:

- `variables.tf` defines inputs.
- `terraform.tfvars` supplies real local values for those inputs.
- `locals` are Terraform-only derived values.
- Outputs are values Terraform prints or exposes after apply.

---

## 3. Protected Terraform state and local values

Files:

- `.gitignore`
- `infra/terraform/terraform.tfvars.example`
- local-only `infra/terraform/terraform.tfvars`
- `infra/terraform/.terraform.lock.hcl`

Why:

- Terraform state can contain sensitive infrastructure metadata.
- `.tfvars` files can contain real account-specific values or secret ARNs.
- These should not be committed.
- `.terraform.lock.hcl` should be committed because it locks provider versions and checksums.

Rules:

- Commit `terraform.tfvars.example`.
- Do not commit `terraform.tfvars`.
- Commit `.terraform.lock.hcl`.
- Do not commit `terraform.tfstate`.
- Do not commit `.terraform/`.
- Do not commit secret-bearing local files.

Relevant `.gitignore` intent:

- ignore `.terraform/`
- ignore `terraform.tfstate`
- ignore `terraform.tfstate.*`
- ignore real `.tfvars`
- allow `.tfvars.example`

---

## 4. Initialized and validated Terraform

Command type:

- Terraform CLI

Actions:

- Ran `terraform init`.
- Ran `terraform validate`.
- Ran `terraform plan`.

Relevant files:

- `providers.tf`
- `variables.tf`
- `main.tf`
- `outputs.tf`

Why:

- `terraform init` downloaded and initialized the AWS provider.
- `terraform validate` confirmed the Terraform configuration was syntactically valid.
- The initial plan confirmed variables, locals, and outputs resolved before real AWS resources were added.

Important distinction:

- A no-resource plan can still validate provider setup, variables, locals, and outputs.
- It does not create AWS resources until resource blocks are added and `terraform apply` is run.

---

## 5. Created ECR repository

File:

- `infra/terraform/resources.tf`

Resource:

- `aws_ecr_repository.app`

Why:

- ECS/Fargate needs a container image to run.
- ECR is the AWS container registry where that image is stored.
- The app image must exist in ECR before an ECS task definition can reliably reference it.

Result:

- ECR repository created:
  - `702630738731.dkr.ecr.eu-west-2.amazonaws.com/aws-python-service-platform-dev-app`

Important distinction:

- ECR stores the app image.
- ECR does not run the app.
- ECS/Fargate later runs the image stored in ECR.

Related output:

- `ecr_repository_url`
  - defined in `outputs.tf`

---

## 6. Built local Docker image

File:

- `Dockerfile`

Command type:

- Docker CLI

Why:

- The Dockerfile defines how to build the runnable FastAPI/FastMCP app image.
- The image packages:
  - Python runtime
  - Python dependencies from `pyproject.toml`
  - app code
  - Uvicorn startup command

Result:

- Local image built:
  - `aws-python-service-platform:local`

Important distinction:

- `pyproject.toml` defines the Python project/dependency contract.
- `Dockerfile` defines the app image build contract.
- `docker-compose.yml` defines the local multi-container runtime contract.
- ECS/Fargate later runs the ECR-hosted version of the same app image.

---

## 7. Verified local container runtime

Files:

- `Dockerfile`
- `docker-compose.yml`
- `.env.docker`
- `.env.docker.example`

Why:

- The app image needed to be tested before pushing it to AWS.
- Docker Compose provides the local analogue of the AWS runtime:
  - app container
  - Postgres container
  - app environment variables
  - service-name database host

Key local mapping:

- `DB_HOST=postgres`
- `postgres` is the Docker Compose service name.
- The app container reaches the local database container through Docker Compose networking.

Important distinction:

- `POSTGRES_*` variables configure the local Postgres container.
- `DB_*` variables configure the FastAPI app so it can connect to Postgres.
- The values may match, but the variables are read by different programs.

Local analogue:

- `docker-compose.yml`
  - local orchestration

AWS analogue:

- Terraform + ECS task definition
  - AWS orchestration

---

## 8. Authenticated Docker to ECR

Command type:

- AWS CLI
- Docker CLI

Why:

- Docker cannot push to ECR until it is authenticated to the AWS ECR registry.
- AWS CLI retrieves an ECR login token.
- Docker CLI uses that token to log in to the registry.

Important distinction:

- The ECR login command does not push an image.
- It only authorizes Docker to push to the ECR registry.

---

## 9. Tagged and pushed Docker image to ECR

Command type:

- Docker CLI
- AWS CLI for verification

Why:

- The local Docker image needed an ECR repository tag.
- Docker pushes images by tag.
- ECS will later reference the ECR image URL.

Result:

- Image pushed to ECR as:
  - `aws-python-service-platform-dev-app:latest`

Verification:

- AWS CLI confirmed the image existed in ECR with an image digest and the `latest` tag.

Important distinction:

- `docker tag` gives the local image its ECR destination name.
- `docker push` uploads the image to ECR.
- AWS CLI verification confirms the image exists in the AWS registry.

---

## 10. Created ECS cluster

File:

- `infra/terraform/resources.tf`

Resource:

- `aws_ecs_cluster.app`

Why:

- ECS cluster is the container runtime grouping for ECS services and tasks.
- It does not run the app by itself.
- It provides the control-plane grouping where the future ECS service will live.

Result:

- ECS cluster created:
  - `aws-python-service-platform-dev-cluster`

Important distinction:

- ECS cluster, ECS service, and task definition are ECS control-plane resources.
- The actual running app appears later as Fargate task network interfaces inside VPC subnets.
- The ECR image is not inside the ECS cluster; the task definition references the ECR image.

---

## 11. Created VPC and subnet foundation

File:

- `infra/terraform/network.tf`

Resources:

- `aws_vpc.app`
- `aws_internet_gateway.app`
- `aws_subnet.public_a`
- `aws_subnet.public_b`
- `aws_subnet.private_app_a`
- `aws_subnet.private_app_b`
- `aws_subnet.private_db_a`
- `aws_subnet.private_db_b`
- `aws_route_table.public`
- `aws_route.public_internet`
- `aws_route_table_association.public_a`
- `aws_route_table_association.public_b`
- `aws_db_subnet_group.app`

Why:

- The VPC defines the private AWS network boundary.
- Public subnets provide ALB network attachment points.
- Private app subnets are where ECS/Fargate app tasks will run.
- Private DB subnets are where RDS is placed.
- The internet gateway and public route table allow public ALB access.
- The DB subnet group tells RDS which private DB subnets it may use.

Important distinction:

- Public subnets are still inside the VPC.
- They are public because their route table sends internet-bound traffic through the internet gateway.
- Private subnets do not have direct public internet routing.
- Subnets are explicit because AWS needs to know where each runtime component can attach to the network.

---

## 12. Created security groups

File:

- `infra/terraform/security_groups.tf`

Resources:

- `aws_security_group.alb`
- `aws_security_group.app`
- `aws_security_group.db`
- `aws_vpc_security_group_ingress_rule.alb_http_from_internet`
- `aws_vpc_security_group_egress_rule.alb_to_app`
- `aws_vpc_security_group_ingress_rule.app_from_alb`
- `aws_vpc_security_group_egress_rule.app_to_db`
- `aws_vpc_security_group_ingress_rule.db_from_app`

Why:

- Security groups define the allowed traffic between AWS resources.
- The rules explicitly permit only the required application path.

Allowed path:

- Internet to ALB on port `80`
- ALB to ECS/Fargate app tasks on port `8000`
- ECS/Fargate app tasks to RDS PostgreSQL on port `5432`

Important distinction:

- Security groups are not route tables.
- Route tables decide where packets can be routed.
- Security groups decide whether traffic is allowed into or out of attached resources.
- Security groups are stateful firewalls around resources.

---

## 13. Created Application Load Balancer, target group, and listener

File:

- `infra/terraform/load_balancer.tf`

Resources:

- `aws_lb.app`
- `aws_lb_target_group.app`
- `aws_lb_listener.http`

Why:

- The ALB creates the public HTTP entry point.
- The listener receives HTTP traffic on port `80`.
- The listener forwards traffic to the target group.
- The target group will later contain the private IPs of healthy ECS/Fargate tasks.

Result:

- ALB DNS name created:
  - `aspsp-dev-alb-1213226492.eu-west-2.elb.amazonaws.com`

Important distinction:

- The ALB is one logical load balancer resource.
- Its ALB nodes/network interfaces are placed in the public subnets.
- The target group is the backend target registry and health-check state.
- ECS will later register Fargate task private IPs with this target group.

Related output:

- `alb_dns_name`
  - defined in `outputs.tf`

---

## 14. Created RDS PostgreSQL instance

File:

- `infra/terraform/rds.tf`

Resource:

- `aws_db_instance.app`

Why:

- RDS is the AWS-managed PostgreSQL equivalent of the local Docker Compose Postgres container.
- The FastAPI app will connect to RDS using `psycopg`, just as it connects to local Postgres.
- The host changes from local service name `postgres` to the RDS endpoint.

Result:

- RDS endpoint:
  - `aspsp-dev-postgres.cvmcgumwqfl1.eu-west-2.rds.amazonaws.com`

Configuration intent:

- PostgreSQL 16
- private-only database
- encrypted storage
- database name: `app_db`
- master username: `app_user`
- RDS-managed master password

Important distinction:

- RDS runs the PostgreSQL server.
- `psycopg` remains the Python PostgreSQL client.
- `DB_HOST` later becomes the RDS endpoint.

Related output:

- `rds_endpoint`
  - defined in `outputs.tf`

---

## 15. Enabled RDS-managed master password

File:

- `infra/terraform/rds.tf`

Setting:

- `manage_master_user_password = true`

Why:

- This tells RDS to create and manage the master user password.
- RDS stores that password in Secrets Manager.
- Terraform does not provide a password value.

Result:

- RDS-managed secret ARN output:
  - `rds_master_user_secret_arn`

Important distinction:

- Terraform created the RDS instance.
- RDS created and manages the database password.
- The secret value is not supplied through Terraform variables.
- Terraform can output the secret ARN without knowing the actual password value.

Related output:

- `rds_master_user_secret_arn`
  - defined in `outputs.tf`

---

## 16. Created agent credential hash secret manually

Command type:

- AWS CLI

Resource:

- Secrets Manager secret:
  - `aws-python-service-platform/dev/agent-credential-hash-secret`

Why:

- `AGENT_CREDENTIAL_HASH_SECRET` is application-secret material.
- It is used by the app to HMAC-hash presented agent API keys.
- It should be created outside Terraform so Terraform does not store or handle the secret value.

Result:

- Secret ARN:
  - `arn:aws:secretsmanager:eu-west-2:702630738731:secret:aws-python-service-platform/dev/agent-credential-hash-secret-YzZRXq`

Important distinction:

- Secrets Manager stores the secret value.
- Terraform should only reference the secret ARN.
- ECS will later inject the value into the app container at task startup.

---

## 17. Added Terraform variable for existing agent secret ARN

Files:

- `infra/terraform/variables.tf`
- `infra/terraform/terraform.tfvars.example`
- local-only `infra/terraform/terraform.tfvars`

Variable:

- `agent_credential_hash_secret_arn`

Why:

- Terraform needs the secret ARN later when defining the ECS task definition.
- The ARN is a reference, not the secret value.
- This allows Terraform to wire ECS to the secret without reading or storing the secret itself.

Important distinction:

- `terraform.tfvars.example` contains placeholder values and is committed.
- `terraform.tfvars` contains real local/account-specific values and is ignored.
- Terraform state should hold the secret ARN reference, not the secret value.

---

## 18. Current completed AWS vertical slice

Completed:

- ECR repository
- Docker image pushed to ECR
- ECS cluster
- VPC
- public subnets
- private app subnets
- private DB subnets
- internet gateway
- public route table
- private app route table
- DB subnet group
- security groups
- VPC endpoints
- ALB
- target group
- HTTP listener
- RDS PostgreSQL instance
- RDS-managed DB secret
- manually-created agent credential hash secret
- Terraform variable for existing agent credential hash secret ARN
- IAM execution role
- IAM task role
- CloudWatch log group
- ECS task definition
- ECS service
- ECS-to-target-group registration
- ECS secret injection
- deployed `/health` check through ALB
- one-off ECS migration task against private RDS
- AWS dev registered-agent credential seeding task
- manual AWS MCP smoke test helper

The deployed AWS path now works end-to-end:

- ALB forwards public HTTP traffic to ECS/Fargate.
- ECS runs the FastAPI/FastMCP app container.
- The app receives database and credential-secret configuration from ECS task definition environment/secrets.
- The app connects to RDS PostgreSQL.
- RDS migrations and seed data have been applied.
- A dev registered-agent credential has been seeded into RDS.
- MCP `docs_tool` smoke tests work through the deployed `/mcp/` endpoint.

Verified smoke-test outcomes:

- `doc1` is public and returns the document body.
- `doc2` is private and returns a denied MCP result with `DEFAULT_DENY`.

Current networking posture:

- ECS app tasks run in private app subnets with `assignPublicIp=DISABLED`.
- Running ECS app tasks have no public IP.
- ALB nodes remain in public subnets and forward to the private task IPs registered in the target group.
- Required AWS-service access from private ECS tasks uses VPC endpoints:
  - interface endpoints for ECR API, ECR Docker registry, CloudWatch Logs, and Secrets Manager
  - S3 gateway endpoint associated with the private app route table
- App task egress is restricted to RDS, the AWS service interface endpoint security group, and the S3 endpoint prefix list.
- No NAT Gateway is currently deployed; this remains deferred until there is a real requirement for general external egress.

Deferred production hardening:

- HTTPS listener with ACM certificate
- optional HTTP `80 -> 443` redirect
- Terraform remote state
- production credential registry/admin process
- migration version table

---

## 19. Added private ECS task networking and VPC endpoints

Files:

- `infra/terraform/network.tf`
- `infra/terraform/security_groups.tf`
- `infra/terraform/vpc_endpoints.tf`
- `infra/terraform/ecs_service.tf`

Why:

- ECS/Fargate app tasks should not need public IP addresses.
- The ALB should remain the public entry point.
- Private ECS tasks still need AWS-service access for image pulls, runtime secrets, and logs.
- The project does not currently require general outbound internet access, so VPC endpoints are more precise than adding a NAT Gateway for this phase.

Implemented changes:

- Added an explicit private app route table for the private app subnets.
- Added an AWS service interface endpoint security group.
- Added interface VPC endpoints for:
  - ECR API
  - ECR Docker registry
  - CloudWatch Logs
  - Secrets Manager
- Added an S3 gateway endpoint associated with the private app route table.
- Moved the ECS service network configuration from public subnets to private app subnets.
- Changed the ECS service network configuration to `assign_public_ip = false`.
- Replaced broad app HTTPS egress to `0.0.0.0/0` with narrower egress rules:
  - app task security group to AWS service interface endpoint security group on port `443`
  - app task security group to the S3 endpoint prefix list on port `443`

Verified result:

- ECS service reports `assignPublicIp = DISABLED`.
- Running task network interface has no public IP.
- VPC endpoints are available for ECR API, ECR Docker registry, CloudWatch Logs, Secrets Manager, and S3.
- `/health` through the ALB returns `{"status":"ok"}` after the change.
- Terraform plan is clean after apply.

Important distinction:

- The Internet Gateway remains because the ALB is public.
- No NAT Gateway is currently used.
- Private ECS task AWS-service access is through VPC endpoint resources, not through public task IPs.

---

## 20. Clarified Terraform bootstrap image tag ownership

Files:

- `infra/terraform/ecs_task_definition.tf`
- `infra/terraform/variables.tf`
- `infra/terraform/ecs_service.tf`

Why:

- Terraform needs an image reference so it can create the initial ECS task definition.
- GitHub Actions CD owns real application releases after infrastructure exists.
- The CD workflow deploys immutable Git commit SHA image tags by registering new ECS task definition revisions.
- Terraform should not roll back the ECS service to its original bootstrap task definition during later infrastructure applies.

Implemented changes:

- Added `var.bootstrap_image_tag`, defaulting to `latest`.
- Updated the Terraform ECS task definition image reference to use `var.bootstrap_image_tag`.
- Kept the ECS service lifecycle rule that ignores `task_definition` and `desired_count`.

Important distinction:

- Terraform owns the ECS task definition shape and bootstrap image reference.
- GitHub Actions CD owns the currently deployed application image revision.
- Manual operations may temporarily own `desired_count`, for example when pausing the service at zero.
- Terraform should not treat SHA-based CD deployments as infrastructure drift.

Verified result:

- `terraform fmt` completed.
- `terraform validate` passed.
- `terraform plan` reported no changes because `var.bootstrap_image_tag` still defaults to `latest`.


## 21. Implemented AWS runtime mapping

Local Docker Compose mapping:

- `docker-compose.yml`
- `.env.docker`
- app container receives environment variables from `.env.docker`
- Postgres container receives `POSTGRES_*` initialization variables

AWS mapping now implemented:

- ECS task definition supplies app environment variables.
- ECS task definition injects secret values from Secrets Manager.
- RDS supplies the database endpoint.
- ECS service keeps the app task running.
- ECS registers private Fargate task IPs with the ALB target group.
- ALB forwards public traffic to healthy private ECS app tasks.
- Private ECS tasks use VPC endpoints for ECR image pulls, CloudWatch Logs, Secrets Manager, and S3-backed ECR image layers.
- CloudWatch receives app logs.
- One-off ECS tasks run operational scripts inside the same AWS runtime boundary.

Equivalent app contract:

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `AGENT_CREDENTIAL_HASH_SECRET`

The application settings code continues reading the same variable names. The deployment layer supplies them differently.

---

## 22. Local-to-AWS environment mapping

Local app configuration:

- `.env.docker`
  - `DB_HOST=postgres`
  - `DB_PORT=5432`
  - `DB_NAME=app_db`
  - `DB_USER=app_user`
  - `DB_PASSWORD=app_password`
  - `AGENT_CREDENTIAL_HASH_SECRET=local-dev-agent-credential-hash-secret`

Local database initialization:

- `docker-compose.yml`
  - `POSTGRES_DB=app_db`
  - `POSTGRES_USER=app_user`
  - `POSTGRES_PASSWORD=app_password`

AWS application configuration:

- ECS task definition
  - `DB_HOST` from `aws_db_instance.app.address`
  - `DB_PORT=5432`
  - `DB_NAME=app_db`
  - `DB_USER=app_user`
  - `DB_PASSWORD` injected from the RDS-managed Secrets Manager secret
  - `AGENT_CREDENTIAL_HASH_SECRET` injected from the existing manually-created Secrets Manager secret

Important distinction:

- `POSTGRES_*` variables are only for the local Postgres Docker image.
- `DB_*` variables are for the FastAPI app.
- In AWS, RDS replaces the local Postgres Docker container.
- ECS task-definition environment and secrets replace `.env.docker`.

Operational helper scripts now used for AWS:

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
  - calls `docs_tool` through the deployed ALB `/mcp/` endpoint
  - accepts `-DocumentId` so both allow and deny paths can be checked

Example smoke checks:

- `doc1` should return a successful document result.
- `doc2` should return a denied result with `DEFAULT_DENY`.

---

## 23. Why so many explicit resources are required

AWS does not infer the runtime wiring automatically.

The infrastructure must explicitly define:

- where the app runs
- where the database runs
- which subnets are public
- which subnets are private
- how public traffic enters the VPC
- which resource can talk to which other resource
- which ports are allowed
- where container images are stored
- where secrets are stored
- how secrets reach the container
- how ALB finds healthy app tasks
- how ECS keeps app tasks running

The Mermaid diagram shows the bones.

The Terraform resources define the tissue, routes, attachment points, permissions, and runtime wiring that make the architecture actually work.

## Production hardening deliberately deferred

This deployment sequence records the implemented AWS/Terraform build path for the current production-representative portfolio slice.

The sequence does not claim to implement every control expected in a full commercial production environment. Production hardening items such as HTTPS/ACM, Terraform remote state, multi-environment state separation, restore testing, monitoring/alerting, migration version tracking, and production credential administration are documented as deliberate boundaries in:

- `docs/aws_deployment_target.md`
- `docs/production_secret_and_state_security.md`
- `docs/aws_operator_runbook.md`

This keeps the deployment sequence focused on what was actually built, while making the remaining commercial hardening boundary explicit.