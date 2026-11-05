#!/usr/bin/env bash
# Manage teams (E.E.A.S.).
#   scripts/eeas-team.sh list
#   scripts/eeas-team.sh show [project-dir]
#   scripts/eeas-team.sh set <team-id> [project-dir]   assigns the team to the project and runs the team's setup, if any
set -euo pipefail
# shellcheck source=common.sh
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

USAGE="usage: $0 list | show [dir] | set <team-id> [dir]"
cmd="${1:-}"

team_field() { python3 -I -c 'import json, sys; print(json.load(open(sys.argv[1])).get(sys.argv[2], ""))' "$MASTER/teams/$1/team.json" "$2"; }

case "$cmd" in
  list)
    for manifest in "$MASTER"/teams/*/team.json; do
      id="$(basename "$(dirname "$manifest")")"
      printf '%s\t%s\n' "$id" "$(team_field "$id" name)"
    done
    ;;
  show)
    dir="$(cd "${2:-.}" && pwd)"
    if [[ -f "$dir/.claude/eeas-team" ]]; then cat "$dir/.claude/eeas-team"; else echo "(no team)"; fi
    ;;
  set)
    id="${2:?$USAGE}"
    dir="${3:-.}"
    [[ "$id" =~ ^[a-z0-9][a-z0-9-]*$ && -f "$MASTER/teams/$id/team.json" ]] || { echo "unknown team '$id' (try: $0 list)" >&2; exit 2; }
    mkdir -p "$dir/.claude"
    dir="$(cd "$dir" && pwd)"
    setup="$(team_field "$id" setup)"
    if [[ -n "$setup" ]]; then "$MASTER/teams/$id/$setup" "$dir"; fi
    printf '%s\n' "$id" >"$dir/.claude/eeas-team"
    echo "team '$id' assigned to $dir"
    ;;
  *) echo "$USAGE" >&2; exit 2 ;;
esac
