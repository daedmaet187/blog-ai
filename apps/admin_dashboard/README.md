# Admin Dashboard

Minimal static MVP admin dashboard connected to `https://api.stuff187.com`.

## V1 critical flows
- Login
- Approval queue for design/deploy (`/admin/projects/approval-queue`)
- Approve/reject design (`/admin/projects/{id}/design/{approve|reject}`)
- Approve/reject deploy (`/admin/projects/{id}/deploy/{approve|reject}`)

## Smoke check
```bash
cd apps/admin_dashboard && python smoke_test.py
```
