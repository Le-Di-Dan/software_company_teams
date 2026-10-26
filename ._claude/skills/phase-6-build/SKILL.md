---
name: phase-6-build
description: Phase 6 - the build loop. Implements features from the locked feature_list.json one at a time with the squad's engineers, two-stage code review, tests and evidence, until all features pass; starts TestFlight and Google Play closed testing early. Use after gate G2.
---

# Phase 6 — Build loop

Precondition: `gates.G2_stack == "approved"`, `state/feature_list.json` locked, smoke check passes.

## Loop (repeat until every active feature has `passes: true`)
1. **Pick** the highest-priority feature with `passes: false`, dependencies satisfied, and runnable on this machine (skip ones whose remaining work is `needs:` the other machine; list them for the PO).
2. **Implement**: delegate to the feature's `owner` (squad agent) with a brief: feature id, paths to story, screen specs, tokens, architecture/ADRs, API contract. They follow `kb-engineering-workflow`.
   - Backend-dependent features: backend/BaaS feature first, then the mobile feature against the contract.
   - Independent features for different owners may run in parallel (one message, ≤3 agents). Use `isolation: "worktree"` for parallel agents editing the same app.
3. **Review**: delegate to `code-reviewer` with the feature id and the changed files/diff. If CHANGES_REQUIRED → send the findings to the same engineer (SendMessage only if it returned less than 4 minutes ago; otherwise a fresh engineer of the same type with the feature id, changed files and findings) → re-review. Max 3 cycles, then escalate to `solution-architect`.
4. **Tests**: when a feature touches a critical path, ask `test-automation-engineer` to add/extend the Maestro flow.
5. **Accept**: confirm evidence exists and `passes: true` is set by the engineer (the hook requires `evidence`). Commit: `feat(F-xxx): <title>`. Log one line in `state/progress.md`.
6. Every ~5 features: run `bash scripts/smoke.sh` and the full test suite; fix regressions before new work.

## Milestones
- **Core flow working** (onboarding + core loop): ask `release-manager` to ship the first build to TestFlight (internal) and Google Play **closed testing**, and remind the PO to opt in ≥12 testers. The 14-day clock should run in parallel with the rest of the build.
- **UI checkpoint** halfway: `uiux-rnd-researcher` reviews screenshots from `docs/07-qa/evidence/` against `kb-production-ui-bar`; failures become bug fixes for the owners.

## Long unattended runs
You may set a goal such as: `/goal every active feature in state/feature_list.json has passes=true with evidence, scripts/smoke.sh passes, or stop after 40 turns`. Report progress to the PO at milestones, not every feature.

## Scope changes
Never add or change features directly — use the `change-request` skill.

Exit: all active features pass (except those `needs:` another machine, which the PO is told about). `phase: "7-qa"`; log; commit.
