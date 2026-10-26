---
name: kb-store-compliance
description: How to run App Store and Google Play compliance audits - where the checklists live, how to verify against live official policy, severity levels and the report format.
user-invocable: false
---

# Store compliance audit method

Checklists: `company/compliance/apple-app-store.md` and `company/compliance/google-play.md` (IDs A-*, G-*).

## Procedure
1. **Refresh**: WebFetch each official source listed at the top of both checklists. Note the date. Look for changes since the checklist date (new guideline numbers, new deadlines, target API, SDK minimums, age rating questions, AI/UGC rules). Record differences in your report under "Policy changes detected".
2. **Scope**: list app capabilities that trigger special rules: accounts, payments/subscriptions, ads/tracking, AI generation, UGC/social, kids audience, health/fitness/medical, finance, location, camera/mic/photos, background work, web views, external links, login providers.
3. **Audit**: for each relevant checklist item record `PASS | FAIL | N/A | RISK`, evidence (file path + line, screenshot path, command output, URL), owner and fix.
4. **Store forms drafts**: Apple App Privacy answers, Google Data safety answers, age/content rating questionnaire answers, export compliance, ads declaration, target audience, permissions declarations. Derive from `docs/05-architecture/data-inventory.md` and verify against code (grep SDK initializations, manifests, Info.plist).
5. **Reviewer path**: confirm demo credentials and review notes let a reviewer reach every feature in under 5 minutes.

## Severity
- **Blocker**: high likelihood of rejection or policy strike → blocks the gate.
- **Risk**: plausible rejection depending on reviewer → fix if cheap, else PO accepts explicitly.
- **Advice**: best practice.

## Report header
```
Audit: <iOS|Android> · Phase P<n> · Date · Sources fetched: <url + date>
Summary: <n> blockers, <n> risks · Verdict: PASS / FAIL
```
