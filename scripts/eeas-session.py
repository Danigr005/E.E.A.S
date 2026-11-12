#!/usr/bin/env python3
"""SessionStart hook: inject the instructions of the team assigned to the current project.

Looks for .claude/eeas-team (one line: the team id) from the session's cwd upwards. Prints the hook JSON
with the team's TEAM.md as additional context, or a prompt to choose a team when none is assigned.
"""
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

MASTER = Path(__file__).resolve().parent.parent
CLAUDE_DIR = Path(os.environ.get("CLAUDE_DIR", Path.home() / ".claude"))
TEAM_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
MARKER = Path(".claude") / "eeas-team"


def read_state(name: str, default: str) -> str:
    for prefix in ("eeas", "cwcdt"):
        path = CLAUDE_DIR / f"{prefix}.{name}"
        if path.is_file():
            return path.read_text(encoding="utf-8").strip() or default
    return default


def find_marker(start: Path):
    for directory in (start, *start.parents):
        candidate = directory / MARKER
        if candidate.is_file():
            return candidate
    return None


def list_teams() -> list:
    teams = []
    for manifest in sorted((MASTER / "teams").glob("*/team.json")):
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            teams.append(f"- {data['id']}: {data['name']} — {data.get('description', '')}")
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return teams


def team_text(team_id: str, lang: str):
    for code in (lang, "es", "en"):
        path = MASTER / "teams" / team_id / "lang" / code / "TEAM.md"
        if path.is_file():
            return path.read_text(encoding="utf-8", errors="replace")
    return None


def build_context(cwd: Path) -> str:
    marker = find_marker(cwd)
    lang = read_state("lang", "es")
    if marker is None:
        return (
            "EEAS · no team assigned to this project (no .claude/eeas-team). Ask the owner ONCE which team to use, "
            f"then save it with skill eeas-teams (repo: {MASTER}). Available teams:\n" + "\n".join(list_teams())
        )
    team_id = marker.read_text(encoding="utf-8", errors="replace").strip()
    text = team_text(team_id, lang) if TEAM_ID.match(team_id) else None
    if text is None:
        return (
            f"EEAS · {marker} names team '{team_id}', which does not exist. Tell the owner and ask which team to use "
            "(skill eeas-teams). Available teams:\n" + "\n".join(list_teams())
        )
    return f"EEAS · active team: {team_id} (set in {marker}; change it only if the owner explicitly asks)\n\n{text}"


def start_team_services(cwd: Path) -> None:
    """Run the background services the owner registered for the project's team (CLAUDE_DIR/eeas.services/<team>).

    One command per line (shlex syntax, `#` comments). Each runs detached and is never waited for, so the session starts
    at once; commands must be idempotent (SessionStart also fires on resume, clear and compact). Projects without a team,
    or whose team has no services file, start nothing.
    """
    marker = find_marker(cwd)
    if marker is None:
        return
    team_id = marker.read_text(encoding="utf-8", errors="replace").strip()
    if not TEAM_ID.match(team_id):
        return
    services = CLAUDE_DIR / "eeas.services" / team_id
    if not services.is_file():
        return
    for line in services.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            subprocess.Popen(shlex.split(line), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True, cwd=str(cwd) if cwd.is_dir() else None)
        except (OSError, ValueError):
            continue  # a broken service line must not break the session


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    cwd = Path(str(payload.get("cwd") or os.getcwd()))
    try:
        start_team_services(cwd)
    except Exception:  # services are a convenience: the team context below matters more
        pass
    try:
        context = build_context(cwd)
    except Exception as error:  # a session-start hook must never fail the session
        context = f"EEAS · could not load the team ({type(error).__name__}). Check .claude/eeas-team and the EEAS repo at {MASTER}."
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}}))


if __name__ == "__main__":
    main()
