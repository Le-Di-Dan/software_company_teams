"""Shared reader for the usage circuit breaker (imported by usage_probe, usage_guard, session_start).

state/usage.json is written by the status line (usage_probe.py) from Claude Code's `rate_limits` data
(Pro/Max plans) and session cost. The policy lives in state/project.json -> usage_policy:
  soft_pct   (default 75)  5-hour window (and budget): director may not dispatch new subagent work
  hard_pct   (default 80)  5-hour window (and budget): everyone stops and writes a handoff to state/handoff/
  seven_day_soft_pct (default 95), seven_day_hard_pct (default 98)  the same levels for the 7-day window.
             75% of a week still leaves several 5-hour sessions, and a 7-day pause lasts days, so it only
             trips close to the real limit.
  budget_usd (default null) for API-key sessions without rate_limits: session cost / budget = usage %
Each window is judged against its own thresholds; the most severe level wins.
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
DEFAULTS = {"soft_pct": 75, "hard_pct": 80, "seven_day_soft_pct": 95, "seven_day_hard_pct": 98, "budget_usd": None}
SEVERITY = {"ok": 0, "soft": 1, "hard": 2}
WINDOW_VI = {"five_hour": "giới hạn 5 giờ", "seven_day": "giới hạn 7 ngày", "budget": "ngân sách USD", "manual": "PO tạm dừng thủ công"}


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def policy():
    project = read_json(STATE / "project.json") or {}
    return {**DEFAULTS, **(project.get("usage_policy") or {})}


def thresholds(window, pol=None):
    """(soft, hard) percentages for a usage window."""
    pol = pol or policy()
    if window == "seven_day":
        return float(pol["seven_day_soft_pct"]), float(pol["seven_day_hard_pct"])
    return float(pol["soft_pct"]), float(pol["hard_pct"])


def current(now=None):
    """Return {level: ok|soft|hard, pct, window, resets_at, soft, hard} for the most severe live window
    (ties: the one closest to its soft threshold); soft/hard are that window's thresholds."""
    now = now or time.time()
    pol = policy()
    usage = read_json(STATE / "usage.json") or {}
    windows = []
    for key in ("five_hour", "seven_day"):
        w = usage.get(key) or {}
        pct, resets = w.get("used_percentage"), w.get("resets_at")
        if pct is None or (resets and resets <= now):
            continue  # window absent or already reset
        windows.append({"pct": float(pct), "window": key, "resets_at": resets})
    if not windows and pol.get("budget_usd") and usage.get("session_cost_usd") is not None:
        windows.append({"pct": 100.0 * usage["session_cost_usd"] / float(pol["budget_usd"]), "window": "budget",
                        "resets_at": None})
    for w in windows:
        w["soft"], w["hard"] = thresholds(w["window"], pol)
        w["level"] = "hard" if w["pct"] >= w["hard"] else "soft" if w["pct"] >= w["soft"] else "ok"
    soft, hard = thresholds("five_hour", pol)
    best = max(windows, key=lambda w: (SEVERITY[w["level"]], w["pct"] / w["soft"] if w["soft"] else 0),
               default={"pct": None, "window": None, "resets_at": None, "soft": soft, "hard": hard, "level": "ok"})
    if (HANDOFF / "PAUSE").exists():
        best = {**best, "window": "manual", "level": "hard"}
    return best


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
