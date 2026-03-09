# Operations Runbook — AI Landing V1

## Scope
This runbook covers release/operations for AI Landing V1 flows:
- Client intake request
- Wayl deposit + webhook confirmation
- Clarification loop
- Design approval gate
- Repo/codegen
- Deploy approval gate
- Final payment + domain mapping

## Environments
- Region: `eu-central-1`
- API: `https://api.stuff187.com`
- Web: `https://app.stuff187.com`
- Admin: `https://admin.stuff187.com`

## Pre-release verification (required)
Run from repo root unless noted.

### 1) API full suite
```bash
cd services/api && PYTHONPATH=. .venv/bin/pytest -v
```
Pass criteria: all tests green.

### 2) UI smoke checks
```bash
cd apps/web && python smoke_test.py
cd apps/admin_dashboard && python smoke_test.py
```
Pass criteria: smoke tests green.

### 3) Health check (code-level in current repo tooling)
```bash
cd services/api && PYTHONPATH=. .venv/bin/python - <<'PY'
from app.main import health, root
print('health()', health())
print('root()', root())
PY
```
Pass criteria: `health() {'status': 'ok'}`.

### 4) Deploy gate checks
```bash
cd services/api && PYTHONPATH=. .venv/bin/pytest -v tests/test_deploy_approval_gate.py tests/test_final_payment_handoff.py
```
Pass criteria: all deploy/final-payment gating tests green.

## Release procedure
1. Run the full pre-release verification set above.
2. Confirm `docs/plans/ai-landing-v1-signoff.md` is updated with evidence and status = GO.
3. Trigger GitHub Actions:
   - `API Deploy Dev`
   - `Static Deploy (Web + Admin)`
4. Confirm post-deploy checks:
   - `GET /health` is OK
   - Web/Admin pages load
   - Approval queue and client request form are reachable

## Rollback
### API
- ECS console -> service `blog-mission-control-dev-api`
- Redeploy previous task definition revision
- Validate health endpoint and ALB target health

### Static (web/admin)
- Re-run static deploy workflow using previous known-good commit
- Verify CloudFront deployment and domain behavior

## Launch-critical incident playbook
1. **Payment webhook failures**
   - Check webhook signing secret configuration
   - Confirm signature verification path in `services/api/app/routers/payments.py`
   - Re-test with known signed payload

2. **Approval queue empty/unexpected**
   - Confirm project state is one of expected gate states
   - Validate admin role and endpoint access

3. **Domain mapping blocked**
   - Expected unless final payment is completed
   - Verify final payment status before forcing retries

## Known non-launch-critical items
- Deprecation warnings from `datetime.utcnow()` and pydantic class config appear in tests; these are non-blocking for V1 launch and tracked for cleanup.