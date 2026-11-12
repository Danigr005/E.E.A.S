#!/usr/bin/env bash
# Prepare the Architecture Review Team. Idempotent.
#   teams/arquitectura/setup.sh [project-dir]     tools + project install
#   teams/arquitectura/setup.sh --tools-only      only the machine-level part (used by bootstrap.sh)
# Machine level: Python 3.12 venv with pinned deps, `arq` launcher on PATH, local copy of the official CTE texts.
# Project level: team skills and agents copied into <project>/.claude, plus a permission for `arq`.
# Env: EEAS_ARQ_VENV (venv path), EEAS_ARQ_HOME (data dir), EEAS_ARQ_SKIP_FETCH=1 (skip the CTE download).
set -euo pipefail

TEAM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="$HOME/.local/bin:$PATH"
VENV="${EEAS_ARQ_VENV:-$HOME/.local/share/eeas/arquitectura-venv}"
DATA="${EEAS_ARQ_HOME:-$HOME/.local/share/eeas/arquitectura}"
TOOLS_ONLY=0
DIR=""
for arg in "$@"; do
  case "$arg" in
    --tools-only) TOOLS_ONLY=1 ;;
    -*) echo "usage: $0 [--tools-only | project-dir]" >&2; exit 2 ;;
    *) DIR="$arg" ;;
  esac
done
if [[ -n "$DIR" && ! -d "$DIR" ]]; then echo "arquitectura: project directory not found: $DIR" >&2; exit 2; fi

command -v uv >/dev/null 2>&1 || { echo "uv is required: https://docs.astral.sh/uv/" >&2; exit 1; }

echo "== arquitectura: Python environment =="
if [[ ! -x "$VENV/bin/python" ]]; then
  uv venv --python 3.12 "$VENV"
fi
uv pip install --quiet --python "$VENV/bin/python" -r "$TEAM_DIR/requirements.txt"
"$VENV/bin/python" -c "import ezdxf, ifcopenshell, pypdfium2, pdfplumber, shapely, cv2, pytesseract, Pynite.FEModel3D" \
  || { echo "arquitectura: dependency import check failed" >&2; exit 1; }

echo "== arquitectura: launcher =="
mkdir -p "$DATA" "$HOME/.local/bin"
if [[ -d "$DATA/tools" && ! -L "$DATA/tools" ]]; then echo "arquitectura: $DATA/tools is a real directory; remove it by hand" >&2; exit 1; fi
ln -sfn "$TEAM_DIR/tools" "$DATA/tools"
launcher="$HOME/.local/bin/arq"
if [[ -e "$launcher" && ! -L "$launcher" ]]; then
  echo "arquitectura: $launcher exists and is not a link; leaving it alone" >&2
else
  ln -sfn "$TEAM_DIR/tools/arq" "$launcher"
fi

for tool in tesseract pdftoppm pdftotext; do
  command -v "$tool" >/dev/null 2>&1 || echo "warning: '$tool' not found; plan OCR/rendering/CTE text needs it (poppler, tesseract)" >&2
done
command -v tesseract >/dev/null 2>&1 && ! tesseract --list-langs 2>/dev/null | grep -qx spa \
  && echo "note: tesseract has no Spanish data (spa); OCR runs in English, accents may be lost. Install tesseract-data-spa for better OCR." >&2
if ! command -v dwg2dxf >/dev/null 2>&1 && ! command -v ODAFileConverter >/dev/null 2>&1; then
  echo "note: no DWG converter (dwg2dxf/ODAFileConverter). DWG plans must be exported to DXF or PDF. Not installed here: it needs sudo/AUR."
fi

echo "== arquitectura: official CTE texts =="
if [[ "${EEAS_ARQ_SKIP_FETCH:-0}" == 1 ]]; then
  echo "skipped (EEAS_ARQ_SKIP_FETCH=1)"
else
  EEAS_ARQ_HOME="$DATA" "$TEAM_DIR/tools/arq" cte fetch || echo "warning: CTE download failed; retry later with 'arq cte fetch'" >&2
fi

if [[ $TOOLS_ONLY -eq 1 || -z "$DIR" ]]; then
  echo "arquitectura tools ready (use setup.sh <project-dir> to install the team into a project)"
  exit 0
fi

echo "== arquitectura: project install ($DIR) =="
mkdir -p "$DIR/.claude/skills" "$DIR/.claude/agents"
for skill in "$TEAM_DIR"/skills/*/; do
  name="$(basename "$skill")"
  rm -rf "${DIR:?}/.claude/skills/$name"
  cp -a "$skill" "$DIR/.claude/skills/$name"
done
cp -a "$TEAM_DIR"/agents/*.md "$DIR/.claude/agents/"

# Allow the read-only/copy-writing `arq` tool without a prompt per call; merge, never replace.
python3 -I - "$DIR/.claude/settings.local.json" <<'PY'
import json, sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text()) if path.exists() else {}
allow = data.setdefault("permissions", {}).setdefault("allow", [])
for rule in ("Bash(arq:*)",):
    if rule not in allow:
        allow.append(rule)
path.write_text(json.dumps(data, indent=2) + "\n")
PY
echo "Architecture Review Team installed in $DIR: $(ls "$TEAM_DIR"/agents | wc -l) agents, $(ls "$TEAM_DIR"/skills | wc -l) skills"
