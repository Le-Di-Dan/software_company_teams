---
name: kb-mobile-appsec
description: Mobile application security knowledge for the Cyber Security team - OWASP MASVS categories and MAS testing profiles, MASTG test areas, the tools and how to run them safely, severity rules and the findings workflow.
user-invocable: false
---

# Mobile application security (MASVS / MASTG)

Standard: **OWASP Mobile Application Security (MAS)**. Verify current versions before quoting them — fetch https://mas.owasp.org/ and note the date. As of this writing: MASVS 2.x (8 control groups), MASTG v2.x (test knowledge base + demos), MASWE weakness catalog. Don't rely on memory for version numbers or specific test IDs.

## MASVS control groups (what to cover)
- **STORAGE** — no sensitive data in plaintext prefs/UserDefaults/SQLite/logs/backups; use Keychain/Keystore; clear on logout and account deletion.
- **CRYPTO** — modern algorithms, keys in the platform keystore, no hard-coded keys or custom crypto.
- **AUTH** — session handling, token expiry/refresh, biometric gating done right, no auth logic trusted to the client alone.
- **NETWORK** — TLS everywhere, no cleartext exceptions, correct certificate validation; pinning where the threat model needs it.
- **PLATFORM** — safe IPC/exported components, deep-link/intent validation, WebView hardening (no unneeded JS bridges, no arbitrary URL/`file://` loading), pasteboard and screenshot hygiene.
- **CODE** — up-to-date dependencies, no debug code/secrets shipped, input validation, safe deserialization.
- **RESILIENCE** (MASVS-R) — root/jailbreak detection, anti-tampering, obfuscation. Lower priority for most consumer apps; raise it for payments/DRM/high-abuse targets.
- **PRIVACY** — data minimization, consent, transparency; aligns with store privacy labels and `docs/05-architecture/data-inventory.md`.

## MAS testing profiles
MASTG defines profiles that decide how deep to test: a baseline profile for all apps (roughly MASVS-L1 controls — storage, crypto, auth, network, platform, code, privacy), a defense-in-depth profile for apps handling sensitive data (adds stronger L2 controls), and a resilience profile (MASVS-R) for apps needing anti-tampering. **Pick the profile in the phase-2 threat model** and scope testing to it; don't apply resilience theater to a simple utility app.

## MASTG test areas and how to attack them
- **Static**: MobSF on the APK/IPA + unzip-and-grep. Check manifest/Info.plist, exported components, permissions, `allowBackup`/backup flags, ATS exceptions, embedded secrets, cleartext config.
- **Storage inspection**: drive the app, then inspect the sandbox (SQLite, prefs, caches, logs) for plaintext tokens/PII; confirm Keychain/Keystore use and that logout + account deletion wipe local data.
- **Network**: intercept with mitmproxy; verify TLS, pinning behavior, no tokens in URLs, what third parties receive, behavior with an untrusted CA.
- **Platform**: fuzz deep links/intents for auth bypass and parameter injection; audit WebView config; check sensitive-screen screenshot/app-switcher exposure.
- **Resilience (if in scope)**: Frida/objection on an emulator to test detections and client-side control bypass.

## Tools (Docker-first, never install system-wide without PO approval; pin tags)
- `opensecurity/mobile-security-framework-mobsf:latest` (port 8000) — static + dynamic analysis.
- `mitmproxy`/`mitmdump` — traffic interception.
- `semgrep` (`p/mobile`), `gitleaks`, `osv-scanner` — covered in `kb-api-cloud-security` too; the auditor runs these on source.
- `frida`/`objection` on emulator — runtime, resilience profile only.
Ask the director (who asks the PO) before the first image pull. Record image + tag in the report.

## Rules of engagement & workflow
- Authorized targets only: this company's own builds on this machine/emulator and the PO's staging. No production, no third-party apps, no DoS.
- Findings go to `state/security-findings.json` with a reproducible `repro`, MASVS/MASTG category, severity + CVSS, concrete `fix`, and owner. Status flow `open → fixed` (dev) `→ verified` (Cyber Security only); `accepted-risk` is PO-only.
- Severity by real exposure: plaintext credentials / broken TLS / exported component leaking data = High+; missing root detection on a low-risk app = Low.
