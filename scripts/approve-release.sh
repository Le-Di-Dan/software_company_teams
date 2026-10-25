#!/usr/bin/env bash
# PO-only: records gate G3 (store submission / production release) approval,
# and is the only way to accept a security risk.
# Run it yourself from the Claude Code prompt:
#   ! bash scripts/approve-release.sh                    # approve gate G3
#   ! bash scripts/approve-release.sh --accept-risk SEC-007   # PO accepts one open finding
# after reading docs/08-release/release-readiness.md and the security clearance.
# Agents are blocked from running this and from setting these flags directly.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT="$ROOT/state/project.json"
FINDINGS="$ROOT/state/security-findings.json"

PY=python3
command -v python3 >/dev/null 2>&1 || PY=python

if [ "${1:-}" = "--accept-risk" ]; then
  SEC_ID="${2:-}"
  [ -n "$SEC_ID" ] || { echo "Usage: approve-release.sh --accept-risk <SEC-id>"; exit 1; }
  "$PY" - "$FINDINGS" "$SEC_ID" <<'EOF'
import json, sys
path, sec_id = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8") as f:
    data = json.load(f)
for find in data.get("findings", []):
    if find.get("id") == sec_id:
        find["status"] = "accepted-risk"
        break
else:
    sys.exit(f"No finding {sec_id} in {path}")
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")
print(f"{sec_id} marked accepted-risk by the PO.")
EOF
  echo "- $(date +%Y-%m-%d) [security] PO: accepted risk $SEC_ID" >> "$ROOT/state/progress.md"
  exit 0
fi

# Default: approve gate G3. Refuse while any Critical/High security finding is unresolved.
if [ -f "$FINDINGS" ]; then
  "$PY" - "$FINDINGS" <<'EOF'
import json, sys
with open(sys.argv[1], encoding="utf-8") as f:
    data = json.load(f)
blocking = [x for x in data.get("findings", [])
            if str(x.get("severity", "")).lower() in ("critical", "high")
            and x.get("status") not in ("verified", "accepted-risk")]
if blocking:
    print("BLOCKED: unresolved Critical/High security findings:")
    for x in blocking:
        print(f"  {x.get('id')} [{x.get('severity')}] {x.get('title')} -> status={x.get('status')}")
    print("Fix and let Cyber Security verify them, or accept each with --accept-risk <id>.")
    sys.exit(1)
EOF
fi

"$PY" - "$PROJECT" <<'EOF'
import json, sys, datetime
path = sys.argv[1]
with open(path, encoding="utf-8") as f:
    project = json.load(f)
project["po_release_approval"] = True
project.setdefault("gates", {})["G3_release"] = "approved"
project["updated_at"] = datetime.datetime.now().isoformat(timespec="seconds")
with open(path, "w", encoding="utf-8") as f:
    json.dump(project, f, indent=2, ensure_ascii=False)
    f.write("\n")
print("G3 approved: store submission commands are now unlocked for this release.")
EOF

echo "- $(date +%Y-%m-%d) [8-release] PO: approved gate G3 (store submission)" >> "$ROOT/state/progress.md"
