resource "aws_vpc" "app" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-vpc"
  })
}

resource "aws_internet_gateway" "app" {
  vpc_id = aws_vpc.app.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-igw"
  })
}

resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.app.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "eu-west-2a"
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-public-a"
    Tier = "public"
  })
}

resource "aws_subnet" "public_b" {
  vpc_id                  = aws_vpc.app.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "eu-west-2b"
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-public-b"
    Tier = "public"
  })
}

resource "aws_subnet" "private_app_a" {
  vpc_id            = aws_vpc.app.id
  cidr_block        = "10.0.11.0/24"
  availability_zone = "eu-west-2a"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-private-app-a"
    Tier = "private-app"
  })
}

resource "aws_subnet" "private_app_b" {
  vpc_id            = aws_vpc.app.id
  cidr_block        = "10.0.12.0/24"
  availability_zone = "eu-west-2b"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-private-app-b"
    Tier = "private-app"
  })
}

resource "aws_subnet" "private_db_a" {
  vpc_id            = aws_vpc.app.id
  cidr_block        = "10.0.21.0/24"
  availability_zone = "eu-west-2a"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-private-db-a"
    Tier = "private-db"
  })
}

resource "aws_subnet" "private_db_b" {
  vpc_id            = aws_vpc.app.id
  cidr_block        = "10.0.22.0/24"
  availability_zone = "eu-west-2b"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-private-db-b"
    Tier = "private-db"
  })
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.app.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-public-rt"
  })
}

resource "aws_route" "public_internet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.app.id
}

resource "aws_route_table_association" "public_a" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_b" {
  subnet_id      = aws_subnet.public_b.id
  route_table_id = aws_route_table.public.id
}

resource "aws_db_subnet_group" "app" {
  name = "${local.name_prefix}-db-subnet-group"

  subnet_ids = [
    aws_subnet.private_db_a.id,
    aws_subnet.private_db_b.id,
  ]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-subnet-group"
  })
}