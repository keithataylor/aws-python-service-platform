data "aws_region" "current" {}

resource "aws_vpc_endpoint" "ecr_api_interface" {
  vpc_id              = aws_vpc.app.id
  service_name        = "com.amazonaws.${data.aws_region.current.region}.ecr.api"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true

  subnet_ids = [
    aws_subnet.private_app_a.id,
    aws_subnet.private_app_b.id,
  ]

  security_group_ids = [
    aws_security_group.aws_service_interface_endpoints.id,
  ]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ecr-api-endpoint"
  })
}

resource "aws_vpc_endpoint" "ecr_docker_registry_interface" {
  vpc_id              = aws_vpc.app.id
  service_name        = "com.amazonaws.${data.aws_region.current.region}.ecr.dkr"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true

  subnet_ids = [
    aws_subnet.private_app_a.id,
    aws_subnet.private_app_b.id,
  ]

  security_group_ids = [
    aws_security_group.aws_service_interface_endpoints.id,
  ]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ecr-dkr-endpoint"
  })
}

resource "aws_vpc_endpoint" "cloudwatch_logs_interface" {
  vpc_id              = aws_vpc.app.id
  service_name        = "com.amazonaws.${data.aws_region.current.region}.logs"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true

  subnet_ids = [
    aws_subnet.private_app_a.id,
    aws_subnet.private_app_b.id,
  ]

  security_group_ids = [
    aws_security_group.aws_service_interface_endpoints.id,
  ]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-logs-endpoint"
  })
}

resource "aws_vpc_endpoint" "secrets_manager_interface" {
  vpc_id              = aws_vpc.app.id
  service_name        = "com.amazonaws.${data.aws_region.current.region}.secretsmanager"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true

  subnet_ids = [
    aws_subnet.private_app_a.id,
    aws_subnet.private_app_b.id,
  ]

  security_group_ids = [
    aws_security_group.aws_service_interface_endpoints.id,
  ]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-secretsmanager-endpoint"
  })
}

resource "aws_vpc_endpoint" "s3_gateway_for_private_app_route_table" {
  vpc_id            = aws_vpc.app.id
  service_name      = "com.amazonaws.${data.aws_region.current.region}.s3"
  vpc_endpoint_type = "Gateway"

  route_table_ids = [
    aws_route_table.private_app_subnets.id,
  ]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-s3-gateway-endpoint"
  })
}