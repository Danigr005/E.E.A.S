---
name: eeas-teams
description: Manage EEAS teams (specialized teams of agents and subagents): list, assign or switch a project's team, and create new teams. Use it when the hook says the project has no team, or when the owner asks to switch teams or create one.
---

# EEAS team management

EEAS repo: `dirname "$(dirname "$(readlink -f ~/.claude/CLAUDE.md)")"` (the script resolves it itself). A team = folder `teams/<id>/` with
`team.json` and `lang/<es|en>/TEAM.md`. The common layer (Claude↔Codex split, tokens, waves) lives in `CLAUDE.md` and applies to all.

## Assign or switch a project's team
1. Only when the owner asks, or the project has no team (ask once, showing `list`).
2. `scripts/eeas-team.sh set <id> <project-dir>` writes `.claude/eeas-team` and runs the team's `setup` if it has one (Spec Kit scaffolds spec-kit).
3. Tell the owner the change applies fully next session; in this one, read `teams/<id>/lang/en/TEAM.md` and follow it right away.
- Query: `scripts/eeas-team.sh list` / `show [dir]`.
- Switching never deletes project files; the previous team's setup leaves its files (`.specify/`…) intact.

## Create a new team
1. Ask the owner (max 3 questions) what the team is for and which tools/agents it uses.
2. Create `teams/<id>/team.json` (`id`, `name`, `description`, optional `setup`) and `teams/<id>/lang/en/TEAM.md` (+ `es/`): specialization, cycle,
   tools. Use `teams/projects-master` and `teams/spec-kit` as models.
3. `TEAM.md` does NOT repeat the common layer; only the specialization. State which part goes to Codex (same four-conditions rule).
4. If something must be installed, put it in `teams/<id>/setup.sh` (idempotent, receives the project dir).
5. Test with `scripts/eeas-team.sh set <id> <test-folder>` and `scripts/check.sh`. Commit only with the owner's OK.
