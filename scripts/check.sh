#!/usr/bin/env bash
# Run a build/test/lint command once, keep its full log in state/runs/, print only a short summary.
# Usage: bash scripts/check.sh <name> [-C dir] [--fresh] [--keep F-xxx] [--timeout sec] -- <command>
#        bash scripts/check.sh --clean | --prune
# Details in scripts/check.py and the kb-run-checks skill.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PY=""
for candidate in python3 python py; do
  if command -v "$candidate" >/dev/null 2>&1; then
    if [ "$candidate" = "py" ]; then PY="py -3"; break; fi
    if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)' >/dev/null 2>&1; then
      PY="$candidate"; break
    fi
  fi
done
if [ -z "$PY" ]; then
  echo "check: Python 3 not found" >&2
  exit 127
fi

# The command runs under this same bash; Windows Python needs its Windows path (not /usr/bin/bash).
CHECK_BASH="$BASH"
if command -v cygpath >/dev/null 2>&1; then CHECK_BASH="$(cygpath -w "$BASH")"; fi
export CHECK_BASH
PYTHONIOENCODING=utf-8 $PY "$ROOT/scripts/check.py" "$@"
