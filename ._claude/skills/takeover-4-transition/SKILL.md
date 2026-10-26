---
name: takeover-4-transition
description: Takeover T4 - prepare the customer's repo for safe change after gate TG1 - integration branch company/v2, module ownership and squad from the existing stack, customer conventions finalized, the build reproducible on both machines, characterization tests for flows that must not change, and a measured baseline (build, tests, performance). Then hand over to phase 2 in takeover mode. Use after TG1.
---

# Takeover T4 — Transition & baseline

Precondition: `gates.TG1_direction == "approved"`. Nothing in `client/` changes before this skill, and everything changed from here on is compared against the baseline it measures.

## Steps
1. **Branch.** Create the integration branch from the audited baseline:
   ```
   git -C client switch -c company/v2 <takeover.baseline_sha>
   ```
   If the customer's `takeover.ref` moved since the baseline (`git -C client fetch origin` then compare), tell the PO what changed and ask whether to rebase onto it before work starts.

   All company work lands on `company/v2`, one commit per feature or fix by the director, in the commit style kept in `.claude/rules/client.md`. Pushes go only to `company/*` branches (hook-enforced). The PO merges our pull requests.
2. **Ownership and squad.** `solution-architect` → `docs/t4-transition/repo-map.md`. Brief: from `docs/t1-discovery/module-map.md` and the TG1 direction, map every module path in `client/` to one owning agent. Use the existing stack: Flutter → flutter-engineer, a Node.js API → nodejs-backend-engineer, and so on. Flag modules no company team covers (for example, a web admin), with a proposal: the nearest team, or a new team for the PO to approve. Propose `stack` and `squad`.

   Then you write `state/project.json`:
   - `takeover.owners`: the path prefix inside `client/` mapped to its agents, for example `{"apps/mobile/": ["flutter-engineer"], "apps/content-api/": ["nodejs-backend-engineer"]}`. `guard_files.py` enforces it.
   - `stack` and `squad`. A stack change, such as a re-platform chosen at TG1, is confirmed again at G2.
3. **Conventions.** Make sure `.claude/rules/client.md` reflects TG0 and TG1. Rules that DROP but live in the customer's own `client/CLAUDE.md`: propose to the PO an updated `client/CLAUDE.md` for the hand-over (director-only path; do it at the end of the engagement, not now).
4. **Baseline** (parallel, one message; each brief names the sections of `company/templates/baseline.md` that agent owns):
   - `devops-engineer`: make the build reproducible on this machine (`check.sh` build lines) and document the other machine's steps (`needs:`); run the customer's CI or explain why it is red. Fixes to CI or build config are allowed now, as separate commits on `company/v2`.
   - `test-automation-engineer`: run the existing suites through `check.sh` (record pass, fail and flaky); add **characterization tests**. These are E2E flows (Maestro) and focused unit tests that pin today's behavior for every module marked keep, fix or rebuild and for each critical path in the walkthrough. Put them in the repo's existing test locations; each must fail if the behavior changes.
   - `performance-engineer`: measure the performance table on the commit with the characterization tests (reuse T1 numbers only if the commit and conditions are identical).

   Output: `docs/t4-transition/baseline.md` (template `company/templates/baseline.md`).
5. **Review and commit.** `code-reviewer` checks the test and CI changes. Then you commit them on `company/v2` in `client/` (`git -C client add <paths> && git -C client commit -m …`), and push `company/v2` (`git -C client push -u origin company/v2`) so the other machine can fetch it.

   Ask the PO whether they want a draft pull request now (`gh pr create --draft --base <ref> --head company/v2`) to follow along, or only at milestones.
6. **Exit.**
   - Set `phase: "2-product"`, `phase_status: "not-started"`. The phase skills apply in takeover mode: see "Takeover mode" in each.
   - Log; commit the workspace.
   - Tell the PO in Vietnamese: what was set up, the baseline numbers, what needs the other machine, and the next phase.
