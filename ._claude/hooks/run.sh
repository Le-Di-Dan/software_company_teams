#!/usr/bin/env bash
# Runs a Python hook with whichever Python 3 launcher exists (macOS: python3, Windows Git Bash: python or py).
# Fails open: a missing hook file or missing Python skips the hook (exit 0) instead of blocking every tool call.
# Only an explicit `exit 2` from a hook script blocks; any other crash is reported as a non-blocking error.
HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$HOOK_DIR/$1"

if [ ! -f "$SCRIPT" ]; then
  echo "[company hooks] $1 not found; skipping" >&2
  exit 0
fi

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
  echo "[company hooks] Python 3 not found; skipping $1" >&2
  exit 0
fi

INPUT="$(cat)"
# Claude Code talks UTF-8; Windows Python would otherwise read and write the pipes as cp1252 and crash on █ ⚠ or Vietnamese.
printf '%s' "$INPUT" | PYTHONIOENCODING=utf-8 $PY "$SCRIPT"
STATUS=$?
# Hooks block deliberately with exit 2. The script's existence is checked above, so Python's own exit 2
# (cannot open file) can't happen here; uncaught exceptions exit 1 and are reported without blocking.
if [ "$STATUS" -eq 2 ]; then exit 2; fi
if [ "$STATUS" -ne 0 ]; then
  echo "[company hooks] $1 crashed (exit $STATUS); not blocking" >&2
  exit 1
fi
exit 0
