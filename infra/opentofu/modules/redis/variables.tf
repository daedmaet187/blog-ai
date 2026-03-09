variable "name" { type = string }
variable "vpc_id" { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "app_cidr" { type = string }
variable "node_type" { type = string }
variable "tags" { type = map(string) }
