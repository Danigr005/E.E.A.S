#!/usr/bin/env bash
# One-shot setup for a fresh machine: installs the toolbox plugins, then applies and checks CWCDT.
#   scripts/bootstrap.sh [--lang en|es] [--profile NAME] [--no-codex]
# Everything CWCDT needs is either in this repo or reinstalled from here; conversation history, logins and
# secrets are deliberately NOT in git (log in again with `claude` and `codex login`).
set -euo pipefail
# shellcheck source=common.sh
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

LANG_ARG=(); PROFILE_ARG=(); CODEX=1
while [[ $# -gt 0 ]]; do
  case "$1" in
    --lang) LANG_ARG=(--lang "${2:?missing value}"); shift 2 ;;
    --profile) PROFILE_ARG=(--profile "${2:?missing value}"); shift 2 ;;
    --no-codex) CODEX=0; shift ;;
    *) echo "usage: $0 [--lang en|es] [--profile NAME] [--no-codex]" >&2; exit 2 ;;
  esac
done

for cmd in claude git python3 node; do
  command -v "$cmd" >/dev/null || { echo "missing required command: $cmd" >&2; exit 1; }
done

echo "== toolbox: ECC =="
claude plugin marketplace add affaan-m/ECC || true
claude plugin install ecc@ecc || true

APPLY_ARGS=("${LANG_ARG[@]}" "${PROFILE_ARG[@]}")
if [[ $CODEX -eq 1 ]]; then
  echo "== Codex =="
  command -v codex >/dev/null || npm i -g @openai/codex
  claude plugin marketplace add openai/codex-plugin-cc || true
  claude plugin install codex@openai-codex || true
  echo "Run 'codex login' yourself afterwards (this script never touches credentials)."
else
  APPLY_ARGS+=(--no-codex)
fi

echo "== CWCDT =="
"$MASTER/scripts/apply.sh" "${APPLY_ARGS[@]}"
"$MASTER/scripts/check.sh"
echo "Done. Restart Claude Code."
