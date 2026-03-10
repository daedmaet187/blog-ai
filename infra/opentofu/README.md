# OpenTofu (AWS)

## Legacy blog environment (existing)
```bash
cd infra/opentofu/envs/dev
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars (db_password)
tofu init
tofu plan
tofu apply
```

## New isolated platform environment (recommended)
```bash
cd infra/opentofu/envs/platform-dev
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars (db_password + origins)
tofu init
tofu plan
tofu apply
```

## Notes
- Region: eu-central-1
- Provisioned: VPC, ECS (API), ALB, RDS Postgres, ElastiCache Redis, ECR
- `envs/platform-dev` is isolated and does not reuse blog-specific naming.
- This is a practical starter; hardening (WAF, ACM, Route53 records, backups, alarms) is next.
