# Operations Runbook

## Environments
- Region: `eu-central-1`
- API: `https://api.stuff187.com`
- Web: `https://app.stuff187.com`
- Admin: `https://admin.stuff187.com`

## Deploy
### API
1. GitHub Actions -> `API Deploy Dev`
2. Wait for ECS service stability
3. Verify `GET /health`

### Static (web/admin)
1. GitHub Actions -> `Static Deploy (Web + Admin)`
2. Verify web/admin pages load

## Rollback API
- ECS console -> service `blog-mission-control-dev-api`
- Deploy previous task definition revision
- Confirm target health returns healthy

## Health checks
- `curl https://api.stuff187.com/health`
- ALB target group healthy count in AWS console

## Alerts configured
- `blog-dev-alb-5xx` (ALB 5xx >= 5/5m)
- `blog-dev-target-unhealthy` (unhealthy targets >= 1)

## Common failure quick fixes
1. **CORS error in browser**
   - ensure allowed origins in `services/api/app/main.py`
   - redeploy API

2. **ECS deploy timeout**
   - check stopped task logs in CloudWatch `/ecs/blog-mission-control-dev-api`
   - fix runtime error and redeploy

3. **HTTPS app/admin not loading**
   - verify CloudFront distribution status is `Deployed`
   - verify Cloudflare CNAME points to CloudFront domains

## RDS backup note
- Current config uses default backup settings for dev.
- Before production: set explicit retention window + snapshot strategy.
