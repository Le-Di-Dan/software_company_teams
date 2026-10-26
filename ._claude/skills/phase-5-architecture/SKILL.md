---
name: phase-5-architecture
description: Phase 5 - choose the stack (mobile language team, backend language team, BaaS), design architecture, data model, API contracts, AI architecture and security; get PO approval (gate G2); assemble the squad; scaffold the projects, CI and smoke test; create and lock feature_list.json. Use after phase 4.
---

# Phase 5 — Architecture & setup

Inputs: all product and design docs, `state/environment.md`.

## A. Decide
1. `solution-architect` → `stack-selection.md`, `architecture.md`, `data-model.md`, `api-contract/`, ADRs, `secrets.md`, `repo-layout.md`. Brief must state: no paid EAS; Mac has Xcode + Flutter; Windows has the full Android toolchain; candidates React Native / Flutter / Swift+Kotlin; backend none / Firebase / Supabase / Node.js / Python / Go / hybrid.
2. In parallel: `ai-rnd-researcher` (+architect) → `ai-architecture.md` if AI in scope; `security-lead` → `security-review.md` (required controls by MASVS/ASVS, backend authz/RLS/Rules, AI endpoint abuse/cost controls) and creates `state/security-findings.json`; `store-compliance-officer` → P5 notes; `privacy-legal-counsel` → update `data-inventory.md` with SDKs.
3. Run `review-board G2`. The PO approves the stack.

## B. Assemble the squad
Write to `state/project.json`: `stack` (e.g. `{"mobile":"flutter","backend":"python","baas":"supabase"}`) and `squad`: chosen mobile agent(s) (`swift-ios-engineer` + `kotlin-android-engineer` for native), backend agent, BaaS agent, plus code-reviewer, test-automation-engineer, qa-engineer, devops-engineer, release-manager, security-lead (pulls in appsec-code-auditor / mobile-pentester / api-cloud-pentester as scope needs), store-compliance-officer.

## C. Set up (squad agents, mostly parallel)
- Mobile team(s): scaffold `apps/...` per `repo-layout.md`, theme from design tokens, navigation shell, empty screens wired to routes, one passing test. Respect machine limits.
- Backend/BaaS team: scaffold `services/...`, local stack (Docker / emulators), health endpoint or rules test.
- `devops-engineer`: `.gitignore`/`.gitattributes` for the stack, CI workflow, `.env.example`, `scripts/smoke.sh`.
- `test-automation-engineer`: Maestro skeleton (`tests/e2e/smoke/launch.yaml`), test utilities.
- `release-manager`: `docs/08-release/release-plan.md` incl. closed-test start date; ask the PO for account status.

## D. Feature list
`solution-architect` → `state/feature_list.json` (all MVP features, owners from the squad, `locked: false` while drafting). You review: every MVP story covered, features small, verification concrete. Then the architect sets `"locked": true`.

## Exit
Smoke script passes on this machine (others tagged `needs:`); `gates.G2_stack: "approved"`; `phase: "6-build"`; log; commit. Tell the PO what they must do now (developer accounts, Firebase/Supabase project creation, API keys into `.env`, recruit testers).

## Takeover mode
- **A. Decide**: the architect starts from `docs/t1-discovery/architecture.md`, `module-map.md`, `docs/t3-assessment/architecture-options.md` and `docs/t4-transition/repo-map.md`. The output is the **target architecture plus a migration plan** (`docs/05-architecture/migration-plan.md`).
  - The migration is ordered so that the app builds, passes the characterization tests and could ship after every step. Use strangler steps: introduce the new module beside the old one, move the callers over, then delete the old one. A big-bang rewrite needs an explicit TG1 decision.
  - Data and user migrations come with rollback.
  - The existing stack is the default. Changing it needs a reason tied to findings.
  - G2 approves the target architecture and the migration plan.
- **B. Squad**: confirm or adjust what T4 wrote. Update `takeover.owners` if modules move.
- **C. Set up**: no scaffolding. The repo exists. Setup work is only what the migration plan's first step needs, committed on `company/v2`.
- **D. Feature list**:
  - Paths in features are relative to `client/`.
  - Each feature carries `findings: [TKO-…]` and, for refactors, the characterization tests that must stay green in `verification`.
  - Migration steps are features too (category `refactor`).
  - When it is locked, set `feature` in `state/findings.json` for each accepted finding (main session).
