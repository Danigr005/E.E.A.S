# EEAS — Specialized Agent and Subagent Teams

Claude leads; subagents and Codex execute; the owner approves the plan and the commit. Common layer (this file) + teams (`teams/<name>/`).
Source: the EEAS repo (`readlink -f ~/.claude/CLAUDE.md`). `~/.claude/CLAUDE.md`, `rules/eeas` and `skills/eeas-*` are links: **edit the repo,
never the links.** Detail: skill `eeas-playbook`; teams: skill `eeas-teams`.

## Teams
- The project's team is in `.claude/eeas-team`; a hook injects its instructions at session start ("EEAS · active team"). Follow them.
- No team: ask ONCE which one (hook's list), save it with `eeas-teams` and continue. No hook: read `.claude/eeas-team` and
  `teams/<team>/lang/en/TEAM.md`.
- Changes only when the owner asks. New teams: `eeas-teams`.

## Delegate to Codex (plugin `codex@openai-codex`)
Standing authorization: delegate without asking when **all four** hold: specified (what, files, interface), bounded (own files, one writer per
file), machine-verifiable (test/typecheck/build/lint) and no design decision. If one fails, it stays with Claude.
- Codex: tests from spec, mechanical refactor, CRUD/boilerplate, types and lint, docs, read-only reviews, long background tasks.
  Claude: plan, architecture, design, cross-module changes, UI, security, integration, merge.
- Writing: `/codex:rescue --background --model <m> --effort <e>` in a separate branch/worktree, with a brief (files, interface, acceptance
  command, "no commit or push"). Review: `/codex:review`, `/codex:adversarial-review`, `/astra-review`. Models and effort: `eeas-playbook`.
- Claude reviews the diff and runs the acceptance check before accepting. No secrets in the brief. Codex review gate off. If Codex hits its
  limit, the task returns to Claude without asking.

## Waves (linked sessions)
Standing authorization: with an approved plan and 2+ long, independent pieces that share no files, or with the master near its context limit,
use `start_session` (own worktree). Small work, research and reviews: `ecc:` subagents or direct. Each brief: owned files, definition of
"done", where the plan is, no push or merge. The master coordinates, reviews each diff, integrates and asks for OK on commit and merge.
Nothing to `main`/`master` without OK. Protocol: `eeas-playbook`.

## Context and tokens
- Stable model and effort within a task. `/clear` between unrelated tasks; `/compact` at natural breaks.
- Read only what you need (grep or ranges). Broad searches → `Explore`/subagent with a short summary. Filter long output; never dump logs.
- Subagents only to isolate context or parallelize; self-contained brief. Long state → `save-session`; owner facts → memory.
- Before an `orch-*` workflow or a wave, estimate the cost (agent count) and pick the lightest flow.

## On compaction keep
Goal and approved plan; decisions and reasons; touched files and test state; pending items; linked sessions (id → piece); `save-session`
paths. Drop long outputs and discarded explorations.

## Owner preferences
- With the user, **Spanish**; code, identifiers and commits, **English**.
- No push, PR or merge to `main` without explicit OK. Secrets never in code, logs or chat.
- Gates: the owner only approves the plan, confirms the commit and authorizes push/merge/deletions. Never ask them to pick an agent, skill, command or hook.
