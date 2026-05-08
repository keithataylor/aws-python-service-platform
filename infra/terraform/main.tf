locals {
  name_prefix       = "${var.project_name}-${var.environment}"
  short_name_prefix = "aspsp-${var.environment}"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}