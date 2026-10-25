"""Status line command: shows plan usage + context to the PO and records it in state/usage.json.

Claude Code pipes session JSON on stdin (see https://code.claude.com/docs/en/statusline): `rate_limits`
(Pro/Max only, after the first API response), `context_window.used_percentage`, `cost.total_cost_usd`.
usage_guard.py reads state/usage.json to pause the company before the plan limit is hit.
"""
import json
import os
import sys
import time
from pathlib import Path

data = json.load(sys.stdin)
os.environ.setdefault("CLAUDE_PROJECT_DIR", (data.get("workspace") or {}).get("project_dir") or data.get("cwd") or ".")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import usage_state as us  # noqa: E402

now = time.time()
previous = us.read_json(us.STATE / "usage.json") or {}
limits = data.get("rate_limits") or {}
record = {"ts": now, "session_id": data.get("session_id"),
          "context_pct": (data.get("context_window") or {}).get("used_percentage"),
          "session_cost_usd": (data.get("cost") or {}).get("total_cost_usd")}
for key in ("five_hour", "seven_day"):
    window = limits.get(key)
    if window is None:  # not sent yet this session: keep the last reading until its window resets
        old = previous.get(key) or {}
        window = old if old.get("resets_at") and old["resets_at"] > now else None
    record[key] = window

if us.STATE.is_dir():
    try:
        tmp = us.STATE / "usage.json.tmp"
        tmp.write_text(json.dumps(record), encoding="utf-8")
        os.replace(tmp, us.STATE / "usage.json")
    except OSError:
        pass

u = us.current(now)
GREEN, YELLOW, RED, DIM, RESET = "\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[0m"
color = {"ok": GREEN, "soft": YELLOW, "hard": RED}[u["level"]]
segs = []
for key, label in (("five_hour", "5h"), ("seven_day", "7d")):
    w = record.get(key) or {}
    if w.get("used_percentage") is not None and not (w.get("resets_at") and w["resets_at"] <= now):
        pct = float(w["used_percentage"])
        c = RED if pct >= u["hard"] else YELLOW if pct >= u["soft"] else GREEN
        bar = "█" * int(pct // 10) + "░" * (10 - int(pct // 10)) if key == "five_hour" else ""
        segs.append(f"{label} {c}{bar}{' ' if bar else ''}{pct:.0f}%{RESET}")
if not segs and record["session_cost_usd"] is not None:
    segs.append(f"${record['session_cost_usd']:.2f}")
if record["context_pct"] is not None:
    segs.append(f"{DIM}ctx {float(record['context_pct']):.0f}%{RESET}")
status = {"ok": "", "soft": f"{color}⚠ ngừng giao việc mới{RESET}", "hard": f"{color}⏸ TẠM DỪNG · viết bàn giao{RESET}"}[u["level"]]
if status:
    segs.append(status)
print(" · ".join(segs) or "usage: chờ phản hồi đầu tiên")
