# Mission Control

## Project
- Name: Blog Mission Control
- Region: eu-central-1
- Domain: stuff187.com
- Backend: FastAPI

## Lanes
1. Product/Architect
2. Backend
3. Frontend (Web + Admin)
4. Mobile (Flutter)
5. DevOps/Infra

## Workflow
- Backlog state: `todo -> active -> review -> done`
- Every task must include:
  - Goal
  - Acceptance criteria
  - Owner lane
  - Dependencies

## Model Routing Policy
- Architecture & planning: strong reasoning model
- Coding/refactor: codex
- QA/review: second-pass model
- Docs/changelog: fast low-cost model

## Delivery Gates
No prod release without:
1. Lint + tests pass
2. API contract checks pass
3. Staging deploy healthy
4. Human approval

## Cadence
- Daily: lane sync + blockers
- Per feature: design -> build -> verify -> release
- Weekly: retrospective and backlog reprioritization
