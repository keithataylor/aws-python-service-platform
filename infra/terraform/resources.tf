resource "aws_ecr_repository" "app" {
  name = "${local.name_prefix}-app"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.common_tags
}

resource "aws_ecs_cluster" "app" {
  name = "${local.name_prefix}-cluster"

  tags = local.common_tags
}