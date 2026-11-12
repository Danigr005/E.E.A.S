# Changelog

## Unreleased
- **EEAS (Specialized Teams of Agents and Subagents).** The repo is now a collection of teams over a mandatory common layer. `core/` holds the shared
  rules; `lang/<l>/CLAUDE.md` is the common layer + team router (Claude↔Codex split, waves, tokens, gates); `teams/<id>/` holds each team.
- Per-project team persistence: `.claude/eeas-team` + SessionStart hook (`scripts/eeas-session.py`) + skill `eeas-teams` + `scripts/eeas-team.sh`.
- CWCDT is now the team **Projects Master Dev Team** (`teams/projects-master`). New team **Spec Kit Dev Team** (`teams/spec-kit`) on GitHub spec-kit.
- New team **Architecture Review Team** (`teams/arquitectura`): reads building plans, judges viability against the Spanish CTE, proposes corrections. 10 `arq-*` agents, 6 skills (`plano-*`, `cte-verificacion`), `arq` toolchain (Python 3.12 venv: ezdxf, ifcopenshell, pdfium, shapely, OpenCV…), local copy of the official CTE texts (`arq cte`). Installed per project by `setup.sh`; `bootstrap.sh` restores the tools on a new machine.
- Toolbox labels are ours: `ecc.lock` → `toolbox.lock`, `ECC-src/` → `toolbox-src/`, `scripts/ecc-update.sh` → `scripts/toolbox-update.sh` (`ECC_REPO` → `TOOLBOX_REPO`). The third-party plugin keeps its id `ecc@ecc`.
- Renames: `cwcdt-playbook` → `eeas-playbook`, `rules/cwcdt` → `core/rules` (linked as `~/.claude/rules/eeas`), state files `cwcdt.*` → `eeas.*`.
- `scripts/bootstrap.sh`: one-shot restore on a new machine (toolbox plugins + apply + check). README "New laptop" section.

## 0.1.0 — 2026-11-05
First public release of CWCDT (Code With Codex Dev Team).

### Methodology
- Operating manual in English and Spanish (`lang/`): router table, two gates, four-point Codex delegation rule, waves, token habits, compaction instructions.
- On-demand `cwcdt-playbook` skill: model and effort table, brief template, delegation flow, waves protocol.
- One core rule (`rules/cwcdt/common/core.md`) replacing ten ECC common rules; per-language rules kept.

### Tooling
- `scripts/`: `apply` (links, profile merge, optional Codex default model), `check`, `revert`, `measure`, `ecc-update`, `test-sandbox`.
- Profiles: `default` and an example `ts-py-rust` stack profile.
- Status line with context, cache, 5h and 7d usage.

### Measured (reference setup)
- Prompt of the first real request 81.3k → 60.4k tokens (−26%); memory files −73%. See `docs/TOKEN-ECONOMY.md`.

### Tested with
Claude Code 2.1.234, ECC 2.2.3 (`b38be6a`), Codex CLI 0.164 with plugin 1.0.6, Linux.
