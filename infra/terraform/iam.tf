# This file defines IAM roles and policies for the ECS tasks, 
# including the execution role and task role.

# The trust policy allows ECS tasks to assume the roles defined in this file.
data "aws_iam_policy_document" "ecs_task_trust_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

# Execution role is used by ECS/Fargate infrastructure to pull the image,
# send logs, and inject secrets before the app container starts.
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${local.short_name_prefix}-ecs-execution-role"

  assume_role_policy = data.aws_iam_policy_document.ecs_task_trust_policy.json

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ecs-execution-role"
  })
}

# This is the AWS-managed policy that grants permissions for ECS task execution.
resource "aws_iam_role_policy_attachment" "ecs_task_execution_managed" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# This policy grants permissions for the ECS task execution role to read secrets from Secrets Manager.
data "aws_iam_policy_document" "ecs_task_execution_secrets_policy_doc" {
  statement {
    sid = "AllowReadRequiredSecrets"

    actions = [
      "secretsmanager:GetSecretValue",
    ]

    resources = [
      aws_db_instance.app.master_user_secret[0].secret_arn,
      var.agent_credential_hash_secret_arn,
    ]
  }
}

# This policy is attached to the ECS task execution role to allow it to read secrets from Secrets Manager.
resource "aws_iam_role_policy" "ecs_task_execution_secrets_policy" {
  name   = "${local.short_name_prefix}-ecs-secrets-access"
  role   = aws_iam_role.ecs_task_execution_role.id
  policy = data.aws_iam_policy_document.ecs_task_execution_secrets_policy_doc.json
}

# Task role is for AWS permissions used by the running app code.
# It is intentionally permissionless for now.
resource "aws_iam_role" "ecs_task_role" {
  name = "${local.short_name_prefix}-ecs-task-role"

  assume_role_policy = data.aws_iam_policy_document.ecs_task_trust_policy.json

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ecs-task-role"
  })
}