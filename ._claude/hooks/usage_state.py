"""Shared reader for the usage circuit breaker (imported by usage_probe, usage_guard, session_start).

state/usage.json is written by the status line (usage_probe.py) from Claude Code's `rate_limits` data
(Pro/Max plans) and session cost. state/account.json (machine-local) records this machine's account plan,
detected by detect_plan() at session start: api | pro | max5x | max20x.

Thresholds depend on the plan. The work that still runs after a trip (subagents finishing their task, then
writing handoffs) costs about the same tokens on every plan, so a bigger plan needs a smaller share of its
window as headroom:
              5-hour soft/hard   7-day soft/hard
  pro             75 / 80            95 / 98
  max5x           82 / 88            96 / 98
  max20x          88 / 93            97 / 99
  api             85 / 95 of budget_usd (pay as you go: no plan windows, only a budget can stop it)
soft: director may not dispatch new subagent work; hard: everyone stops and writes a handoff to state/handoff/.
The 7-day window trips close to its limit: 75% of a week still leaves several 5-hour sessions, and a 7-day
pause lasts days.

state/project.json -> usage_policy (all optional):
  plan        "auto" (default: detected) or one of the plans above
  budget_usd  (default null) for API sessions without rate_limits: session cost / budget = usage %
  soft_pct, hard_pct, seven_day_soft_pct, seven_day_hard_pct   override the table for every plan
  plans       e.g. {"max5x": {"soft_pct": 85}}                  override it for one plan
Each window is judged against its own thresholds; the most severe level wins.
A file state/handoff/PAUSE forces the hard level (manual pause, e.g. to test the mechanism).
"""
import json
import os
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
STATE = ROOT / "state"
HANDOFF = STATE / "handoff"
ACCOUNT = STATE / "account.json"
PLANS = {
    "pro": {"soft_pct": 75, "hard_pct": 80, "seven_day_soft_pct": 95, "seven_day_hard_pct": 98},
    "max5x": {"soft_pct": 82, "hard_pct": 88, "seven_day_soft_pct": 96, "seven_day_hard_pct": 98},
    "max20x": {"soft_pct": 88, "hard_pct": 93, "seven_day_soft_pct": 97, "seven_day_hard_pct": 99},
    "api": {"soft_pct": 85, "hard_pct": 95, "seven_day_soft_pct": 95, "seven_day_hard_pct": 98},
}
PLAN_LABEL = {"api": "API", "pro": "Pro", "max5x": "Max 5x", "max20x": "Max 20x"}
FALLBACK_PLAN = "pro"  # subscription of unknown size: the plan with the least headroom
THRESHOLD_KEYS = ("soft_pct", "hard_pct", "seven_day_soft_pct", "seven_day_hard_pct")
DEFAULTS = {"plan": "auto", "budget_usd": None, "plans": {}}
SEVERITY = {"ok": 0, "soft": 1, "hard": 2}
WINDOW_VI = {"five_hour": "giới hạn 5 giờ", "seven_day": "giới hạn 7 ngày", "budget": "ngân sách USD", "manual": "PO tạm dừng thủ công"}


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


# ---------- account plan ----------

def _oauth_account():
    """oauthAccount from Claude Code's global config (~/.claude.json): profile fields only, no tokens."""
    cfg = os.environ.get("CLAUDE_CONFIG_DIR")
    path = Path(cfg) / ".claude.json" if cfg else Path.home() / ".claude.json"
    return (read_json(path) or {}).get("oauthAccount") or {}


def _subscription_plan(subscription, oauth):
    """Map subscriptionType / organizationType plus the rate-limit tier to pro|max5x|max20x."""
    sub = (subscription or oauth.get("organizationType") or "").lower()
    tier = " ".join(str(oauth.get(k) or "") for k in ("organizationRateLimitTier", "userRateLimitTier")).lower()
    if "pro" in sub:
        return "pro"
    if "20x" in tier:
        return "max20x"
    if "5x" in tier or "max" in sub:
        return "max5x"  # Max with no readable tier: assume the smaller one
    return FALLBACK_PLAN  # pro, team, enterprise: Pro-sized headroom unless the tier says otherwise


def _cli_status():
    """`claude auth status --json`, or None when the CLI is missing, slow or not logged in."""
    exe = shutil.which("claude")
    if not exe:
        return None
    try:
        out = subprocess.run([exe, "auth", "status", "--json"], capture_output=True, text=True, timeout=20,
                             stdin=subprocess.DEVNULL).stdout
        status = json.loads(out)
    except (OSError, subprocess.SubprocessError, ValueError):
        return None
    return status if isinstance(status, dict) and status.get("loggedIn") else None


def detect_plan(run_cli=True):
    """Work out which account Claude Code uses on this machine: {plan, source, detail}."""
    oauth = _oauth_account()
    status = _cli_status() if run_cli else None
    if status:
        method, provider = status.get("authMethod"), status.get("apiProvider") or "firstParty"
        if provider != "firstParty":
            return {"plan": "api", "source": "claude auth status", "detail": f"provider {provider}"}
        if method == "claude.ai":
            sub = status.get("subscriptionType")
            return {"plan": _subscription_plan(sub, oauth), "source": "claude auth status",
                    "detail": f"subscription {sub}, tier {oauth.get('organizationRateLimitTier')}"}
        return {"plan": "api", "source": "claude auth status", "detail": f"auth {method}"}
    if any(os.environ.get(k) for k in ("CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY",
                                       "ANTHROPIC_API_KEY")):
        return {"plan": "api", "source": "environment", "detail": "API key or cloud provider in env"}
    if oauth.get("organizationType") or oauth.get("organizationRateLimitTier"):
        return {"plan": _subscription_plan(None, oauth), "source": "~/.claude.json",
                "detail": f"{oauth.get('organizationType')}, tier {oauth.get('organizationRateLimitTier')}"}
    return {"plan": FALLBACK_PLAN, "source": "fallback", "detail": "no account info found"}


def save_account(acc):
    acc = {**acc, "ts": time.time()}
    try:
        tmp = STATE / "account.json.tmp"
        tmp.write_text(json.dumps(acc), encoding="utf-8")
        os.replace(tmp, ACCOUNT)
    except OSError:
        pass
    return acc


def account():
    """This machine's cached plan; detects it from local files (no CLI call) when there is no cache yet."""
    acc = read_json(ACCOUNT)
    if not acc or acc.get("plan") not in PLANS:
        acc = save_account(detect_plan(run_cli=False))
    return acc


# ---------- policy ----------

def policy(plan=None):
    """usage_policy with the plan's thresholds filled in (plan: configured, else detected)."""
    project = read_json(STATE / "project.json") or {}
    raw = project.get("usage_policy") or {}
    pol = {**DEFAULTS, **raw}
    if plan is None:
        plan = pol["plan"] if pol["plan"] in PLANS else account()["plan"]
    pol["plan"] = plan
    pol.update(PLANS[plan])
    pol.update({k: raw[k] for k in THRESHOLD_KEYS if k in raw})
    pol.update({k: v for k, v in ((pol.get("plans") or {}).get(plan) or {}).items() if k in THRESHOLD_KEYS})
    return pol


def window_policy(pol=None):
    """Policy for the 5-hour/7-day windows. Only subscriptions send them, so on an 'api' plan detection was
    wrong (e.g. an API key in env while the claude.ai login is in use): fall back to the most cautious plan."""
    pol = pol or policy()
    return policy(FALLBACK_PLAN) if pol["plan"] == "api" else pol


def thresholds(window, pol=None):
    """(soft, hard) percentages for a usage window."""
    pol = pol or policy()
    if window == "seven_day":
        return float(pol["seven_day_soft_pct"]), float(pol["seven_day_hard_pct"])
    return float(pol["soft_pct"]), float(pol["hard_pct"])


def current(now=None):
    """Return {level: ok|soft|hard, pct, window, resets_at, soft, hard, plan} for the most severe live window
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
    if windows:
        pol = window_policy(pol)
    elif pol.get("budget_usd") and usage.get("session_cost_usd") is not None:
        windows.append({"pct": 100.0 * usage["session_cost_usd"] / float(pol["budget_usd"]), "window": "budget",
                        "resets_at": None})
    for w in windows:
        w["soft"], w["hard"] = thresholds(w["window"], pol)
        w["level"] = "hard" if w["pct"] >= w["hard"] else "soft" if w["pct"] >= w["soft"] else "ok"
    soft, hard = thresholds("five_hour", pol)
    best = max(windows, key=lambda w: (SEVERITY[w["level"]], w["pct"] / w["soft"] if w["soft"] else 0),
               default={"pct": None, "window": None, "resets_at": None, "soft": soft, "hard": hard, "level": "ok"})
    best = {**best, "plan": pol["plan"]}
    if (HANDOFF / "PAUSE").exists():
        best = {**best, "window": "manual", "level": "hard"}
    return best


def describe(u):
    """Short Vietnamese/English-neutral description, e.g. '82% of five_hour usage (Max 5x plan, pause at 88%)'."""
    parts = []
    if u["window"] == "manual":
        parts.append("manual pause (state/handoff/PAUSE)")
    if u["pct"] is not None:
        plan = f" ({PLAN_LABEL.get(u.get('plan'), u.get('plan'))} plan, pause at {u['hard']:.0f}%)" if u.get("plan") else ""
        parts.append(f"{u['pct']:.0f}% of {u['window'] if u['window'] != 'manual' else 'plan'} usage{plan}")
    if u["resets_at"]:
        parts.append("resets at " + datetime.fromtimestamp(u["resets_at"]).strftime("%H:%M %d/%m"))
    return ", ".join(parts) or "usage unknown"
