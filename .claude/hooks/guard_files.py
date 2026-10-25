"""PreToolUse hook for Write/Edit/MultiEdit.

Blocks (exit 2, reason on stderr):
1. Secrets written into tracked files.
2. Agents granting PO-only approvals in state/project.json (po_release_approval, gate G3).
3. Illegal changes to a locked state/feature_list.json:
   - deleting features or unlocking the list
   - changing a feature's contract (title/story/acceptance/verification/platforms/category/status)
     or adding a feature without a `cr` that points to an approved change request
   - setting passes=true without evidence
4. Illegal changes to state/security-findings.json: engineers may only move a finding to `fixed`;
   only the Cyber Security team sets `verified`; `accepted-risk` is PO-only (the approval script).
5. Lane violations: inside a subagent (input carries `agent_id`/`agent_type`), code and state paths may
   only be edited by the teams that own them (see OWNERS). The main session (delivery-director) and
   the PO are not restricted; docs/ ownership stays a CLAUDE.md convention.
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()

SECRET_PATTERNS = [
    (re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----"), "private key"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key"),
    (re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}"), "Anthropic API key"),
    (re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9]{32,}"), "OpenAI-style API key"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"), "GitHub token"),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"service_role[\"'\s:=]+eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+"), "Supabase service_role key"),
]
SECRET_SAFE_PATHS = re.compile(r"(^|/)(\.env(\.[\w-]+)?|secrets/.*)$")

CONTRACT_FIELDS = ("title", "story", "acceptance", "verification", "platforms", "category", "status")

MOBILE = {"react-native-engineer", "flutter-engineer", "swift-ios-engineer", "kotlin-android-engineer"}
BACKEND = {"nodejs-backend-engineer", "python-backend-engineer", "go-backend-engineer"}
BAAS = {"firebase-engineer", "supabase-engineer"}
TESTERS = {"test-automation-engineer", "qa-engineer"}
RELEASE = {"release-manager", "devops-engineer"}
CYBER = {"security-lead", "appsec-code-auditor", "mobile-pentester", "api-cloud-pentester"}
ENGINEERS = MOBILE | BACKEND | BAAS | TESTERS

# First matching rule wins. Paths are repo-relative POSIX. Empty set = no subagent may edit.
OWNERS = [
    (re.compile(r"^(\.claude|company)/"), set()),
    (re.compile(r"^state/feature_list\.json$"), {"solution-architect"} | ENGINEERS),
    (re.compile(r"^state/security-findings\.json$"), CYBER | ENGINEERS),
    (re.compile(r"^state/"), set()),
    (re.compile(r"(^|/)fastlane/"), RELEASE),
    (re.compile(r"(^|/)(tests?|__tests__|integration_test|test_driver|androidTest|e2e|[A-Za-z]*Tests)/"), ENGINEERS),
    (re.compile(r"^apps/mobile/"), {"react-native-engineer", "flutter-engineer"}),
    (re.compile(r"^apps/ios/"), {"swift-ios-engineer"}),
    (re.compile(r"^apps/android/"), {"kotlin-android-engineer"}),
    (re.compile(r"^services/api/"), BACKEND),
    (re.compile(r"^services/baas/firebase/"), {"firebase-engineer"}),
    (re.compile(r"^services/baas/supabase/"), {"supabase-engineer"}),
    (re.compile(r"^services/baas/"), BAAS),
    (re.compile(r"^(\.github|infra)/"), RELEASE),
    (re.compile(r"^docs/change-requests/"), {"product-manager"}),
]


def block(reason):
    sys.stderr.write(f"[company guard] BLOCKED: {reason}\n")
    sys.exit(2)


def rel_path(file_path):
    p = Path(file_path)
    if not p.is_absolute():
        p = ROOT / p
    try:
        return p.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def new_content(tool_name, tool_input, current):
    if tool_name == "Write":
        return tool_input.get("content", "")
    edits = tool_input.get("edits") if tool_name == "MultiEdit" else [tool_input]
    text = current
    for e in edits or []:
        old, new = e.get("old_string", ""), e.get("new_string", "")
        text = text.replace(old, new) if e.get("replace_all") else text.replace(old, new, 1)
    return text


def parse_json(text, label):
    try:
        return json.loads(text)
    except ValueError as exc:
        block(f"{label} would not be valid JSON ({exc}). Keep it valid.")


def cr_approved(cr_id):
    if not cr_id:
        return False
    doc = ROOT / "docs" / "change-requests" / f"{cr_id}.md"
    if not doc.exists():
        return False
    return re.search(r"(?im)^\W*status\W*:\W*approved\b", doc.read_text(encoding="utf-8")) is not None


def check_feature_list(old_text, new_text):
    new = parse_json(new_text, "state/feature_list.json")
    if not old_text.strip():
        return
    try:
        old = json.loads(old_text)
    except ValueError:
        return
    if not old.get("locked"):
        return
    if not new.get("locked"):
        block("feature_list.json is locked; it cannot be unlocked. Use the change-request skill for scope changes.")
    old_by_id = {f.get("id"): f for f in old.get("features", [])}
    new_by_id = {f.get("id"): f for f in new.get("features", [])}
    missing = sorted(str(i) for i in set(old_by_id) - set(new_by_id))
    if missing:
        block(f"features cannot be deleted from a locked list: {missing}. Set status=dropped via an approved change request.")
    for fid, nf in new_by_id.items():
        of = old_by_id.get(fid)
        if of is None:
            if not cr_approved(nf.get("cr")):
                block(f"new feature {fid} needs `cr` pointing to docs/change-requests/<CR>.md containing 'Status: approved'.")
            continue
        changed = [k for k in CONTRACT_FIELDS if of.get(k) != nf.get(k)]
        if changed and not (nf.get("cr") != of.get("cr") and cr_approved(nf.get("cr"))):
            block(f"{fid}: {changed} belong to the feature contract. Changing them needs a new approved change request in `cr`.")
        if nf.get("passes") and not of.get("passes") and not str(nf.get("evidence", "")).strip():
            block(f"{fid}: passes=true requires `evidence` (test command + result, report or screenshot path).")


def check_project_json(old_text, new_text):
    new = parse_json(new_text, "state/project.json")
    try:
        old = json.loads(old_text) if old_text.strip() else {}
    except ValueError:
        old = {}
    if new.get("po_release_approval") and not old.get("po_release_approval"):
        block("po_release_approval is PO-only: ask the PO to run `! bash scripts/approve-release.sh`.")
    if new.get("gates", {}).get("G3_release") == "approved" and old.get("gates", {}).get("G3_release") != "approved":
        block("Gate G3 is approved only by the PO via `! bash scripts/approve-release.sh`.")


def check_lane(rel, agent):
    for pattern, owners in OWNERS:
        if pattern.search(rel):
            if agent not in owners:
                who = ", ".join(sorted(owners)) or "the delivery-director (main session) only"
                block(f"{agent} may not edit {rel}; owner(s): {who}. Put the requested change in your output for the owner.")
            return


def check_security_findings(old_text, new_text, agent, in_subagent):
    """Status flow: open -> fixed (dev teams) -> verified (Cyber Security only).
    accepted-risk is PO-only (set by scripts/approve-release.sh, not a subagent)."""
    new = parse_json(new_text, "state/security-findings.json")
    try:
        old = json.loads(old_text) if old_text.strip() else {}
    except ValueError:
        old = {}
    old_by_id = {f.get("id"): f for f in old.get("findings", [])}
    for nf in new.get("findings", []):
        of = old_by_id.get(nf.get("id"))
        old_status = of.get("status") if of else None
        new_status = nf.get("status")
        if new_status == old_status:
            continue
        if new_status == "accepted-risk":
            block(f"{nf.get('id')}: accepting a security risk is PO-only via `! bash scripts/approve-release.sh --accept-risk {nf.get('id')}`.")
        if not in_subagent:
            continue  # the director/PO may do the rest
        if new_status == "verified" and agent not in CYBER:
            block(f"{nf.get('id')}: only the Cyber Security team marks a finding `verified` after re-testing. Set it to `fixed` and hand back for verification.")
        if agent in ENGINEERS and agent not in CYBER and new_status not in (None, "open", "fixed"):
            block(f"{nf.get('id')}: engineers may only move a finding to `fixed`. Verification is the Cyber Security team's.")


def check_change_request(rel, old_text, new_text, in_subagent):
    approved = re.compile(r"(?im)^\W*status\W*:\W*approved\b")
    if in_subagent and approved.search(new_text) and not approved.search(old_text):
        block(f"{rel}: only the delivery-director marks a change request approved, after the PO decides.")


def main():
    data = json.load(sys.stdin)
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input") or {}
    file_path = tool_input.get("file_path")
    if not file_path:
        return
    rel = rel_path(file_path)
    in_subagent = bool(data.get("agent_id"))
    if in_subagent:
        check_lane(rel, data.get("agent_type") or "unknown-subagent")
    target = ROOT / rel
    try:
        current = target.read_text(encoding="utf-8") if target.is_file() else ""
    except (OSError, UnicodeDecodeError):
        current = ""
    content = new_content(tool_name, tool_input, current)

    if not SECRET_SAFE_PATHS.search(rel):
        for pattern, label in SECRET_PATTERNS:
            if pattern.search(content) and not pattern.search(current):
                block(f"{label} detected in {rel}. Put secrets in .env* or secrets/ (gitignored) and reference them by name.")

    if rel == "state/feature_list.json":
        check_feature_list(current, content)
    elif rel == "state/project.json":
        check_project_json(current, content)
    elif rel == "state/security-findings.json":
        check_security_findings(current, content, data.get("agent_type") or "unknown-subagent", in_subagent)
    elif rel.startswith("docs/change-requests/"):
        check_change_request(rel, current, content, in_subagent)


if __name__ == "__main__":
    main()
