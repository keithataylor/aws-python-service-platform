# AWS Operator Runbook

## Purpose

This runbook records the operational commands and checks for the AWS deployment of `aws-python-service-platform`.

It is intended for development/portfolio operation, not production operations.

Current AWS shape:

```text
Internet client
-> public ALB
-> ECS/Fargate app task in private app subnet
-> FastAPI + FastMCP app
-> RDS PostgreSQL in private DB subnet

Private ECS task AWS-service access:
ECS task
-> VPC endpoints
-> ECR / CloudWatch Logs / Secrets Manager / S3
```

---

## Current operating model

Terraform manages the AWS infrastructure.

GitHub Actions manual CD deploys application image updates into the existing ECS service.

Operational scripts handle controlled tasks such as:

- running RDS migrations
- registering/rotating the AWS dev agent credential
- smoke-testing deployed MCP tool calls

---

## Important safety rules

Do not commit:

```text
.env
.env.docker
terraform.tfvars
terraform.tfstate
terraform.tfstate.*
.terraform/
raw API keys
AWS access keys
secret values
```

Do not paste raw dev API keys into documentation, GitHub variables, GitHub secrets, or commits.

The AWS dev agent API key is smoke-test-only material.

---

## Pause AWS runtime

Use this when the deployed runtime is not currently needed.

### 1. Scale ECS app service to zero

```powershell
aws ecs update-service `
  --cluster aws-python-service-platform-dev-cluster `
  --service aspsp-dev-app-service `
  --desired-count 0
```

Verify:

```powershell
aws ecs describe-services `
  --cluster aws-python-service-platform-dev-cluster `
  --services aspsp-dev-app-service `
  --query "services[0].{Desired:desiredCount,Running:runningCount,Pending:pendingCount}" `
  --output table
```

Expected:

```text
Desired = 0
Running = 0
Pending = 0
```

### 2. Stop RDS

```powershell
aws rds stop-db-instance `
  --db-instance-identifier aspsp-dev-postgres
```

Verify:

```powershell
aws rds describe-db-instances `
  --db-instance-identifier aspsp-dev-postgres `
  --query "DBInstances[0].DBInstanceStatus" `
  --output text
```

Expected final state:

```text
stopped
```

Note: stopping RDS can take several minutes.

---

## Restart AWS runtime

Use this when the deployed app needs to be tested again.

### 1. Start RDS

```powershell
aws rds start-db-instance `
  --db-instance-identifier aspsp-dev-postgres
```

Wait until available:

```powershell
aws rds describe-db-instances `
  --db-instance-identifier aspsp-dev-postgres `
  --query "DBInstances[0].DBInstanceStatus" `
  --output text
```

Expected:

```text
available
```

### 2. Scale ECS service back to one task

```powershell
aws ecs update-service `
  --cluster aws-python-service-platform-dev-cluster `
  --service aspsp-dev-app-service `
  --desired-count 1
```

Verify:

```powershell
aws ecs describe-services `
  --cluster aws-python-service-platform-dev-cluster `
  --services aspsp-dev-app-service `
  --query "services[0].{Desired:desiredCount,Running:runningCount,Pending:pendingCount}" `
  --output table
```

Expected:

```text
Desired = 1
Running = 1
Pending = 0
```

### 3. Check health endpoint

```powershell
curl.exe http://aspsp-dev-alb-1213226492.eu-west-2.elb.amazonaws.com/health
```

Expected:

```json
{"status":"ok"}
```

### 4. Verify ECS private networking

Check the ECS service network configuration:

```powershell
aws ecs describe-services `
  --cluster aws-python-service-platform-dev-cluster `
  --services aspsp-dev-app-service `
  --query "services[0].networkConfiguration.awsvpcConfiguration"
```

Expected:

```text
assignPublicIp = DISABLED
subnets = private app subnet IDs
```

Check the running task network interface:

```powershell
$taskArn = aws ecs list-tasks `
  --cluster aws-python-service-platform-dev-cluster `
  --service-name aspsp-dev-app-service `
  --query "taskArns[0]" `
  --output text

$networkInterfaceId = aws ecs describe-tasks `
  --cluster aws-python-service-platform-dev-cluster `
  --tasks $taskArn `
  --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value" `
  --output text

aws ec2 describe-network-interfaces `
  --network-interface-ids $networkInterfaceId `
  --query "NetworkInterfaces[0].{SubnetId:SubnetId,PrivateIp:PrivateIpAddress,PublicIp:Association.PublicIp,Status:Status}" `
  --output table
```

Expected:

```text
PublicIp = None
SubnetId = private app subnet ID
```

---

## Manual CD deployment

Manual CD is run from GitHub Actions.

Path:

```text
GitHub
-> Actions
-> Deploy to AWS ECS
-> Run workflow
-> Branch: main
-> Run workflow
```

The workflow:

```text
GitHub OIDC
-> assumes AWS deploy role
-> builds Docker image
-> tags image with Git commit SHA and latest
-> pushes image to ECR
-> registers new ECS task definition revision
-> updates ECS service
-> waits for service stability
-> checks /health
```

Verify deployed task definition:

```powershell
aws ecs describe-services `
  --cluster aws-python-service-platform-dev-cluster `
  --services aspsp-dev-app-service `
  --query "services[0].taskDefinition" `
  --output text
```

Inspect deployed image:

```powershell
aws ecs describe-task-definition `
  --task-definition aspsp-dev-app-task `
  --query "taskDefinition.containerDefinitions[0].image" `
  --output text
```

Expected: the image tag should be a Git commit SHA, not only `latest`.

---

## Run AWS migrations

Use only when the RDS schema needs applying/updating.

From project root:

```powershell
.\scripts\run-aws-migrations-task.ps1
```

This starts a one-off ECS/Fargate task that runs:

```text
python scripts/run_aws_migrations.py
```

Check logs:

```powershell
aws logs tail /ecs/aws-python-service-platform-dev-app --since 15m
```

Expected:

```text
All migrations completed successfully.
```

---

## Register or rotate AWS dev agent credential

Use this to create or rotate the AWS dev credential used for MCP smoke tests.

From project root:

```powershell
.\scripts\register-aws-dev-agent-task.ps1
```

Then check CloudWatch logs:

```powershell
aws logs tail /ecs/aws-python-service-platform-dev-app --since 15m
```

Copy the newly printed raw dev API key into a local/private location only.

Do not commit it.

---

## Run deployed MCP smoke tests

Requires a current raw AWS dev agent API key.

Allow-path check:

```powershell
.\scripts\smoke-aws-docs-tool.ps1 -RawApiKey "AWS_DEV_AGENT_KEY_HERE" -DocumentId "doc1"
```

Expected:

```text
Tool response status:
200

document_id:
doc1
```

Deny-path check:

```powershell
.\scripts\smoke-aws-docs-tool.ps1 -RawApiKey "AWS_DEV_AGENT_KEY_HERE" -DocumentId "doc2"
```

Expected:

```text
decision:
deny

rationale:
DEFAULT_DENY
```

---

## Check CloudWatch logs

```powershell
aws logs tail /ecs/aws-python-service-platform-dev-app --since 15m
```

Use this for:

- app startup checks
- migration task output
- credential registration task output
- runtime errors
- ECS task command failures

---

## Check cost drivers

Main ongoing cost drivers while infrastructure exists:

```text
ALB
VPC public IPv4
VPC interface endpoints
ECS/Fargate tasks when running
RDS when running
Secrets Manager
CloudWatch logs
ECR image storage
```

Check monthly cost by service:

```text
AWS Console
-> Billing and Cost Management
-> Cost Explorer
-> Cost analysis
-> Group by: Service
```

Pausing ECS and RDS reduces runtime cost, but ALB, public IPv4, VPC interface endpoints, Secrets Manager, CloudWatch, and ECR storage costs can remain until the infrastructure is destroyed.

---

## Destroy AWS infrastructure

Use only when the live AWS environment is no longer needed.

From `infra/terraform`:

```powershell
terraform plan -destroy
```

Review the plan carefully.

Then:

```powershell
terraform destroy
```

This removes the Terraform-managed AWS resources.

Do not run this if you still need the live ALB/ECS/RDS environment for testing or demonstration.

---

## Current known development limitations

The current AWS environment is a development/portfolio deployment.

Known non-production limitations:

- HTTP only; HTTPS/ACM is not yet configured.
- Terraform state is currently local, not remote S3-backed state.
- RDS migration version tracking is not yet implemented.
- Dev credential registration is operational-script based, not a production admin workflow.
- No NAT Gateway is currently deployed; this is acceptable for the current AWS-service-only egress model, but would need revisiting if the app calls external APIs.
- Post-deploy smoke testing currently checks `/health`; fuller MCP smoke checks remain manual.