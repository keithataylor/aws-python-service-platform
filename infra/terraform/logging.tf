resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/ecs/${local.name_prefix}-app"
  retention_in_days = 7

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-app-logs"
  })
}

