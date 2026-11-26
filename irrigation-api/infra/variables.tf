# AWS deployment region
variable "aws_region" {
  type        = string
  description = "AWS region for infrastructure resources"
  default     = "eu-central-1"
}

# Target environment ("prod" or "acc")
variable "environment" {
  type        = string
  description = "Deployment environment name"
  default     = "prod"
}

# Base project name for IAM naming
variable "project_name" {
  type        = string
  description = "Project prefix for IAM resources"
  default     = "smart-irrigation"
}

# Frontend S3 bucket name (supplied via terraform.tfvars)
variable "frontend_bucket_name" {
  type        = string
  description = "S3 bucket name hosting static frontend files"
}

# [CORS] Allowed browser origins for API Gateway and Lambda
variable "cors_origins" {
  type        = list(string)
  description = "List of allowed CORS origins without trailing slashes"
  default     = []
}

# Path to packaged Lambda deployment zip archive
variable "lambda_zip_path" {
  type        = string
  description = "Path to Lambda deployment zip file"
  default     = "../aws_deploy/lambda.zip"
}