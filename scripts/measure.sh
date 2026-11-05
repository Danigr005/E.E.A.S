#!/usr/bin/env bash
# Snapshot of the fixed context cost: what every session pays before you type anything.
#   scripts/measure.sh <label> [--real]
# Free: uses `claude -p /context` (a local estimate). --real also sends one tiny request and reports the true
# size of the first prompt (uses a little quota). Output goes to docs/metrics/<date>-<label>.md.
set -euo pipefail
# shellcheck source=common.sh
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

LABEL="${1:-snapshot}"
REAL=0
if [[ "${2:-}" == "--real" ]]; then REAL=1; fi
OUT="$MASTER/docs/metrics/$(date +%F)-$LABEL.md"
mkdir -p "$MASTER/docs/metrics"

cd /tmp
CTX="$(with_timeout 120 claude -p /context 2>&1)"

{
  echo "# Context snapshot — $LABEL ($(date +%Y-%m-%dT%H:%M:%S%z))"
  echo
  echo '```'
  grep -E '^\*\*(Model|Tokens)' <<<"$CTX" || true
  awk '/^\| Category/,/^$/' <<<"$CTX"
  echo '```'
  echo
  echo "Memory files:"
  awk '/^### Memory Files/,/^### Skills/' <<<"$CTX" | grep -E '^\| (User|Project)' | sed "s|$HOME|~|g" || true
  echo
  echo "Agents listed: $(awk '/^### Custom Agents/,/^### Memory/' <<<"$CTX" | grep -c '^| [a-z]*:' || true)"
  echo "Skills listed: $(awk '/^### Skills/,0' <<<"$CTX" | grep -c '^| [a-z-]*:' || true)"
} >"$OUT"

if (( REAL )); then
  {
    echo
    echo "First real request:"
    with_timeout 180 claude -p "Reply only: ok" --output-format json 2>/dev/null | python3 -I -c '
import json, sys
usage = json.load(sys.stdin).get("usage", {})
keys = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
total = sum(usage.get(k, 0) for k in keys)
written = usage.get("cache_creation_input_tokens")
read = usage.get("cache_read_input_tokens")
print(f"- prompt tokens: {total} (cache written {written}, cache read {read})")
'
  } >>"$OUT"
fi

echo "$OUT"
cat "$OUT"
