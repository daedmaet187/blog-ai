# Blog Multi-Platform Beta Design (Parallel Feature Squads)

## Objective
Ship a fast-but-solid internal beta across web, admin, and Flutter mobile with shared backend rules, including authoring and moderation.

## Chosen Approach
**Approach 1: Parallel Feature Squads** (approved)

Tracks:
1. Backend/API
2. Web/Admin
3. Flutter
4. DevOps/QA

Rationale:
- Best fit for 1-week beta timeline with balanced speed/polish.
- Maintains quality by locking shared API contracts while allowing parallel delivery.

## Product/Scope Decisions (approved)
- Launch target: **Fast beta (~1 week)**
- Mobile scope: **Full authoring from mobile (create/edit/publish)**
- Publish roles on mobile: **Admin + Editor**
- Distribution: **TestFlight + Play Internal**
- Auth in beta: **Email + password only**
- Moderation mode: **Auto rules + manual override**
- Auto moderation rules (minimum set):
  - profanity/blocked words
  - link spam limits
  - duplicate-content check
  - max media count
- Delivery posture: **Balanced speed vs polish**

## Section 1 — Delivery Architecture

### 1) Backend/API lane
- Enforce Auth + RBAC (`admin`, `editor`, `reader`) server-side.
- Implement post lifecycle and moderation pipeline.
- Enforce media validations and limits.
- Emit audit logs for publish/moderation actions.

### 2) Web/Admin lane
- Build moderation console with reason codes and override actions.
- Ensure editorial flows align with backend contracts.
- Surface API reason codes clearly for fast operator decisions.

### 3) Flutter lane
- Implement login, feed, post detail.
- Implement create/edit/publish for `admin` + `editor`.
- Add media upload and client-side guardrails aligned with backend.

### 4) DevOps/QA lane
- Validate staging parity and health checks.
- Keep release automation for TestFlight + Play Internal.
- Run daily smoke matrix across web/admin/mobile.

## Section 2 — Data Flow + Moderation Pipeline

### Publish flow
1. User logs in with email/password.
2. API validates role for create/edit/publish.
3. Draft persists.
4. On publish request, moderation engine evaluates:
   - profanity/blocked words
   - link spam threshold
   - duplicate-content check
   - max media count
5. Decision:
   - **Pass** → publish
   - **Flag** → hold with reason codes
   - **Override** (authorized) → publish + audit trail

### API behavior requirements
- Role checks server-side only.
- Same moderation rule engine for web/admin/flutter.
- Reason-code based API errors for actionable UI handling.
- Audit log coverage for publish/reject/override and sensitive actions.
- Idempotent publish endpoint to prevent double-publish from retry behavior.

## Section 3 — Task Split + 7-Day Plan

### Backend/API tasks
- Finalize RBAC matrix and enforcement.
- Complete posts endpoints and lifecycle operations.
- Build moderation engine and decision schema.
- Add moderation queue endpoints + override actions.
- Add audit logging and integration tests.

### Web/Admin tasks
- Build moderation queue UI and actions.
- Add clear reason-code rendering.
- Ensure editor/publish parity with backend rules.
- Add smoke coverage for core admin paths.

### Flutter tasks
- Implement auth, feed, detail.
- Implement draft/edit/publish with role-aware UI.
- Add media upload constraints matching backend limits.
- Configure internal release builds (iOS + Android).

### DevOps/QA tasks
- Staging reliability checks (migrations/secrets/health).
- CI gate checks for API and app stability.
- Internal release pipeline checks.
- End-to-end smoke checklist + rollback playbook.

### 7-day sequence
- **Day 1:** lock contracts, reason-code schema, owners/checkpoints
- **Day 2-3:** backend moderation + admin moderation MVP + flutter baseline
- **Day 4:** flutter authoring + admin override + full integration
- **Day 5:** QA sweep and blocker-only fixes
- **Day 6:** release prep (TestFlight + Play Internal) + staging regression
- **Day 7:** internal beta launch + triage/hotfix prioritization

## Definition of Done (beta)
- API health stable and monitored.
- Shared backend rules enforce parity across web/admin/flutter.
- Mobile authoring functional for `admin`/`editor`.
- Auto moderation + manual override works end-to-end.
- TestFlight and Play Internal builds available to testers.
