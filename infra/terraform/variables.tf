variable "aws_region" {
  description = "AWS region used for the deployment."
  type        = string
  default     = "eu-west-2"
}

variable "project_name" {
  description = "Project name used for resource naming and tags."
  type        = string
  default     = "aws-python-service-platform"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"
}

variable "agent_credential_hash_secret_arn" {
  description = "ARN of the existing Secrets Manager secret containing AGENT_CREDENTIAL_HASH_SECRET."
  type        = string
}