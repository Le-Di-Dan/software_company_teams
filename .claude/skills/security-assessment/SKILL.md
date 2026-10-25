---
name: security-assessment
description: Run a full Cyber Security assessment (threat model refresh, SAST + secret + dependency scan, mobile pentest, API/cloud/AI pentest) or re-test fixed findings, then report blockers to the PO. Use in phase 7, before gate G3, in phase 9, or whenever the PO asks for a security check.
argument-hint: "[full | retest | mobile | api | <scope note>]"
---

# Security assessment

Run by the director, driven by `security-lead`. Argument `$ARGUMENTS` selects scope (default `full`).

## Preconditions
- There is something to test: a built app (mobile), and/or a backend running locally or on the PO's staging. If a build needs the other machine, run what you can and tag the rest `needs: mac|windows`.
- Rules of engagement (remind every agent): authorized targets are this company's own local/emulator/staging only — never production, third-party services, or other people's accounts; no DoS/load attacks. Tool images pull via Docker with the PO's OK (ask once, record in `state/open-questions.md`).

## Steps
1. **Scope & threat model** → `security-lead`: refresh `docs/05-architecture/security-review.md` / threat model, decide which targets are in scope (mobile / api / baas / ai) and the MAS profile. Ensure `state/security-findings.json` exists (create from the schema in `security-lead` if missing).
2. **Parallel assessment** (one message, brief each with scope + rules of engagement):
   - `appsec-code-auditor` → semgrep + gitleaks + dependency scan on the repo → `docs/07-qa/appsec-audit-<date>.md`.
   - `mobile-pentester` (if a build exists) → MobSF + storage + mitmproxy + platform tests → `docs/07-qa/mobile-pentest-<date>.md`.
   - `api-cloud-pentester` (if a backend/BaaS runs) → API Top 10 + Rules/RLS + LLM Top 10 → `docs/07-qa/api-cloud-pentest-<date>.md`.
   Each appends findings to `state/security-findings.json`.
3. **Triage** → `security-lead`: de-duplicate, set severity + CVSS, assign owners; summarize counts and top risks.
4. **Fix loop**: for each open Critical/High (then Medium) the director delegates to the owning engineer → `code-reviewer` → the finding's pentester/auditor re-tests and sets `verified` (or re-opens). Only the Cyber Security team sets `verified`.
5. **Report to the PO** (Vietnamese): counts by severity, what blocks release, plain-language risk of each Critical/High, and for any the PO chooses to accept, note that accepting a risk is PO-only via `! bash scripts/approve-release.sh --accept-risk SEC-xxx`.

## `retest` mode
Skip discovery; re-run verification only on findings currently `fixed`, updating them to `verified` or re-opening with new evidence.

## Gate G3 dependency
`security-lead` writes `docs/08-release/security-clearance.md` (go/no-go + open-findings table). The release-readiness gate blocks while any Critical/High is not `verified` or PO-`accepted-risk`.
