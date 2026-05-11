resource "aws_ecs_service" "app_service" {
  name            = "${local.short_name_prefix}-app-service"
  cluster         = aws_ecs_cluster.app.id
  task_definition = aws_ecs_task_definition.app_task_definition.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  platform_version = "LATEST"

  health_check_grace_period_seconds = 60

  network_configuration {
    subnets = [
      aws_subnet.public_a.id,
      aws_subnet.public_b.id,
    ]

    security_groups = [
      aws_security_group.app.id,
    ]

    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "app"
    container_port   = 8000
  }

  depends_on = [
    aws_lb_listener.http,
  ]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-app-service"
  })
}