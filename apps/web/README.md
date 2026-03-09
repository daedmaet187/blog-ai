# Client Portal (Web)

Minimal static MVP client portal connected to `https://api.stuff187.com`.

## V1 critical flows
- Login
- Submit project request (`/projects/requests`)
- Clarification inbox (`/projects/{id}/clarification/start`, `/projects/{id}/clarification/answers`)
- Project timeline / status from project state

## Smoke check
```bash
cd apps/web && python smoke_test.py
```
