# CI/CD Pipeline: GitHub Actions to AWS with Canary Deploys

A production CI/CD pipeline that deploys a containerised application to ECS Fargate with canary traffic shifting, automated rollback, and Slack notifications.

Full walkthrough: [Build a CI/CD Pipeline From Scratch](https://digital.taatal.com/blogs/build-cicd-pipeline-from-scratch)

## What this sets up

- GitHub Actions workflow (test, build, deploy)
- Docker image pushed to Amazon ECR, tagged by commit SHA
- ECS Fargate service behind an Application Load Balancer
- Canary deployments (10% traffic for 5 minutes, then full rollout)
- Automatic rollback on CloudWatch alarm (5xx rate > 5%)
- Slack notifications on build, deploy success, and failure
- OIDC authentication (no static AWS credentials)

## Prerequisites

- AWS account with permissions for ECS, ALB, CodeDeploy, IAM
- Terraform 1.5+
- AWS CLI configured
- Docker installed
- A GitHub repository with a containerised application

## Setup

1. Copy the variables file:

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

2. Edit `terraform.tfvars` with your VPC, subnet, and certificate details.

3. Initialize and apply:

```bash
terraform init
terraform plan
terraform apply
```

4. Add these secrets to your GitHub repository:
   - `AWS_DEPLOY_ROLE_ARN` - The ARN of the `api-github-deploy` IAM role created by Terraform
   - `SLACK_WEBHOOK` - Your Slack incoming webhook URL

5. Copy `.github/workflows/deploy.yml` to your application repository.

## Architecture

```
git push -> GitHub Actions (test + build) -> ECR -> CodeDeploy (canary) -> ECS Fargate
                                                         |
                                              CloudWatch alarm -> auto rollback
```

## Cost

Approximately $85/month for the running infrastructure (ECS Fargate 3 tasks + ALB + ECR + CloudWatch). GitHub Actions and CodeDeploy are free at this usage level.

## Deployment flow

1. Push to `main`
2. Tests and lint run
3. Docker image builds and pushes to ECR
4. CodeDeploy shifts 10% traffic to new version
5. 5-minute monitoring window
6. If healthy: remaining 90% shifts over (~12 min total)
7. If alarm fires: immediate rollback (~30 seconds)
