"""PreToolUse cost policy: keeps the company's token burn down (state/project.json -> cost_policy).

Measured on the habit_app trial (phases 0-3): 96% of usage was Opus, 37% was cache writes from resuming
subagents whose prompt cache had expired, and agents re-read whole 50-120 KB docs dozens of times.

- Agent/Task: sets tool_input.model from the cost profile (returned as updatedInput, so the director never
  has to remember it). A cheaper model requested by the caller is kept; a dearer one is capped.
- SendMessage: blocked when the target subagent returned more than `resume_idle_min` minutes ago. Subagent
  prompt caches live 5 minutes; after that a resume re-bills its whole context (100-360K tokens each in the
  trial) as cache writes. A fresh agent that reads the files is cheaper.
- Read: a docs/, state/ or company/research/ text file over `read_max_kb` must be read in chunks of at
  most `read_max_lines` lines; the block message carries the file's heading outline with line numbers.
- Bash: cat/less/more/awk/bat dumps of those files are blocked, head/tail/sed -n only for small ranges.

Policy keys (all optional): profile (economy|balanced|quality), model_overrides {agent: model},
max_parallel, resume_idle_min, read_max_kb, read_max_lines. Any error fails open.
"""
import glob
import json
import re
import shlex
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import usage_state as us  # noqa: E402

ROOT = us.ROOT
DEFAULTS = {"profile": "economy", "model_overrides": {}, "max_parallel": 3, "resume_idle_min": 4,
            "read_max_kb": 30, "read_max_lines": 200}

# Agents that run on Opus per profile; every other company agent runs on Sonnet.
OPUS = {
    "economy": {"devils-advocate", "solution-architect", "code-reviewer", "product-manager", "security-lead"},
}
OPUS["balanced"] = OPUS["economy"] | {"business-rnd-researcher", "uiux-rnd-researcher", "ai-rnd-researcher",
                                      "monetization-strategist"}
OPUS["quality"] = OPUS["balanced"] | {"business-analyst", "store-compliance-officer", "privacy-legal-counsel"}
RANK = {"haiku": 0, "sonnet": 1, "opus": 2}
# Built-in helpers keep their own defaults (Explore already runs on a small model).
UNROUTED = {"Explore", "statusline-setup", "claude-code-guide"}

READ_SCOPES = ("docs/", "state/", "company/research/")
READ_EXTS = {".md", ".jsonl", ".txt", ".csv", ".log"}
DUMP_CMDS = {"cat", "less", "more", "awk", "bat", "nl"}
RANGE_CMDS = {"head", "tail", "sed"}


def block(msg):
    sys.stderr.write(msg + "\n")
    sys.exit(2)


def policy():
    project = us.read_json(us.STATE / "project.json") or {}
    return {**DEFAULTS, **(project.get("cost_policy") or {})}


# ---------- Agent: model routing ----------

def route_model(data, pol):
    ti = dict(data.get("tool_input") or {})
    agent = ti.get("subagent_type") or "general-purpose"
    if agent in UNROUTED:
        return
    profile = pol["profile"] if pol["profile"] in OPUS else "economy"
    target = (pol.get("model_overrides") or {}).get(agent)
    if target not in RANK:
        target = "opus" if agent in OPUS[profile] else "sonnet"
    requested = ti.get("model")
    if requested in RANK and RANK[requested] < RANK[target]:
        target = requested
    if requested == target:
        return
    ti["model"] = target
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "updatedInput": ti}}))


# ---------- SendMessage: no resuming cold subagents ----------

def last_event(agent_id):
    """(ev, ts, agent) of the newest start/stop event for this subagent id, from state/activity.jsonl."""
    try:
        lines = (us.STATE / "activity.jsonl").read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        if agent_id not in line:
            continue
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("id") == agent_id and e.get("ev") in ("start", "stop"):
            return e.get("ev"), float(e.get("ts") or 0), e.get("agent") or "agent"
    return None


def guard_resume(data, pol):
    to = str((data.get("tool_input") or {}).get("to") or "")
    found = last_event(to) if to else None
    if not found or found[0] != "stop":
        return
    _, ts, agent = found
    idle_min = (time.time() - ts) / 60
    if idle_min <= float(pol["resume_idle_min"]):
        return
    block(f"[cost guard] {agent} ({to}) returned {idle_min:.0f} min ago. A subagent's prompt cache expires after "
          f"5 minutes, so resuming it now re-bills its whole context (often 100-300K tokens). Start a fresh "
          f"`{agent}` Agent instead: give it the paths of its earlier output plus the new inputs or feedback "
          f"(files are the memory). SendMessage is only for follow-ups within "
          f"{pol['resume_idle_min']} minutes of the agent's last reply.")


# ---------- Read / Bash: read lean ----------

def scoped_big_file(path, pol):
    """Repo-relative path if `path` is an in-scope text file larger than the read limit, else None."""
    try:
        p = Path(path).resolve()
        rel = p.relative_to(ROOT).as_posix()
    except (OSError, ValueError):
        return None
    if not rel.startswith(READ_SCOPES) or p.suffix.lower() not in READ_EXTS or not p.is_file():
        return None
    return rel if p.stat().st_size > float(pol["read_max_kb"]) * 1024 else None


def outline(rel, limit=40):
    try:
        lines = (ROOT / rel).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return "", 0
    heads = [f"  {i}: {line[:90]}" for i, line in enumerate(lines, 1) if line.startswith("#")]
    more = f"\n  … {len(heads) - limit} more headings" if len(heads) > limit else ""
    return ("\n".join(heads[:limit]) + more) if heads else "  (no markdown headings)", len(lines)


def read_lean_msg(rel, pol, what):
    size_kb = (ROOT / rel).stat().st_size / 1024
    heads, n = outline(rel)
    return (f"[cost guard] {what} `{rel}` ({size_kb:.0f} KB, {n} lines) at once is too costly. Read only the "
            f"sections you need with Read offset/limit (≤{pol['read_max_lines']} lines per call) or `Grep -n`. "
            f"Do not re-read parts already in your context unless the file changed. Outline (line: heading):\n"
            f"{heads}")


def guard_read(data, pol):
    ti = data.get("tool_input") or {}
    rel = scoped_big_file(ti.get("file_path") or "", pol)
    if not rel:
        return
    limit = ti.get("limit")
    if isinstance(limit, int) and 0 < limit <= int(pol["read_max_lines"]):
        return
    block(read_lean_msg(rel, pol, "Reading all of"))


def range_lines(cmd, args):
    """Lines a head/tail/sed segment prints, or None when it can't be bounded."""
    joined = " ".join(args)
    if cmd in ("head", "tail"):
        if cmd == "tail" and re.search(r"(?:-n\s*|-)\+\d", joined):
            return None
        m = re.search(r"(?:-n\s*|--lines[= ]|-)\+?(\d+)\b", joined)
        return int(m.group(1)) if m else 10
    if cmd == "sed" and re.search(r"(?:^|\s)-[a-zA-Z]*n", joined):
        ranges = re.findall(r"(\d+)\s*,\s*(\d+)\s*p", joined)
        singles = re.findall(r"(?:^|['\"\s;])(\d+)p\b", joined)
        if not ranges and not singles:
            return None
        return sum(int(b) - int(a) + 1 for a, b in ranges) + len(singles)
    return None


def candidates(token, bases):
    if any(ch in token for ch in "*?["):
        found = []
        for base in bases:
            found += glob.glob(str(base / token)) if not token.startswith("/") else glob.glob(token)
        return found
    return [token] if token.startswith("/") else [str(base / token) for base in bases]


def guard_bash(data, pol):
    command = str((data.get("tool_input") or {}).get("command") or "")
    bases = [Path(data.get("cwd") or ROOT), ROOT]
    bases += [ROOT / d for d in re.findall(r"\bcd\s+([^\s;&|]+)", command) if not d.startswith("/")]
    bases += [Path(d) for d in re.findall(r"\bcd\s+(/[^\s;&|]+)", command)]
    for segment in re.split(r"\|\|?|;|&&|\n", command):
        try:
            words = shlex.split(segment)
        except ValueError:
            words = segment.split()
        if not words:
            continue
        cmd, args = Path(words[0]).name, words[1:]
        if cmd not in DUMP_CMDS | RANGE_CMDS:
            continue
        for token in args:
            if token.startswith(">"):
                break
            if token.startswith("-"):
                continue
            for path in candidates(token, bases):
                rel = scoped_big_file(path, pol)
                if not rel:
                    continue
                if cmd in RANGE_CMDS:
                    n = range_lines(cmd, args)
                    if n is not None and n <= int(pol["read_max_lines"]):
                        continue
                block(read_lean_msg(rel, pol, f"Dumping (`{cmd}`)"))


def main():
    data = json.load(sys.stdin)
    if not us.STATE.is_dir():
        return
    pol = policy()
    tool = data.get("tool_name") or ""
    if tool in ("Agent", "Task"):
        route_model(data, pol)
    elif tool == "SendMessage":
        guard_resume(data, pol)
    elif tool == "Read":
        guard_read(data, pol)
    elif tool == "Bash":
        guard_bash(data, pol)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001 - a broken cost policy must never stall the company
        sys.exit(0)
