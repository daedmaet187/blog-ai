# Mission Control Blueprint + HR System Roadmap

This document is a handoff/playbook for coworkers.
It covers:
1) What we built in this project
2) The reusable blueprint for future products
3) How to execute an HR system end-to-end (Backend + Dashboard + Flutter apps)
4) Automation, deployment, and mobile store publishing process

---

## 1) What We Built (Current Project: Blog Mission Control)

### Goal
Build a reusable AWS-based delivery platform ("Mission Control") and ship a real MVP vertical slice first.

### Stack
- **Cloud:** AWS (`eu-central-1`)
- **DNS:** Cloudflare (`stuff187.com`)
- **Backend:** FastAPI + SQLAlchemy + Postgres + Redis
- **Containers:** Docker + ECS Fargate + ECR
- **Infra as Code:** OpenTofu
- **Web/Admin:** static HTML/JS on S3 + CloudFront
- **CI/CD:** GitHub Actions with AWS OIDC

### Working Domains
- API: `https://api.stuff187.com`
- Web: `https://app.stuff187.com`
- Admin: `https://admin.stuff187.com`

### Key Delivered Capabilities
- End-to-end auth + post workflow (register/login/create/publish/read)
- Admin dashboard with post management (list/filter/edit/publish/unpublish/delete)
- Markdown editor + preview + toolbar in admin
- Public web with modern UI and markdown-rendered post page
- CloudWatch alarms + operations runbook
- Alembic migration setup
- S3 media upload pipeline via presigned URLs (in progress hardening and final behavior validation)

### Major Lessons Learned
- S3 website endpoints are HTTP-only; for HTTPS custom domains use CloudFront + ACM.
- ECS deployment can look "successful" while app code path still fails during startup (always inspect CloudWatch logs).
- Alembic + legacy schema requires careful bootstrap (stamp head vs create table conflict).
- Fish shell users need fish-safe command style (bash-style env assignment can break).
- Protect repo from large/accidental artifacts (`.terraform`, tfstate, tfplan, binaries).

---

## 2) Reusable Mission Control Blueprint (For Future Projects)

## 2.1 Architecture Pattern
- **Frontend channels**
  - Web app (CloudFront)
  - Admin dashboard (CloudFront)
  - Mobile app (Flutter)
- **API layer**
  - FastAPI services on ECS Fargate
- **Data layer**
  - RDS Postgres (system of record)
  - Redis (cache/session/rate limits/queues if needed)
- **Asset/media layer**
  - S3 + presigned URLs
- **Edge/security**
  - CloudFront + ACM + Cloudflare DNS
- **Delivery**
  - GitHub Actions + OIDC + ECR/ECS rolling deploy

## 2.2 Environment Strategy
- `dev` (fast iteration)
- `staging` (production-like QA)
- `prod` (customer traffic)

Use separate:
- DB instances
- buckets
- SSM secrets paths
- CloudFront distributions
- IAM roles/policies

## 2.3 Repo/Monorepo Layout

```text
apps/
  web/
  admin_dashboard/
  mobile_flutter/
services/
  api/
infra/
  opentofu/
docs/
  runbooks, ADRs, blueprints
.github/workflows/
```

## 2.4 CI/CD Baseline
- PR checks: lint, tests, build
- Main branch:
  - Build API image -> push ECR
  - Deploy ECS task definition
  - Deploy static assets to S3/CloudFront
- Add migration gate:
  - run Alembic migrations pre-start or controlled migration job

## 2.5 Operational Guardrails
- CloudWatch alarms: 5xx, unhealthy targets, CPU/memory
- Structured logging and trace IDs
- Backup retention policy (RDS) + restore drills
- Least privilege IAM for task/runtime roles
- Incident runbook + rollback playbook

---

## 3) HR System Plan (Backend + Dashboard + Flutter)

This is the direct expansion path using the same platform.

## 3.1 HR MVP Modules
1. **Auth + RBAC**
   - Roles: Super Admin, HR Admin, Manager, Employee
2. **Employee Directory**
   - profile, department, manager, status
3. **Attendance**
   - check-in/check-out, shift, late/absence rules
4. **Leave Management**
   - leave types, balances, request/approval flow
5. **Announcements/Notifications**
6. **Basic Payroll Inputs** (MVP: attendance + leave export)

## 3.2 Backend Design (FastAPI)
- Services/domains:
  - `auth`, `employees`, `attendance`, `leave`, `notifications`, `reports`
- Patterns:
  - Pydantic schemas + SQLAlchemy models + Alembic migrations
  - Service layer for business rules
  - background jobs (reminders, leave accrual, report generation)
- Security:
  - JWT access + refresh token strategy
  - optional MFA for admin roles
  - audit logs for sensitive actions

## 3.3 Admin Dashboard (Web)
- Modules:
  - employee CRUD
  - organization structure
  - leave approvals queue
  - attendance anomalies
  - reports export (CSV/PDF)
- UX requirements:
  - role-aware navigation
  - search/filter/sort everywhere
  - optimistic updates + clear error toasts

## 3.4 Flutter App (Employee + Manager)
- Employee features:
  - profile, attendance actions, leave requests, policy docs
- Manager features:
  - approve/reject leave, team attendance summary
- Tech choices:
  - clean architecture + repository pattern
  - secure token storage
  - push notifications (Firebase Cloud Messaging)

---

## 4) HR System Delivery Plan (Execution Roadmap)

## Phase 0: Foundations (1 week)
- Create HR service skeleton
- Role model + auth refresh flow
- Alembic migration baseline
- CI pipelines + staging env

## Phase 1: Core HR (2–3 weeks)
- Employee directory
- Attendance check-in/out API + UI
- Leave request + approval workflow
- Flutter employee basics

## Phase 2: Manager + Reporting (2 weeks)
- Manager dashboard widgets
- Attendance anomalies
- Leave balances and exports

## Phase 3: Hardening (1–2 weeks)
- observability, alerting, load testing
- security review + pen-test checklist
- backup/restore drills

## Phase 4: Release & Scale
- pilot customer/org rollout
- collect metrics + iterate

---

## 5) Automation & Deployment Blueprint

## 5.1 Infrastructure as Code (OpenTofu)
- Reusable modules:
  - network, ecs_service, db, redis, storage, cdn
- One env folder per environment
- Secrets in SSM/Secrets Manager

## 5.2 Release Workflows
- API workflow
  - build image with commit SHA
  - push ECR
  - update ECS task definition
  - wait for stability
- Static workflow
  - sync S3
  - (optional) CloudFront invalidation
- Mobile workflow
  - automated build pipelines for Android/iOS artifacts

## 5.3 Recommended Pipeline Enhancements
- blue/green deployments for API
- database migration job separated from app startup
- smoke tests post-deploy
- automatic rollback on failed health checks

---

## 6) Mobile Store Publishing (Google Play + Apple App Store)

## 6.1 Google Play Store (Flutter Android)
1. Prepare app identity
   - stable package name (cannot change later)
2. Build signed release (AAB)
3. Create Play Console app
4. Fill store listing (text, screenshots, privacy policy)
5. Configure content rating + data safety
6. Upload internal test build first
7. Promote to closed/open/production tracks

## 6.2 Apple App Store (Flutter iOS)
1. Apple Developer account + App ID
2. Configure certificates/profiles or automatic signing
3. Build archive via Xcode / CI
4. Upload via Xcode / Transporter
5. App Store Connect listing
6. Privacy nutrition labels + review info
7. TestFlight beta -> production submission

## 6.3 Shared Mobile Release Checklist
- crash reporting integrated
- analytics events defined
- API base URLs by environment
- legal docs live (privacy policy/terms)
- support contact + rollback plan

---

## 7) Standard Operating Rules for Future Projects

1. **Always deliver a vertical slice first** (login -> core action -> visible output).
2. **Lock infra conventions early** (naming, envs, region, DNS).
3. **Treat migrations as first-class** (never ad-hoc schema drift).
4. **No manual secrets in code or CI logs**.
5. **All deploys are reproducible via pipeline**.
6. **Every system must have runbook + alarms before production.**
7. **Track decisions in docs/ADRs to reduce tribal knowledge.**

---

## 8) Immediate Next Actions (Recommended)

For this repo right now:
1. Finalize media upload browser flow verification end-to-end.
2. Separate Alembic migration from API container startup into dedicated migration step/job.
3. Create `staging` environment copy of current `dev` with isolated DB and domain.
4. Add baseline tests for auth, posts, media presign.
5. Start HR service scaffold in `services/hr_api` using same conventions.

---

## 9) Ownership / Communication Format for Team

For each feature ticket, include:
- Problem statement
- API contract
- UI contract (admin/mobile)
- Migration impact
- Monitoring impact
- Rollback steps

For each release, publish:
- commit/tag
- changed services
- data migration notes
- risk level
- post-deploy verification results

---

This blueprint is intentionally practical: it is designed to be copied for upcoming products (HR system first), while keeping shared infrastructure and delivery muscle reusable.
