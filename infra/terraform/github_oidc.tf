# GitHub Actions OIDC identity provider and limited ECS deployment role.
#
# This role is for application deployment only:
# - push Docker images to ECR
# - register a new ECS task definition revision
# - update the existing ECS service
#
# It is intentionally separate from the ECS task roles and from human Terraform admin access.

resource "aws_iam_openid_connect_provider" "github_actions" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com",
  ]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-github-actions-oidc"
  })
}

data "aws_iam_policy_document" "github_actions_deploy_trust_policy" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type = "Federated"
      identifiers = [
        aws_iam_openid_connect_provider.github_actions.arn,
      ]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values = [
        "repo:keithataylor/aws-python-service-platform:ref:refs/heads/main",
      ]
    }
  }
}

resource "aws_iam_role" "github_actions_ecs_deploy_role" {
  name = "${local.short_name_prefix}-github-ecs-deploy-role"

  assume_role_policy = data.aws_iam_policy_document.github_actions_deploy_trust_policy.json

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-github-ecs-deploy-role"
  })
}

data "aws_iam_policy_document" "github_actions_ecs_deploy_policy_doc" {
  statement {
    sid = "AllowEcrLogin"

    actions = [
      "ecr:GetAuthorizationToken",
    ]

    resources = ["*"]
  }

  statement {
    sid = "AllowPushToAppRepository"

    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart",
    ]

    resources = [
      aws_ecr_repository.app.arn,
    ]
  }

  statement {
    sid = "AllowRegisterAndReadTaskDefinitions"

    actions = [
      "ecs:DescribeTaskDefinition",
      "ecs:RegisterTaskDefinition",
    ]

    resources = ["*"]
  }

  statement {
    sid = "AllowUpdateAppService"

    actions = [
      "ecs:DescribeServices",
      "ecs:UpdateService",
    ]

    resources = [
      aws_ecs_service.app_service.id,
    ]
  }

  statement {
    sid = "AllowPassOnlyEcsTaskRoles"

    actions = [
      "iam:PassRole",
    ]

    resources = [
      aws_iam_role.ecs_task_execution_role.arn,
      aws_iam_role.ecs_task_role.arn,
    ]

    condition {
      test     = "StringEquals"
      variable = "iam:PassedToService"
      values   = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "github_actions_ecs_deploy_policy" {
  name   = "${local.short_name_prefix}-github-ecs-deploy"
  role   = aws_iam_role.github_actions_ecs_deploy_role.id
  policy = data.aws_iam_policy_document.github_actions_ecs_deploy_policy_doc.json
}