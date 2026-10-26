"""Activity hook for the HQ dashboard: appends one JSON line per agent event to state/activity.jsonl.

Registered on SubagentStart, SubagentStop, UserPromptSubmit, Stop and PreToolUse (Agent + file/search/web
tools). It never blocks and never prints: any error is swallowed so a broken log can't stall the company.

Events (field `ev`):
  assign  director launches a subagent (PreToolUse Agent): agent, desc, bg
  start   a subagent starts (SubagentStart): agent, id
  stop    a subagent finishes (SubagentStop): agent, id, msg (first line of its final answer, trimmed)
  tool    a subagent uses a tool (PreToolUse with agent_id): agent, id, tool, target (repo-relative path,
          host or short label)
  po      the PO sent a message (UserPromptSubmit) - content is NOT logged
  idle    the main session finished its turn and waits for the PO (Stop)

The file is machine-local (gitignored) and rotated at ~512 KB. Set COMPANY_ACTIVITY=0 to disable.
scripts/dashboard.py reads it to animate the HQ map.
"""
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
LOG = ROOT / "state" / "activity.jsonl"
MAX_BYTES = 512 * 1024
KEEP_LINES = 400
TOOLS = {"Read", "Write", "Edit", "MultiEdit", "Grep", "Glob", "Bash", "WebSearch", "WebFetch"}


def clip(text, n):
    text = " ".join(str(text or "").split())
    return text if len(text) <= n else text[: n - 1] + "…"


def rel(path):
    if not path:
        return ""
    p = Path(path)
    try:
        return p.resolve().relative_to(ROOT).as_posix() if p.is_absolute() else p.as_posix()
    except ValueError:
        return p.name


def tool_target(tool, ti):
    if tool in ("Read", "Write", "Edit", "MultiEdit"):
        return rel(ti.get("file_path"))
    if tool == "Grep":
        return rel(ti.get("path")) or clip(ti.get("pattern"), 40)
    if tool == "Glob":
        return clip(ti.get("pattern"), 60)
    if tool == "WebFetch":
        return urlparse(ti.get("url") or "").netloc
    if tool == "WebSearch":
        return clip(ti.get("query"), 60)
    if tool == "Bash":
        # Only the program and its first argument: commands can carry tokens or paths we don't want logged.
        words = str(ti.get("command") or "").split()
        return " ".join(words[:2])[:40]
    return ""


def build_event(data):
    hook = data.get("hook_event_name")
    agent = data.get("agent_type") or ""
    agent_id = data.get("agent_id") or ""
    if hook == "SubagentStart":
        return {"ev": "start", "agent": agent, "id": agent_id}
    if hook == "SubagentStop":
        msg = str(data.get("last_assistant_message") or "").strip().splitlines()
        return {"ev": "stop", "agent": agent, "id": agent_id, "msg": clip(msg[0] if msg else "", 140)}
    if hook == "UserPromptSubmit":
        return {"ev": "po"}
    if hook == "Stop":
        return {"ev": "idle"}
    if hook != "PreToolUse":
        return None
    tool = data.get("tool_name") or ""
    ti = data.get("tool_input") or {}
    if tool in ("Agent", "Task") and not agent_id:
        return {"ev": "assign", "agent": ti.get("subagent_type") or "general-purpose",
                "desc": clip(ti.get("description"), 80), "bg": bool(ti.get("run_in_background"))}
    if agent_id and tool in TOOLS:
        return {"ev": "tool", "agent": agent, "id": agent_id, "tool": tool,
                "target": tool_target(tool, ti)}
    return None


def rotate():
    try:
        if LOG.stat().st_size <= MAX_BYTES:
            return
        lines = LOG.read_text(encoding="utf-8", errors="replace").splitlines()[-KEEP_LINES:]
        tmp = LOG.with_suffix(".jsonl.tmp")
        tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
        os.replace(tmp, LOG)
    except OSError:
        pass


def main():
    if os.environ.get("COMPANY_ACTIVITY") == "0" or not (ROOT / "state").is_dir():
        return
    event = build_event(json.load(sys.stdin))
    if not event:
        return
    event = {"ts": round(time.time(), 3), **event}
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    rotate()


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - the activity log must never block or break a tool call
        pass
    sys.exit(0)
