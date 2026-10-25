"""Shared reader for the usage circuit breaker (imported by usage_probe, usage_guard, session_start).

state/usage.json is written by the status line (usage_probe.py) from Claude Code's `rate_limits` data
(Pro/Max plans) and session cost. The policy lives in state/project.json -> usage_policy:
  soft_pct   (default 75)  director may not dispatch new subagent work
  hard_pct   (default 80)  everyone stops and writes a handoff to state/handoff/
  budget_usd (default null) for API-key sessions without rate_limits: session cost / budget = usage %
A file state/handoff/PAUSE forces the hard level (manual pause, e.g. to test the mechanism).
"""
import json
import os
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
STATE = ROOT / "state"
HANDOFF = STATE / "handoff"
DEFAULTS = {"soft_pct": 75, "hard_pct": 80, "budget_usd": None}
WINDOW_VI = {"five_hour": "giới hạn 5 giờ", "seven_day": "giới hạn 7 ngày", "budget": "ngân sách USD", "manual": "PO tạm dừng thủ công"}


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def policy():
    project = read_json(STATE / "project.json") or {}
    return {**DEFAULTS, **(project.get("usage_policy") or {})}


def current(now=None):
    """Return {level: ok|soft|hard, pct, window, resets_at, soft, hard} for the highest live window."""
    now = now or time.time()
    pol = policy()
    usage = read_json(STATE / "usage.json") or {}
    best = {"pct": None, "window": None, "resets_at": None}
    for key in ("five_hour", "seven_day"):
        w = usage.get(key) or {}
        pct, resets = w.get("used_percentage"), w.get("resets_at")
        if pct is None or (resets and resets <= now):
            continue  # window absent or already reset
        if best["pct"] is None or pct > best["pct"]:
            best = {"pct": float(pct), "window": key, "resets_at": resets}
    if best["pct"] is None and pol.get("budget_usd") and usage.get("session_cost_usd") is not None:
        best = {"pct": 100.0 * usage["session_cost_usd"] / float(pol["budget_usd"]), "window": "budget", "resets_at": None}
    if (HANDOFF / "PAUSE").exists():
        best = {"pct": best["pct"], "window": "manual", "resets_at": best["resets_at"]}
        level = "hard"
    elif best["pct"] is None:
        level = "ok"
    else:
        level = "hard" if best["pct"] >= pol["hard_pct"] else "soft" if best["pct"] >= pol["soft_pct"] else "ok"
    return {"level": level, "soft": pol["soft_pct"], "hard": pol["hard_pct"], **best}


def describe(u):
    """Short Vietnamese/English-neutral description, e.g. '82% of the 5-hour limit, resets 14:30'."""
    parts = []
    if u["window"] == "manual":
        parts.append("manual pause (state/handoff/PAUSE)")
    if u["pct"] is not None:
        parts.append(f"{u['pct']:.0f}% of {u['window'] if u['window'] != 'manual' else 'plan'} usage")
    if u["resets_at"]:
        parts.append("resets at " + datetime.fromtimestamp(u["resets_at"]).strftime("%H:%M %d/%m"))
    return ", ".join(parts) or "usage unknown"
