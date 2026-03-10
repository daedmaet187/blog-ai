variable "project_slug" {
  description = "Global project slug for platform resources"
  type        = string
  default     = "siteforge-platform"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-central-1"
}

variable "vpc_cidr" {
  type    = string
  default = "10.30.0.0/16"
}

variable "public_subnet_cidrs" {
  type    = list(string)
  default = ["10.30.1.0/24", "10.30.2.0/24"]
}

variable "private_subnet_cidrs" {
  type    = list(string)
  default = ["10.30.11.0/24", "10.30.12.0/24"]
}

variable "azs" {
  type    = list(string)
  default = ["eu-central-1a", "eu-central-1b"]
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.micro"
}

variable "db_name" {
  type    = string
  default = "siteforgedb"
}

variable "db_username" {
  type    = string
  default = "siteforgeadmin"
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "redis_node_type" {
  type    = string
  default = "cache.t4g.micro"
}

variable "client_app_origin" {
  description = "Origin for client portal"
  type        = string
  default     = "https://platform.stuff187.com"
}

variable "admin_app_origin" {
  description = "Origin for admin console"
  type        = string
  default     = "https://admin-platform.stuff187.com"
}
