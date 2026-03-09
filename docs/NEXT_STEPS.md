# Immediate Next Steps

## 1) GitHub repo setup
- Push this monorepo to GitHub.
- Add repo secret: `AWS_GITHUB_ROLE_ARN`.
- Configure OIDC IAM role trust for GitHub Actions.

## 2) OpenTofu apply (dev)
- `cd infra/terraform/envs/dev` (OpenTofu config path; folder name kept for compatibility)
- `cp terraform.tfvars.example terraform.tfvars`
- set strong `db_password`
- `tofu init && tofu apply`

## 3) Build + push first API image
- Trigger `API Deploy Dev` workflow (or push to main).
- Verify ECS service health and ALB `/health`.

## 4) Domain wiring
- Route53 hosted zone for `stuff187.com`.
- Add `api.stuff187.com` (ALB), `app.stuff187.com`, `admin.stuff187.com`.
- Add ACM cert + HTTPS listener.

## 5) Product sprint kickoff
- Implement auth and posts APIs in FastAPI.
- Build first vertical slice: create post (admin) -> read post (web/mobile).
