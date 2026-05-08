resource "aws_db_instance" "app" {
  identifier = "${local.short_name_prefix}-postgres"

  engine         = "postgres"
  engine_version = "16"
  instance_class = "db.t4g.micro"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = "app_db"
  username = "app_user"

  manage_master_user_password = true

  db_subnet_group_name = aws_db_subnet_group.app.name

  vpc_security_group_ids = [
    aws_security_group.db.id,
  ]

  publicly_accessible = false
  multi_az            = false

  backup_retention_period = 1
  deletion_protection     = false
  skip_final_snapshot     = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-postgres"
  })
}