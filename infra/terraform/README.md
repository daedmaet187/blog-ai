# Terraform (AWS)

## Dev bootstrap (OpenTofu)
```bash
cd infra/terraform/envs/dev
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars (db_password)
tofu init
tofu plan
tofu apply
```

## Notes
- Region: eu-central-1
- Provisioned: VPC, ECS (API), ALB, RDS Postgres, ElastiCache Redis, ECR
- This is a practical starter; hardening (WAF, ACM, Route53 records, backups, alarms) is next.
