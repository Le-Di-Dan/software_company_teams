---
name: phase-8-release
description: Phase 8 - release readiness - compliance audits for App Store and Google Play, privacy policy and terms published, store listings and screenshots, signed release builds, closed-test completion, review notes, then gate G3 where the PO approves and submits. Use after QA sign-off.
---

# Phase 8 — Release readiness (gate G3)

## Parallel (one message)
- `store-compliance-officer`: P8 audits → `docs/08-release/compliance-audit-ios.md`, `compliance-audit-android.md`, store-form drafts (App Privacy, Data safety, ratings, declarations).
- `privacy-legal-counsel`: final `privacy-policy.md`, `terms-of-use.md`, `licenses.md` matching `data-inventory.md` and the code.
- `aso-marketing-specialist`: `store-listing.md`, `screenshots-brief.md`, `launch-plan.md`.
- `release-manager`: signed release builds (iOS archive on the Mac, AAB where the SDK exists), `review-notes.md`, closed-test status (testers, days elapsed, feedback log).
- `security-lead`: run `security-assessment retest` on the release build, then write `docs/08-release/security-clearance.md` (go/no-go + open-findings table). Any open Critical/High blocks G3 until fixed+verified or PO-accepted.

## Then
- `devops-engineer`: publish privacy policy, terms and support page to public URLs; put URLs in listing and in the app (owner engineer adds them if missing).
- `qa-engineer`: capture final store screenshots per `screenshots-brief.md` from release builds (`docs/08-release/screenshots/`).
- Fix loop for any compliance blocker (owner → reviewer → compliance re-check).
- `release-manager`: fill `docs/08-release/release-readiness.md` (template) with evidence for every row, and write `docs/08-release/submission-guide-vi.md`: step-by-step Vietnamese guide for the PO (App Store Connect and Play Console click paths, what to paste where, which files to upload, how to answer each form).

## Gate G3 (PO-only)
Present to the PO in Vietnamese: readiness table (all ✅ or accepted risks), the security clearance (open findings by severity), closed-test status (Google production access only after ≥12 testers × 14 days), costs going live, rollout plan. Then instruct:
(The approval script itself refuses while any Critical/High finding is unresolved; the PO accepts a specific risk with `! bash scripts/approve-release.sh --accept-risk SEC-xxx`.)
1. Read `docs/08-release/release-readiness.md`.
2. Run `! bash scripts/approve-release.sh` to approve G3 (agents cannot).
3. Follow `submission-guide-vi.md` to submit (or let release-manager run the `release*` fastlane lanes now that G3 is approved, if the PO prefers).

After submission: log; `phase: "9-maintain"`; commit; handle reviewer feedback via `phase-9-maintain` (rejection handling section).

## Takeover mode
- Release from the customer's repo after the PO merged the `company/v2` pull request. Signed builds come from the merged default branch, not from an unmerged company branch.
- Identity:
  - If the app is already published, keep the bundle/application ID and signing key; losing either loses the existing listing and users.
  - If it never shipped, replace placeholder IDs, names and icons before the first upload (they are permanent once uploaded).
- `release-readiness.md` adds a row for each accepted critical or high finding: verified, or deferred by the PO.
- Hand-over pack (`docs/08-release/handover-vi.md`, release-manager): what changed against the baseline, how to build and release from the customer's repo without the company, the updated `client/CLAUDE.md` proposal, and the open deferred findings.
