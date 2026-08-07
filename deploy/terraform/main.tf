# Terraform Infrastructure as Code for AI Visibility Operating System (AWS)
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default = "us-east-1"
}

variable "environment" {
  default = "production"
}

# 1. Virtual Private Cloud (VPC)
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "ai-visibility-vpc-${var.environment}"
    Environment = var.environment
  }
}

# 2. Subnets
resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true
}

resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.10.0/24"
  availability_zone = "${var.aws_region}a"
}

# 3. Security Groups
resource "aws_security_group" "alb_sg" {
  name        = "ai-visibility-alb-sg"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 4. Managed RDS PostgreSQL 16 Instance
resource "aws_db_instance" "postgres" {
  allocated_storage       = 50
  max_allocated_storage   = 200
  engine                  = "postgres"
  engine_version          = "16.1"
  instance_class          = "db.r6g.large"
  db_name                 = "aivisibility"
  username                = "postgres_admin"
  password                = "ManagedPasswordSecretFromSecretsManager"
  skip_final_snapshot     = false
  backup_retention_period = 30
  multi_az                = true
}

# 5. Managed ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "ai-visibility-redis"
  engine               = "redis"
  node_type            = "cache.t4g.medium"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
}

# 6. S3 Artifact Storage
resource "aws_s3_bucket" "artifacts" {
  bucket = "ai-visibility-artifacts-${var.environment}"
}
