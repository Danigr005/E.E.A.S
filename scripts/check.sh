#!/usr/bin/env bash
# Verify CWCDT is applied correctly. Exit code 1 if anything is off.
#   scripts/check.sh            (set CWCDT_SKIP_TOOLBOX_CHECK=1 to skip the `claude plugin list` check)
set -uo pipefail
# shellcheck source=common.sh
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

FAIL=0
ok() { printf '  ✔ %s\n' "$1"; }
warn() { printf '  ! %s\n' "$1"; }
bad() { printf '  ✘ %s\n' "$1"; FAIL=1; }
is_link() {
  if [[ -L "$2" && "$(real "$2")" == "$(real "$1")" ]]; then ok "$2"; else bad "$2 does not link to $1"; fi
}

LANG_CODE="$(state_get lang en)"
PROFILE="$(state_get profile default)"

echo "== links (language: $LANG_CODE, profile: $PROFILE) =="
is_link "$MASTER/lang/$LANG_CODE/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
is_link "$MASTER/rules/cwcdt" "$CLAUDE_DIR/rules/cwcdt"
is_link "$MASTER/lang/$LANG_CODE/skills/cwcdt-playbook" "$CLAUDE_DIR/skills/cwcdt-playbook"
if [[ -d "$CODEX_DIR" ]]; then
  if [[ -L "$CODEX_DIR/AGENTS.md" ]]; then is_link "$MASTER/codex/AGENTS.md" "$CODEX_DIR/AGENTS.md"; else warn "$CODEX_DIR/AGENTS.md is not linked (apply.sh --no-codex, or a file of your own)"; fi
fi
if [[ -d "$CLAUDE_DIR/rules/ecc" && ! -L "$CLAUDE_DIR/rules/ecc" ]]; then
  warn "$CLAUDE_DIR/rules/ecc is a real directory (manual ECC rules install): its common rules duplicate rules/cwcdt/common/core.md"
fi

echo "== settings.json =="
managed=(--managed "$MASTER/profiles/default.json")
if [[ "$PROFILE" != default ]]; then managed+=(--managed "$MASTER/profiles/$PROFILE.json"); fi
if out="$(python3 -I "$MASTER/scripts/merge_settings.py" --target "$CLAUDE_DIR/settings.json" "${managed[@]}" --check)"; then
  ok "profile '$PROFILE' is fully present in settings.json"
else
  sed 's/^/  /' <<<"$out"
  bad "settings.json lacks keys of the profile (run scripts/apply.sh)"
fi

echo "== toolbox =="
if [[ "${CWCDT_SKIP_TOOLBOX_CHECK:-0}" == 1 ]]; then
  warn "toolbox check skipped"
elif ! command -v claude >/dev/null 2>&1; then
  warn "claude CLI not found; cannot check plugins"
else
  plugins="$(claude plugin list 2>/dev/null || true)"
  plugin_status() { awk -v p="$1" 'index($0, p) {f=1} f && /Status:/ {print; exit}' <<<"$plugins"; }
  if [[ "$(plugin_status 'ecc@ecc')" == *enabled* ]]; then
    ok "ecc@ecc enabled"
  else
    bad "ecc@ecc is not enabled: claude plugin marketplace add affaan-m/ECC && claude plugin install ecc@ecc"
  fi
  if [[ "$(plugin_status 'codex@openai-codex')" == *enabled* ]]; then
    ok "codex@openai-codex enabled"
  else
    warn "codex@openai-codex not enabled (optional: only needed for Codex delegation)"
  fi
fi

echo "== repo =="
en_lines="$(wc -l <"$MASTER/lang/en/CLAUDE.md")"
es_lines="$(wc -l <"$MASTER/lang/es/CLAUDE.md")"
if (( en_lines * 10 > es_lines * 13 || es_lines * 10 > en_lines * 13 )); then
  warn "lang/en and lang/es CLAUDE.md differ a lot in length ($en_lines vs $es_lines lines): translations may have drifted"
else
  ok "lang/en and lang/es CLAUDE.md are in step ($en_lines vs $es_lines lines)"
fi

exit "$FAIL"
