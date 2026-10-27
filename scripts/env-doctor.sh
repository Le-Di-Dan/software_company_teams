#!/usr/bin/env bash
# Detects the toolchain on this machine (macOS or Windows Git Bash) and writes state/environment.md,
# so agents know which builds/tests can run here and which must be marked `needs: mac|windows`.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/state/environment.md"

case "$(uname -s)" in
  Darwin) OS="macOS $(sw_vers -productVersion 2>/dev/null)" ; MACHINE="mac" ;;
  MINGW*|MSYS*|CYGWIN*) OS="Windows ($(uname -s))" ; MACHINE="windows" ;;
  Linux) OS="Linux" ; MACHINE="linux" ;;
  *) OS="$(uname -s)" ; MACHINE="unknown" ;;
esac

version_of() {
  # $1 = command, rest = version args. Prints first line of version output or "-".
  local cmd="$1"; shift
  if command -v "$cmd" >/dev/null 2>&1; then
    "$cmd" "$@" 2>&1 | head -n 1 | tr -d '\r' | cut -c1-80
  else
    echo "-"
  fi
}

row() { printf '| %s | %s | %s |\n' "$1" "$2" "$3"; }

{
  echo "# Environment — $(hostname 2>/dev/null)"
  echo
  echo "- Machine: **$MACHINE** · OS: $OS · Generated: $(date '+%Y-%m-%d %H:%M')"
  echo "- Regenerate with \`bash scripts/env-doctor.sh\`. Tasks needing a missing tool are tagged \`needs: mac\` or \`needs: windows\`."
  echo
  echo "| Area | Tool | Version (\`-\` = missing) |"
  echo "|---|---|---|"
  row "core" "git" "$(version_of git --version)"
  row "core" "python3" "$(version_of python3 --version)"
  row "core" "node" "$(version_of node --version)"
  row "core" "gh (GitHub CLI)" "$(version_of gh --version)"
  row "core" "docker" "$(version_of docker --version)"
  row "iOS" "xcodebuild" "$(version_of xcodebuild -version)"
  row "iOS" "cocoapods" "$(version_of pod --version)"
  row "iOS/Android" "fastlane" "$(version_of fastlane --version | grep -m1 -o 'fastlane [0-9.]*' || echo -)"
  row "Android" "java" "$(version_of java -version)"
  row "Android" "adb" "$(version_of adb version)"
  row "Android" "ANDROID_HOME" "${ANDROID_HOME:-${ANDROID_SDK_ROOT:--}}"
  row "Flutter" "flutter" "$(version_of flutter --version)"
  row "React Native" "npx" "$(version_of npx --version)"
  row "Backend" "go" "$(version_of go version)"
  row "Backend" "pip" "$(version_of pip3 --version)"
  row "BaaS" "firebase CLI" "$(version_of firebase --version)"
  row "BaaS" "supabase CLI" "$(version_of supabase --version)"
  row "QA" "maestro" "$(version_of maestro --version)"
  echo
  echo "## Capabilities on this machine"
  if command -v xcodebuild >/dev/null 2>&1; then echo "- iOS build & simulator: YES"; else echo "- iOS build & simulator: NO → needs: mac"; fi
  if command -v adb >/dev/null 2>&1 || [ -n "${ANDROID_HOME:-}${ANDROID_SDK_ROOT:-}" ]; then echo "- Android build & emulator: YES"; else echo "- Android build & emulator: NO → needs: windows (or install Android Studio here)"; fi
  if command -v maestro >/dev/null 2>&1; then echo "- Maestro E2E: YES"; else echo "- Maestro E2E: NO (install: https://maestro.dev)"; fi
  if command -v node >/dev/null 2>&1; then echo "- Web frontends build & Playwright E2E: YES (browsers are project-local: \`npx playwright install\` in tests/web-e2e/)"; else echo "- Web frontends: NO (needs Node.js LTS)"; fi
  echo
  echo "## Suggested MCP servers (add per machine, local scope)"
  echo "- iOS (mac): \`claude mcp add XcodeBuildMCP -- npx -y xcodebuildmcp@latest\`"
  echo "- E2E: \`claude mcp add maestro -- maestro mcp\` (after installing Maestro)"
  echo "- Web frontends: \`claude mcp add playwright -- npx -y @playwright/mcp@latest\`"
  echo "- Figma (if the PO wants designs in Figma): the Figma plugin for Claude Code, or \`claude mcp add --transport http figma https://mcp.figma.com/mcp\`, then sign in with the PO's Figma account"
  echo "- Firebase: \`claude mcp add firebase -- npx -y firebase-tools@latest mcp\`"
  echo "- Supabase: see https://supabase.com/docs/guides/getting-started/mcp"
} > "$OUT"

echo "Wrote $OUT"
cat "$OUT"
