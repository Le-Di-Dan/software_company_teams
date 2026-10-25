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

sys.stdout.write("\n".join(lines) + "\n")
