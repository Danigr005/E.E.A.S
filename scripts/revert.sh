#!/usr/bin/env bash
# Undo scripts/apply.sh using one of its backups (default: the most recent = undo the last apply).
#   scripts/revert.sh [--original | <backup-dir>]
# --original uses the oldest backup, i.e. the state before EEAS was ever applied.
set -euo pipefail
# shellcheck source=common.sh
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

case "${1:-}" in
  "") BACKUP="$(backups_oldest_first | tail -1)" ;;
  --original) BACKUP="$(backups_oldest_first | head -1)" ;;
  *) BACKUP="$1" ;;
esac
if [[ -z "$BACKUP" || ! -d "$BACKUP" ]]; then
  echo "No backup found${BACKUP:+: $BACKUP}" >&2
  exit 2
fi

# A link created by apply.sh (or by an earlier layout of this repo) is removed; if the backup holds the original, it moves back.
restore_moved() {
  local dest="$1" saved="$BACKUP/$(flat "$1")"
  if [[ -L "$dest" ]]; then
    local target
    target="$(readlink "$dest")"
    if [[ ! -e "$dest" || "$(real "$dest")" == "$MASTER"/* || "$target" == */claude-setup/* ]]; then
      rm -- "$dest"
      echo "  removed  $dest"
    fi
  fi
  if [[ -e "$dest" || -L "$dest" ]]; then
    echo "  skip     $dest exists and is not one of our links; check it by hand"
    return
  fi
  if [[ -e "$saved" || -L "$saved" ]]; then
    mv -- "$saved" "$dest"
    echo "  restored $dest"
  fi
}

# Files merged or edited in place were copied into the backup, so copy them back.
restore_copied() {
  local dest="$1" saved="$BACKUP/$(flat "$1")"
  if [[ -f "$saved" ]]; then
    cp -a -- "$saved" "$dest"
    echo "  restored $dest"
  fi
}

echo "Restoring from $BACKUP"
restore_moved "$CLAUDE_DIR/CLAUDE.md"
restore_moved "$CLAUDE_DIR/rules/ecc"
restore_moved "$CLAUDE_DIR/rules/cwcdt"
restore_moved "$CLAUDE_DIR/rules/eeas"
restore_moved "$CLAUDE_DIR/skills/owner-playbook"
restore_moved "$CLAUDE_DIR/skills/cwcdt-playbook"
restore_moved "$CLAUDE_DIR/skills/eeas-playbook"
restore_moved "$CLAUDE_DIR/skills/eeas-teams"
restore_moved "$CODEX_DIR/AGENTS.md"
restore_copied "$CLAUDE_DIR/settings.json"
restore_copied "$CODEX_DIR/config.toml"
rm -f -- "$CLAUDE_DIR"/{eeas,cwcdt}.{lang,profile}
echo "Done."
