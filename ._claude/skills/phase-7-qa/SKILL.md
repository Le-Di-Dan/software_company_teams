---
name: phase-7-qa
description: Phase 7 - full QA and hardening on iOS and Android - test plan execution, E2E suite, exploratory and store-reviewer walkthrough, UI bar review, security audit, performance and accessibility - with a bug-fix loop until QA sign-off. Use after the build loop.
---

# Phase 7 — QA & hardening

## Parallel kickoff (one message)
- `qa-engineer`: execute `docs/07-qa/test-plan.md` (write it first if missing) on this machine's platform; exploratory testing incl. store-reviewer path; report in `docs/07-qa/reports/`; bugs in `docs/07-qa/bugs.md`.
- `test-automation-engineer`: run the full automated suite (unit, integration, Maestro E2E on available simulators/emulators, Playwright for each web surface); report failures and flakiness.
- `security-lead`: run the `security-assessment` skill (full) — directs appsec-code-auditor + mobile-pentester + api-cloud-pentester, collects into `state/security-findings.json`, writes the per-area reports in `docs/07-qa/`.
- `uiux-rnd-researcher`: final UI bar review from QA screenshots → `docs/04-design/uiux-rnd-review.md` (final section).

## Fix loop
For each bug (blocker → critical → major): delegate to the owning engineer (with bug id and evidence) → `code-reviewer` → `qa-engineer` verifies and closes. Minor bugs: fix if cheap, otherwise log for next version with PO visibility.

## Cross-machine
Anything `needs: windows` or `needs: mac` gets a checklist in `docs/07-qa/pending-other-machine.md`; tell the PO to open the repo on that machine and run `company-status` → it resumes these.

## Exit criteria (QA sign-off)
- 0 open blocker/critical bugs; major bugs fixed or explicitly accepted by the PO.
- E2E green on iOS and Android (both machines), crash-free in TestFlight / closed test so far.
- Web surfaces (if any): Playwright suites green against staging on Chromium, Firefox and WebKit; no serious/critical axe violations; Core Web Vitals budget met on key public pages (Lighthouse); `kb-web-ui-bar` has no FAIL on key pages; admin role-denied cases pass.
- Security: `state/security-findings.json` has no open Critical/High (fixed+verified or PO-accepted). UI bar: no FAIL on core screens.

Then `phase: "8-release"`; log; commit.

## Takeover mode
- Add `performance-engineer` to the kickoff: `docs/07-qa/performance-<date>.md`, compared against `docs/t4-transition/baseline.md`.
- QA re-runs the T1 walkthrough on the release candidate: every symptom and every accepted finding in `state/findings.json` is re-checked, then set to `verified` or sent back to `accepted` with evidence.
- Extra exit criteria:
  - no accepted critical or high finding is left unverified (unless the PO deferred it);
  - the characterization suite is green, or each changed expectation is traced to an approved story;
  - no performance regression above 10% against the baseline.
