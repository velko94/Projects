# Terraform CLI and AWS provider version constraints
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# AWS provider configured with local CLI credentials/profile
provider "aws" {
  region = var.aws_region
}