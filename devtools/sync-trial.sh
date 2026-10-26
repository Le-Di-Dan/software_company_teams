#!/usr/bin/env bash
# Dev-only: copy the current framework into a trial app so the next session uses the latest agents/skills/hooks.
# Usage: bash devtools/sync-trial.sh ~/testing/habit_app
# Copies ._claude/ -> .claude/, _CLAUDE.md -> CLAUDE.md, company/, framework scripts, README.md, .gitignore.
# Never touches the trial's state/ (except migrating usage_policy), docs/, apps/, services/ or tests/.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TRIAL="${1:?trial directory required}"
[ -d "$TRIAL/state" ] || { echo "Not a company project: $TRIAL/state missing" >&2; exit 1; }
# The template keeps them as ._claude/ and _CLAUDE.md so they don't load while developing the framework.
rsync -a --delete --exclude 'settings.local.json' --exclude 'agent-memory-local/' --exclude '__pycache__/' \
  "$REPO/._claude/" "$TRIAL/.claude/"
cp "$REPO/_CLAUDE.md" "$TRIAL/CLAUDE.md"
rsync -a --delete "$REPO/company/" "$TRIAL/company/"
for f in dashboard.py env-doctor.sh approve-release.sh setup.sh check.sh check.py; do cp "$REPO/scripts/$f" "$TRIAL/scripts/$f"; done
cp "$REPO/README.md" "$REPO/.gitignore" "$TRIAL/"

python3 - "$TRIAL/state/project.json" <<'PY'
import json, sys
p = sys.argv[1]; d = json.load(open(p, encoding="utf-8"))
pol = d.setdefault("usage_policy", {})
# Thresholds now follow the account plan: drop the old fixed defaults, which would pin every plan to Pro's.
old = {"soft_pct": 75, "hard_pct": 80, "seven_day_soft_pct": 95, "seven_day_hard_pct": 98}
changed = [k for k, v in old.items() if pol.get(k) == v]
for k in changed:
    del pol[k]
for k, v in (("plan", "auto"), ("budget_usd", None), ("plans", {})):
    if k not in pol:
        pol[k] = v
        changed.append(k)
if changed:
    open(p, "w", encoding="utf-8").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("updated usage_policy in state/project.json:", ", ".join(changed))
PY
echo "Synced framework -> $TRIAL. Restart the trial's Claude session to load new hooks/settings."
