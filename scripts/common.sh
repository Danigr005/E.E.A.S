# Shared helpers for the EEAS scripts. Source it; do not execute it.
# Written for bash 3.2+ (macOS default) and GNU/Linux.

MASTER="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_DIR="${CLAUDE_DIR:-$HOME/.claude}"
CODEX_DIR="${CODEX_DIR:-$HOME/.codex}"

# flat /a/b/c -> a_b_c : file names inside a backup directory
flat() { echo "${1#/}" | tr '/' '_'; }

# real <path> : canonical path (readlink -f is not portable)
real() { python3 -I -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "$1"; }

# state_get <name> <default> : value saved by apply.sh in $CLAUDE_DIR/eeas.<name> (cwcdt.<name> = earlier name)
state_get() {
  local file
  for file in "$CLAUDE_DIR/eeas.$1" "$CLAUDE_DIR/cwcdt.$1"; do
    if [[ -f "$file" ]]; then tr -d '[:space:]' <"$file"; return; fi
  done
  echo "$2"
}

# backups_oldest_first : every backup directory this tool (or its earlier name) created
backups_oldest_first() {
  ls -dtr "$CLAUDE_DIR"/backups/eeas-* "$CLAUDE_DIR"/backups/cwcdt-* "$CLAUDE_DIR"/backups/claude-setup-* 2>/dev/null || true
}

# with_timeout <seconds> <command...> : use timeout/gtimeout when available, otherwise just run
with_timeout() {
  local secs="$1"
  shift
  if command -v timeout >/dev/null 2>&1; then timeout "$secs" "$@"
  elif command -v gtimeout >/dev/null 2>&1; then gtimeout "$secs" "$@"
  else "$@"; fi
}
