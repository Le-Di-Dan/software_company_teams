"""SessionStart hook: inject the company's current state so every session resumes in the right phase."""
import json
import os
import sys
from pathlib import Path

root = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
state = root / "state"


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


lines = ["# Company state (auto-loaded)"]
project = read_json(state / "project.json")
if project is None:
    lines.append("state/project.json missing or invalid. Run the `company-status` skill to repair it.")
else:
    lines.append(f"- App: {project.get('app_name') or '(not named yet)'}")
    lines.append(f"- Phase: {project.get('phase')} ({project.get('phase_status')})")
    gates = project.get("gates", {})
    lines.append("- Gates: " + ", ".join(f"{k}={v}" for k, v in gates.items()))
    stack = project.get("stack", {})
    lines.append("- Stack: " + ", ".join(f"{k}={v}" for k, v in stack.items()))
    cost = project.get("cost_policy") or {}
    lines.append(f"- Cost policy: profile={cost.get('profile', 'economy')}, max_parallel={cost.get('max_parallel', 3)}, "
                 f"doc_language={project.get('doc_language', 'en')} (see 'Cost discipline' in your instructions)")

features = read_json(state / "feature_list.json")
if features and features.get("features"):
    items = features["features"]
    done = sum(1 for f in items if f.get("passes"))
    lines.append(f"- Features passing: {done}/{len(items)} (locked={features.get('locked', False)})")

findings = read_json(state / "security-findings.json")
if findings and findings.get("findings"):
    items = findings["findings"]
    blocking = [f for f in items if str(f.get("severity", "")).lower() in ("critical", "high")
                and f.get("status") not in ("verified", "accepted-risk")]
    if blocking:
        lines.append(f"- ⚠ Security: {len(blocking)} open Critical/High finding(s) (state/security-findings.json) — these block gate G3")

questions = state / "open-questions.md"
if questions.exists():
    open_count = sum(1 for line in questions.read_text(encoding="utf-8").splitlines() if line.startswith("- [ ]"))
    if open_count:
        lines.append(f"- Open PO questions: {open_count} (state/open-questions.md)")

env_file = state / "environment.md"
if not env_file.exists():
    lines.append("- state/environment.md missing: run `bash scripts/env-doctor.sh` before toolchain work.")

progress = state / "progress.md"
if progress.exists():
    tail = [l for l in progress.read_text(encoding="utf-8").splitlines() if l.strip()][-8:]
    if tail:
        lines.append("\n## Last progress entries")
        lines.extend(tail)

# Resume mode: work was paused by usage_guard.py or cut off by an API limit.
handoff_dir = state / "handoff"
handoffs = sorted(p for p in handoff_dir.glob("*.md")) if handoff_dir.is_dir() else []
interrupted = read_json(handoff_dir / "INTERRUPTED.json")
if handoffs or interrupted:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import usage_state as us

    u = us.current()
    lines.append("\n## RESUME MODE: company work was paused")
    for p in handoffs:
        lines.append(f"- handoff: {p.relative_to(root).as_posix()}")
    for a in (interrupted or {}).get("unfinished", []):
        lines.append(f"- interrupted without handoff (API {interrupted.get('error')}): {a.get('agent')} "
                     f"id={a.get('id')} task=\"{a.get('desc') or '?'}\"")
    if u["level"] == "ok":
        lines.append("Usage is below the soft limit. Before anything else run the `resume-work` skill: verify the "
                     "handoffs, re-dispatch each paused task to the same agent type, archive the handoff files.")
    else:
        lines.append(f"Usage is still {u['level']} ({us.describe(u)}). Do NOT dispatch work. Greet the PO, explain "
                     "in Vietnamese that the company resumes after the reset, and stop.")

sys.stdout.write("\n".join(lines) + "\n")
