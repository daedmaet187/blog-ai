output "alb_dns_name" { value = aws_lb.this.dns_name }
output "ecs_cluster_name" { value = aws_ecs_cluster.this.name }
output "ecs_service_name" { value = aws_ecs_service.api.name }
output "ecs_service_sg_id" { value = aws_security_group.ecs.id }
