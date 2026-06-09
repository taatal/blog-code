variable "aws_region" {
  type    = string
  default = "eu-west-1"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID for the ECS service and ALB"
}

variable "public_subnet_ids" {
  type        = list(string)
  description = "Public subnets for the ALB"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "Private subnets for ECS tasks"
}

variable "certificate_arn" {
  type        = string
  description = "ACM certificate ARN for HTTPS"
}

variable "ecr_repository_url" {
  type        = string
  description = "ECR repository URL (without tag)"
}

variable "github_repo" {
  type        = string
  description = "GitHub repository in format org/repo"
}
