# AWS Deployment Target

## Purpose

Define the AWS runtime shape for `aws-python-service-platform` before implementing Terraform.

## Target runtime path

```text
Client / MCP caller
  -> Application Load Balancer
  -> ECS Fargate service
  -> FastAPI + FastMCP app
  -> RDS PostgreSQL
  -> CloudWatch logs
```

## AWS services

| Concern | AWS service |
|---|---|
| Container runtime | ECS Fargate |
| HTTP ingress | Application Load Balancer |
| Database | RDS PostgreSQL |
| Secrets | Secrets Manager or SSM Parameter Store |
| Logs | CloudWatch Logs |
| Runtime permissions | ECS task role |
| Infrastructure | Terraform |

## Runtime configuration mapping

The AWS deployment should keep the same application configuration contract used locally, but change where values come from.

| Setting | Local source | AWS source | Notes |
|---|---|---|---|
| `DB_HOST` | `.env` / local Docker Postgres host | Terraform output from RDS endpoint | Changes from `localhost` to the RDS endpoint |
| `DB_PORT` | `.env` | ECS environment variable | Usually remains `5432` |
| `DB_NAME` | `.env` | ECS environment variable | Same logical application database name |
| `DB_USER` | `.env` | ECS environment variable or secret | Database user for RDS PostgreSQL |
| `DB_PASSWORD` | `.env` | Secrets Manager | Injected into the ECS task at runtime |
| `TEST_DB_NAME` | `.env` | Not required for deployed runtime | Used by local/CI test flows |
| `AGENT_CREDENTIAL_HASH_SECRET` | `.env` | Secrets Manager | Used to HMAC-hash presented agent API keys |

The application code should continue reading configuration through the existing settings module. Terraform and ECS are responsible for supplying the correct runtime values.

## Initial deployment scope

The first AWS deployment will run the existing service using RDS-backed configuration and CloudWatch logging.

## Deferred scope

Credential brokerage, STS-based tool credentials, S3-backed document reads, admin API, and advanced concurrency testing are deferred until the baseline deployment is working.

## AWS runtime boundary model

```mermaid
---
config:
  flowchart:
    nodeSpacing: 0
    rankSpacing: 80
    subGraphTitleMargin:
      top: 10
      bottom: 20
---

flowchart TB
    Client["Internet client / MCP caller"]

    subgraph AWS["AWS Account / eu-west-2"]

        subgraph ControlPlane["AWS control-plane resources"]
            ECSCluster["ECS Cluster"]
            ECSService["ECS Service<br/>desired task count"]
            TaskDef["Task Definition<br/>image + env + CPU/memory"]
            ECR["ECR Repository<br/>container image"]
        end

        subgraph VPC["VPC: private network boundary"]

            ALB["Logical Application Load Balancer"]
            Listener["ALB Listener<br/>HTTP/HTTPS"]
            TG["Target Group<br/>registered task IPs + health state"]

            subgraph PublicA["Public Subnet A"]
                ALBNodeA["ALB node / network interface<br/>AZ: eu-west-2a<br/>public-facing IP"]
            end

            subgraph PublicB["Public subnet B"]
                ALBNodeB["ALB node / network interface<br/>AZ: eu-west-2b<br/>public-facing IP"]
            end

            subgraph PrivateAppA["Private app subnet A"]
                TaskA["Fargate task<br/>FastAPI container<br/>AZ: eu-west-2a<br/>private IP: 10.0.11.x:8000"]
            end

            subgraph PrivateAppB["Private app subnet B"]
                TaskB["Fargate task<br/>FastAPI container<br/>AZ: eu-west-2b<br/>private IP: 10.0.12.x:8000"]
            end

            subgraph PrivateDB["Private DB subnets"]
                RDS["RDS PostgreSQL"]
            end
        end
    end

    Client -->|"requests ALB DNS name"| ALB
    ALB -->|"AWS DNS resolves to ALB node IP"| ALBNodeA
    ALB -->|"AWS DNS resolves to ALB node IP"| ALBNodeB

    ALBNodeA --> Listener
    ALBNodeB --> Listener
    Listener --> TG
    TG -->|"healthy target"| TaskA
    TG -->|"healthy target"| TaskB

    ECSCluster --> ECSService
    ECSService --> TaskDef
    TaskDef --> ECR
    ECSService -->|"starts/registers tasks"| TaskA
    ECSService -->|"starts/registers tasks"| TaskB

    TaskA --> RDS
    TaskB --> RDS
```