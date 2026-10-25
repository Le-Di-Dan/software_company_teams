---
name: resume-work
description: Resume the company after a usage pause or an API limit interruption - verify the handoffs in state/handoff/, re-dispatch every paused task to the same agent type with its handoff as input, archive the handoff files, and brief the PO. Use when SessionStart shows "RESUME MODE", or when the PO says "tiếp tục / resume" after a pause.
---

# Resume work after a pause

Only the delivery-director runs this. The usage breaker (`.claude/hooks/usage_guard.py`) still blocks dispatching while usage is at or above the soft limit, so first make sure it is below.

1. **Check usage.** Read `state/usage.json` and `state/project.json → usage_policy`. If the 5-hour percentage is still ≥ `soft_pct`, the 7-day percentage ≥ `seven_day_soft_pct` (default 95), or `state/handoff/PAUSE` exists, tell the PO in Vietnamese when usage resets (the `resets_at` time) and stop. A manual pause ends when the PO runs `! rm state/handoff/PAUSE`.
2. **Read the handoffs.** `state/handoff/HANDOFF.md` (if written), every `state/handoff/<agent>-<id>.md`, and `state/handoff/INTERRUPTED.json` (agents cut off by an API limit before they could write a handoff).
3. **Verify, don't trust.** For each "Done" item, check the file exists and is complete. For each "In progress" file, open it and confirm where it stops. For interrupted agents without a handoff, look up their activity in `state/activity.jsonl` (`"id": "<id>"` lines: files read/written) and inspect those files; decide "continue" or "redo" and write that decision into the resume brief.
4. **Archive before dispatching.** Move the handoff files to `state/handoff/archive/<YYYYMMDD-HHMM>/` (keep `INTERRUPTED.json` there too) and delete the `state/handoff/.*.paused` markers. A new pause during the resume then writes fresh files that can't be confused with old ones.
5. **Re-dispatch** each unfinished task as a **new Agent call** of the **same agent type** (never SendMessage to the paused agent: its cache is long gone and its context would be re-billed in full), parallel where independent, ≤3 at a time, using the normal delegation brief plus:
   - `Handoff: state/handoff/archive/<stamp>/<file>.md`: read it first; do not redo items listed under Done after verifying them.
   - The partial file(s) to continue and the exact remaining work.
   Follow the current phase's SOP for anything that comes after the resumed tasks.
6. **Record.** Append to `state/progress.md`: `<date> resumed after pause: <agents re-dispatched>, <archive path>`. Tell the PO in 2–3 Vietnamese lines what resumed and what is still waiting on them.
