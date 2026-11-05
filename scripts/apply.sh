#!/usr/bin/env bash
# Install EEAS (teams of agents and subagents) on this machine. Idempotent; whatever it replaces is kept in a timestamped backup.
#   scripts/apply.sh [--lang en|es] [--profile NAME] [--codex-default-model MODEL] [--no-codex] [--dry-run]
set -euo pipefail
# shellcheck source=common.sh
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

USAGE="usage: $0 [--lang en|es] [--profile NAME] [--codex-default-model MODEL] [--no-codex] [--dry-run]"
LANG_CODE="$(state_get lang en)"
PROFILE="$(state_get profile default)"
CODEX_MODEL=""
CODEX=1
DRY=0
while (( $# )); do
  case "$1" in
    --lang) LANG_CODE="${2:?$USAGE}"; shift 2 ;;
    --profile) PROFILE="${2:?$USAGE}"; shift 2 ;;
    --codex-default-model) CODEX_MODEL="${2:?$USAGE}"; shift 2 ;;
    --no-codex) CODEX=0; shift ;;
    --dry-run) DRY=1; shift ;;
    *) echo "$USAGE" >&2; exit 2 ;;
  esac
done

if [[ ! -f "$MASTER/lang/$LANG_CODE/CLAUDE.md" ]]; then
  echo "unknown language '$LANG_CODE' (available: $(ls "$MASTER/lang" | tr '\n' ' '))" >&2
  exit 2
fi
if [[ ! -f "$MASTER/profiles/$PROFILE.json" ]]; then
  echo "unknown profile '$PROFILE' (available: $(ls "$MASTER/profiles" | sed 's/\.json$//' | tr '\n' ' '))" >&2
  exit 2
fi

BACKUP="$CLAUDE_DIR/backups/eeas-$(date +%Y%m%d-%H%M%S)"

act() { if (( DRY )); then echo "  [dry-run] $*"; else "$@"; fi; }

# link <target> <dest>: dest becomes a symlink to target; whatever was there moves into $BACKUP.
link() {
  local target="$1" dest="$2"
  if [[ -L "$dest" && "$(readlink "$dest")" == "$target" ]]; then
    echo "  ok      $dest"
    return
  fi
  if [[ -e "$dest" || -L "$dest" ]]; then
    act mkdir -p "$BACKUP"
    act mv -- "$dest" "$BACKUP/$(flat "$dest")"
  fi
  act mkdir -p "$(dirname "$dest")"
  act ln -s "$target" "$dest"
  echo "  linked  $dest -> $target"
}

# copy_backup <file>: keep a pristine copy of a file we are about to edit (never overwrites an earlier copy).
copy_backup() {
  [[ -f "$1" ]] || return 0
  if [[ -e "$BACKUP/$(flat "$1")" ]]; then return 0; fi
  act mkdir -p "$BACKUP"
  act cp -a -- "$1" "$BACKUP/$(flat "$1")"
}

# drop_legacy_link <path>: remove a link left by an earlier layout of this repo (dangling, or pointing into it).
drop_legacy_link() {
  local dest="$1" target
  [[ -L "$dest" ]] || return 0
  target="$(readlink "$dest")"
  if [[ ! -e "$dest" || "$target" == "$MASTER"/* || "$target" == */claude-setup/* ]]; then
    act rm -- "$dest"
    echo "  removed legacy link $dest"
  fi
}

echo "== language: $LANG_CODE | profile: $PROFILE =="
echo "== links ($CLAUDE_DIR) =="
drop_legacy_link "$CLAUDE_DIR/rules/ecc"
drop_legacy_link "$CLAUDE_DIR/skills/owner-playbook"
drop_legacy_link "$CLAUDE_DIR/rules/cwcdt"
drop_legacy_link "$CLAUDE_DIR/skills/cwcdt-playbook"
link "$MASTER/lang/$LANG_CODE/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
link "$MASTER/core/rules" "$CLAUDE_DIR/rules/eeas"
link "$MASTER/lang/$LANG_CODE/skills/eeas-playbook" "$CLAUDE_DIR/skills/eeas-playbook"
link "$MASTER/lang/$LANG_CODE/skills/eeas-teams" "$CLAUDE_DIR/skills/eeas-teams"

echo "== settings.json =="
managed=(--managed "$MASTER/profiles/default.json")
if [[ "$PROFILE" != default ]]; then managed+=(--managed "$MASTER/profiles/$PROFILE.json"); fi
# Back up only when the merge will really change something (a no-op run must not leave a "backup" of the new state).
plan="$(python3 -I "$MASTER/scripts/merge_settings.py" --target "$CLAUDE_DIR/settings.json" "${managed[@]}" --dry-run)"
if grep -q ' set ' <<<"$plan"; then copy_backup "$CLAUDE_DIR/settings.json"; fi
dry_flag=()
if (( DRY )); then dry_flag=(--dry-run); fi
python3 -I "$MASTER/scripts/merge_settings.py" --target "$CLAUDE_DIR/settings.json" "${managed[@]}" ${dry_flag[@]+"${dry_flag[@]}"}

if (( CODEX )) && [[ -d "$CODEX_DIR" ]]; then
  echo "== Codex ($CODEX_DIR) =="
  link "$MASTER/codex/AGENTS.md" "$CODEX_DIR/AGENTS.md"
  if [[ -n "$CODEX_MODEL" ]]; then
    python3 -I - "$CODEX_DIR/config.toml" "$DRY" "$BACKUP/$(flat "$CODEX_DIR/config.toml")" "$CODEX_MODEL" <<'PY'
import os
import re
import shutil
import sys

path, dry, backup, model = sys.argv[1], sys.argv[2] == "1", sys.argv[3], sys.argv[4]
try:
    text = open(path, encoding="utf-8").read()
except FileNotFoundError:
    print("  skip    config.toml not found")
    raise SystemExit(0)

# Top-level keys live before the first [table].
head, sep, rest = text.partition("\n[")
line = f'model = "{model}"'
if re.search(r"(?m)^model\s*=", head):
    new_head = re.sub(r"(?m)^model\s*=.*$", line, head, count=1)
else:
    new_head = head.rstrip("\n") + "\n" + line + "\n"

if new_head == head:
    print(f"  ok      config.toml (default model already {model})")
elif dry:
    print(f"  [dry-run] config.toml: default model -> {model}")
else:
    os.makedirs(os.path.dirname(backup), exist_ok=True)
    if not os.path.exists(backup):
        shutil.copy2(path, backup)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(new_head + sep + rest)
    print(f"  set     config.toml: default model -> {model}")
PY
  fi
fi

if (( DRY )); then
  echo "dry-run: nothing was changed"
else
  mkdir -p "$CLAUDE_DIR"
  printf '%s\n' "$LANG_CODE" >"$CLAUDE_DIR/eeas.lang"
  printf '%s\n' "$PROFILE" >"$CLAUDE_DIR/eeas.profile"
  rm -f -- "$CLAUDE_DIR/cwcdt.lang" "$CLAUDE_DIR/cwcdt.profile"
  if [[ -d "$BACKUP" ]]; then echo "backup: $BACKUP"; fi
  "$MASTER/scripts/check.sh" || echo "(check.sh reported issues above)"
fi
