# AI Landing Platform Design (Wayl.io + Approval-Gated Autonomous Delivery)

## Objective
Build a platform where people/companies request landing pages via structured intake, pay deposit, and have AI clarify/build/deploy with minimal owner intervention.

## Approved Scope Decisions
- Product scope (V1): **Landing pages only**
- Pricing model: **Fixed packages**
- Generation model: **Template-guided generation**
- Payment flow: **Deposit first, final payment before handoff**
- Human approvals: **Owner approves design + deploy only**
- Hosting/deployment: **Hosted on our infra**
- Payment gateway: **Wayl.io (Iraqi local gateway)**
- Localization: **Bilingual Arabic/English + IQD (optional USD reference)**
- Code ownership: **Per-client GitHub repo**
- Architecture choice: **Monolith + job workers (recommended and approved)**

## Section 1 — Product Architecture (V1)

### Core flow
1. User registers/logs in.
2. User submits structured landing-page request (industry, goals, style, package, assets).
3. User pays deposit through Wayl.io.
4. AI analyzes request:
   - asks clarification questions if needed;
   - otherwise proceeds to design planning.
5. AI generates design brief + template-mapped structure.
6. **Approval Gate 1:** owner design approval.
7. AI generates code to per-client GitHub repo and deploys preview/prod on managed infra.
8. **Approval Gate 2:** owner deploy approval.
9. User pays remaining balance.
10. Domain mapping + handoff.

### Modules
- Auth & Accounts
- Intake & Package Pricing
- Wayl.io Payments
- AI Orchestrator (analysis/questions/generation)
- Project Pipeline & State Tracking
- Repo Provisioning (per-client)
- Deployment Engine
- Admin Approval Console
- Client Portal (Q/A + status + invoices)

## Section 2 — Data Model + State Machine

### Core entities
- User
- ProjectRequest
- ClarificationThread
- Quote/Invoice
- PaymentTransaction
- Project
- AIJob
- ApprovalGate
- Repository
- Deployment
- Asset

### State machine
`draft_request`
→ `submitted`
→ `deposit_pending`
→ `deposit_paid`
→ `clarification_needed` (loop)
→ `ready_for_design`
→ `design_generated`
→ `awaiting_admin_design_approval`
→ `design_approved`
→ `build_in_progress`
→ `preview_ready`
→ `awaiting_admin_deploy_approval`
→ `deploy_approved`
→ `final_payment_pending`
→ `final_payment_paid`
→ `domain_mapping`
→ `delivered`

### Guardrails
- No build before deposit confirmation.
- No deploy before design approval.
- No domain handoff before final payment.
- All transitions audited.
- Approval states are hard gates.

## Section 3 — Task Split + Phased Launch

### Team lanes
1. Backend/API lane
2. Frontend lane (client/admin portals)
3. AI orchestration lane
4. Codegen/deployment lane
5. Payments/finance lane

### Phase plan
- **Phase 1:** Auth + intake + packages + deposit + state machine + admin shell
- **Phase 2:** AI clarification loop + design brief + design approval gate + repo generation
- **Phase 3:** Auto build/deploy preview + deploy approval gate + final payment + domain mapping
- **Phase 4:** Optimization (templates, conversion analytics, throughput improvements)

## Owner interaction model (minimal)
Owner actions are limited to:
1. Design approval
2. Deploy approval
3. Optional domain/configuration entry

Everything else is handled by orchestrated AI + platform workflows under guardrails.
