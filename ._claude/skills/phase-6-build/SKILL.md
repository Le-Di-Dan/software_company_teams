---
name: phase-6-build
description: Phase 6 - the build loop. Implements features from the locked feature_list.json one at a time with the squad's engineers, two-stage code review, tests and evidence, until all features pass; starts TestFlight and Google Play closed testing early. Use after gate G2.
---

# Phase 6 — Build loop

Precondition: `gates.G2_stack == "approved"`, `state/feature_list.json` locked, smoke check passes.

## Loop (repeat until every active feature has `passes: true`)
1. **Pick** the highest-priority feature with `passes: false`, dependencies satisfied, and runnable on this machine (skip ones whose remaining work is `needs:` the other machine; list them for the PO).
2. **Implement**: delegate to the feature's `owner` (squad agent) with a brief: feature id, paths to story, screen specs, tokens, architecture/ADRs, API contract. They follow `kb-engineering-workflow`.
   - Backend-dependent features: backend/BaaS feature first, then the mobile or web feature against the contract. Web features (`platforms: ["web:<surface>"]`, e.g. `["web:site"]`) go to the frontend team of that surface's framework.
   - Independent features for different owners may run in parallel (one message, ≤3 agents). Use `isolation: "worktree"` for parallel agents editing the same app.
3. **Review**: delegate to `code-reviewer` with the feature id and the changed files/diff. If CHANGES_REQUIRED → send the findings to the same engineer (SendMessage only if it returned less than 4 minutes ago; otherwise a fresh engineer of the same type with the feature id, changed files and findings) → re-review. Max 3 cycles, then escalate to `solution-architect`.
4. **Tests**: when a feature touches a critical path, ask `test-automation-engineer` to add/extend the Maestro flow (web surfaces: the Playwright spec in `tests/web-e2e/<surface>/`).
5. **Accept**: confirm evidence exists and `passes: true` is set by the engineer (the hook requires `evidence`). Commit: `feat(F-xxx): <title>`. Log one line in `state/progress.md`.
6. Every ~5 features: run `bash scripts/smoke.sh` and the full test suite; fix regressions before new work.

## Milestones
- **Core flow working** (onboarding + core loop): ask `release-manager` to ship the first build to TestFlight (internal) and Google Play **closed testing**, and remind the PO to opt in ≥12 testers. The 14-day clock should run in parallel with the rest of the build.
- **UI checkpoint** halfway: `uiux-rnd-researcher` reviews screenshots from `docs/07-qa/evidence/` against `kb-production-ui-bar` (web pages: `kb-web-ui-bar`); failures become bug fixes for the owners.
- **Web surfaces on staging**: once a surface's first complete flow passes, ask `devops-engineer` to deploy it to its preview/staging URL so the PO can try it (with staging accounts where it needs sign-in).

## Long unattended runs
You may set a goal such as: `/goal every active feature in state/feature_list.json has passes=true with evidence, scripts/smoke.sh passes, or stop after 40 turns`. Report progress to the PO at milestones, not every feature.

## Scope changes
Never add or change features directly — use the `change-request` skill.

## Takeover mode (code lives in `client/`, the customer's repo)
- Work on the `company/v2` branch of `client/`. **No `isolation: "worktree"`.** It isolates the workspace repo, which does not contain `client/`. Run parallel engineers only on features whose files don't overlap, and commit each feature yourself with its own paths: `git -C client add <paths> && git -C client commit -m "<type>(F-xxx): <title>"`, in the commit style kept in `.claude/rules/client.md`.
- Brief engineers with the client paths from `takeover.owners`, the "today → v2" screen specs, the migration-plan step, and the characterization tests that must stay green. Refactor features follow the strangler order. Keep the app buildable and the characterization suite green after every feature.
- Accept a feature only when its own verification passes **and** the characterization tests of the modules it touches pass (run through `check.sh -C client/...`). When a feature resolves findings, the engineer sets them to `fixed`; QA, performance or cyber re-test and set `verified`.
- Push `company/v2` at milestones. Open or update the pull request (`gh pr create` / `gh pr edit`) with a Vietnamese summary of what changed for users, the findings resolved, and the evidence. Merging is the PO's.
- The ~5-feature regression run also compares startup and app size against `docs/t4-transition/baseline.md`. A regression above 10% is a bug.

Exit: all active features pass (except those `needs:` another machine, which the PO is told about). `phase: "7-qa"`; log; commit.
