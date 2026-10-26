"""Takeover engagements: the customer's existing app repository is cloned into client/ (scripts/setup.sh --takeover).

state/project.json carries `engagement: "takeover"` and a `takeover` block (source_repo, ref, baseline_sha,
owners). The customer's repo stays read-only for everyone until the PO approves gate TG1 (the direction chosen
from the assessment); afterwards code paths inside client/ follow `takeover.owners` and the built-in lanes.
Shared by guard_files.py, guard_bash.py, cost_guard.py and session_start.py.
"""
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
CLIENT = "client"


def project():
    try:
        return json.loads((ROOT / "state" / "project.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def active(proj=None):
    return (proj if proj is not None else project()).get("engagement") == "takeover"


def writable(proj=None):
    proj = proj if proj is not None else project()
    return (proj.get("gates") or {}).get("TG1_direction") == "approved"


def inner(rel):
    """Path inside the customer's repo for a repo-relative path under client/, else None."""
    if rel == CLIENT:
        return ""
    return rel[len(CLIENT) + 1:] if rel.startswith(CLIENT + "/") else None


def owner_for(proj, inner_path):
    """Agents `takeover.owners` assigns to a path inside client/ (longest matching prefix), or None."""
    best = None
    for prefix, agents in ((proj.get("takeover") or {}).get("owners") or {}).items():
        prefix = prefix.strip("/") + "/"
        if inner_path.startswith(prefix) and (best is None or len(prefix) > len(best[0])):
            best = (prefix, set(agents or []))
    return best[1] if best else None


def git(*args):
    """stdout of a git command in client/ ('' on any failure)."""
    try:
        out = subprocess.run(["git", "-C", str(ROOT / CLIENT), *args], capture_output=True, timeout=20)
        return out.stdout.decode("utf-8", "replace").strip() if out.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""
