---
name: kb-api-cloud-security
description: Backend, BaaS and AI security knowledge for the Cyber Security team - OWASP API Security Top 10, ASVS, Firebase Rules / Supabase RLS testing, OWASP LLM Top 10 for AI endpoints, tools, and the findings workflow.
user-invocable: false
---

# API, cloud & AI security

Standards: **OWASP API Security Top 10**, **OWASP ASVS** (web/app verification), **OWASP Top 10 for LLM Applications** (AI endpoints). Verify current versions and item names before quoting — fetch the official pages and note the date; don't trust memory for exact IDs.

## OWASP API Security Top 10 (attacker's checklist)
- **BOLA / IDOR** — the #1 API bug: as user A, access user B's object by changing an id in the path/body/query. Test every endpoint that takes an object id.
- **Broken authentication** — weak/guessable tokens, tokens that don't expire or survive logout, credential stuffing with no lockout.
- **Broken object property-level authz** — mass assignment (set fields you shouldn't, e.g. `role`, `is_premium`) and excessive data exposure (endpoint returns more fields than the client needs).
- **Unrestricted resource consumption** — missing pagination, rate limits, or size caps (demonstrate with a small bounded burst, never a flood).
- **Broken function-level authz** — call admin/privileged routes as a normal user.
- **SSRF**, **security misconfiguration** (verbose errors, default creds, bad CORS, missing security headers), **improper inventory** (debug or old `/v0` endpoints still live), **unsafe third-party API consumption**.
- **JWT specifics**: reject `alg:none`, verify the signature, check `exp`/`aud`/`iss`, no weak HMAC secret, no sensitive data in the payload.

## Firebase Security Rules / Supabase RLS
- Rules/policies must **deny by default**; access is granted explicitly per operation and scoped to `auth.uid()` / `request.auth`.
- With a low-privilege test user, attempt to read/write other users' rows/documents, escalate role, and bypass validation. There must be emulator (`firebase emulators:exec`) or local (`supabase start` + pgTAP/SQL) tests covering the **denied** cases, not just the allowed ones.
- No privileged key (service_role, admin SDK) ever reaches the client; those run only server-side / in functions.

## AI endpoints — OWASP Top 10 for LLM Applications
- **Prompt injection & system-prompt leakage** — user input that overrides instructions or extracts the system prompt.
- **Sensitive information disclosure** — model returns secrets, other users' data, or internal details.
- **Unbounded consumption / cost attacks** — can a user trigger unlimited or oversized expensive calls? Require per-user quotas/rate limits, output token caps, and the provider key **server-side only** (never in the mobile app). This is both a security and a cost-control issue — coordinate with the monetization/architecture docs.
- **Excessive agency / insecure output handling** — if the model can call tools or its output is rendered/executed, validate and constrain it.

## Tools (Docker-first; pin tags; ask before first image pull)
- `ghcr.io/zaproxy/zaproxy:stable` — `zap-baseline.py` (passive) and `zap-api-scan.py` against the OpenAPI spec in `docs/05-architecture/api-contract/`.
- `nuclei` — templated checks for misconfig/exposures.
- `semgrep` (`p/owasp-top-ten`, stack packs), `gitleaks`, `osv-scanner`, `trivy image` — static/secret/dependency/container scans.
- `curl`/`httpie` — targeted authz tests (keep two test accounts for BOLA proofs).

## Rules of engagement & workflow
- Authorized targets only: backend running locally (Docker / emulator suite / `supabase start`) or the PO's own staging project. **No production, no third-party APIs, no DoS/load attacks.**
- Findings go to `state/security-findings.json` with an exact runnable `repro` (the request + which accounts), API/LLM/ASVS category, severity + CVSS, concrete `fix`, owner. Status flow `open → fixed` (dev) `→ verified` (Cyber Security only); `accepted-risk` is PO-only.
- Severity by real impact: a BOLA exposing other users' data or an RLS bypass = Critical/High; a missing security header = Low.
- Give `devops-engineer` the exact scan commands to wire into CI (fail the build on High+).
