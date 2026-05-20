resource "aws_security_group" "alb" {
  name        = "${local.name_prefix}-alb-sg"
  description = "Allow public HTTP traffic to the application load balancer."
  vpc_id      = aws_vpc.app.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alb-sg"
  })
}

resource "aws_security_group" "app" {
  name        = "${local.name_prefix}-app-sg"
  description = "Allow ALB traffic to the ECS/Fargate application tasks."
  vpc_id      = aws_vpc.app.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-app-sg"
  })
}

resource "aws_security_group" "db" {
  name        = "${local.name_prefix}-db-sg"
  description = "Allow PostgreSQL traffic from the ECS/Fargate application tasks."
  vpc_id      = aws_vpc.app.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-sg"
  })
}

resource "aws_security_group" "aws_service_interface_endpoints" {
  name        = "${local.name_prefix}-aws-service-endpoints-sg"
  description = "Allow private app tasks to reach AWS service interface endpoints."
  vpc_id      = aws_vpc.app.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-aws-service-endpoints-sg"
  })
}

resource "aws_vpc_security_group_ingress_rule" "aws_service_interface_endpoints_from_app_tasks" {
  security_group_id = aws_security_group.aws_service_interface_endpoints.id
  description       = "Allow app tasks to connect to AWS service interface endpoints over HTTPS."

  referenced_security_group_id = aws_security_group.app.id
  ip_protocol                  = "tcp"
  from_port                    = 443
  to_port                      = 443
}

resource "aws_vpc_security_group_ingress_rule" "alb_http_from_internet" {
  security_group_id = aws_security_group.alb.id
  description       = "Allow HTTP traffic from the internet to the ALB."

  cidr_ipv4   = "0.0.0.0/0"
  ip_protocol = "tcp"
  from_port   = 80
  to_port     = 80
}

resource "aws_vpc_security_group_egress_rule" "alb_to_app" {
  security_group_id = aws_security_group.alb.id
  description       = "Allow ALB to forward traffic to the app tasks."

  referenced_security_group_id = aws_security_group.app.id
  ip_protocol                  = "tcp"
  from_port                    = 8000
  to_port                      = 8000
}

resource "aws_vpc_security_group_ingress_rule" "app_from_alb" {
  security_group_id = aws_security_group.app.id
  description       = "Allow app traffic from the ALB."

  referenced_security_group_id = aws_security_group.alb.id
  ip_protocol                  = "tcp"
  from_port                    = 8000
  to_port                      = 8000
}

resource "aws_vpc_security_group_egress_rule" "app_to_db" {
  security_group_id = aws_security_group.app.id
  description       = "Allow app tasks to connect to PostgreSQL."

  referenced_security_group_id = aws_security_group.db.id
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
}

resource "aws_vpc_security_group_ingress_rule" "db_from_app" {
  security_group_id = aws_security_group.db.id
  description       = "Allow PostgreSQL traffic from app tasks."

  referenced_security_group_id = aws_security_group.app.id
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
}

resource "aws_vpc_security_group_egress_rule" "app_to_aws_service_interface_endpoints" {
  security_group_id = aws_security_group.app.id
  description       = "Allow app tasks to reach AWS service interface endpoints over HTTPS."

  referenced_security_group_id = aws_security_group.aws_service_interface_endpoints.id
  ip_protocol                  = "tcp"
  from_port                    = 443
  to_port                      = 443
}

resource "aws_vpc_security_group_egress_rule" "app_to_s3_gateway_endpoint" {
  security_group_id = aws_security_group.app.id
  description       = "Allow app tasks to reach S3 through the private app S3 gateway endpoint."

  prefix_list_id = aws_vpc_endpoint.s3_gateway_for_private_app_route_table.prefix_list_id
  ip_protocol    = "tcp"
  from_port      = 443
  to_port        = 443
}