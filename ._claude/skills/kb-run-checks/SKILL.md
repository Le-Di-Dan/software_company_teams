---
name: kb-run-checks
description: How to run build, test, lint and typecheck commands cheaply - once, through scripts/check.sh, reading only the failing part of the kept log; re-running only the failures; long runs in the background.
user-invocable: false
---

# Running checks (build / test / lint / typecheck)

A failing 10-minute test run must cost one run, not three. Run every such command through the check runner:
```
bash scripts/check.sh <name> [-C <dir>] -- <command>
bash scripts/check.sh unit -C apps/mobile -- flutter test
bash scripts/check.sh typecheck -C services/api -- npx tsc --noEmit
```
Call it from the project root; `-C` is the directory the command runs in. Name checks by what they verify (`unit`, `widget`, `typecheck`, `lint`, `api-tests`). A plain `flutter test`, `npx tsc`, `pytest`, `./gradlew …` is rewritten to `check.sh auto` by a hook, and the same commands piped into `tail`/`grep` or redirected to a file are blocked.

## What you get
- Pass: one line, `✔ unit PASS · 4m12s · 309 passed · log: …`. Move on.
- Fail: each failing test or error with the **line range in the log**, plus the command that re-runs only the failures. The full log (colors and progress redraws stripped) is in `state/runs/<name>/`.
- Cached: same command, same code (git HEAD + uncommitted + untracked changes) as the last run returns that run's result instantly. A cached FAIL means you haven't changed anything yet: fix first.

## Rules
1. **Never re-run a command to see its output.** Read the reported ranges with Read `offset`/`limit`, or `Grep -n` the log. Don't read the whole log.
2. **Fix, then re-run only the failures** with the printed `<name>~rerun` command (seconds instead of minutes). When they pass, run the full check **once** at the end.
3. **Long checks** (the summary says when a run took over 90 s): start them with the Bash tool's `run_in_background: true` and keep working, or wait for the completion notice; the output you get is still just the summary. Otherwise set the Bash `timeout` (up to 600000 ms) so the run isn't cut off and restarted.
4. `--fresh` only when you believe the result is flaky or depends on the environment (emulator, network, staging). E2E/integration runs and builds are never cached.
5. **Evidence**: put the one-line summary in `feature_list.json` `evidence` or your report, not log text. When a log must be kept (QA report, release), add `--keep <feature-id>`: it is copied to `docs/07-qa/evidence/<feature-id>/`.
6. Logs clean themselves up: a pass deletes the check's failed logs and its `~rerun` checks; old or oversized logs are pruned. Don't delete or move files in `state/runs/` yourself.
