---
name: kb-engineering-workflow
description: Build-loop protocol for every engineer agent - startup routine, one feature at a time, test-first, verification evidence, feature_list.json rules, cross-machine tagging and hand-off format.
user-invocable: false
---

# Engineering build-loop protocol

Adapted from Anthropic's harness for long-running agents: state lives in files and git, not in memory.

## 1. Startup (every assignment)
1. `pwd`; read `state/environment.md` (what this machine can build/run).
2. Read the last entries of `state/progress.md` and `git log --oneline -15` (if git exists).
3. Read your feature in `state/feature_list.json` (id from the brief): acceptance, verification, depends_on, platforms.
4. Read the story (`docs/02-product/user-stories.md`), screen specs (`docs/04-design/screens/`), design tokens, architecture docs and ADRs relevant to it. Load the stack KB skill.
5. Run the smoke check (`bash scripts/smoke.sh` if it exists, else the stack's build + test command) through `bash scripts/check.sh` (kb-run-checks). If it's already broken, fix or report that first — never build on a broken base.

## 2. Implement one feature
- Scope = exactly this feature's acceptance criteria. No drive-by refactors; note them as suggestions instead.
- Test-first where practical: write the failing test from the acceptance criteria, then make it pass.
- UI: use design tokens and components from the design system; implement every state in the spec (loading, empty, error, offline, success); add accessibility labels and stable test ids.
- Keep secrets out of code; read config from env/config files documented in `docs/05-architecture/secrets.md`.

## 3. Verify (evidence or it didn't happen)
- Run every command in the feature's `verification` list plus lint/typecheck/unit tests for touched modules, each through `bash scripts/check.sh` (kb-run-checks): on failure read the reported log lines, fix, re-run only the failures, then the full check once.
- UI features: run on simulator/emulator available on this machine and save screenshots to `docs/07-qa/evidence/<feature-id>/`.
- If a verification step needs the other machine, run everything you can and tag the rest `needs: mac` or `needs: windows` in the feature's `notes`.

## 4. Update feature_list.json (hook-enforced rules)
- You may only change `passes`, `evidence`, `notes`, `owner` of existing features.
- Set `passes: true` only when all verification passed here; put the commands and results summary (or report path) in `evidence`.
- Never delete features or edit acceptance/verification/title/status: that requires an approved change request.

## 5. Hand-off (your final message)
```
Feature: F-xxx — <title>
Result: DONE | PARTIAL (needs: …) | BLOCKED (reason)
Files changed: …
Verification: <command> → <result> (one line each)
Evidence: <paths>
Notes for reviewer / other teams: …
Questions for PO: …
```
The director commits after code review approves; don't push.

## Cross-machine rules
- macOS (Xcode, iOS simulator, Flutter) and Windows (Android SDK, emulators, full toolchain). Scripts must work in bash on both (Git Bash on Windows): no GNU-only flags, LF line endings.
- Don't install system-wide tools without the PO's approval; project-local dependencies (npm/pub/pip in venv/go mod) are fine.
