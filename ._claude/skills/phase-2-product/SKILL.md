---
name: phase-2-product
description: Phase 2 - turn research into the PRD, personas, user stories with acceptance criteria, user flows, AI feature specs, tracking plan and a compliance pre-check, ready for the MVP scope review board. Use after phase 1.
---

# Phase 2 — Product definition

Inputs: everything in `docs/00-intake/` and `docs/01-research/`.

## Steps
1. **PRD & stories** → `product-manager`: write `docs/02-product/prd.md`, `user-stories.md`, `personas.md`, `scope.md` (MVP/Next/Later/Won't with RICE). Every MVP item traces to a ranked problem in `synthesis.md`.
2. **In parallel, once the PRD draft exists** (waves of ≤3 agents):
   - `ux-designer` → `docs/02-product/user-flows.md` (IA, navigation, Mermaid flows for all MVP stories).
   - `ai-rnd-researcher` → `docs/02-product/ai-features.md` (only for AI features in scope).
   - `data-analyst` → `docs/02-product/tracking-plan.md`.
   - `store-compliance-officer` → `docs/02-product/compliance-precheck.md` (checkpoint P2).
   - `privacy-legal-counsel` → first draft of `docs/05-architecture/data-inventory.md` from the PRD (data types per feature).
   - `security-lead` → `docs/02-product/security-threat-model.md` (early STRIDE threat model, abuse cases, required security stories, MAS/ASVS profile).
3. **Integrate** → a fresh `product-manager` with the paths of its PRD/stories and every step-2 output: incorporate flows, AI specs, compliance-required stories (account deletion, restore purchases, report content, permission rationale, privacy policy screen), the security stories from the threat model (e.g. rate limiting, session/logout, data wipe on delete) and tracking events into the PRD and stories. Resolve or list conflicts.
4. **Self-check before the board** (you verify): each MVP story has testable Given/When/Then incl. error/empty/offline; each has flows; compliance blockers addressed; AI features have cost per user; tracking covers the KPIs.

Update state: `phase: "3-review-board"`; log; commit. Next: run `review-board` with gate G1.

## Takeover mode (`engagement: "takeover"`, after T4)
- Inputs replace the intake and research: `docs/t3-assessment/assessment.md` (the PO's TG1 decision), `docs/t2-market/positioning.md`, `docs/t1-discovery/*`, `state/findings.json` (accepted findings), `docs/t1-discovery/walkthrough.md` (how the app behaves today).
- The PRD describes **v2 as a whole** and marks each story with the module verdict it comes from: `keep` (the current behavior is the spec, covered by T4's characterization tests), `fix` / `rebuild` (new acceptance criteria) or `add`. Cut features get a removal story: what happens to their screens, data and users. Every accepted finding maps to at least one story (`findings: [TKO-…]`).
- Scope comes from the TG1 decision. If the PRD needs more or less than the chosen option, list the difference and ask the PO before moving on. There is no G1 board: TG1 already decided scope.
- Then `phase: "4-design"`.
