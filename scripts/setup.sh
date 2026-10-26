#!/usr/bin/env bash
# Run once after cloning the template: turns it into a company project Claude Code can load.
# The template stores the framework as ._claude/ and _CLAUDE.md so that working on the framework itself
# doesn't load the company's agents, hooks and instructions; this renames them to .claude/ and CLAUDE.md,
# then records this machine's toolchain (env-doctor.sh). Safe to run again, e.g. on the second machine.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# git mv when the path is tracked, so the rename is staged as a rename; plain mv otherwise.
move() {
  if git ls-files --error-unmatch "$1" >/dev/null 2>&1; then git mv "$1" "$2"; else mv "$1" "$2"; fi
}

if [ -d ._claude ]; then
  if [ ! -e .claude ]; then
    move ._claude .claude
  else
    # .claude/ already exists (e.g. Claude Code wrote settings.local.json before setup ran): merge, never overwrite.
    for entry in ._claude/* ._claude/.[!.]*; do
      [ -e "$entry" ] || continue
      name="${entry#._claude/}"
      if [ -e ".claude/$name" ]; then
        echo "setup: .claude/$name already exists; resolve it by hand, then run this script again." >&2
        exit 1
      fi
    done
    for entry in ._claude/* ._claude/.[!.]*; do
      [ -e "$entry" ] || continue
      move "$entry" ".claude/${entry#._claude/}"
    done
    rmdir ._claude
  fi
  echo "setup: ._claude/ -> .claude/"
fi

if [ -f _CLAUDE.md ]; then
  if [ -e CLAUDE.md ]; then
    echo "setup: CLAUDE.md already exists; merge _CLAUDE.md into it by hand, then delete _CLAUDE.md." >&2
    exit 1
  fi
  move _CLAUDE.md CLAUDE.md
  echo "setup: _CLAUDE.md -> CLAUDE.md"
fi

[ -d .claude ] && [ -f CLAUDE.md ] || { echo "setup: .claude/ or CLAUDE.md missing; is this the template?" >&2; exit 1; }

bash scripts/env-doctor.sh
echo "setup: done. Commit the rename (git add -A && git commit -m 'Set up company project'), then start with: claude"
