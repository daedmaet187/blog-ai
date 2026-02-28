output "api_ecr_repository_url" {
  value = aws_ecr_repository.api.repository_url
}

output "alb_dns_name" {
  value = module.ecs_api.alb_dns_name
}

output "ecs_cluster_name" {
  value = module.ecs_api.ecs_cluster_name
}

output "ecs_service_name" {
  value = module.ecs_api.ecs_service_name
}

output "db_endpoint" {
  value = module.db.db_endpoint
}

output "redis_endpoint" {
  value = module.redis.redis_endpoint
}

output "media_bucket" {
  value = aws_s3_bucket.media.bucket
}
