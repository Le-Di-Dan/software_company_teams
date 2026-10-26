"""PreToolUse cost policy: keeps the company's token burn down (state/project.json -> cost_policy).

Measured on the habit_app trial (phases 0-3): 96% of usage was Opus, 37% was cache writes from resuming
subagents whose prompt cache had expired, and agents re-read whole 50-120 KB docs dozens of times.

- Agent/Task: sets tool_input.model from the cost profile (returned as updatedInput, so the director never
  has to remember it). A cheaper model requested by the caller is kept; a dearer one is capped.
- SendMessage: blocked when the target subagent returned more than `resume_idle_min` minutes ago. Subagent
  prompt caches live 5 minutes; after that a resume re-bills its whole context (100-360K tokens each in the
  trial) as cache writes. A fresh agent that reads the files is cheaper.
- Read: a docs/, state/ or company/research/ text file (in a takeover also the customer's docs, reports and
  data files under client/) over `read_max_kb` must be read in chunks of at most `read_max_lines` lines; the
  block message carries the file's heading outline with line numbers.
- Bash: cat/less/more/awk/bat dumps of those files are blocked, head/tail/sed -n only for small ranges.
- Bash: build/test/lint commands (flutter test, tsc, jest, pytest, gradlew, ...) are rewritten to run through
  scripts/check.sh, which keeps the full log in state/runs/ and returns a short summary with the failing line
  ranges, so a failure never has to be re-run just to see its output. The same commands piped into
  tail/grep/head or redirected to a file are blocked. The rewrite is auto-approved only when the original
  command is allowed by the permission rules; otherwise the normal permission prompt shows the wrapped command.

Policy keys (all optional): profile (economy|balanced|quality), model_overrides {agent: model},
max_parallel, resume_idle_min, read_max_kb, read_max_lines. Any error fails open.
"""
import fnmatch
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
# Takeover: the customer's repo (client/) often carries megabytes of docs, reports and evidence JSON.
CLIENT_SCOPE, CLIENT_EXTS = "client/", READ_EXTS | {".json", ".html", ".xml", ".yaml", ".yml"}
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
    ext = p.suffix.lower()
    in_scope = ((rel.startswith(READ_SCOPES) and ext in READ_EXTS)
                or (rel.startswith(CLIENT_SCOPE) and ext in CLIENT_EXTS))
    if not in_scope or not p.is_file():
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


# ---------- Bash: build/test commands through scripts/check.sh ----------

CHECK_TOOL = re.compile(r"""(?x) ^ (?:\w+=\S*\s+)* (?:(?:npx|bunx|pnpm\s+exec|yarn\s+exec|fvm)\s+)? (?:
      flutter\s+(?:test|analyze|build)\b | dart\s+(?:test|analyze)\b
    | (?:npm|pnpm|yarn|bun)\s+(?:test\b|run\s+(?:test|lint|build|typecheck|type-check|check)\S*)
    | (?:tsc|jest|vitest|eslint|pytest|mypy|pyright)\b | python3?\s+-m\s+pytest\b | ruff\s+check\b
    | go\s+(?:test|vet|build)\b | golangci-lint\s+run\b | (?:\./)?gradlew(?:\.bat)?\s | gradle\s
    | xcodebuild\b | swift\s+(?:test|build)\b | maestro\s+test\b )""")
NOT_A_CHECK = re.compile(r"--watch\b|\s-w\b|--version\b|--help\b|\s-h\b|\bxcodebuild\s+-(?:list|showsdks|version)\b")


def split_top(command):
    """[(segment, separator)] split on && || ; and newlines outside quotes."""
    parts, buf, quote, i = [], "", None, 0
    while i < len(command):
        c = command[i]
        if quote:
            buf += c
            if c == quote:
                quote = None
            elif c == "\\" and quote == '"' and i + 1 < len(command):
                buf += command[i + 1]
                i += 1
        elif c in "'\"":
            quote, buf = c, buf + c
        elif c == "\\" and i + 1 < len(command):
            buf += command[i:i + 2]
            i += 1
        elif command.startswith(("&&", "||"), i):
            parts.append((buf, command[i:i + 2]))
            buf, i = "", i + 1
        elif c in ";\n":
            parts.append((buf, c))
            buf = ""
        else:
            buf += c
        i += 1
    parts.append((buf, ""))
    return parts


def unquoted(segment):
    """The segment with quoted text blanked, so operators inside strings don't count."""
    return re.sub(r"'[^']*'|\"(?:\\.|[^\"\\])*\"", "''", segment)


def permission_rules():
    allow, deny = [], []
    for f in (ROOT / ".claude" / "settings.json", ROOT / ".claude" / "settings.local.json",
              Path.home() / ".claude" / "settings.json"):
        perms = (us.read_json(f) or {}).get("permissions") or {}
        allow += perms.get("allow") or []
        deny += perms.get("deny") or []
    return allow, deny


def rule_hits(rules, cmd):
    for rule in rules:
        m = re.fullmatch(r"Bash(?:\((.*)\))?", str(rule).strip())
        if not m:
            continue
        pat = m.group(1)
        if pat is None:
            return True
        if pat.endswith(":*"):
            pat = pat[:-2] + " *"
        if (pat.endswith(" *") and cmd == pat[:-2]) or fnmatch.fnmatchcase(cmd, pat):
            return True
    return False


def check_inner(segment):
    """The command an explicit `bash .../check.sh <name> ... -- <command>` call runs ('' for --clean/--prune)."""
    try:
        words = shlex.split(segment)
    except ValueError:
        return None
    if len(words) < 2 or not words[1].endswith("scripts/check.sh"):
        return None
    if "--" not in words:
        return "" if words[2:3] in (["--clean"], ["--prune"]) else None
    rest = words[words.index("--") + 1:]
    return rest[0] if len(rest) == 1 else shlex.join(rest)


def guard_checks(data):
    ti = dict(data.get("tool_input") or {})
    command = str(ti.get("command") or "")
    script = ROOT / "scripts" / "check.sh"
    if not script.is_file():
        return
    out, runs, changed, explicit = "", [], False, False
    for seg, sep in split_top(command):
        core = seg.strip()
        inner = check_inner(core)
        if inner is not None:
            runs.append(inner)
            explicit = True
        elif CHECK_TOOL.match(core) and not NOT_A_CHECK.search(core):
            outside = re.sub(r"\d?>&\d", "", unquoted(core))
            if outside.rstrip().endswith("&"):
                runs.append(core)  # backgrounded with &: leave it alone
            elif "|" in outside or re.search(r"[<>]", outside):
                block(f"[cost guard] Don't pipe or redirect `{' '.join(core.split()[:2])}` output: it hides the failure and "
                      f"you end up re-running a long command to see it. Run it through the check runner, which "
                      f"keeps the full log and prints the failures with their log line ranges:\n"
                      f"  bash scripts/check.sh <name> [-C <dir>] -- {shlex.quote(core)}\n"
                      f"(see the kb-run-checks skill)")
            else:
                lead, trail = seg[:len(seg) - len(seg.lstrip())], seg[len(seg.rstrip()):]
                seg = f"{lead}bash {shlex.quote(script.as_posix())} auto -- {shlex.quote(core)}{trail}"
                runs.append(core)
                changed = True
        else:
            runs.append(core)
        out += seg + sep
    if not changed and not explicit:
        return
    allow, deny = permission_rules()
    allowed = all(not r or r == "cd" or r.startswith("cd ") or (rule_hits(allow, r) and not rule_hits(deny, r))
                  for r in runs)
    result = {"hookEventName": "PreToolUse"}
    if changed:
        ti["command"] = out
        result["updatedInput"] = ti
    if allowed:
        result.update(permissionDecision="allow",
                      permissionDecisionReason="build/test command run through scripts/check.sh")
    elif not changed:
        return
    print(json.dumps({"hookSpecificOutput": result}))


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
        guard_checks(data)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001 - a broken cost policy must never stall the company
        sys.exit(0)
