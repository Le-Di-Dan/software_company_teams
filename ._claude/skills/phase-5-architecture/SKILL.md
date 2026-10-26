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
