"""PreToolUse hook for Bash: keeps PO-only and destructive actions out of agents' hands.

- Store submission / production release commands run only after the PO ran scripts/approve-release.sh.
  Convention: fastlane lanes named `beta*` go to TestFlight / internal / closed testing (allowed);
  lanes named `release*` / `production*` submit for review or production (gated).
- Obviously destructive commands are blocked outright.
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()

CMD_START = r"(?:^|[;&|]\s*|\bexec\s+)(?:bundle\s+exec\s+)?"
RELEASE_PATTERNS = [
    CMD_START + r"fastlane\s+(?:\w+\s+)?(?:release|production|submit|deliver|appstore)\w*\b",
    CMD_START + r"(?:fastlane\s+)?(?:deliver|upload_to_app_store)\b",
    # Play uploads default to the production track, so only an explicit testing track is allowed.
    CMD_START + r"(?:fastlane\s+)?(?:supply|upload_to_play_store)\b(?!.*--track[= ]+['\"]?(?:internal|alpha|beta|closed)\b)",
    r"\bxcrun\s+altool\b.*--upload-app",
    r"\beas\s+submit\b",
    r"--track[= ]+['\"]?production\b",
    r"\bsubmit_for_review\b",
]

DESTRUCTIVE_PATTERNS = [
    (r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*\s+(?:/|~|\$HOME|\.\.?)(?:\s|$|/\*)", "recursive delete of root, home or the repo"),
    (r"\bgit\s+push\b.*(?:--force\b|\s-f\b)", "force-push"),
    (r"\bgit\s+reset\s+--hard\s+origin", "hard reset discarding local work"),
    (r"\b(?:firebase\s+projects:delete|supabase\s+projects\s+delete)\b", "deleting a cloud project"),
    (r"\bmkfs\b|\bdd\s+if=.*of=/dev/", "disk-level write"),
    (r"approve-release\.sh", "PO-only approval; the PO runs it with `! bash scripts/approve-release.sh`"),
]


def release_approved():
    try:
        project = json.loads((ROOT / "state" / "project.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return bool(project.get("po_release_approval"))


def main():
    data = json.load(sys.stdin)
    command = (data.get("tool_input") or {}).get("command", "")
    for pattern, label in DESTRUCTIVE_PATTERNS:
        if re.search(pattern, command):
            sys.stderr.write(f"[company guard] BLOCKED ({label}): {command}\n")
            sys.exit(2)
    for pattern in RELEASE_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE | re.MULTILINE) and not release_approved():
            sys.stderr.write(
                "[company guard] BLOCKED: store submission / production release is a PO-only action. "
                "Prepare everything in docs/08-release/ and ask the director to request gate G3. "
                "The PO approves with `! bash scripts/approve-release.sh`.\n"
            )
            sys.exit(2)


if __name__ == "__main__":
    main()
