# Blog Mission Control (AWS)

Monorepo for:
- Flutter mobile app
- Public website
- Admin dashboard
- Backend API
- Shared packages
- AWS infrastructure (OpenTofu)

## Architecture (v1)
- Compute: ECS Fargate
- DB: RDS PostgreSQL
- Cache: ElastiCache Redis
- Storage: S3
- CDN: CloudFront
- Ingress: ALB
- Secrets: AWS Secrets Manager / SSM
- CI/CD: GitHub Actions + ECR + ECS deploy

## Repo layout
- `apps/mobile_flutter` - Flutter app
- `apps/web` - Public web app
- `apps/admin_dashboard` - Admin web app
- `services/api` - Backend API
- `packages/shared` - Shared contracts/types
- `infra/opentofu` - AWS IaC (OpenTofu configs; legacy folder name)
- `docs` - Product and technical docs

## Next steps
1. Confirm AWS region + domain.
2. Bootstrap backend service.
3. Bootstrap Flutter + web apps.
4. Provision AWS dev environment with OpenTofu.
5. Add CI/CD pipelines.
