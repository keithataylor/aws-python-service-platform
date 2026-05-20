# AWS Deployment Target

## Purpose

Define the implemented AWS runtime shape for `aws-python-service-platform`.

## Target runtime path

```text
Client / MCP caller
  -> Application Load Balancer
  -> ECS Fargate service in private app subnets
  -> FastAPI + FastMCP app
  -> RDS PostgreSQL in private DB subnets
  -> CloudWatch logs via VPC endpoint
```

## AWS services

| Concern | AWS service |
|---|---|
| Container runtime | ECS Fargate |
| HTTP ingress | Application Load Balancer |
| Database | RDS PostgreSQL |
| Secrets | Secrets Manager or SSM Parameter Store |
| Logs | CloudWatch Logs |
| Private AWS service access | VPC endpoints for ECR, CloudWatch Logs, Secrets Manager, and S3 |
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

## Implemented deployment scope

The current AWS deployment runs the existing service using RDS-backed configuration, CloudWatch logging, private ECS task networking, and VPC endpoints for required AWS-service access.

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
            Logs["CloudWatch Logs<br/>container logs"]
            Secrets["Secrets Manager<br/>runtime secrets"]
            S3["S3<br/>ECR image layers"]
        end

        subgraph VPC["VPC: private network boundary"]

            ALB["Logical Application Load Balancer"]
            Listener["ALB Listener<br/>HTTP/HTTPS"]
            TG["Target Group<br/>registered private task IPs + health state"]

            subgraph PublicA["Public subnet A"]
                ALBNodeA["ALB node / network interface<br/>AZ: eu-west-2a<br/>public-facing IP"]
            end

            subgraph PublicB["Public subnet B"]
                ALBNodeB["ALB node / network interface<br/>AZ: eu-west-2b<br/>public-facing IP"]
            end

            subgraph PrivateAppA["Private app subnet A"]
                TaskA["Fargate task<br/>FastAPI container<br/>AZ: eu-west-2a<br/>private IP only<br/>no public IP"]
            end

            subgraph PrivateAppB["Private app subnet B"]
                TaskB["Fargate task<br/>FastAPI container<br/>AZ: eu-west-2b<br/>private IP only<br/>no public IP"]
            end

            subgraph VPCEndpoints["VPC endpoints for AWS service access"]
                EcrApiVpce["Interface endpoint<br/>ECR API"]
                EcrDkrVpce["Interface endpoint<br/>ECR Docker registry"]
                LogsVpce["Interface endpoint<br/>CloudWatch Logs"]
                SecretsVpce["Interface endpoint<br/>Secrets Manager"]
                S3GatewayVpce["Gateway endpoint<br/>S3 via private app route table"]
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
    TG -->|"healthy private target"| TaskA
    TG -->|"healthy private target"| TaskB

    ECSCluster --> ECSService
    ECSService --> TaskDef
    TaskDef --> ECR
    ECSService -->|"starts/registers private tasks"| TaskA
    ECSService -->|"starts/registers private tasks"| TaskB

    TaskA --> RDS
    TaskB --> RDS

    TaskA -->|"HTTPS 443"| EcrApiVpce
    TaskA -->|"HTTPS 443"| EcrDkrVpce
    TaskA -->|"HTTPS 443"| LogsVpce
    TaskA -->|"HTTPS 443"| SecretsVpce
    TaskA -->|"S3 route"| S3GatewayVpce

    TaskB -->|"HTTPS 443"| EcrApiVpce
    TaskB -->|"HTTPS 443"| EcrDkrVpce
    TaskB -->|"HTTPS 443"| LogsVpce
    TaskB -->|"HTTPS 443"| SecretsVpce
    TaskB -->|"S3 route"| S3GatewayVpce

    EcrApiVpce --> ECR
    EcrDkrVpce --> ECR
    LogsVpce --> Logs
    SecretsVpce --> Secrets
    S3GatewayVpce --> S3
```