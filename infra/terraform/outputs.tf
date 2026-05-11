output "name_prefix" {
  description = "Common resource name prefix."
  value       = local.name_prefix
}

output "ecr_repository_url" {
  description = "ECR repository URL for the application image."
  value       = aws_ecr_repository.app.repository_url
}

output "alb_dns_name" {
  description = "Public DNS name of the application load balancer."
  value       = aws_lb.app.dns_name
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint address."
  value       = aws_db_instance.app.address
}

output "rds_master_user_secret_arn" {
  description = "Secrets Manager ARN for the RDS-managed master user secret."
  value       = aws_db_instance.app.master_user_secret[0].secret_arn
}

output "ecs_cluster_name" {
  description = "ECS cluster name."
  value       = aws_ecs_cluster.app.name
}

output "ecs_task_definition_family" {
  description = "ECS app task definition family."
  value       = aws_ecs_task_definition.app_task_definition.family
}

output "public_subnet_ids" {
  description = "Public subnet IDs used for the first runnable ECS/Fargate deployment."
  value = [
    aws_subnet.public_a.id,
    aws_subnet.public_b.id,
  ]
}

output "app_security_group_id" {
  description = "Security group ID used by the ECS/Fargate app task."
  value       = aws_security_group.app.id
}