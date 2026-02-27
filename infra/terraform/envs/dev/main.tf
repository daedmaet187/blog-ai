terraform {
  required_version = ">= 1.6.0"

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

locals {
  project = "blog-mission-control"
  env     = "dev"
  name    = "${local.project}-${local.env}"

  tags = {
    Project     = local.project
    Environment = local.env
    ManagedBy   = "terraform"
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
  tags               = local.tags
}

module "db" {
  source             = "../../modules/db"
  name               = local.name
  vpc_id             = module.network.vpc_id
  private_subnet_ids = module.network.private_subnet_ids
  app_sg_id          = module.ecs_api.ecs_service_sg_id
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
  app_sg_id          = module.ecs_api.ecs_service_sg_id
  node_type          = var.redis_node_type
  tags               = local.tags
}
