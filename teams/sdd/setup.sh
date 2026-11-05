#!/usr/bin/env bash
# Prepare a project for SDD Dev Team: spec-kit scaffold with Claude and Codex integrations. Idempotent.
#   teams/sdd/setup.sh [project-dir]
set -euo pipefail

DIR="${1:-.}"
export PATH="$HOME/.local/bin:$PATH"

if ! command -v specify >/dev/null 2>&1; then
  command -v uv >/dev/null 2>&1 || { echo "uv is required: https://docs.astral.sh/uv/" >&2; exit 1; }
  uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
fi

cd "$DIR"
if [[ ! -d .specify ]]; then
  # --force would overwrite existing project files; only allow it on a fresh directory unless the owner opts in.
  others="$(find . -mindepth 1 -maxdepth 1 ! -name .git ! -name .claude | head -1)"
  if [[ -n "$others" && "${EEAS_SDD_FORCE:-0}" != 1 ]]; then
    echo "$(pwd) already has files and no .specify/: spec-kit init could overwrite them. Re-run with EEAS_SDD_FORCE=1 if that is fine." >&2
    exit 3
  fi
  specify init --here --force --non-interactive --integration claude
fi
if ! grep -q '"codex"' .specify/integration.json 2>/dev/null; then
  specify integration install codex --integration-options="--skills"
fi
echo "SDD ready in $(pwd): $(specify --version)"
