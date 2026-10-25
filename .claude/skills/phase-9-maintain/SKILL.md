---
name: phase-9-maintain
description: Phase 9 - post-submission and post-launch operations - handle App Review rejections, monitor reviews, crashes and metrics, plan updates, keep up with policy/SDK deadlines, and run recurring maintenance. Use after submission, on a schedule, or when the PO reports store feedback.
---

# Phase 9 — Maintain

## A. Store rejection handling
1. Save the reviewer's message verbatim to `docs/09-maintain/rejections/<date>-<store>.md`.
2. `store-compliance-officer`: map it to the exact guideline/policy, root cause, fix plan, whether to fix or reply/appeal (draft the Resolution Center / appeal reply).
3. Fix via change request if scope changes, or as bugs → owner → reviewer → QA → new build (release-manager). Update `company/compliance/*` suggestions in the report so the framework learns (the PO/maintainer edits framework files).

## B. Recurring health check (weekly, or when the PO asks)
Parallel:
- `support-feedback-analyst` → `docs/09-maintain/feedback-<date>.md` (reviews, tester feedback, crash summaries the PO exports).
- `data-analyst` → `docs/09-maintain/metrics-<date>.md` (if analytics exports available).
- `store-compliance-officer` → policy watch: new Apple/Google requirements and deadlines (SDK minimums, target API, privacy rules) affecting this app → `docs/09-maintain/policy-watch-<date>.md`.
- `appsec-code-auditor` → dependency + secret vulnerability scan summary (new CVEs in shipped dependencies); `security-lead` triages anything new into `state/security-findings.json`. Run a full `security-assessment` before any release that changes auth, payments, backend or AI.
Then `product-manager` proposes the next version scope from these inputs (change requests), and you present it to the PO.

## C. Automation options (tell the PO)
- In-session: `/loop 1w run phase-9-maintain section B` while a session is open.
- Cloud: `/schedule` a weekly task on this repo (needs a claude.ai subscription and GitHub access). Cloud sessions run Linux: fine for research/compliance/feedback analysis, but no iOS builds.

## D. Next version
A new version is a mini-project: `change-request` for each item → phase 4 (if design changes) → phase 6 build loop → phase 7 → phase 8.
