"""PreToolUse hook for Bash: keeps PO-only and destructive actions out of agents' hands.

- Store submission / production release commands run only after the PO ran scripts/approve-release.sh.
  Convention: fastlane lanes named `beta*` go to TestFlight / internal / closed testing (allowed);
  lanes named `release*` / `production*` submit for review or production (gated).
- Obviously destructive commands are blocked outright.
- Takeover engagements (takeover.py): commands that touch the customer's repo in client/ may not change it
  until gate TG1 (git writes, in-place edits, deletes, redirects into it). Afterwards pushes go only to
  `company/*` branches, merging PRs stays the PO's, and `git clean` never runs there (it would delete the
  customer's .env and local data). Text matching is a safety net: each takeover phase also ends with
  `git -C client status` clean.
"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import takeover as tk  # noqa: E402

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


CLIENT_REF = r"(?:^|[\s'\"=:(/])(?:\./)?" + tk.CLIENT + r"(?:/|[\s'\";&|)]|$)"
GIT_WRITE = (r"\bgit\s+(?:-C\s+\S+\s+)?(?:(?:commit|merge|rebase|reset|revert|cherry-pick|am|apply|stash|pull|push"
             r"|tag|switch|checkout|worktree|rm|mv)\b|branch\s+(?!--list\b|-[avr]+\b|--show-current\b|--contains\b)\S)")
FILE_WRITE = (r"\b(?:sed|perl)\s+(?:-\w+\s+)*-i|\b(?:rm|mv|truncate|tee|chmod|unlink|rmdir)\s"
              r"|>>?\s*['\"]?(?:\./)?" + tk.CLIENT + r"/|\bcp\s.*\s['\"]?(?:\./)?" + tk.CLIENT + r"/\S*['\"]?\s*$")
PUSH = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?push\b([^;&|\n]*)")


def touches_client(command, cwd):
    try:
        if cwd and Path(cwd).resolve().is_relative_to(ROOT / tk.CLIENT):
            return True
    except (OSError, ValueError):
        pass
    return re.search(CLIENT_REF, command) is not None


def check_client(command, cwd):
    project = tk.project()
    if not tk.active(project) or not touches_client(command, cwd):
        return
    if re.search(r"\bgit\s+(?:-C\s+\S+\s+)?clean\b(?!.*\s-n\b|.*--dry-run)", command):
        block("git clean in the customer's repo (deletes their untracked .env and local data)")
    if re.search(r"\bgh\s+pr\s+merge\b", command):
        block("merging a PR into the customer's repo is the PO's decision; they merge on GitHub")
    if not tk.writable(project):
        if re.search(GIT_WRITE, command) or re.search(FILE_WRITE, command, re.MULTILINE):
            block("the customer's repo in client/ is read-only until the PO approves gate TG1; builds and tests "
                  "may run, nothing may change. Record the change you want as a finding in state/findings.json")
        return
    for m in PUSH.finditer(command):
        args = m.group(1)
        if (not re.search(r"(?:^|[\s:])company/[\w./-]+", args) or "--delete" in args or "--mirror" in args
                or re.search(r"(?:^|\s)--all\b|(?:^|[\s:])(?:main|master|develop)\b", args)):
            block("pushes to the customer's repo name a `company/<feature-id>` branch explicitly, "
                  "e.g. `git -C client push -u origin company/F-001`; the PO merges the PR")


def block(label):
    sys.stderr.write(f"[company guard] BLOCKED ({label})\n")
    sys.exit(2)


def release_approved():
    try:
        project = json.loads((ROOT / "state" / "project.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return bool(project.get("po_release_approval"))


def main():
    data = json.load(sys.stdin)
    command = (data.get("tool_input") or {}).get("command", "")
    check_client(command, data.get("cwd"))
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
