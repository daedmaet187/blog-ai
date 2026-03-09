variable "name" { type = string }
variable "cluster_name" { type = string }
variable "vpc_id" { type = string }
variable "public_subnet_ids" { type = list(string) }
variable "private_subnet_ids" { type = list(string) }
variable "container_port" { type = number }
variable "image_uri" { type = string }
variable "aws_region" { type = string }
variable "environment" {
  type    = map(string)
  default = {}
}

variable "secrets" {
  type    = map(string)
  default = {}
}

variable "task_policy_json" {
  type    = string
  default = null
}

variable "tags" { type = map(string) }
