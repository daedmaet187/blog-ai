terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "registry.opentofu.org/hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  project = "blog-mission-control"
  env     = "dev"
  name    = "${local.project}-${local.env}"

  db_url    = "postgresql://${var.db_username}:${var.db_password}@${module.db.db_endpoint}:5432/${var.db_name}"
  redis_url = "redis://${module.redis.redis_endpoint}:6379"

  tags = {
    Project     = local.project
    Environment = local.env
    ManagedBy   = "opentofu"
  }
}

resource "aws_ecr_repository" "api" {
  name                 = "${local.project}-api-${local.env}"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  tags                 = local.tags
}

module "network" {
  source               = "../../modules/network"
  name                 = local.name
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  azs                  = var.azs
  tags                 = local.tags
}

module "ecs_api" {
  source             = "../../modules/ecs_api"
  name               = local.name
  cluster_name       = local.name
  vpc_id             = module.network.vpc_id
  public_subnet_ids  = module.network.public_subnet_ids
  private_subnet_ids = module.network.private_subnet_ids
  container_port     = 8000
  image_uri          = "${aws_ecr_repository.api.repository_url}:latest"
  aws_region         = var.aws_region
  environment = {
    APP_ENV      = "dev"
    AWS_REGION   = var.aws_region
    MEDIA_BUCKET = aws_s3_bucket.media.bucket
  }
  secrets = {
    DATABASE_URL = aws_ssm_parameter.database_url.arn
    REDIS_URL    = aws_ssm_parameter.redis_url.arn
  }
  task_policy_json = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:PutObject", "s3:GetObject"]
        Resource = ["${aws_s3_bucket.media.arn}/*"]
      }
    ]
  })
  tags = local.tags
}

module "db" {
  source             = "../../modules/db"
  name               = local.name
  vpc_id             = module.network.vpc_id
  private_subnet_ids = module.network.private_subnet_ids
  app_cidr           = var.vpc_cidr
  instance_class     = var.db_instance_class
  db_name            = var.db_name
  db_username        = var.db_username
  db_password        = var.db_password
  tags               = local.tags
}

module "redis" {
  source             = "../../modules/redis"
  name               = local.name
  vpc_id             = module.network.vpc_id
  private_subnet_ids = module.network.private_subnet_ids
  app_cidr           = var.vpc_cidr
  node_type          = var.redis_node_type
  tags               = local.tags
}

resource "aws_ssm_parameter" "database_url" {
  name      = "/${local.name}/DATABASE_URL"
  type      = "SecureString"
  value     = local.db_url
  overwrite = true
  tags      = local.tags
}

resource "aws_ssm_parameter" "redis_url" {
  name      = "/${local.name}/REDIS_URL"
  type      = "SecureString"
  value     = local.redis_url
  overwrite = true
  tags      = local.tags
}

resource "aws_s3_bucket" "media" {
  bucket        = "${local.name}-media"
  force_destroy = true
  tags          = local.tags
}

resource "aws_s3_bucket_public_access_block" "media" {
  bucket = aws_s3_bucket.media.id

  block_public_acls       = false
  ignore_public_acls      = false
  block_public_policy     = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_cors_configuration" "media" {
  bucket = aws_s3_bucket.media.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["PUT", "GET", "HEAD"]
    allowed_origins = ["https://admin.stuff187.com", "https://app.stuff187.com"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

resource "aws_s3_bucket_policy" "media_public_read" {
  bucket = aws_s3_bucket.media.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = ["s3:GetObject"]
        Resource  = ["${aws_s3_bucket.media.arn}/*"]
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.media]
}
