#!/usr/bin/env bash
# Dev-only: copy the current framework into a trial app so the next session uses the latest agents/skills/hooks.
# Usage: bash devtools/sync-trial.sh ~/testing/habit_app
# Copies .claude/, CLAUDE.md, company/, framework scripts, README.md, .gitignore.
# Never touches the trial's state/ (except adding missing usage_policy), docs/, apps/, services/ or tests/.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TRIAL="${1:?trial directory required}"
[ -d "$TRIAL/state" ] || { echo "Not a company project: $TRIAL/state missing" >&2; exit 1; }
# While the framework is under construction, .claude/ and CLAUDE.md may be parked one level up.
SRC_CLAUDE="$REPO/.claude"; [ -d "$SRC_CLAUDE" ] || SRC_CLAUDE="$REPO/../.claude"
SRC_MD="$REPO/CLAUDE.md"; [ -f "$SRC_MD" ] || SRC_MD="$REPO/../CLAUDE.md"

rsync -a --delete --exclude 'settings.local.json' --exclude 'agent-memory-local/' "$SRC_CLAUDE/" "$TRIAL/.claude/"
cp "$SRC_MD" "$TRIAL/CLAUDE.md"
rsync -a --delete "$REPO/company/" "$TRIAL/company/"
for f in dashboard.py env-doctor.sh approve-release.sh; do cp "$REPO/scripts/$f" "$TRIAL/scripts/$f"; done
cp "$REPO/README.md" "$REPO/.gitignore" "$TRIAL/"

python3 - "$TRIAL/state/project.json" <<'PY'
import json, sys
p = sys.argv[1]; d = json.load(open(p, encoding="utf-8"))
if "usage_policy" not in d:
    d["usage_policy"] = {"soft_pct": 75, "hard_pct": 80, "budget_usd": None}
    open(p, "w", encoding="utf-8").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("added usage_policy to state/project.json")
PY
echo "Synced framework -> $TRIAL. Restart the trial's Claude session to load new hooks/settings."
