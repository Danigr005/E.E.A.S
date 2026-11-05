#!/usr/bin/env bash
# Sandbox test: for every language and profile, run apply -> check -> idempotent re-apply -> revert against
# throwaway copies of ~/.claude and ~/.codex. Your real configuration is never touched.
#   scripts/test-sandbox.sh
set -uo pipefail
# shellcheck source=common.sh
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

T="$(mktemp -d)"
trap '[[ "$T" == /tmp/* || "$T" == /var/folders/* ]] && rm -rf "$T"' EXIT
FAILED=0
pass() { printf '  ✔ %s\n' "$1"; }
fail() { printf '  ✘ %s\n' "$1"; FAILED=1; }

for lang_dir in "$MASTER"/lang/*/; do
  lang="$(basename "$lang_dir")"
  for profile_file in "$MASTER"/profiles/*.json; do
    profile="$(basename "$profile_file" .json)"
    name="$lang/$profile"
    echo "== $name =="
    C="$T/$lang-$profile/claude"
    X="$T/$lang-$profile/codex"
    mkdir -p "$C/rules" "$X"
    echo "# my own CLAUDE.md" >"$C/CLAUDE.md"
    echo '{"theme":"dark","permissions":{"deny":["Bash(rm -rf /)"]}}' >"$C/settings.json"
    printf 'model = "gpt-old"\n\n[desktop]\nx = 1\n' >"$X/config.toml"
    cp -a "$C" "$C.orig"
    cp -a "$X" "$X.orig"
    # an earlier layout of this repo left a link behind (created after the snapshot, so revert must remove it)
    ln -s "$MASTER/rules/cwcdt" "$C/rules/ecc"

    export CLAUDE_DIR="$C" CODEX_DIR="$X" CWCDT_SKIP_TOOLBOX_CHECK=1
    if "$MASTER/scripts/apply.sh" --lang "$lang" --profile "$profile" --codex-default-model gpt-test >"$T/apply.out" 2>&1; then pass "apply"; else fail "apply"; sed 's/^/      /' "$T/apply.out"; fi
    if "$MASTER/scripts/check.sh" >"$T/check.out" 2>&1; then pass "check"; else fail "check"; sed 's/^/      /' "$T/check.out"; fi
    [[ ! -e "$C/rules/ecc" ]] && pass "legacy link removed" || fail "legacy link still there"
    grep -q 'gpt-test' "$X/config.toml" && pass "codex default model set" || fail "codex default model not set"
    grep -q '"theme": "dark"' "$C/settings.json" && grep -q 'Bash(rm -rf /)' "$C/settings.json" && pass "existing settings preserved" || fail "existing settings lost"

    "$MASTER/scripts/apply.sh" --lang "$lang" --profile "$profile" --codex-default-model gpt-test >"$T/apply2.out" 2>&1
    if grep -E '^  (linked|set|removed)' "$T/apply2.out" >/dev/null; then fail "second apply is not a no-op"; sed 's/^/      /' "$T/apply2.out"; else pass "second apply is a no-op"; fi

    "$MASTER/scripts/revert.sh" --original >"$T/revert.out" 2>&1
    if diff -r -x backups -x skills -x 'cwcdt.*' "$C" "$C.orig" >"$T/diff.out" 2>&1 && diff -r "$X" "$X.orig" >>"$T/diff.out" 2>&1; then
      pass "revert --original restores the starting state"
    else
      fail "revert left differences"; sed 's/^/      /' "$T/diff.out"
    fi
    unset CLAUDE_DIR CODEX_DIR CWCDT_SKIP_TOOLBOX_CHECK
  done
done

if (( FAILED )); then echo "SANDBOX TEST FAILED"; exit 1; fi
echo "SANDBOX TEST PASSED"
