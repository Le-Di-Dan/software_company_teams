"""Usage circuit breaker (PreToolUse on every tool + StopFailure).

Levels come from usage_state.current() (state/usage.json written by the status line):
  Thresholds per window: 5-hour soft/hard 75/80, 7-day 95/98 (usage_state.py, state/project.json -> usage_policy).
  soft                            main session may not start or resume subagent work (Agent, SendMessage);
                                  running subagents finish their current task normally.
  hard                            every subagent is blocked except one Write of its handoff file, then must
                                  return "PAUSED: <path>"; the main session may only touch state/ to write
                                  state/handoff/HANDOFF.md, log progress and tell the PO when usage resets.
StopFailure with a rate-limit/billing error records state/handoff/INTERRUPTED.json (agents that were
running) so the next session can recover even when the breaker was too late.
Blocking = exit 2 with the reason on stderr (fed back to the model).
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import usage_state as us  # noqa: E402

ROOT = us.ROOT
FILE_TOOLS = {"Write", "Edit", "MultiEdit"}
READ_TOOLS = {"Read", "Glob", "Grep"}
DISPATCH_TOOLS = {"Agent", "Task", "SendMessage"}
HANDOFF_SECTIONS = (
    "# Handoff: <agent> - <task>\n"
    "## Task (original objective, inputs, output paths, definition of done)\n"
    "## Done (each item with the file path that proves it)\n"
    "## In progress (file + exactly where you stopped; is the file complete or partial?)\n"
    "## Next steps (ordered, concrete enough for a fresh agent)\n"
    "## Open questions / risks\n"
    "## How to verify (commands or checks)"
)


def block(msg):
    sys.stderr.write(msg + "\n")
    sys.exit(2)


def rel_path(file_path):
    if not file_path:
        return ""
    p = Path(file_path)
    p = p if p.is_absolute() else ROOT / p
    try:
        return p.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def log_activity(event):
    try:
        with open(us.STATE / "activity.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": round(time.time(), 3), **event}, ensure_ascii=False) + "\n")
    except OSError:
        pass


def first_time(marker_name):
    """True once per pause episode per agent (marker files live in state/handoff/, gitignored)."""
    marker = us.HANDOFF / marker_name
    if marker.exists():
        return False
    try:
        us.HANDOFF.mkdir(parents=True, exist_ok=True)
        marker.write_text(str(time.time()), encoding="utf-8")
    except OSError:
        pass
    return True


def guard_subagent(data, u, why):
    tool, ti = data.get("tool_name") or "", data.get("tool_input") or {}
    agent, agent_id = data.get("agent_type") or "agent", data.get("agent_id") or "x"
    handoff = f"state/handoff/{agent}-{agent_id[:8]}.md"
    if tool in FILE_TOOLS and rel_path(ti.get("file_path")) == handoff:
        return
    if (ROOT / handoff).exists():
        block(f"[usage guard] PAUSED ({why}). Your handoff is saved. Stop now: reply to the director with exactly "
              f"one line `PAUSED: {handoff}` and nothing else. Do not call any tool.")
    if first_time(f".{agent_id}.{int(u['resets_at'] or 0)}.paused"):
        log_activity({"ev": "pause", "agent": agent, "id": agent_id, "pct": u["pct"], "resets_at": u["resets_at"]})
    block(f"[usage guard] USAGE PAUSE ({why}). The company is stopping before the plan limit. Stop your task now "
          f"and do not start anything new. Make ONE Write call to `{handoff}` (that is the only tool allowed), "
          f"in the project's doc language, with these sections:\n{HANDOFF_SECTIONS}\n"
          f"Then reply to the director with exactly `PAUSED: {handoff}`.")


def guard_main(data, u, why):
    tool, ti = data.get("tool_name") or "", data.get("tool_input") or {}
    if tool in DISPATCH_TOOLS:
        if u["level"] == "soft":
            block(f"[usage guard] Usage soft limit ({why}): do not start or resume subagent work. Let running "
                  f"subagents finish, record what is still pending in state/progress.md, and tell the PO in "
                  f"Vietnamese that new work waits until usage resets.")
        block(f"[usage guard] USAGE PAUSE ({why}): no dispatching. Follow 'Usage limits & handoff' in your "
              f"instructions: collect the subagents' handoffs into state/handoff/HANDOFF.md and stop.")
    if u["level"] != "hard":
        return
    target = rel_path(ti.get("file_path") or ti.get("path") or ti.get("pattern") or "")
    if tool in FILE_TOOLS | READ_TOOLS and target.startswith("state/"):
        return
    if tool in ("AskUserQuestion", "TaskStop", "TaskOutput"):
        return
    if first_time(f".main.{int(u['resets_at'] or 0)}.paused"):
        log_activity({"ev": "pause", "agent": "delivery-director", "pct": u["pct"], "resets_at": u["resets_at"]})
    block(f"[usage guard] USAGE PAUSE ({why}). Only state/ may be read or written now. Wait for running "
          f"subagents to return `PAUSED: <path>`, then write state/handoff/HANDOFF.md (phase, which agents paused "
          f"with their handoff paths, what is done, what to dispatch first on resume, PO decisions pending), "
          f"append one line to state/progress.md, tell the PO in Vietnamese when usage resets and that they can "
          f"continue with `claude --continue` afterwards, then end your turn.")


def record_interruption(data):
    """Turn ended on an API limit before the breaker could act: remember who was mid-task."""
    started, stopped, descs = {}, set(), {}
    try:
        lines = (us.STATE / "activity.jsonl").read_text(encoding="utf-8").splitlines()[-400:]
    except OSError:
        lines = []
    pending = {}
    for line in lines:
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("ev") == "assign":
            pending.setdefault(e.get("agent"), []).append(e.get("desc"))
        elif e.get("ev") == "start":
            started[e.get("id")] = e.get("agent")
            queue = pending.get(e.get("agent")) or []
            descs[e.get("id")] = queue.pop(0) if queue else ""
        elif e.get("ev") == "stop":
            stopped.add(e.get("id"))
    unfinished = [{"agent": a, "id": i, "desc": descs.get(i, "")} for i, a in started.items() if i not in stopped]
    us.HANDOFF.mkdir(parents=True, exist_ok=True)
    (us.HANDOFF / "INTERRUPTED.json").write_text(json.dumps({
        "ts": time.time(), "error": data.get("error"), "details": data.get("error_details"),
        "unfinished": unfinished}, ensure_ascii=False, indent=2), encoding="utf-8")
    log_activity({"ev": "limit", "error": data.get("error")})


def main():
    data = json.load(sys.stdin)
    if not us.STATE.is_dir():
        return
    if data.get("hook_event_name") == "StopFailure":
        if data.get("error") in ("rate_limit", "billing_error"):
            record_interruption(data)
        return
    u = us.current()
    if u["level"] == "ok":
        return
    why = us.describe(u)
    if data.get("agent_id"):
        if u["level"] == "hard":
            guard_subagent(data, u, why)
    else:
        guard_main(data, u, why)


if __name__ == "__main__":
    main()
