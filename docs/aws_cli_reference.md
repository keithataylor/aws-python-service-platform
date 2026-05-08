# AWS CLI Reference

## Purpose

This document lists the AWS CLI commands used to inspect and support the local-to-AWS deployment path for `aws-python-service-platform`.

The main deployment flow is:

```text
Dockerfile
  -> local Docker image
  -> ECR repository
  -> ECS/Fargate service
  -> ALB
  -> RDS PostgreSQL
  -> CloudWatch logs
```

Terraform creates the AWS infrastructure. The AWS CLI is used for authentication checks, ECR login, and operational inspection.

---

## Confirm current AWS identity

Check which AWS account and identity the local machine is currently using.

```powershell
aws sts get-caller-identity
```

Show the active AWS CLI configuration, including region, profile, and credential source.

```powershell
aws configure list
```

---

## Authenticate Docker to ECR

Authenticate the local Docker client to the AWS ECR registry.

```powershell
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 702630738731.dkr.ecr.eu-west-2.amazonaws.com
```

This does not push an image. It only allows Docker to push to the ECR registry.

---

## Check ECR repository

Confirm that the ECR repository exists.

```powershell
aws ecr describe-repositories --region eu-west-2 --repository-names aws-python-service-platform-dev-app
```

List image tags/digests currently stored in the ECR repository.

```powershell
aws ecr list-images --region eu-west-2 --repository-name aws-python-service-platform-dev-app
```

Show detailed metadata for images in the ECR repository.

```powershell
aws ecr describe-images --region eu-west-2 --repository-name aws-python-service-platform-dev-app
```

---

## Push local Docker image to ECR

Tag the local image with the ECR repository URL.

```powershell
docker tag aws-python-service-platform:local 702630738731.dkr.ecr.eu-west-2.amazonaws.com/aws-python-service-platform-dev-app:latest
```

Push the tagged image to ECR.

```powershell
docker push 702630738731.dkr.ecr.eu-west-2.amazonaws.com/aws-python-service-platform-dev-app:latest
```

Verify that the image is now present in ECR.

```powershell
aws ecr list-images --region eu-west-2 --repository-name aws-python-service-platform-dev-app
```

---

## Check ECS resources

List ECS clusters in the target region.

```powershell
aws ecs list-clusters --region eu-west-2
```

Describe a specific ECS cluster.

```powershell
aws ecs describe-clusters --region eu-west-2 --clusters <cluster-name>
```

List ECS services in a cluster.

```powershell
aws ecs list-services --region eu-west-2 --cluster <cluster-name>
```

Describe a specific ECS service.

```powershell
aws ecs describe-services --region eu-west-2 --cluster <cluster-name> --services <service-name>
```

List running tasks for a service.

```powershell
aws ecs list-tasks --region eu-west-2 --cluster <cluster-name> --service-name <service-name>
```

Describe a specific ECS task.

```powershell
aws ecs describe-tasks --region eu-west-2 --cluster <cluster-name> --tasks <task-arn>
```

---

## Check Application Load Balancer resources

List load balancers.

```powershell
aws elbv2 describe-load-balancers --region eu-west-2
```

List target groups.

```powershell
aws elbv2 describe-target-groups --region eu-west-2
```

Check target health for an ALB target group.

```powershell
aws elbv2 describe-target-health --region eu-west-2 --target-group-arn <target-group-arn>
```

---

## Check RDS resources

List RDS database instances.

```powershell
aws rds describe-db-instances --region eu-west-2
```

Describe a specific RDS database instance.

```powershell
aws rds describe-db-instances --region eu-west-2 --db-instance-identifier <db-instance-id>
```

---

## Check Secrets Manager resources

List Secrets Manager secrets.

```powershell
aws secretsmanager list-secrets --region eu-west-2
```

Describe a specific secret without printing the secret value.

```powershell
aws secretsmanager describe-secret --region eu-west-2 --secret-id <secret-name-or-arn>
```

---

## Check CloudWatch logs

List CloudWatch log groups.

```powershell
aws logs describe-log-groups --region eu-west-2
```

Stream logs from a specific log group.

```powershell
aws logs tail <log-group-name> --region eu-west-2 --follow
```

---

## Immediate ECR image push sequence

Use this sequence after Terraform has created the ECR repository.

```powershell
aws sts get-caller-identity
```

```powershell
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 702630738731.dkr.ecr.eu-west-2.amazonaws.com
```

```powershell
docker tag aws-python-service-platform:local 702630738731.dkr.ecr.eu-west-2.amazonaws.com/aws-python-service-platform-dev-app:latest
```

```powershell
docker push 702630738731.dkr.ecr.eu-west-2.amazonaws.com/aws-python-service-platform-dev-app:latest
```

```powershell
aws ecr list-images --region eu-west-2 --repository-name aws-python-service-platform-dev-app
```